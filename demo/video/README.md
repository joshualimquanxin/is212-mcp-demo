# Backup video

Builds `demo/backup/mcp-demo-backup.mp4` (about 1:30, narrated, with burned-in subtitles
and a matching `.srt`) from two real recorded runs of the demo. `demo/backup/` is
gitignored.

Windows only. Needs Python 3.10+ and:

```
pip install pywinpty pyte edge-tts imageio-ffmpeg pillow
```

| Command | What it does |
|---|---|
| `python demo/video/build.py demo/video/script.json demo/backup/mcp-demo-backup` | Re-narrate and re-edit from the saved recordings. No new run, nothing touches Jira. |
| `python demo/video/recorder.py act1` | Re-record Act 1. **Real Jira writes** on LIB-3 (comment, In Review); run `/demo-reset` after. |
| `python demo/video/recorder.py act2` | Re-record the sandbox act. It answers No at the first approval. |

- `recorder.py` runs Claude Code with `demo/stage-settings.json` in a hidden
  pseudo-terminal, presses the approval keys, and saves every byte it draws to
  `demo/backup/rec/`. It stops without answering if Claude Code asks to trust a folder.
- `build.py` replays those bytes through a terminal emulator (`feed.py`,
  `termrender.py`), narrates `script.json` with edge-tts (this sends the narration text
  to Microsoft's speech service), holds or speeds up the picture to fit each line (every
  speed-up shows a "sped up" badge), and encodes with the ffmpeg bundled in imageio-ffmpeg.
- Change the narrator with `"voice"` in `script.json`, for example `en-SG-WayneNeural`
  or `en-SG-LunaNeural` for Singapore English. Shot times are offsets from when Enter
  was pressed (`enter+6.3`), because Claude Code v2.1.303 doesn't show tool names.
