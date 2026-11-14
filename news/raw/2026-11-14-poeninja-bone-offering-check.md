# poe.ninja: does the defence calculation include Bone Offering for KBoC Necromancers? Covens, collected 2026-11-14 (day 2)

Snapshot **2100-20261114-51085** (still served). Search `https://poe.ninja/poe1/api/builds/2100-20261114-51085/search?overview=covens&type=exp...` (protobuf, same decoder as the other 2026-11-14 files); character JSON `https://poe.ninja/poe1/api/builds/2100-20261114-51085/character?account=<acct>&name=<char>&overview=covens&type=exp`. Character and account names omitted.

## B1. KBoC Necromancers WITHOUT a Bone Offering gem
Exclusion on the all-gems dimension works: `allgems=!Bone Offering` (URL `%21Bone%20Offering`).
- count for `&skills=Kinetic%20Blast%20of%20Clustering&class=Necromancer&allgems=%21Bone%20Offering`: 66
- count for `&skills=Kinetic%20Blast%20of%20Clustering&class=Necromancer&allgems=Bone%20Offering`: 839
- count for `&skills=Kinetic%20Blast%20of%20Clustering&class=Necromancer`: 886
- B1 filter check: of 8 characters checked from the `allgems=!Bone Offering` table (highest level first), 8 have no Bone Offering gem

Lines (the 8 highest-level rows of the `allgems=!Bone Offering` table, each confirmed by the character JSON to carry no Bone Offering gem):
- N1: lvl 88; life 3,494; ES 1,441; EHP 12,435; phys max hit 4,935; block 44% / spell block 14%; shield: Beast Charm Titanium Spirit Shield [Rare]; Tempest Shield: no; Rumi's Concoction: no; Bone Offering gem: no; keystones: -; ascendancy notables: Plaguebringer, Corpse Pact, Mistress of Sacrifice
- N2: lvl 87; life 3,632; ES 1,915; EHP 22,008; phys max hit 5,863; block 49% / spell block 53%; shield: Miracle Guard Thorium Spirit Shield [Rare]; Tempest Shield: yes; Rumi's Concoction: yes; Bone Offering gem: no; keystones: -; ascendancy notables: Plaguebringer, Corpse Pact, Mistress of Sacrifice
- N3: lvl 84; life 2,559; ES 1,474; EHP 16,373; phys max hit 5,916; block 25% / spell block 6%; shield: Eagle Star Titanium Spirit Shield [Rare]; Tempest Shield: no; Rumi's Concoction: no; Bone Offering gem: no; keystones: Mind Over Matter; ascendancy notables: Plaguebringer, Corpse Pact, Commander of Darkness
- N4: lvl 83; life 2,749; ES 1,118; EHP 9,158; phys max hit 3,899; block 26% / spell block 22%; shield: Mind Rock Crimson Round Shield [Rare]; Tempest Shield: no; Rumi's Concoction: no; Bone Offering gem: no; keystones: -; ascendancy notables: Plaguebringer, Corpse Pact, Mistress of Sacrifice
- N5: lvl 80; life 2,428; ES 172; EHP 4,535; phys max hit 3,142; block 20% / spell block 0%; shield: Eclipse Solaris Faun's Horn [Unique]; Tempest Shield: no; Rumi's Concoction: no; Bone Offering gem: no; keystones: -; ascendancy notables: Plaguebringer, Corpse Pact, Mistress of Sacrifice
- N6: lvl 79; life 3,039; ES 237; EHP 6,801; phys max hit 3,365; block 24% / spell block 5%; shield: Vortex Barrier Mosaic Kite Shield [Rare]; Tempest Shield: no; Rumi's Concoction: no; Bone Offering gem: no; keystones: -; ascendancy notables: Plaguebringer, Corpse Pact, Mistress of Sacrifice
- N7: lvl 79; life 2,248; ES 962; EHP 8,170; phys max hit 3,743; block 22% / spell block 36%; shield: Corpse Guard Ivory Spirit Shield [Rare]; Tempest Shield: yes; Rumi's Concoction: no; Bone Offering gem: no; keystones: -; ascendancy notables: Plaguebringer, Corpse Pact, Mistress of Sacrifice
- N8: lvl 79; life 2,264; ES 1,006; EHP 9,924; phys max hit 3,270; block 33% / spell block 46%; shield: Brood Song Thorium Spirit Shield [Rare]; Tempest Shield: yes; Rumi's Concoction: no; Bone Offering gem: no; keystones: -; ascendancy notables: Plaguebringer, Corpse Pact, Mistress of Sacrifice

For comparison, the A1..A12 lines of 2026-11-14-poeninja-kboc-whispers.md (KBoC Necromancers without Whispers, levels 92-95, nearly all with Bone Offering): EHP median 46,595 (range 37,303-60,638); block 57-75% (median 75); spell block 69-75% (median 75).

## B2. Path of Building exports from the character JSON
The character JSON has a field `pathOfBuildingExport` (base64url + zlib PoB XML). Decoded for two characters; XMLs saved outside the repo as `C:\repos\drafts\poeninja-pob-necromancer-kboc-boneoffering.xml` and `C:\repos\drafts\poeninja-pob-elementalist-tendrils-staff.xml`.

**P1: KBoC Necromancer with Bone Offering** (highest-level row of `allgems=Bone Offering`; level 95, Chaos Inoculation + Ghost Reaver, Whispers of Infinity, Demon Ward Thorium Spirit Shield, Rumi's Concoction)
- Bone Offering: in an ENABLED skill group (slot Weapon 1: Spellslinger + Bone Offering + Tornado; group enabled="true", gem enabled="true"), gem level 20, quality 20.
- Tempest Shield: enabled group (slot Weapon 2: Assassin's Mark + Mark On Hit + Tempest Shield), level 20.
- Flasks marked active: all five (Flask 1-5 active="true"): Physician's Basalt Flask of the Lizard; Continuous Quicksilver Flask of the Cheetah; Dabbler's Silver Flask of the Mockingbird; Analyst's Diamond Flask of Stinging; Rumi's Concoction Granite Flask.
- Config inputs set: BrandsAttachedToEnemy=1; DisableEHPGainOnBlock=true; bandit=Alira; buffUnholyMight=true; conditionBeenHitByAttackRecently, conditionBeenHitRecently, conditionBlockedRecently, conditionConsumedCorpseRecently, conditionCritRecently, conditionEnemyBleeding, conditionEnemyChilled, conditionEnemyIgnited, conditionFullLife, conditionGainedPowerChargeRecently, conditionHaveEnergyShield, conditionMinionsDiedRecently, conditionSpawnedCorpseRecently, conditionUsedBrandRecently = true; multiplierNearbyEnemies=1; multiplierNearbyRareOrUniqueEnemies=1; multiplierRage=30; multiplierWitheredStackCount=15; pantheonMajorGod=TheBrineKing; pantheonMinorGod=Abberath; useFrenzyCharges=true; usePowerCharges=true. (Everything else is PoB default Placeholders: enemy level 84, enemy hit 2241 per element, etc.) The custom modifier block holds only tattoo-like lines (curse effect, chaos damage, movement speed, Withered effect).
- PlayerStat vs poe.ninja: EffectiveBlockChance 75 vs ninja block 75; EffectiveSpellBlockChance 75 vs ninja spell block 75; TotalEHP 88,710.5 vs ninja EHP 88,710; PhysicalMaximumHitTaken 8,595 vs ninja 8,595. (PoB Life 1 / ES 6,027 vs ninja life 1 / ES 6,027.) Identical: poe.ninja shows this PoB calculation.

**P2: Lightning Tendrils staff Elementalist** (highest-level row of `items=Xirgil's Crank`; level 94; same character as T1 / X1)
- No Bone Offering gem anywhere.
- Flasks marked active: all five (Experimenter's Quicksilver Flask of the Kakapo; Doctor's Silver Flask of Craft; Masochist's Sulphur Flask of the Owl; Perpetual Divine Life Flask of Sealing; Continuous Granite Flask of the Pangolin).
- Config inputs set: BrandsAttachedToEnemy=1; DisableEHPGainOnBlock=true; bandit=Eramir; buffArcaneSurge=true; conditionBeenHitByAttackRecently, conditionBeenHitRecently, conditionBlockedRecently, conditionConvergence, conditionCritRecently, conditionEnemyBleeding, conditionEnemyChilled, conditionEnemyIgnited, conditionEnemyOnConsecratedGround, conditionEnemyShocked, conditionGainedPowerChargeRecently, conditionMinionsDiedRecently, conditionOnConsecratedGround, conditionUsedBrandRecently = true; conditionEnemyChilledEffect=15; conditionShockEffect=21; infusedChannellingInfusion=true; multiplierNearbyEnemies=1; multiplierNearbyRareOrUniqueEnemies=1; pantheonMajorGod=Arakaali; pantheonMinorGod=Shakari; useEnduranceCharges=true; useInspirationCharges=true; usePowerCharges=true.
- PlayerStat vs poe.ninja: EffectiveBlockChance 63 vs 63; EffectiveSpellBlockChance 74 vs 74; TotalEHP 67,953.5 vs 67,953; PhysicalMaximumHitTaken 11,252 vs 11,252. Identical.
- Observation: both exports share the same always-on conditions (BeenHitRecently, BlockedRecently, EnemyIgnited/Bleeding/Chilled, UsedBrandRecently, MinionsDiedRecently) and all flasks active, which looks like a poe.ninja default config rather than each player's choice.

## B3. Block sum for P1
Sources read from the character JSON; tree stats from tools/pob_data/tree.json; gem values from Path of Building's src/Data/Skills/act_int.lua (GitHub master).

Gem data: Bone Offering L20 = minions +35% attack block, +34% spell block (L21: 35/35). Tempest Shield L20 = +25% spell block. Mistress of Sacrifice (allocated): Offering skills also affect you; Offerings have 50% reduced effect on you. Body armour (Arcane Vestment) implicit: 13% increased effect of Offerings. Effect on self taken as 100 - 50 + 13 = 63% (additive, assumed): attack 35 x 0.63 = 22.05 -> 22; spell 34 x 0.63 = 21.42 -> 21.

Attack block:
- Shield base (Thorium Spirit Shield) 25%
- Body armour implicit +5%
- Replica Reckless Defence jewel +6%
- Rumi's Concoction (marked active in PoB) +12% during effect
- No attack block on the passive tree, the 7 masteries, the amulet (Whispers of Infinity; anoint Force of Darkness = chaos penetration) or other gear.
- Sum without Bone Offering: **48%** (36% without Rumi's). With Bone Offering at 63% effect: **70%**; at full effect (35) it would be 83% -> capped 75. Reported: **75%**. Unresolved: 5 points between my 70 and the reported 75 (not found: another offering-effect source, a rounding rule, or a 3.30 change to the gem or node).

Spell block:
- Shield explicit 9%; jewel +5%; tree: 2x Shield Spell Damage and Spell Block +3% each, Arcane Sanctuary +8%, Mana and Spell Block +2% (16% total); Tempest Shield +25%; Rumi's +6%
- Sum without Bone Offering: **61%** (55% without Rumi's). With Bone Offering (+21): **82% -> capped 75**. Reported: **75%**.

So the reported 75/75 needs Bone Offering for both (48/61 without it); the poe.ninja figures are the PoB numbers with Bone Offering enabled and every flask active.
