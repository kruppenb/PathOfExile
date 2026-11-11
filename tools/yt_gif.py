#!/usr/bin/env python3
"""Cut short mapping GIFs out of YouTube build videos.

YouTube is blocked from Claude's cloud sessions, so run this on a normal PC
(Nick's desktop, or a Claude Remote Control session on it).

Setup (once):
    pip install -U yt-dlp imageio-ffmpeg
    (imageio-ffmpeg ships an ffmpeg binary; a system ffmpeg on PATH also works)

Usage:
    python tools/yt_gif.py                 # every clip in tools/mapping_clips.json
    python tools/yt_gif.py winter-orb-occultist kinetic-bolt-elementalist
    python tools/yt_gif.py --force         # redo clips that already exist
    python tools/yt_gif.py --width 480 --fps 12

Each clip becomes builds/media/<slug>.gif (and a still <slug>.jpg of the first
frame, handy for checking the clip shows mapping). Clips are ~8 s; keep them short
so each GIF stays under ~6 MB. Edit start/seconds in mapping_clips.json to move a clip.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CLIPS = REPO_ROOT / "tools" / "mapping_clips.json"
OUT = REPO_ROOT / "builds" / "media"


def find_ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("ffmpeg not found. Run: pip install -U imageio-ffmpeg")


def download_section(url: str, start: int, seconds: int, ffmpeg: str, workdir: Path) -> Path:
    import yt_dlp
    from yt_dlp.utils import download_range_func

    opts = {
        "format": "bv*[height<=720][ext=mp4]/bv*[height<=720]/b[height<=720]/b",
        "outtmpl": str(workdir / "clip.%(ext)s"),
        "download_ranges": download_range_func(None, [(start, start + seconds)]),
        "force_keyframes_at_cuts": True,
        "ffmpeg_location": ffmpeg,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    files = [p for p in workdir.iterdir() if p.name.startswith("clip.")]
    if not files:
        raise RuntimeError("download produced no file")
    return files[0]


def to_gif(src: Path, dest: Path, ffmpeg: str, width: int, fps: int, seconds: int) -> None:
    vf = f"fps={fps},scale={width}:-1:flags=lanczos"
    palette = src.with_name("palette.png")
    subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-t", str(seconds), "-i", str(src),
                    "-vf", f"{vf},palettegen=stats_mode=diff", str(palette)], check=True)
    subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-t", str(seconds), "-i", str(src), "-i", str(palette),
                    "-lavfi", f"{vf}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle",
                    "-loop", "0", str(dest)], check=True)
    subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-ss", "2", "-i", str(src), "-frames:v", "1",
                    "-vf", f"scale={width}:-1", str(dest.with_suffix(".jpg"))], check=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="*", help="only these clips (default: all)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--width", type=int, default=480)
    ap.add_argument("--fps", type=int, default=12)
    args = ap.parse_args()

    clips = json.loads(CLIPS.read_text(encoding="utf-8"))
    if args.slugs:
        clips = [c for c in clips if c["slug"] in args.slugs]
    ffmpeg = find_ffmpeg()
    OUT.mkdir(parents=True, exist_ok=True)

    failed = []
    for c in clips:
        dest = OUT / f"{c['slug']}.gif"
        if dest.exists() and not args.force:
            print(f"skip   {dest.name} (exists; --force to redo)")
            continue
        try:
            with tempfile.TemporaryDirectory() as tmp:
                src = download_section(c["url"], int(c["start"]), int(c["seconds"]), ffmpeg, Path(tmp))
                to_gif(src, dest, ffmpeg, args.width, args.fps, int(c["seconds"]))
            print(f"ok     {dest.name}  {dest.stat().st_size / 1e6:.1f} MB")
        except Exception as e:  # keep going on one bad clip
            failed.append(c["slug"])
            print(f"FAILED {c['slug']}: {e}")
    if failed:
        sys.exit(f"{len(failed)} clip(s) failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
