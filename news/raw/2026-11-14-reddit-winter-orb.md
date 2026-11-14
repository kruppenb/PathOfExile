# Reddit raw data: Winter Orb (Arctic Shift), collected 2026-11-14

Source: https://arctic-shift.photon-reddit.com/api (posts/search, comments/search), after=2026-11-13T19:00:00Z, subreddits PathOfExileBuilds, pathofexile. Authors omitted. Scores/comment counts are captured by the archive soon after posting and run low.

## Collection notes

- posts/search r/PathOfExileBuilds title='winter orb': 0 results (https://arctic-shift.photon-reddit.com/api/posts/search?subreddit=PathOfExileBuilds&after=2026-11-13T19%3A00%3A00Z&limit=100&sort=desc&fields=id%2Ctitle%2Cscore%2Cnum_comments%2Ccreated_utc%2Clink_flair_text%2Cselftext&title=winter+orb)
- FAILED (twice, skipped): https://arctic-shift.photon-reddit.com/api/posts/search?subreddit=PathOfExileBuilds&after=2026-11-13T19%3A00%3A00Z&limit=100&sort=desc&fields=id%2Ctitle%2Cscore%2Cnum_comments%2Ccreated_utc%2Clink_flair_text%2Cselftext&query=winter+orb -> HTTP Error 422: Unprocessable Entity b'{"data":null,"error":"Timeout. Maybe slow down a bit"}'
- posts/search r/PathOfExileBuilds selftext='winter orb': 0 results (https://arctic-shift.photon-reddit.com/api/posts/search?subreddit=PathOfExileBuilds&after=2026-11-13T19%3A00%3A00Z&limit=100&sort=desc&fields=id%2Ctitle%2Cscore%2Cnum_comments%2Ccreated_utc%2Clink_flair_text%2Cselftext&selftext=winter+orb)
- FAILED (twice, skipped): https://arctic-shift.photon-reddit.com/api/posts/search?subreddit=pathofexile&after=2026-11-13T19%3A00%3A00Z&limit=100&sort=desc&fields=id%2Ctitle%2Cscore%2Cnum_comments%2Ccreated_utc%2Clink_flair_text%2Cselftext&title=winter+orb -> HTTP Error 422: Unprocessable Entity b'{"data":null,"error":"Timeout. Maybe slow down a bit"}'
- FAILED (twice, skipped): https://arctic-shift.photon-reddit.com/api/posts/search?subreddit=pathofexile&after=2026-11-13T19%3A00%3A00Z&limit=100&sort=desc&fields=id%2Ctitle%2Cscore%2Cnum_comments%2Ccreated_utc%2Clink_flair_text%2Cselftext&query=winter+orb -> HTTP Error 422: Unprocessable Entity b'{"data":null,"error":"Timeout. Maybe slow down a bit"}'
- FAILED (twice, skipped): https://arctic-shift.photon-reddit.com/api/posts/search?subreddit=pathofexile&after=2026-11-13T19%3A00%3A00Z&limit=100&sort=desc&fields=id%2Ctitle%2Cscore%2Cnum_comments%2Ccreated_utc%2Clink_flair_text%2Cselftext&selftext=winter+orb -> HTTP Error 422: Unprocessable Entity b'{"data":null,"error":"Timeout. Maybe slow down a bit"}'
- comments/search r/PathOfExileBuilds body='winter orb': 0 hits (https://arctic-shift.photon-reddit.com/api/comments/search?subreddit=PathOfExileBuilds&body=winter+orb&after=2026-11-13T19%3A00%3A00Z&limit=100&sort=desc&fields=id%2Cscore%2Cbody%2Clink_id%2Ccreated_utc)
- comments/search r/pathofexile body='winter orb': 1 hits (https://arctic-shift.photon-reddit.com/api/comments/search?subreddit=pathofexile&body=winter+orb&after=2026-11-13T19%3A00%3A00Z&limit=100&sort=desc&fields=id%2Cscore%2Cbody%2Clink_id%2Ccreated_utc)
- Unique posts found: 0; comments fetched under them: 0; keyword comment hits: 1

# Posts matching 'winter orb'

(none)

# Comments mentioning 'winter orb'

- r/pathofexile link_id=t3_1xvtszg 2026-11-14 11:42 UTC [2] Just supply and demand. Last league a fuckton of people started aoe cold spells (specifically Winter Orb). That's no longer the case due to nerfs and probably the new boss-oriented league mechanic.

## Follow-up check (manual, same session)
- Retried posts/search r/pathofexile title='winter orb' once more: again "Timeout. Maybe slow down a bit" (skipped after second failure).
- Sanity check: comments/search r/PathOfExileBuilds body='orb' after the same date returned only 1 comment, so Arctic Shift's full-text index looks thin for this window rather than Winter Orb simply being absent. Re-run later for a fuller picture.
