# Leveling plans from PoBs

Made with [`tools/pob_leveling.py`](../../tools/pob_leveling.py) (see [tools/README.md](../../tools/README.md#our-own-toolspob_levelingpy-pob--leveling-plan)).
One file per build: the PoB's trees in order with the points to take between them, gem setups, which gems to take/buy in each act, and the uniques used.

Keep the PoB code next to each plan as `<build>.pob.txt` so the plan can be regenerated when the tree/gem data updates for 3.30.

| Plan | Build | Source PoB | Made |
|---|---|---|---|
| [volatile-dead-spellslinger-elementalist.md](volatile-dead-spellslinger-elementalist.md) | Volatile Dead Spellslinger Elementalist (Ky), 19 act-by-act trees | PoB code embedded in the [mobalytics guide](https://mobalytics.gg/poe/builds/volatile-dead-spellslinger-elementalist-starter) | 2026-11-09 (3.29 PoB) |
| [bladefall-blade-blast-spellslinger-assassin.md](bladefall-blade-blast-spellslinger-assassin.md) | Bladefall + Blade Blast Spellslinger Assassin (Scorpius), Cobra Lash → Pconc → Bladefall | https://pobb.in/HxNbIbUatkWL ([guide](https://mobalytics.gg/poe/builds/shadow-league-start-leveling-scorpius)) | 2026-11-09 (3.29 PoB) |
| [power-siphon-trickster.md](power-siphon-trickster.md) | Power Siphon (AFANA). The forum guide is filed as Assassin, but this PoB is a **Trickster**. Trees named by point count | https://pobb.in/ie_9DLFzpq6P ([forum guide](https://www.pathofexile.com/forum/view-thread/3459073)) | 2026-11-09 (3.29 PoB) |

These are samples made from 3.29 guides to test the tool. Regenerate from the guide's 3.30 PoB once Nick picks a build.
