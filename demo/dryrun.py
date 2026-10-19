"""Run the demo prompt headless and print a timeline of what the agent did.

Usage (from the repo root):
    python demo/dryrun.py                 # LIB-3, the live-demo prompt
    python demo/dryrun.py --story LIB-1   # the backup story
    python demo/dryrun.py --model opus    # pin a model for this run

The three "human approval" tools are pre-approved for the run, so the timeline
measures agent time only. Add roughly 3 x 3 s for the live approval clicks.
Raw events are written to demo/logs/<timestamp>-<story>.jsonl.
"""

import argparse
import datetime as dt
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROMPT = (ROOT / "demo" / "prompt.txt").read_text(encoding="utf-8").strip()

APPROVAL_TOOLS = [
    "mcp__github__create_pull_request",
    "mcp__claude_ai_Atlassian_MCP__addOrEditJiraIssueComment",
    "mcp__claude_ai_Atlassian_MCP__transitionJiraIssue",
]


def child_env():
    """The environment for the headless run.

    A GitHub token saved as a Windows *User* variable is invisible to a shell
    started before it was set, so read it from the registry when it is missing.
    CLAUDECODE is dropped so the run also works from inside a Claude Code session.
    """
    env = os.environ.copy()
    env.pop("CLAUDECODE", None)
    if sys.platform == "win32" and "GITHUB_PERSONAL_ACCESS_TOKEN" not in env:
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                env["GITHUB_PERSONAL_ACCESS_TOKEN"] = winreg.QueryValueEx(
                    key, "GITHUB_PERSONAL_ACCESS_TOKEN")[0]
        except OSError:
            pass
    return env


def brief(name, inp):
    if name == "Bash":
        return inp.get("command", "")[:90]
    if name in ("Read", "Edit", "Write"):
        return str(inp.get("file_path", "")).replace(str(ROOT), "").lstrip("\\/")
    if name.startswith("mcp__"):
        keys = [k for k in ("issueIdOrKey", "fileId", "title", "transitionName", "head")
                if k in inp]
        return ", ".join(f"{k}={inp[k]}" for k in keys)
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--story", default="LIB-3")
    ap.add_argument("--model", default=None)
    args = ap.parse_args()

    prompt = PROMPT.replace("LIB-3", args.story)
    claude = shutil.which("claude")
    if not claude:
        sys.exit("claude not found on PATH")

    cmd = [claude, "-p", prompt, "--output-format", "stream-json", "--verbose",
           "--allowedTools", ",".join(APPROVAL_TOOLS)]
    if args.model:
        cmd += ["--model", args.model]

    logs = ROOT / "demo" / "logs"
    logs.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = logs / f"{stamp}-{args.story}.jsonl"

    print(f"prompt : {prompt}")
    print(f"log    : {log_path.relative_to(ROOT)}")
    print("-" * 72)

    t0 = time.monotonic()
    started = {}
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace", cwd=ROOT,
                            env=child_env())
    with log_path.open("w", encoding="utf-8") as log:
        for line in proc.stdout:
            t = time.monotonic() - t0
            log.write(line)
            line = line.strip()
            if not line.startswith("{"):
                continue
            ev = json.loads(line)
            kind = ev.get("type")
            if kind == "system" and ev.get("subtype") == "init":
                servers = ", ".join(f"{s.get('name')}={s.get('status')}"
                                    for s in ev.get("mcp_servers", []))
                print(f"{t:6.1f}s  init  model={ev.get('model')}  mcp: {servers}")
            elif kind == "assistant":
                for block in ev.get("message", {}).get("content", []):
                    if block.get("type") == "text" and block.get("text", "").strip():
                        print(f"{t:6.1f}s  say   {block['text'].strip()[:100]}")
                    elif block.get("type") == "tool_use":
                        started[block["id"]] = t
                        print(f"{t:6.1f}s  call  {block['name']}  {brief(block['name'], block.get('input', {}))}")
            elif kind == "user":
                for block in ev.get("message", {}).get("content", []):
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        t_start = started.get(block.get("tool_use_id"), t)
                        flag = "ERROR " if block.get("is_error") else ""
                        print(f"{t:6.1f}s  done  {flag}({t - t_start:.1f}s)")
            elif kind == "result":
                print("-" * 72)
                print(f"{t:6.1f}s  end   turns={ev.get('num_turns')}  "
                      f"api_ms={ev.get('duration_api_ms')}  cost=${ev.get('total_cost_usd', 0):.2f}  "
                      f"{ev.get('subtype')}")
    proc.wait()
    print(f"exit {proc.returncode}")


if __name__ == "__main__":
    main()
