# YouTube build videos

Claude can't open YouTube from the cloud, so `tools/yt_transcript.py` runs on Nick's PC
and saves each video's description, chapters and full transcript to `videos/raw/`.
Claude then reads those and writes the short summaries below.

## How to add videos

On Nick's PC (or ask Claude to do it through Remote Control):

```bash
pip install -U yt-dlp youtube-transcript-api
python tools/yt_transcript.py https://www.youtube.com/watch?v=VIDEO_ID
python tools/yt_transcript.py --from-md builds/wand-and-spell-shortlist.md   # every link in a file
git add videos && git commit -m "Add video transcripts" && git push
```

Then ask Claude to "summarize the new videos in videos/raw".

## Summaries

_None yet._
