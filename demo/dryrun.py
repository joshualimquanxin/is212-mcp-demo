"""Run the demo prompt headless and print a timeline of what the agent did.

Usage (from the repo root):
    python demo/dryrun.py                  # LIB-3; Jira writes are refused, nothing is written
    python demo/dryrun.py --writes         # also post the comment and move the card (then /demo-reset)
    python demo/dryrun.py --model sonnet   # pin a model for this run

It uses the same stage settings as the live sessions (plugins and auto-memory off).
Headless mode ignores the project's allow list, so it is passed explicitly. Without
--writes the two Jira writes are not pre-approved, so headless mode refuses them: the
run touches only the local files (undo with demo/reset.ps1) and the timeline shows
when the agent reached the first approval, counted from when every MCP server was
connected (on stage the session is already connected before you press Enter). Add
about 2 x 3 s for the live approval clicks. Raw events are written to
demo/logs/<timestamp>-<story>.jsonl.
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
SETTINGS = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))

APPROVAL_TOOLS = [
    "mcp__claude_ai_Atlassian_MCP__addOrEditJiraIssueComment",
    "mcp__claude_ai_Atlassian_MCP__transitionJiraIssue",
]


def brief(name, inp):
    if name == "Bash":
        return inp.get("command", "")[:90]
    if name in ("Read", "Edit", "Write"):
        return str(inp.get("file_path", "")).replace(str(ROOT), "").lstrip("\\/")
    if name.startswith("mcp__"):
        keys = [k for k in ("issueIdOrKey", "fileId", "transitionName", "commentBody")
                if k in inp]
        return ", ".join(f"{k}={str(inp[k])[:120]}" for k in keys)
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--story", default="LIB-3")
    ap.add_argument("--model", default=None)
    ap.add_argument("--writes", action="store_true",
                    help="pre-approve the Jira comment and transition (writes to Jira)")
    args = ap.parse_args()

    prompt = PROMPT.replace("LIB-3", args.story)
    claude = shutil.which("claude")
    if not claude:
        sys.exit("claude not found on PATH")

    allowed = SETTINGS["permissions"]["allow"] + (APPROVAL_TOOLS if args.writes else [])
    cmd = [claude, "-p", prompt, "--output-format", "stream-json", "--verbose",
           "--settings", str(ROOT / "demo" / "stage-settings.json"),
           "--allowedTools", ",".join(allowed)]
    if args.model:
        cmd += ["--model", args.model]

    logs = ROOT / "demo" / "logs"
    logs.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = logs / f"{stamp}-{args.story}.jsonl"

    print(f"prompt : {prompt}")
    print(f"writes : {'pre-approved (real Jira writes)' if args.writes else 'refused'}")
    print(f"log    : {log_path.relative_to(ROOT)}")
    print("-" * 72)

    env = os.environ.copy()
    env.pop("CLAUDECODE", None)  # so the run also works from inside a Claude Code session
    t0 = time.monotonic()
    started, first_write, ready_at, waits = {}, None, None, set()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace", cwd=ROOT, env=env)
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
                servers = ev.get("mcp_servers", [])
                if all(s.get("status") == "connected" for s in servers):
                    ready_at = t
                listing = ", ".join(f"{s.get('name')}={s.get('status')}" for s in servers)
                print(f"{t:6.1f}s  init  model={ev.get('model')}  mcp: {listing}")
            elif kind == "assistant":
                for block in ev.get("message", {}).get("content", []):
                    if block.get("type") == "text" and block.get("text", "").strip():
                        print(f"{t:6.1f}s  say   {block['text'].strip()[:100]}")
                    elif block.get("type") == "tool_use":
                        started[block["id"]] = t
                        if block["name"] == "WaitForMcpServers":
                            waits.add(block["id"])
                        if block["name"] in APPROVAL_TOOLS and first_write is None:
                            first_write = t
                        print(f"{t:6.1f}s  call  {block['name']}  {brief(block['name'], block.get('input', {}))}")
            elif kind == "user":
                for block in ev.get("message", {}).get("content", []):
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        t_start = started.get(block.get("tool_use_id"), t)
                        if block.get("tool_use_id") in waits and not block.get("is_error"):
                            ready_at = t
                        flag = "ERROR " if block.get("is_error") else ""
                        print(f"{t:6.1f}s  done  {flag}({t - t_start:.1f}s)")
            elif kind == "result":
                print("-" * 72)
                if first_write is not None and ready_at is not None:
                    print(f"first approval {first_write - ready_at:.1f}s after all MCP servers "
                          f"were connected (servers ready at {ready_at:.1f}s)")
                print(f"{t:6.1f}s  end   turns={ev.get('num_turns')}  "
                      f"api_ms={ev.get('duration_api_ms')}  cost=${ev.get('total_cost_usd', 0):.2f}  "
                      f"{ev.get('subtype')}")
    proc.wait()
    print(f"exit {proc.returncode}")


if __name__ == "__main__":
    main()
