# PoE 1 tools and build-sharing (as of Nov 2026)

The short version for a returning player: **Path of Building Community** is still the build planner,
**poe.ninja** is still the ladder/economy site, and **Maxroll / Mobalytics / poe-vault** are the main written guide sites.
The game itself now has a Currency Exchange and async trade, which changes how you use trade tools.

## Build planning

| Tool | URL | What it's for | Notes |
|---|---|---|---|
| Path of Building Community (PoB) | https://pathofbuilding.community · [GitHub](https://github.com/PathOfBuildingCommunity/PathOfBuilding) | Offline planner: tree, gems, gear, full DPS/defence calcs. Import any build via a "PoB code" or pastebin/pobb.in link | Maintained by LocalIdentity and team. Latest seen: **v2.67.2 (Aug 2026, 3.29)**. Expect a 3.30 update on/just after Nov 13 — update before planning. Has a built-in trade-search helper. Supports pob.codes export/import (2.66.0) |
| pobb.in / pob.codes | https://pobb.in · https://pob.codes | Paste a PoB code, get a shareable web page of the build | How streamers and guides share builds now, instead of raw pastebin |
| PoB Archives | https://pobarchives.com | Searchable archive of PoB builds, with meta/tier pages | |
| Official passive tree | https://www.pathofexile.com/passive-skill-tree | Official web tree | PoB is better for planning |

## Build discovery / meta

| Tool | URL | What it's for |
|---|---|---|
| **poe.ninja builds** | https://poe.ninja/builds | Every ladder character, filterable by class, skill, item, keystone. **The** place to check what's actually working in week 1–2 and what gear real players wear. Click any character to open it in PoB |
| poe.ninja economy | https://poe.ninja/economy | Prices of currency, uniques, div cards, gems — use to price your build |
| Maxroll | https://maxroll.gg/poe | Polished build guides with leveling sections, atlas strategy guides, tier lists |
| Mobalytics | https://mobalytics.gg/poe/builds | Creator-hosted build guides (many streamers publish here) |
| poe-vault | https://www.poe-vault.com/guides/builds-for-path-of-exile | Build guides tagged League Starter / budget |
| poebuilds.cc | https://www.poebuilds.cc/poe1 | Aggregates creator build videos and tier lists per league |
| YouTube / Twitch | — | League-start builds from creators (e.g. Lexyu, BalorMage, GhazzyTV, POEGuy, PathofEvening, VizzarD, Palsteron, Pohx, Ziggyd, Fubgun, Ghazzy) |

**Avoid treating RMT/currency shop blogs (aoeah, poecurrency, iggm, mmoexp, u4gm, etc.) as authoritative.** They show up in search but are often speculative.

## Trade, pricing, crafting

| Tool | URL | What it's for |
|---|---|---|
| Official trade site | https://www.pathofexile.com/trade | Item search. Since 3.27 supports async trade (buy without the seller being online) |
| In-game Currency Exchange | (Faustus in town) | Since 3.25. Swap currency in-game; no website needed for currency |
| Awakened PoE Trade | https://github.com/SnosMe/awakened-poe-trade | Hover an item, press a hotkey, see price checks. Still the standard overlay |
| Sidekick | https://github.com/Sidekick-Poe/Sidekick | Alternative price-check overlay |
| Craft of Exile | https://www.craftofexile.com | Crafting simulator and mod weights |
| poedb | https://poedb.tw/us/ | Datamined mods, bases, league data — fastest place for new-league info |

## Loot filters

| Tool | URL | Notes |
|---|---|---|
| FilterBlade (NeverSink) | https://www.filterblade.xyz | Customise NeverSink's filter and sync it to your account. **3.30's loot rework (item tiers, fewer drops) means use the updated filter for 3.30** |
| NeverSink filter | https://github.com/NeverSinkDev/NeverSink-Filter | Raw filter |

## Leveling helpers

| Tool | URL | What it's for |
|---|---|---|
| Exile UI (formerly Lailloken UI) | https://github.com/Lailloken/Exile-UI | Overlay: leveling tracker (zone-by-zone route + gem pickups from your PoB), lab tracker, map info |
| exile-leveling (HeartofPhos) | https://heartofphos.github.io/exile-leveling/ | Web leveling route; import a PoB to get gem/vendor steps |
| poelab.com | https://www.poelab.com | Daily Labyrinth layouts for ascending |

### Our own: `tools/pob_leveling.py` (PoB → leveling plan)

Reads a PoB code or link and writes a markdown leveling plan with only the leveling pieces:
every tree in the PoB in order (points to add between trees, grouped as "path to this notable", respecs, masteries, ascendancy order by lab),
every skill set with what changed, **which quest reward to take and what to buy from which vendor, act by act, for your class**,
item sets and the uniques the guide uses. Plans go in [`builds/leveling/`](../builds/leveling/).

Two outputs, picked by the file extension:
- **`.html` = the one-page glance sheet** (what to keep open while leveling). One card per act: gems to take/buy at each quest, link changes, passives in click order with a mini tree map (gold = this act), lab picks, leveling uniques, and a few must-do tips (trials, bandits, Quicksilver strongbox, move-speed boots recipe; from the exile-leveling speedrun route). Hover any chip for details. Layout borrowed from Nick's FFXIV hotbar kit.
- `.md` = the full reference (every tree, skill set and item set).

```
python tools/pob_leveling.py https://pobb.in/XXXXXXXX -o builds/leveling/<build>.html --label <guide URL>
python tools/pob_leveling.py https://pobb.in/XXXXXXXX -o builds/leveling/<build>.md
python tools/pob_leveling.py code.txt -o builds/leveling/<build>.md     # file with the code
python tools/pob_leveling.py --update-data                              # refresh tree/gem/quest data
```

- Plain Python 3.9+, no installs. Data lives in `tools/pob_data/` (GGG tree export + exile-leveling gem/quest data); refresh it once 3.30 data lands.
- Takes pobb.in, pastebin, poe.ninja/pob and maxroll.gg/poe/pob links, and guide pages that embed a PoB (mobalytics pages carry the code in a `"pobCode"` field).
- Those sites are **blocked from Claude's cloud sessions** (and from the device VM). Either run it on Nick's PC, have Claude start a Remote Control session on the PC to fetch the codes into `C:\repos\drafts\pob-codes\`, or paste the PoB code to Claude (PoB → Import/Export Build → Generate → Copy).
- If a PoB lists the endgame tree first, trees are shown sorted by points, and skill/item sets with a level or act in the title are moved first (`--keep-order` turns this off).
- The plan is only as good as the PoB: guides with several trees (e.g. "Level 12", "Act 3", "Level 40") and several skill sets give the best result. A single endgame tree still gives a sensible point order, but no level breakpoints.
- **Vendor recipes:** `python tools/vendor_recipes.py` (on Nick's PC; poewiki is blocked in the cloud) saves poewiki's full recipe list to `tools/pob_data/vendor_recipes.json`. The sheet's Act 1 card then lists the recipes that fit the build's early main skill (move-speed boots and resist rings always; spell damage / +1 element spell gems for spells; +% phys / added damage for attacks; minion helmet for minions), using RePoE skill tags. `--show <word>` searches the whole list. Re-run after a league launch.
- After the plan exists, the `poe1-leveling-guide-builder` skill can turn it into an act-by-act HTML guide.

## Wikis and reference

- **poewiki.net** (community wiki, the current one — the old Fandom wiki is outdated): https://www.poewiki.net
- poedb: https://poedb.tw/us/
- Official patch notes forum: https://www.pathofexile.com/forum/view-forum/patch-notes
- Announcements forum: https://www.pathofexile.com/forum/view-forum/announcements

## Where Claude looks for guides (and what it can't reach)

| Source | Can Claude read it? | Use |
|---|---|---|
| Mobalytics build pages | Mostly yes (some pages error) | Main source for creator guides; each has tags (Starter, patch) and pros/cons |
| poe-vault guides | Yes | League-starter tagged guides, creator hubs (Ghazzy, Lexyu, BalorMage) |
| Maxroll build guides | **No** (blocks automated reading) | Titles found through search only |
| poe.ninja builds | **No data** (page loads data with JavaScript; the API is closed to this environment) | Nick can check it directly, see below |
| YouTube | **Not directly** (blocked) | Run `tools/yt_transcript.py` on Nick's PC to save transcripts to `videos/raw/`, then Claude reads them. See [videos/README.md](../videos/README.md) |
| Reddit | **No** (blocked) | — |
| RMT shop blogs (aoeah, iggm, poecurrency, accountshark) | Yes | Use for news roundups only; treat tier lists as opinion |

### Checking early-league popularity on poe.ninja yourself
poe.ninja keeps **time-machine snapshots** for each league (hour-3/6/12/18, day-1 to day-6, week-1 onward). For last league:
- Day 3: https://poe.ninja/poe1/builds/allflame?timemachine=day-3
- Week 1: https://poe.ninja/poe1/builds/allflame?timemachine=week-1
Filter by skill (e.g. Kinetic Fusillade, Spark) to see how many played it and what they wore. A screenshot pasted into chat is enough for Claude to read.

## Also available here

This Claude project has two skills that work well with the knowledge base:
- `poe1-leveling-guide` — full passive tree data with a pathfinding script for leveling tree order.
- `poe1-leveling-guide-builder` — makes an act-by-act HTML leveling guide for a chosen build.

Use them once a build is picked.

Sources: [PoB releases](https://github.com/PathOfBuildingCommunity/PathOfBuilding/releases),
[maxroll PoB partnership](https://maxroll.gg/poe2/news/pob2-release-and-pob-team-partnership), plus general knowledge for long-standing tools
(verify any link that 404s; tools do get renamed).
