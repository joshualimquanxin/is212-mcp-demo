"""Drive an interactive Claude Code session in a hidden pseudo-terminal and record it.

Writes an asciinema-v2 style .cast (every byte the TUI drew, with timestamps) plus a
markers JSON (when each beat appeared on screen) for the renderer.

    python demo/video/recorder.py act1      # REAL Jira writes on LIB-3; run /demo-reset after
    python demo/video/recorder.py act2      # the sandbox act; answers No

Act 1 presses 1 at each approval (real Jira writes). Act 2 presses 3 (No) at its first
approval. Aborts without answering if Claude Code shows its workspace-trust prompt.
"""

import argparse
import json
import os
import pathlib
import re
import shutil
import sys
import threading
import time

from winpty import PtyProcess

from feed import Feeder

REPO = pathlib.Path(__file__).resolve().parents[2]
OUT = REPO / "demo" / "backup" / "rec"
COLS, ROWS = 120, 30
SETTINGS_OVERRIDE = None

RE_APPROVAL = re.compile(r"Do you want to (proceed|make this edit|allow)")
RE_BUSY = re.compile(r"esc to interrupt", re.I)
RE_TRUST = re.compile(r"trust (the files in )?this folder|Do you trust", re.I)
READY_MARK = "writes ask first"          # our status line, shown once the TUI is up

BEATS_ACT1 = {
    "jira": "getJiraIssue",
    "drive": "read_file_content",
    "edit": "Update(",
    "pytest": "pytest",
}
BEATS_ACT2 = {
    "read_note": "read_note",
    "save_note": "save_note",
}


def child_env():
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("CLAUDE", "VSCODE_")) and k not in ("TERM_PROGRAM", "TERM_PROGRAM_VERSION")}
    env["TERM"] = "xterm-256color"
    env["COLORTERM"] = "truecolor"
    return env


class Session:
    def __init__(self, argv, cwd):
        self.feeder = Feeder(COLS, ROWS)
        self.screen = self.feeder.screen
        self.lock = threading.Lock()
        self.events = []                  # (t, data)
        self.queries = []
        self.t0 = time.monotonic()
        self.last_out = self.t0
        self.proc = PtyProcess.spawn(argv, cwd=str(cwd), env=child_env(), dimensions=(ROWS, COLS))
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()

    def now(self):
        return time.monotonic() - self.t0

    def _answer_queries(self, data):
        # Answer the terminal queries a real terminal would, so the TUI never waits on us.
        replies = []
        if "\x1b[6n" in data:
            y, x = self.screen.cursor.y, self.screen.cursor.x
            replies.append(f"\x1b[{y + 1};{x + 1}R")
        if re.search(r"\x1b\[0?c", data):
            replies.append("\x1b[?62;22c")
        if re.search(r"\x1b\[>0?c", data):
            replies.append("\x1b[>1;10;0c")
        if "\x1b]11;?" in data:
            replies.append("\x1b]11;rgb:1e1e/1e1e/1e1e\x1b\\")
        if "\x1b]10;?" in data:
            replies.append("\x1b]10;rgb:d4d4/d4d4/d4d4\x1b\\")
        for r in replies:
            self.queries.append((round(self.now(), 2), repr(r)))
            self.proc.write(r)

    def _read(self):
        while True:
            try:
                data = self.proc.read(65536)
            except EOFError:
                break
            if not data:
                if not self.proc.isalive():
                    break
                time.sleep(0.01)
                continue
            t = self.now()
            with self.lock:
                self.events.append((t, data))
                self.feeder.feed(data)
                self.last_out = time.monotonic()
            self._answer_queries(data)

    def text(self):
        with self.lock:
            return "\n".join(self.screen.display)

    def quiet_for(self):
        with self.lock:
            return time.monotonic() - self.last_out

    def write(self, s):
        self.proc.write(s)

    def wait(self, pred, timeout, what):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            if pred():
                return True
            time.sleep(0.1)
        print(f"  timeout waiting for {what}")
        return False

    def close(self, path):
        self.proc.write("/exit\r")
        if not self.wait(lambda: not self.proc.isalive(), 10, "exit"):
            self.proc.terminate(force=True)
        time.sleep(0.3)
        with path.open("w", encoding="utf-8") as f:
            f.write(json.dumps({"version": 2, "width": COLS, "height": ROWS}) + "\n")
            for t, data in self.events:
                f.write(json.dumps([round(t, 4), "o", data]) + "\n")


def run(act, story, test=False):
    OUT.mkdir(exist_ok=True)
    claude = shutil.which("claude")
    if act == "act1":
        cwd, settings = REPO, "demo/stage-settings.json"
        prompt = (REPO / "demo" / "prompt.txt").read_text(encoding="utf-8").strip().replace("LIB-3", story)
        # --test answers No at the first approval, so nothing is written to Jira
        beats, key, max_approvals = BEATS_ACT1, ("3" if test else "1"), (0 if test else 2)
    else:
        cwd, settings = REPO / "sandbox", "../demo/stage-settings.json"
        prompt = (REPO / "sandbox" / "prompt.txt").read_text(encoding="utf-8").strip()
        beats, key, max_approvals = BEATS_ACT2, "3", 1

    if SETTINGS_OVERRIDE:
        settings = SETTINGS_OVERRIDE
    s = Session([claude, "--settings", settings], cwd)
    marks = {"act": act, "prompt": prompt, "beats": {}, "approvals": [], "screens": {}}
    print(f"[{act}] started, waiting for the TUI")

    def ready():
        txt = s.text()
        return READY_MARK in txt and not RE_BUSY.search(txt)

    if not s.wait(lambda: ready() or RE_TRUST.search(s.text()), 90, "TUI ready"):
        marks["screens"]["stuck"] = s.text()
        s.close(OUT / f"{act}.cast")
        sys.exit(f"[{act}] TUI never became ready; see screen dump in markers")
    if RE_TRUST.search(s.text()):
        marks["screens"]["trust"] = s.text()
        (OUT / f"{act}.markers.json").write_text(json.dumps(marks, indent=1), encoding="utf-8")
        s.proc.terminate(force=True)
        sys.exit(f"[{act}] Claude Code is asking to trust {cwd}. Not answering it: the user must.")

    s.wait(lambda: s.quiet_for() > 2.0, 15, "startup to settle")
    time.sleep(25)                        # let every MCP server connect, as on stage
    marks["ready"] = s.now()
    s.write(prompt)
    time.sleep(2.5)                       # the prompt sits pre-typed, as on stage
    marks["screens"]["pretyped"] = s.text()
    marks["enter"] = s.now()
    s.write("\r")
    print(f"[{act}] Enter at {marks['enter']:.1f}s")

    showing = False
    deadline = time.monotonic() + 240
    while time.monotonic() < deadline:
        txt = s.text()
        for name, needle in beats.items():
            if name not in marks["beats"] and needle in txt:
                marks["beats"][name] = s.now()
                print(f"  {s.now():6.1f}s  {name}")
        approval = bool(RE_APPROVAL.search(txt))
        if approval and not showing:
            showing = True
            n = len(marks["approvals"])
            t_seen = s.now()
            time.sleep(0.8)               # let the prompt finish drawing
            marks["screens"][f"approval{n + 1}"] = s.text()
            press = key if n < max_approvals else "3"
            print(f"  {t_seen:6.1f}s  approval {n + 1}, pressing {press}")
            time.sleep(2.2)               # a human reads it before answering
            s.write(press)
            marks["approvals"].append({"seen": t_seen, "pressed": s.now(), "key": press})
            if act == "act2" or press == "3":
                time.sleep(3)
                break
        elif not approval and showing:
            showing = False
        if (marks["approvals"] or act == "act2") and not approval and not RE_BUSY.search(txt) \
                and s.quiet_for() > 4 and s.now() - marks["enter"] > 8:
            break
        time.sleep(0.1)

    s.wait(lambda: s.quiet_for() > 2.5 and not RE_BUSY.search(s.text()), 30, "final settle")
    marks["done"] = s.now()
    marks["screens"]["final"] = s.text()
    marks["queries"] = s.queries
    name = f"{act}-test" if test else act
    s.close(OUT / f"{name}.cast")
    (OUT / f"{name}.markers.json").write_text(json.dumps(marks, indent=1), encoding="utf-8")
    print(f"[{act}] done at {marks['done']:.1f}s, {len(s.events)} output chunks -> rec/{name}.cast")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("act", choices=["act1", "act2"])
    ap.add_argument("--story", default="LIB-3")
    ap.add_argument("--test", action="store_true", help="act1: answer No at the first approval (no Jira writes)")
    ap.add_argument("--settings", default=None, help="absolute path to a settings file instead of the stage settings")
    a = ap.parse_args()
    SETTINGS_OVERRIDE = a.settings
    run(a.act, a.story, a.test)
