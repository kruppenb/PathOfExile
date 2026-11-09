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

Read 2026-11-09 from the transcripts in `raw/`. Captions are YouTube's auto-generated ones, so some item names
were garbled. I only name items I'm confident about. All videos are **3.29 or older**, so re-check against 3.30 patch notes.

### Takeaways for Nick

- **Winter Orb Occultist** comes out best for Nick's rules. It's the main skill from about level 28 and stays that way. One creator
  reached all 4 Voidstones on a **5-link** with cheap uniques. It's tanky with CI and capped block, and it auto-targets.
  The main care point is mana: your mana regen has to cover its cost.
- **Kinetic Fusillade**. Self-cast is a few-divine build that gets to T16. One creator says it's squishy and will "100% get randomly
  one-shot" (topside tree, so softcore only). The ballista test hit T11–12 maps 4 hours in with plenty of damage, but died a lot.
  3.29 made KF *easier* early (less attack-speed homework) and a bit weaker at the top end.
- **Kinetic Blast of Clustering** breaks the "no late switch" rule. The videos level it as spell → Firestorm → Power Siphon totems,
  then swap to KBoC at 70–80 and to CI/chaos at 90+. Legi1 calls it B/B- tier and weak early after the 3.29 nerf.
- **Spark Archmage** is still "insanely strong" and very tanky per Big Ducks (75% block / 75% spell block). It's best in corridors
  and weak in open maps. The detailed endgame video is from 3.25 (2024), so its prices are old.
- The 3.30 "DoT Slinger" video is a 4-hour stream with little useful talk. It's a cold-DoT Spellslinger levelling setup (DoT, so less Nick's style).

### Winter Orb Occultist

| Video | Gist |
|---|---|
| [ronarray: 3.29 in-depth starter guide](https://www.youtube.com/watch?v=yn1MzoinnUw) (Jul 2026, 150k views) · [raw](raw/2026-07-19-ronarray-poe-3-29-winter-orb-occultist-build-in-d-yn1MzoinnUw.md) | WO was the big 3.29 winner (base projectiles 1 → 3). Play it right after level 28 and keep it to uber endgame. CI + capped block. Channelling gives a power charge per second via the caster mastery (level ~33). **Mana regen must exceed WO's cost per second** (set PoB to 3 s of channelling). Uniques to buy in order: Ralakesh's Impatience first, then Willclash, Tulfall, Malachai's Loop, Graven's Secret. Late game: Red Nightmare + Sanctuary for capped block, Safeguard anoint. Occultist outscales Elementalist late. Pact of Beidat (3.29) might add 6 projectiles but was untested. Guide + PoBs: [mobalytics](https://mobalytics.gg/poe/builds/winter-orb-occultist-witch-build-league-starter-to-endgame) |
| [SoloHood: started 3.29 with WO Occultist](https://www.youtube.com/watch?v=3oedKtr6Hls) · [raw](raw/2026-07-25-solohood-started-poe-3-29-with-winter-orb-occulti-3oedKtr6Hls.md) | Levels with **Freezing Pulse → Winter Orb** on the same cold/spell tree, so the swap is smooth. First uniques: **Bitterdream**, then **Mark of Submission**. Self-cast WO for clear plus a WO spell totem for bosses, and Herald of Ice. Comfortable at T8–10. [PoB](https://pobb.in/BhCgI7Yxt04n) |
| [SoloHood: WO Occultist to 4 Voidstones](https://www.youtube.com/watch?v=zYLg8-yYkoY) · [raw](raw/2026-07-28-solohood-winter-orb-occultist-to-4-voidstones-poe-zYLg8-yYkoY.md) | CI, ES leech for recovery. Got **2 Voidstones on a 5-link**. Key uniques: a projectile wand, Light of Lunaris shield, **Anathema** ring, so Arcanist Brand casts 3 curses on bosses. Rest is rare ES gear. Needs a dexterity source. Next big upgrade is pricier (power-charge boots). [PoB](https://pobb.in/GIh4XFQO9VLm) |
| [Devildoll: Velka boss fight](https://www.youtube.com/watch?v=qPs0HdPh0BA) | No captions. Short 3.29 boss kill with a power-stacker WO Occultist |

### Kinetic Fusillade

| Video | Gist |
|---|---|
| [Caliathlol: 3.29 self-cast KF Elementalist](https://www.youtube.com/watch?v=sPebNu-PKm0) · [raw](raw/2026-07-24-caliathlol-poe-3-29-selfcast-kinetic-fusillade-elem-sPebNu-PKm0.md) | 3.29 change: attack-speed scaling 200% → 125%, hover 0.7 → 0.5 s. That's a slight endgame nerf but makes levelling easier (less duration stacking). Kinetic Bolt → **double KF at level 12**. Golem ascendancy (4 golems). Stack flat added damage everywhere; CI by red maps; Prismweave early; 6-link before Voidstones. **"Squishy… you will 100% get randomly one-shot"**, softcore only. Few-divine budget to T16. Esh's Mirror and Thunderfist are big cheap damage upgrades. [PoB](https://pobb.in/In-zqnbz66RI) |
| [peuget2: 3.28 KF Hierophant](https://www.youtube.com/watch?v=5uQMm6JJKsU) · [raw](raw/2026-02-27-peuget2-poe-3-28-kinetic-fusillade-hierophant-le-5uQMm6JJKsU.md) | Hierophant for MoM + mana scaling (Elementalist/Champion are "glass cannon"). The "machine gun" effect needs the [calculator](https://nemrod10.github.io/KF/) + Warped Timepiece / Timeclasp. Author **doesn't like levelling with KF** before those items and levels with Power Siphon or KBoC instead. Arcane Cloak uptime is short, so damage is spiky. Pre-3.29, so the numbers are out of date |
| [Ventrua: 3.29 ballista test 1–80](https://www.youtube.com/watch?v=oXTR0Q1vK14) · [raw](raw/2026-07-11-ventrua-3-29-leaguestart-test-kinetic-fusillade-oXTR0Q1vK14.md) | 4-hour speedrun stream, recorded before the 3.29 nerf (the title was later changed to "nerfed by 40%"). Rolling Magma → Firestorm, then swap to KF ballistas at **level 31 after lab with an RRGB 4-link**. Use a wand of 1.5 attack time or slower. Hit T11–12 by hour 4 with campaign gear and plenty of damage, but **died a lot**. His fixes: better armour bases, Granite/Jade flask, block shield, Flesh and Stone. Totems need defences. [PoB](https://pobb.in/55b409ZnR0YF) |

### Kinetic Blast of Clustering Necromancer

| Video | Gist |
|---|---|
| [Legi1: 3.29 league-start primer](https://www.youtube.com/watch?v=lRjDLu8c6Dw) · [raw](raw/2026-07-24-legi1-kinetic-blast-of-clustering-necromancer-lRjDLu8c6Dw.md) | 3.29 nerf ≈ 15% less damage on low gear, 6–7% endgame. **"B / B- tier" starter**, weak early, struggles in early reds unless experienced; great for day-2/3 Breach and Legion. Kinetic Bolt → KF at 12 → KB at 28 → KBoC ~70. Converts to chaos with an Overwhelming Malice cluster, CI at ~90. Prismweave early. [Maxroll guide](https://maxroll.gg/poe/build-guides/league-starter/kinetic-blast-of-clustering-necromancer-league-starter) |
| [Tino: level 1–90](https://www.youtube.com/watch?v=AymYc83c6ZI) · [raw](raw/2026-07-20-tino-level-1-90-with-kinetic-blast-of-cluster-AymYc83c6ZI.md) | Spell (Rolling Magma / Flame Wall) → Firestorm act 3 → **Power Siphon ballistas act 7** → KBoC at 75–80. MoM in act 5 is optional. Malachai's Loop + power-charge uniques early. Spellslinger Tornado is "mandatory" with KB. Split Shot anoint. [PoB](https://pobb.in/Dr92No-Jkguh) |
| [Tino: day 2–3 update + loot rant](https://www.youtube.com/watch?v=5T8yx4dhd9E) · [raw](raw/2026-07-27-tino-poe-3-29-kinetic-blast-of-clustering-day-5T8yx4dhd9E.md) | Went full CI + chaos; wants 8–9k ES to feel comfortable (has 10k ES / 11k mana). Swapped to Mind Spiral helmet. The second half is a rant: **3.29 ground loot was awful** (4 divines in ~2 days of play) |

### Spark Archmage Hierophant

| Video | Gist |
|---|---|
| [Big Ducks: Spark Archmage is BACK (3.29)](https://www.youtube.com/watch?v=DpHXNVNeH88) · [raw](raw/2026-07-18-big-ducks-spark-archmage-hierophant-is-back-3-29-l-DpHXNVNeH88.md) | "Very tanky map blaster": 75 block / 75 spell block, big EHP. **Excels in tight corridors** (Toxic Sewers, Ritual, Ultimatum). 3.29 nerfs: Spark of the Nova −1 projectile, Arcane Cloak and Archmage slightly down. Pact of Beidat could add 6 projectiles. For levelling, Rolling Magma got hit hard and Fireball was buffed (Fireball → Firestorm). Helmet ideas used 3.29 Legion items that may not exist in 3.30. [Guide](https://mobalytics.gg/poe/builds/bigducks-spark-archmage-heirophant) |
| [anime princess: Archmage Spark endgame (30–100 div)](https://www.youtube.com/watch?v=MDDTlW1SsLY) · [raw](raw/2024-08-01-anime-princess-archmage-spark-endgame-build-guide-30-10-MDDTlW1SsLY.md) | **3.25 (2024)**, so prices are stale. Shopping list: 6-link Widowhail, Forbidden Flame/Flesh, a fractured quiver, Doppelgänger Guise (mitigation vs physical hits, its main weakness), Ravenous Passion, Glorious Vanity for MoM through ES. 30-div budget version keeps most of the power. Lightning leech is mandatory for sustain |
| [Kina: 3.25 7/7 uber bosses](https://www.youtube.com/watch?v=rkTF2B19IiM) | No captions. Description: weakest vs Sirus/Exarch (big arenas); "not cheap/efficient" |

### Other

| Video | Gist |
|---|---|
| [Desmo Saze: 3.30 practice, DoT Slinger Elementalist campaign](https://www.youtube.com/watch?v=sAPeJA7nWWc) · [raw](raw/2026-11-06-desmo-saze-3-30-league-start-practice-dot-slinger-e-sAPeJA7nWWc.md) | Stream VOD, mostly chatter. Uses Spellslinger to trigger **Vortex + Creeping Frost** from attacks, plus Cold Snap and golems. 3 h 43 campaign without prep; "DPS is crazy", but he expects it to get squishy after yellow maps. He plans to use it only to farm Heist and then swap to Eviscerate. [PoB](https://pobb.in/eDTjt-pgXaNy) |
