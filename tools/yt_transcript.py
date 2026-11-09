#!/usr/bin/env python3
"""Pull a YouTube video's transcript, chapters and description into a markdown note.

YouTube is blocked from Claude's cloud sessions, so run this on a normal PC
(Nick's desktop, or a Claude Remote Control session on it).

Setup (once):
    pip install -U yt-dlp youtube-transcript-api

Usage:
    python tools/yt_transcript.py https://www.youtube.com/watch?v=lRjDLu8c6Dw
    python tools/yt_transcript.py URL1 URL2 ...
    python tools/yt_transcript.py --from-md builds/wand-and-spell-shortlist.md
    python tools/yt_transcript.py --list urls.txt --out videos/raw

Each video becomes videos/raw/<upload-date>-<channel>-<title>-<id>.md with:
    - metadata (title, channel, date, length, views, link)
    - description (where creators put PoB links and timestamps)
    - chapters
    - the full transcript, grouped by chapter, with clickable timestamps
Videos already saved are skipped unless --force is given.

The notes are raw material. Claude reads them and writes the short summaries
in videos/README.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

ID_RE = re.compile(
    r"(?:youtube\.com/(?:watch\?(?:[^\s)\]]*&)?v=|shorts/|live/|embed/)|youtu\.be/)([A-Za-z0-9_-]{11})"
)
REPO_ROOT = Path(__file__).resolve().parent.parent


def video_ids(text: str) -> list[str]:
    seen, out = set(), []
    for vid in ID_RE.findall(text):
        if vid not in seen:
            seen.add(vid)
            out.append(vid)
    return out


def ts(seconds: float) -> str:
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def slug(text: str, n: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s[:n].strip("-") or "x"


# --------------------------------------------------------------------------- fetch
def fetch_metadata(vid: str) -> dict:
    import yt_dlp

    opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False)


def fetch_transcript_api(vid: str, langs: list[str]) -> tuple[list[dict], str]:
    """Return ([{start, text}], note) using youtube-transcript-api (supports 0.6 and 1.x)."""
    from youtube_transcript_api import YouTubeTranscriptApi

    if hasattr(YouTubeTranscriptApi, "get_transcript"):  # 0.6.x
        rows = YouTubeTranscriptApi.get_transcript(vid, languages=langs)
        return [{"start": r["start"], "text": r["text"]} for r in rows], "youtube-transcript-api"
    api = YouTubeTranscriptApi()  # 1.x
    fetched = api.fetch(vid, languages=langs)
    kind = "auto-generated" if getattr(fetched, "is_generated", False) else "creator captions"
    return [{"start": s.start, "text": s.text} for s in fetched], f"youtube-transcript-api ({kind})"


def fetch_transcript_ytdlp(info: dict, langs: list[str]) -> tuple[list[dict], str]:
    """Fallback: read the json3 caption track yt-dlp found."""
    import json
    import urllib.request

    for source, label in ((info.get("subtitles") or {}, "creator captions"),
                          (info.get("automatic_captions") or {}, "auto-generated")):
        for lang in langs + [k for k in source if k.startswith("en")]:
            for fmt in source.get(lang, []):
                if fmt.get("ext") == "json3":
                    with urllib.request.urlopen(fmt["url"], timeout=30) as r:
                        data = json.load(r)
                    rows = []
                    for ev in data.get("events", []):
                        text = "".join(seg.get("utf8", "") for seg in ev.get("segs") or [])
                        if text.strip():
                            rows.append({"start": ev.get("tStartMs", 0) / 1000, "text": text})
                    if rows:
                        return rows, f"yt-dlp ({label}, {lang})"
    raise RuntimeError("no caption track found")


# --------------------------------------------------------------------------- render
def clean(text: str) -> str:
    text = text.replace("\n", " ").replace("[Music]", "").replace("[music]", "")
    return re.sub(r"\s+", " ", text).strip()


def paragraphs(rows: list[dict], start: float, end: float, every: float) -> list[tuple[float, str]]:
    """Group caption rows between start and end into ~`every`-second paragraphs."""
    out, cur, cur_start = [], [], None
    for r in rows:
        if not (start <= r["start"] < end):
            continue
        if cur_start is None:
            cur_start = r["start"]
        cur.append(clean(r["text"]))
        if r["start"] - cur_start >= every and cur[-1][-1:] in ".?!" or r["start"] - cur_start >= every * 1.5:
            out.append((cur_start, " ".join(t for t in cur if t)))
            cur, cur_start = [], None
    if cur:
        out.append((cur_start, " ".join(t for t in cur if t)))
    return out


def render(vid: str, info: dict, rows: list[dict] | None, source: str, every: float) -> str:
    url = f"https://www.youtube.com/watch?v={vid}"
    title = info.get("title") or vid
    date = info.get("upload_date") or ""
    date_fmt = f"{date[:4]}-{date[4:6]}-{date[6:]}" if len(date) == 8 else "unknown"
    lines = [
        f"# {title}",
        "",
        f"- **Channel:** {info.get('channel') or info.get('uploader') or '?'}",
        f"- **Uploaded:** {date_fmt}",
        f"- **Length:** {ts(info.get('duration') or 0)}",
        f"- **Views:** {info.get('view_count') or '?'}",
        f"- **Link:** {url}",
        f"- **Transcript:** {source}",
        f"- **Fetched:** {dt.date.today().isoformat()} by tools/yt_transcript.py",
        "",
        "## Description",
        "",
        "```text",
        (info.get("description") or "(none)").strip(),
        "```",
        "",
    ]
    chapters = info.get("chapters") or []
    if chapters:
        lines += ["## Chapters", ""]
        for c in chapters:
            lines.append(f"- [{ts(c['start_time'])}]({url}&t={int(c['start_time'])}s) {c.get('title', '')}")
        lines.append("")

    lines += ["## Transcript", ""]
    if not rows:
        lines.append("_No transcript available._")
        return "\n".join(lines) + "\n"
    sections = chapters or [{"start_time": 0, "end_time": float("inf"), "title": None}]
    for c in sections:
        if c.get("title"):
            lines += [f"### {ts(c['start_time'])} {c['title']}", ""]
        end = c.get("end_time") or float("inf")
        for start, text in paragraphs(rows, c["start_time"], end, every):
            lines += [f"[{ts(start)}]({url}&t={int(start)}s) {text}", ""]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- main
def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("urls", nargs="*", help="YouTube URLs or 11-char video ids")
    p.add_argument("--from-md", action="append", default=[], help="pull every YouTube link out of a markdown file")
    p.add_argument("--list", help="text file with one URL per line")
    p.add_argument("--out", default=str(REPO_ROOT / "videos" / "raw"), help="output folder (default videos/raw)")
    p.add_argument("--lang", default="en,en-US,en-GB", help="preferred caption languages, comma separated")
    p.add_argument("--para", type=float, default=45, help="seconds of speech per transcript paragraph")
    p.add_argument("--force", action="store_true", help="re-fetch videos already saved")
    a = p.parse_args()

    text = " ".join(a.urls)
    for f in a.from_md + ([a.list] if a.list else []):
        text += "\n" + Path(f).read_text(encoding="utf-8")
    ids = video_ids(text) + [u for u in a.urls if re.fullmatch(r"[A-Za-z0-9_-]{11}", u)]
    ids = list(dict.fromkeys(ids))
    if not ids:
        p.error("no YouTube links found")

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    langs = [x.strip() for x in a.lang.split(",") if x.strip()]
    ok = fail = 0
    for vid in ids:
        existing = list(out.glob(f"*-{vid}.md"))
        if existing and not a.force:
            print(f"skip  {vid}  (already saved: {existing[0].name})")
            continue
        try:
            info = fetch_metadata(vid)
        except Exception as e:  # noqa: BLE001
            print(f"FAIL  {vid}  metadata: {e}", file=sys.stderr)
            fail += 1
            continue
        rows, source = None, "none"
        try:
            rows, source = fetch_transcript_api(vid, langs)
        except Exception as e1:  # noqa: BLE001
            try:
                rows, source = fetch_transcript_ytdlp(info, langs)
            except Exception as e2:  # noqa: BLE001
                source = f"unavailable ({type(e1).__name__}; yt-dlp: {e2})"
        date = info.get("upload_date") or "00000000"
        name = f"{date[:4]}-{date[4:6]}-{date[6:]}-{slug(info.get('channel') or '', 20)}-{slug(info.get('title'))}-{vid}.md"
        for old in existing:
            old.unlink()
        (out / name).write_text(render(vid, info, rows, source, a.para), encoding="utf-8")
        words = sum(len(r["text"].split()) for r in rows or [])
        print(f"saved {vid}  {words:>6} words  {name}")
        ok += 1
    print(f"\n{ok} saved, {fail} failed, folder: {out}")
    return 1 if fail and not ok else 0


if __name__ == "__main__":
    sys.exit(main())
