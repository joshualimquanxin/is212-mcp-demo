"""Build the backup video from the recordings: narration, edit, subtitles, encode.

    python demo/video/build.py demo/video/script.json demo/backup/mcp-demo-backup

script.json lists shots in order. Each shot shows one recording (or a card) between two
source times, with narration lines spoken over it. A shot lasts as long as its
narration: if the recording is shorter it holds the last frame; if longer it is sped
up (and a "sped up" badge shows), capped at max_speed.
"""

import array
import asyncio
import json
import pathlib
import subprocess
import sys
import wave

import edge_tts
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

from feed import Feeder
from termrender import TermRenderer

HERE = pathlib.Path(__file__).resolve().parent
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS, RATE = 1920, 1080, 30, 48000
F = r"C:\Windows\Fonts"
UI = ImageFont.truetype(rf"{F}\segoeui.ttf", 22)
UI_B = ImageFont.truetype(rf"{F}\seguisb.ttf", 22)
SUB = ImageFont.truetype(rf"{F}\seguisb.ttf", 38)
SMALL = ImageFont.truetype(rf"{F}\segoeui.ttf", 19)
CARD_T = ImageFont.truetype(rf"{F}\segoeuib.ttf", 64)
CARD_S = ImageFont.truetype(rf"{F}\segoeui.ttf", 34)
BG, FRAME, TITLE = (18, 18, 18), (30, 30, 30), (45, 45, 45)
ACT_COL = {"act1": (17, 168, 205), "act2": (229, 165, 10)}


# ---------- narration ----------

async def _tts(text, voice, rate, mp3):
    comm = edge_tts.Communicate(text, voice, rate=rate, boundary="SentenceBoundary")
    audio, sentences = bytearray(), []
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            audio += chunk["data"]
        elif chunk["type"] == "SentenceBoundary":
            sentences.append((chunk["offset"] / 1e7, (chunk["offset"] + chunk["duration"]) / 1e7, chunk["text"]))
    mp3.write_bytes(bytes(audio))
    return sentences


def tts(text, voice, rate, stem):
    mp3, wav = stem.with_suffix(".mp3"), stem.with_suffix(".wav")
    sentences = asyncio.run(_tts(text, voice, rate, mp3))
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(mp3), "-ac", "1", "-ar", str(RATE),
                    "-sample_fmt", "s16", str(wav)], check=True)
    with wave.open(str(wav)) as w:
        samples = array.array("h", w.readframes(w.getnframes()))
    if not sentences:
        sentences = [(0.0, len(samples) / RATE, text)]
    return samples, sentences


# ---------- recordings ----------

class Recording:
    def __init__(self, cast):
        with open(cast, encoding="utf-8") as f:
            self.header = json.loads(f.readline())
            self.events = [json.loads(line) for line in f]
        self.reset()

    def reset(self):
        self.feeder = Feeder(self.header["width"], self.header["height"])
        self.i = 0

    def seek(self, t):
        """Advance to source time t; returns how many events have been fed (a frame key)."""
        if self.i and self.events[self.i - 1][0] > t:
            self.reset()
        while self.i < len(self.events) and self.events[self.i][0] <= t:
            self.feeder.feed(self.events[self.i][2])
            self.i += 1
        return self.i


# ---------- drawing ----------

def wrap(text, font, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.getlength(trial) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def card(lines):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    title, *rest = lines
    y = H // 2 - 60 - 28 * len(rest)
    d.text(((W - CARD_T.getlength(title)) / 2, y), title, font=CARD_T, fill=(240, 240, 240))
    y += 100
    for line in rest:
        d.text(((W - CARD_S.getlength(line)) / 2, y), line, font=CARD_S, fill=(170, 170, 170))
        y += 52
    return img


def compose(term_img, shot, speed, subtitle, note):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    x0, y0 = (W - term_img.width) // 2, 20
    d.rounded_rectangle([x0 - 2, y0, x0 + term_img.width + 1, y0 + 40 + term_img.height + 2], 10, fill=FRAME)
    d.rounded_rectangle([x0 - 2, y0, x0 + term_img.width + 1, y0 + 40], 10, fill=TITLE)
    d.rectangle([x0 - 2, y0 + 30, x0 + term_img.width + 1, y0 + 40], fill=TITLE)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([x0 + 14 + i * 24, y0 + 13, x0 + 28 + i * 24, y0 + 27], fill=c)
    d.text((x0 + 100, y0 + 7), shot["window"], font=UI, fill=(200, 200, 200))
    badge = shot["badge"]
    bw = UI_B.getlength(badge) + 28
    bx = x0 + term_img.width - bw - 12
    d.rounded_rectangle([bx, y0 + 6, bx + bw, y0 + 34], 14, fill=ACT_COL[shot["act"]])
    d.text((bx + 14, y0 + 6), badge, font=UI_B, fill=(10, 10, 10))
    if speed > 1.25:
        sp = f"sped up {speed:.0f}x" if speed >= 1.95 else f"sped up {speed:.1f}x"
        sw = UI_B.getlength(sp) + 28
        d.rounded_rectangle([bx - sw - 10, y0 + 6, bx - 10, y0 + 34], 14, fill=(90, 90, 90))
        d.text((bx - sw + 4, y0 + 6), sp, font=UI_B, fill=(240, 240, 240))
    img.paste(term_img, (x0, y0 + 41))
    band_top = y0 + 41 + term_img.height + 8
    if subtitle:
        lines = wrap(subtitle, SUB, W - 240)[:2]
        lh = 50
        y = band_top + (H - band_top - 26 - lh * len(lines)) // 2
        for line in lines:
            d.text(((W - SUB.getlength(line)) / 2, y), line, font=SUB, fill=(250, 250, 250))
            y += lh
    d.text((W - SMALL.getlength(note) - 24, H - 30), note, font=SMALL, fill=(120, 120, 120))
    return img


# ---------- build ----------

def main(script_path, out_stem):
    script = json.loads(pathlib.Path(script_path).read_text(encoding="utf-8"))
    out_stem = pathlib.Path(out_stem)
    out_stem.parent.mkdir(parents=True, exist_ok=True)
    tmp = HERE.parent / "backup" / "tts"
    tmp.mkdir(exist_ok=True)
    voice, rate, max_speed = script["voice"], script.get("rate", "+0%"), script.get("max_speed", 6)
    gap, lead, tail = script.get("gap", 0.35), script.get("lead", 0.3), script.get("tail", 0.2)

    recs = {k: Recording(HERE / v) for k, v in script["recordings"].items()}
    marks = {k: json.loads((HERE / v).read_text(encoding="utf-8")) for k, v in script["markers"].items()}
    renderer = TermRenderer(120, 30, 26)

    def resolve(act, ref):
        """'enter', 'approval1.seen', 'beats.edit', 'done' or a number, plus optional '+1.5'."""
        if isinstance(ref, (int, float)):
            return float(ref)
        base, _, delta = ref.partition("+")
        m = marks[act]
        if base.startswith("approval"):
            n, field = base[len("approval"):].split(".")
            v = m["approvals"][int(n) - 1][field]
        elif base.startswith("beats."):
            v = m["beats"][base[6:]]
        else:
            v = m[base]
        return v + (float(delta) if delta else 0.0)

    # 1. narration and the timeline
    audio = array.array("h")
    subs, timeline, t_out, seg_no = [], [], 0.0, 0
    for shot in script["shots"]:
        start = t_out
        cursor = start + shot.get("lead", lead)
        for line in shot.get("say", []):
            seg_no += 1
            samples, sentences = tts(line, voice, rate, tmp / f"seg{seg_no:02d}")
            pos = int(cursor * RATE)
            if len(audio) < pos + len(samples):
                audio.extend([0] * (pos + len(samples) - len(audio)))
            audio[pos:pos + len(samples)] = samples
            for a, b, text in sentences:
                subs.append((cursor + a, cursor + b, text))
            cursor += len(samples) / RATE + gap
        narr = cursor - start + shot.get("tail", tail)
        if shot.get("card"):
            dur, speed = max(narr, shot.get("min", 1.5)), 1.0
        else:
            act = shot["act"]
            s0, s1 = resolve(act, shot["from"]), resolve(act, shot["to"])
            span = max(0.0, s1 - s0)
            dur = max(narr, shot.get("min", 0.0))
            if shot.get("realtime"):
                dur = max(dur, span)
            speed = 1.0 if span <= dur else min(span / dur, max_speed)
            dur = max(dur, span / speed)
            shot["_src"] = (s0, s1)
        timeline.append((start, start + dur, shot, speed))
        label = shot.get("badge", "card") if not shot.get("card") else "card: " + shot["card"][0]
        print(f"  {start:5.1f}s +{dur:4.1f}s  speed {speed:3.1f}x  {label}")
        t_out = start + dur
    total = t_out
    audio.extend([0] * (int(total * RATE) + RATE // 2 - len(audio)))
    wav_path = out_stem.with_suffix(".wav")
    with wave.open(str(wav_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(audio.tobytes())
    print(f"timeline {total:.1f}s, {len(subs)} subtitle lines")

    # 2. subtitles file
    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    srt = [f"{i}\n{ts(a)} --> {ts(b)}\n{text}\n" for i, (a, b, text) in enumerate(subs, 1)]
    out_stem.with_suffix(".srt").write_text("\n".join(srt), encoding="utf-8")

    # 3. frames -> ffmpeg
    mp4 = out_stem.with_suffix(".mp4")
    enc = subprocess.Popen([FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(wav_path),
                            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(mp4)],
                           stdin=subprocess.PIPE)
    note = script["note"]
    cache_key, cache_bytes, term_cache = None, None, {}
    for f in range(int(total * FPS)):
        T = f / FPS
        start, end, shot, speed = next(x for x in timeline if x[0] <= T < x[1] or x is timeline[-1])
        sub = next((s for s in subs if s[0] <= T < s[1]), None)
        sub_text = sub[2] if sub else None
        if shot.get("card"):
            key = ("card", id(shot), sub_text)
        else:
            s0, s1 = shot["_src"]
            t = min(s1, s0 + (T - start) * speed)
            rec = recs[shot["act"]]
            fed = rec.seek(t)
            key = (shot["act"], fed, id(shot), sub_text, round(speed, 2))
        if key != cache_key:
            if shot.get("card"):
                img = card(shot["card"])
                if sub_text:
                    d = ImageDraw.Draw(img)
                    lines = wrap(sub_text, SUB, W - 240)[:2]
                    y = H - 60 - 50 * len(lines)
                    for line in lines:
                        d.text(((W - SUB.getlength(line)) / 2, y), line, font=SUB, fill=(250, 250, 250))
                        y += 50
            else:
                tk = (shot["act"], fed)
                if tk not in term_cache:
                    term_cache.clear()
                    term_cache[tk] = renderer.render(rec.feeder.screen)
                img = compose(term_cache[tk], shot, speed, sub_text, note)
            cache_key, cache_bytes = key, img.tobytes()
        enc.stdin.write(cache_bytes)
        if f % (FPS * 10) == 0:
            print(f"  frame {f} / {int(total * FPS)}")
    enc.stdin.close()
    enc.wait()
    print("wrote", mp4, "and", out_stem.with_suffix(".srt"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
