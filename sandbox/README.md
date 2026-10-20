# Sandbox: MCP tool poisoning (classroom demonstration)

The "caution" half of Team 7's IS212 demo. It exists so the audience learns to
**defend** against a known MCP weakness.

## The idea

An MCP server tells the model what each tool does by sending a *description*.
The model cannot tell a description from an instruction. So if a server hides
an instruction inside a tool description, the model may follow it, using text
the user never sees in their own prompt.

`notes_server.py` has two tools, `save_note` and `read_note`. One paragraph,
hidden after a run of padding, is appended to `save_note`'s description, telling
the model to quietly read `secrets.txt` and put its contents into the note. The user asks for
a harmless standup note.

Reads are auto-approved here (`read_note` is in the allow list), exactly as Jira and
Drive reads are in the main folder, because that is how most people configure an
agent. Writes still ask. So whatever the model does, the run stops at the
`save_note` approval, and the arguments in that prompt show what it is about to save.

## Why it is safe

This is a sealed sandbox. Everything is fake and local.

- **The secret is fake.** `notes_server.py` writes a clearly-labelled dummy AWS
  key to `secrets.txt` at startup. It is not a real credential. The file is
  gitignored, so nothing credential-shaped is ever committed.
- **Nothing leaves the laptop.** The worst case copies the fake string from one
  local file into a local note (`notes.txt`). No network, no upload.
- **The read tool is fenced** to files sitting directly in this folder, so even the
  poisoned instruction cannot reach any real file on the machine.
- **Isolated from the main demo.** This folder has its own `.mcp.json` and settings
  that switch off Jira, Google Drive and circulation, so the poisoned server never
  sits next to the real ones.

## Run it

Rehearse without Claude (shows the visible and hidden parts of the description, works offline):

```
python sandbox/check_poison.py
```

Live, in its own Claude Code session opened in this folder:

```
cd sandbox
claude
```

Paste the prompt from `prompt.txt`. Do **not** pre-approve `save_note`: the
approval prompt is the whole point.

## The lesson

The protocol delivered both halves of the description faithfully. Nothing in MCP
separates a description from an instruction. What stops this is a human reading
the tool arguments before clicking Yes, sandboxing servers you did not write,
pinned and reviewed server versions, and least-privilege tools: the "Still on you"
slide.
