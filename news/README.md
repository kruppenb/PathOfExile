# Pre-league "what's new" digest

A repeatable check for the run-up to **3.30 Covens of Umbra (launch Fri Nov 13, 2026)** (ends at launch).
Each run reports only what's **new since the last run**: a short news summary, then what it means for Nick's build list.

- Runs automatically every 6 hours until league launch (last run Fri Nov 13, 18:47 UTC); a scheduled task posts the digest in the "Track pre-league news and build shifts" project thread.
- On demand: ask Claude in the project **"what's new?"** and it follows this file.
- Output: newest digest at the top of [digests.md](digests.md). What's been seen so far: [state.json](state.json).

## Procedure (for Claude)

1. **Load context.** `git pull` on `main`. Read [state.json](state.json) (`last_run`, `seen`, `ranking`, `patch_notes`),
   the Top picks + "Current call" table in [../builds/wand-and-spell-shortlist.md](../builds/wand-and-spell-shortlist.md),
   the "Look for" columns in [../leagues/3.30-nerf-watch.md](../leagues/3.30-nerf-watch.md), and Nick's rules (top of the shortlist).
2. **Check sources** (WebSearch, then a web-fetch agent for pages; curl is blocked for most PoE sites). Only things dated after `last_run` count.
   | Priority | Source | What to look for |
   |---|---|---|
   | 1 | pathofexile.com/forum/view-forum/patch-notes (readable). The announcements forum fails, so find GGG announcements through Reddit (next row) or search, then open the forum thread by its URL | 3.30.0 patch notes, hotfixes, announcements |
   | 1 | **Reddit via the Arctic Shift archive** (web-fetch agent; curl is blocked). List posts since `last_run`: `https://arctic-shift.photon-reddit.com/api/posts/search?subreddit=<sub>&after=<last_run ISO>&limit=100&sort=desc&fields=id,title,score,num_comments,created_utc,link_flair_text,url`. Do **r/pathofexile** (GGG-flaired posts land here first: patch notes, announcements, FAQ) and **r/PathOfExileBuilds** (player build threads, practice runs, starter reviews). If 100 come back, page with `before=<oldest created_utc>`. Comments: `.../api/comments/search?link_id=<id>&limit=100&fields=author,score,body`. Title search and `posts/ids` fail; reddit.com galleries are blocked. Scores are captured early and run low | New GGG posts; threads on shortlisted skills; new starter ideas that fit Nick |
   | 2 | Search "3.30 league starter" + each top-pick skill name (YouTube titles show up in search even though YouTube itself is blocked) | Creator videos/guides for 3.30. New videos worth hearing: ask Nick to run `tools/yt_transcript.py` on his PC |
   | 2 | mobalytics.gg/poe tier list + build pages, poe-vault.com starter lists, poebuilds.cc league page, pathofexile.com forum build sections | Tier list relabelled 3.30? New 3.30 guides for shortlisted skills |
   | 2 | Community practice-run sheet (linked in the shortlist's Community check) | New timed runs, especially for shortlisted builds |
   | 2 | maxroll.gg (blocked: titles via search only; Nick can screenshot the tier list) | Tier list updated for 3.30? |
   | 3 | poe.ninja/poe1/builds (after launch only; JS page, ask Nick for a screenshot) | What people actually play |
   | 3 | outputlag, sportskeeda, game news sites | Recaps (fine as pointers; verify against GGG) |
   GGG's announcement images (web.poecdn.com) are blocked from the cloud and from Nick's PC VM: say what the post covers and ask Nick for a screenshot if it matters.
   RMT/currency-shop sites (aoeah, poecurrency, iggm, mmoexp, u4gm, mmogah, ssegold, ezg, accountshark, timesaver) are speculative: label them *(RMT site)* and never move a build on their word alone.
3. **Judge each new item against the shortlist.**
   - Patch-note change to a "Look for" term → buff / nerf / neutral for that pick, with the exact quote. **Check the section heading first:** lines under "Ruthless-specific Changes" don't apply to Nick's trade league.
   - A new 3.30 guide or tier placement for a listed build → note it (raises confidence; a top-tier placement can move a pick up).
   - A **new build** that fits Nick's rules (trigger/CoC/Spellslinger, wand attacks, Spark-like or brand spells, pops the screen, tanky, bosses early under ~30 div, works from early levels, no melee/minions/totems/traps/mines, ideally hit not DoT) → propose it as a new entry.
   - Re-score with the shortlist formula (**Boss + Def + Pop/2**) when a rating changes, and compare with `ranking` in state.json to show ↑/↓.
4. **Write the digest** (template below) at the top of [digests.md](digests.md). Keep it under ~25 lines. Links for every claim.
5. **Don't edit the shortlist here.** Nick wants build-list changes made by the "Build PoE league knowledge base" project thread, which has the build context. Record findings in the digest (and patch-note results in [../leagues/3.30-nerf-watch.md](../leagues/3.30-nerf-watch.md)), then message that thread with what's new and the suggested rating/confidence changes.
6. **Update [state.json](state.json):** `last_run`, add new URLs to `seen` (keep it to the last ~150), set `ranking` to the current order, set `patch_notes` status.
7. **Commit and push to `main`** (no PRs): `News digest YYYY-MM-DD HH:MM UTC`.
8. **Post in the thread:** the digest text itself (short), with a link to digests.md. If nothing new: don't post (Nick doesn't need a ping) and skip the commit; on-demand runs still answer "nothing new since <time>".

## Digest template

```markdown
## YYYY-MM-DD HH:MM UTC (since <last_run>)

**News**
- <1-line item> ([source](url)) — one bullet each, most important first, max ~6

**Your build list**
| Change | Build | Why |
|---|---|---|
| ↑ / ↓ / 🆕 / ⚠ nerf / ✅ buff / — | ... | ... (quote/link) |

**Current top 5:** 1. … 2. … 3. … 4. … 5. …  (B + D + Pop/2)
**Next:** <what to watch for in the next run, e.g. patch notes due Nov 10>
```
