# Pre-league "what's new" digest

A repeatable check for the run-up to **3.30 Covens of Umbra (launch Fri Nov 13, 2026)** and launch week.
Each run reports only what's **new since the last run**: a short news summary, then what it means for Nick's build list.

- Runs automatically every 6 hours (a scheduled task posts the digest in the "Track pre-league news and build shifts" project thread).
- On demand: ask Claude in the project **"what's new?"** and it follows this file.
- Output: newest digest at the top of [digests.md](digests.md). What's been seen so far: [state.json](state.json).

## Procedure (for Claude)

1. **Load context.** `git pull` on `main`. Read [state.json](state.json) (`last_run`, `seen`, `ranking`, `patch_notes`),
   the Top picks + "Current call" table in [../builds/wand-and-spell-shortlist.md](../builds/wand-and-spell-shortlist.md),
   the "Look for" columns in [../leagues/3.30-nerf-watch.md](../leagues/3.30-nerf-watch.md), and Nick's rules (top of the shortlist).
2. **Check sources** (WebSearch, then a web-fetch agent for pages; curl is blocked for most PoE sites). Only things dated after `last_run` count.
   | Priority | Source | What to look for |
   |---|---|---|
   | 1 | pathofexile.com/forum/view-forum/patch-notes and /view-forum/announcements | 3.30.0 patch notes, hotfixes, launch/teaser posts |
   | 1 | GGG news on poe.ninja / reddit summaries via search ("3.30 patch notes", "3.30 balance") | Skill/ascendancy buffs and nerfs |
   | 2 | maxroll.gg/poe/tierlists/league-starter-build-tier-list, maxroll build guides | Tier list updated for 3.30? New/moved starters |
   | 2 | mobalytics.gg/poe, poe-vault.com, pathofexile.com forum build sections | New 3.30 guides for shortlisted skills or Nick-style builds |
   | 2 | Search "3.30 league starter" + each top-pick skill name (YouTube titles show up in search even though YouTube itself is blocked) | Creator videos/guides for 3.30 |
   | 3 | poe.ninja/poe1/builds (after launch only; JS page, ask Nick for a screenshot) | What people actually play |
   | 3 | outputlag, sportskeeda, game news sites | Recaps (fine as pointers; verify against GGG) |
   RMT/currency-shop sites (aoeah, poecurrency, iggm, mmoexp, u4gm, mmogah, ssegold, ezg, accountshark, timesaver) are speculative: label them *(RMT site)* and never move a build on their word alone.
3. **Judge each new item against the shortlist.**
   - Patch-note change to a "Look for" term → buff / nerf / neutral for that pick, with the exact quote.
   - A new 3.30 guide or tier placement for a listed build → note it (raises confidence; a top-tier placement can move a pick up).
   - A **new build** that fits Nick's rules (trigger/CoC/Spellslinger, wand attacks, Spark-like or brand spells, pops the screen, tanky, bosses early under ~30 div, works from early levels, no melee/minions/totems/traps/mines, ideally hit not DoT) → propose it as a new entry.
   - Re-score with the shortlist formula (**Boss + Def + Pop/2**) when a rating changes, and compare with `ranking` in state.json to show ↑/↓.
4. **Write the digest** (template below) at the top of [digests.md](digests.md). Keep it under ~25 lines. Links for every claim.
5. **Update the knowledge base only for solid changes:** GGG patch notes or multiple reputable guides. Edit the shortlist ratings/ranking table, nerf-watch, or the 3.30 league file, and say so in the digest. Single-source or RMT claims stay in the digest only.
6. **Update [state.json](state.json):** `last_run`, add new URLs to `seen` (keep it to the last ~150), set `ranking` to the current order, set `patch_notes` status.
7. **Commit and push to `main`** (no PRs): `News digest YYYY-MM-DD HH:MM UTC`.
8. **Post in the thread:** the digest text itself (short), with a link to digests.md. If nothing new: one line, "Nothing new since <time>", and skip the commit unless state changed.

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
