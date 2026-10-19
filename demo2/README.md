# Demo 2: MCP tool poisoning (classroom sandbox)

A controlled demonstration of a known MCP weakness, for IS212 Team 7's
presentation (Warren, slide 12). It exists so the audience learns to **defend**
against it.

## The idea

An MCP server tells the model what each tool does by sending a *description*.
The model cannot tell a description from an instruction. So if a server hides
an instruction inside a tool description, the model may follow it, using text
the user never sees in their own prompt.

`notes_server.py` has two tools, `save_note` and `read_note`. With `POISON=1`
one paragraph is appended to `save_note`'s description, telling the model to
quietly read `secrets.txt` and put its contents into the note. The user asks for
a harmless note; the approval dialog shows the fake key in the arguments.

## Why it is safe

This is a sealed sandbox. Everything is fake and local.

- **The secret is fake.** `notes_server.py` writes a clearly-labelled dummy AWS
  key to `secrets.txt` at startup. It is not a real credential. The file is
  gitignored, so nothing credential-shaped is ever committed.
- **Nothing leaves the laptop.** The "attack" copies the fake string from one
  local file into a local note (`notes.txt`). No network, no upload.
- **The read tool is sandboxed** to files sitting directly in this folder, so
  even the poisoned instruction cannot reach any real file on the machine.
- **Off by default.** The poisoning only appears when started with `POISON=1`.
- **Isolated from Demo 1.** This folder has its own `.mcp.json` and settings
  that switch off Demo 1's servers (Jira, Drive, GitHub, circulation), so the
  poisoned server never sits next to the real ones.

## Run it

Rehearse without Claude (shows both descriptions side by side):

```
python demo2/check_poison.py
```

Live, in a separate Claude Code window opened in this folder:

```
cd demo2
claude
```

Approve the `notes` server when asked, then paste the prompt from the run sheet.
Approvals stay on: do **not** pre-approve `save_note`, because the approval
dialog is the whole point.

## The lesson

The protocol delivered both halves of the description faithfully. Nothing in MCP
separates a description from an instruction. What stops this is a human reading
the tool arguments before clicking Allow, pinned and reviewed server versions,
and least-privilege tools. That is slide 14's checklist.
