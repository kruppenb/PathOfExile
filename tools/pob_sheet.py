"""One-page, glanceable HTML leveling sheet from a parsed PoB.

Called by pob_leveling.py when the output file ends in .html. One card per
act: gems to take/buy, links, the passives to click (in order, with a mini
tree map), lab picks and leveling uniques. Hover anything for details.
"""
from __future__ import annotations

import datetime as dt
import html
import re

import pob_leveling as P

ACT_LEVELS = [(a, end) for a, end, _ in P.ACT_END]  # (act, level at end of act)
MAPS = 11
LAB_ACT = {1: 4, 2: 7, 3: 10, 4: MAPS}  # lab number -> card it goes in (speedrun route timing)

# The few campaign tips worth a line on the sheet (Nick cut boss levels, Kitava,
# lab timing and /passives as already known). Trials, Quicksilver strongbox and
# the boots recipe come from the exile-leveling route
# (github.com/HeartofPhos/exile-leveling, common/data/routes).
TIPS = {
    1: ["<b>Quicksilver:</b> open the Chemist's Strongbox in Upper Prison (high chance)",
        "<b>Boots:</b> vendor Quicksilver Flask + Orb of Augmentation + any boots = 10% move speed; "
        "do it again on those boots for more",
        "<b>Trial:</b> Lower Prison"],
    2: ["{bandit}", "<b>Trials:</b> Chamber of Sins 2, Crypt 1"],
    3: ["<b>Trials:</b> Crematorium, Catacombs, Imperial Gardens (all 6 needed for Normal Lab)"],
    6: ["<b>Trial:</b> Lower Prison"],
    7: ["<b>Trials:</b> Crypt, Chamber of Sins 2"],
    8: ["<b>Trial:</b> Bath House"],
    9: ["<b>Trial:</b> The Tunnel"],
    10: ["<b>Trial:</b> Ossuary"],
}
BANDIT = {"None": "<b>Bandits:</b> kill all three (+2 passive points)", "": "<b>Bandits:</b> kill all three (+2 passive points)",
          "Alira": "<b>Bandits:</b> help <b>Alira</b> (this PoB's choice), kill the others",
          "Kraityn": "<b>Bandits:</b> help <b>Kraityn</b> (this PoB's choice), kill the others",
          "Oak": "<b>Bandits:</b> help <b>Oak</b> (this PoB's choice), kill the others"}
CAMPAIGN_LEVEL = 70


def act_for_level(lvl: float) -> int:
    for act, end in ACT_LEVELS:
        if lvl <= end:
            return act
    return MAPS


def act_range(act: int) -> str:
    if act == MAPS:
        return "68+"
    start = 1 if act == 1 else ACT_LEVELS[act - 2][1] + 1
    return f"{start}–{ACT_LEVELS[act - 1][1]}"


def set_act(title: str) -> int | None:
    a = P.act_from_title(title)
    if a:
        return min(int(re.match(r"\d+", a).group(0)), 10)
    lv = P.level_from_title(title)
    if lv:
        return act_for_level(int(re.match(r"\d+", lv).group(0)))
    return None


e = html.escape


def link(src: str) -> str:
    return f'<a href="{e(src)}">{e(src)}</a>' if src.startswith("http") else e(src)


def gem_chip(name: str, gdb_entry: dict | None, new: bool = True, note: str = "", tip: str = "") -> str:
    attr = (gdb_entry or {}).get("attr") or "none"
    sup = " sup" if (gdb_entry or {}).get("support") or name.endswith("Support") else ""
    cls = f"g {attr[:3]}{sup}{'' if new else ' old'}"
    n = f'<small>{e(note)}</small>' if note else ""
    return f'<span class="{cls}" title="{e(tip or name)}">{e(name)}{n}</span>'


def node_chip(tree: P.Tree, nid: int, smalls: list[int], step_pts: int) -> str:
    k = tree.kind(nid)
    stats = "\n".join(tree.nodes.get(nid, {}).get("stats", []))
    via = f"\nvia {len(smalls)} small: {tree.small_summary(smalls)}" if smalls else ""
    name = "Jewel socket" if k == "jewel" else tree.name(nid)
    plus = f"<small>+{len(smalls)}</small>" if smalls else ""
    return (f'<span class="p {k}" title="{e(name)} (point {step_pts})\n{e(stats)}{e(via)}">'
            f'{plus}{e(name)}</span>')


def minimap(tree: P.Tree, old: set[int], new: list[int], big_new: set[int], w: int = 300, h: int = 210) -> str:
    pts = {n: tree.nodes[n]["xy"] for n in old | set(new) if "xy" in tree.nodes.get(n, {})}
    if not new or not pts:
        return ""
    focus = [pts[n] for n in new if n in pts] or list(pts.values())
    xs, ys = [p[0] for p in focus], [p[1] for p in focus]
    pad = 900
    x0, x1, y0, y1 = min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad
    # keep the aspect ratio of the box
    sx, sy = (x1 - x0) / w, (y1 - y0) / h
    s = max(sx, sy)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    x0, y0 = cx - w * s / 2, cy - h * s / 2

    def P_(xy):
        return (xy[0] - x0) / s, (xy[1] - y0) / s

    def inside(xy):
        x, y = P_(xy)
        return -10 <= x <= w + 10 and -10 <= y <= h + 10

    bg, edges = [], []
    new_set, alloc = set(new), old | set(new)
    seen = set()
    for nid, nd in tree.nodes.items():
        xy = nd.get("xy")
        if not xy or not inside(xy) or tree.is_asc(nid) or nd.get("isMastery"):
            continue
        for nb in nd.get("nb", []):
            if (nb, nid) in seen or nb not in tree.nodes or "xy" not in tree.nodes[nb] or tree.is_asc(nb):
                continue
            seen.add((nid, nb))
            a, b = P_(xy), P_(tree.nodes[nb]["xy"])
            cls = "en" if (nid in new_set and nb in alloc) or (nb in new_set and nid in alloc) else \
                  "eo" if nid in alloc and nb in alloc else "eb"
            edges.append(f'<line class="{cls}" x1="{a[0]:.0f}" y1="{a[1]:.0f}" x2="{b[0]:.0f}" y2="{b[1]:.0f}"/>')
        x, y = P_(xy)
        big = tree.is_big(nid)
        cls = "nn" if nid in new_set else "no" if nid in old else "nb"
        r = 4.2 if big else 2.2
        if nid in new_set:
            r += 0.8
        bg.append(f'<circle class="{cls}{" big" if big else ""}" cx="{x:.0f}" cy="{y:.0f}" r="{r}">'
                  f'<title>{e(tree.name(nid))}</title></circle>')
    labels = []
    for nid in big_new:
        if "xy" in tree.nodes.get(nid, {}) and inside(tree.nodes[nid]["xy"]):
            x, y = P_(tree.nodes[nid]["xy"])
            anchor = "end" if x > w * 0.7 else "start"
            dx = -7 if anchor == "end" else 7
            labels.append(f'<text x="{x + dx:.0f}" y="{y + 3:.0f}" text-anchor="{anchor}">'
                          f'{e(tree.name(nid) if tree.kind(nid) != "jewel" else "Jewel")}</text>')
    # order: edges, nodes, labels
    edges.sort(key=lambda l: {"eb": 0, "eo": 1, "en": 2}[l[13:15]])
    return (f'<svg class="map" viewBox="0 0 {w} {h}" role="img" aria-label="passive tree area">'
            + "".join(edges) + "".join(sorted(bg, key=lambda c: ("nb" not in c[:20], "nn" in c[:20])))
            + "".join(labels) + "</svg>")


def build_cards(build: dict, tree: P.Tree, gems_db: dict, quests_db: dict) -> tuple[dict, dict]:
    prep = build["_prep"]
    class_name = prep["class_name"]
    gdb = gems_db["gems"]
    specs = build["specs"]
    cards = {a: {"gems": [], "links": [], "pass": [], "respec": [], "mast": [], "asc": [], "gear": [],
                 "old": set(), "new": [], "trees": []} for a in range(1, MAPS + 1)}
    info = {"later_tree": None}

    # ---- campaign trees, plus the first tree after them (goes in the maps card)
    def bounds(s):
        """(lo_act, hi_act) the guide's title pins this tree to, or None."""
        a = P.act_from_title(s["title"])
        if a:
            nums = [min(int(x), 10) for x in re.findall(r"\d+", a)]
            return nums[-1], nums[-1]
        lv = P.level_from_title(s["title"])
        if lv:
            nums = [int(x) for x in re.findall(r"\d+", lv)]
            return act_for_level(nums[0]), act_for_level(nums[-1]) if len(nums) > 1 else MAPS
        return None

    camp, maps_tree = [], None
    for s in specs:
        bd = bounds(s)
        is_camp = (bd[0] <= 10) if bd else \
            P.est_level(s["_points"] + len(s["masteries"]), build["bandit"]) <= CAMPAIGN_LEVEL
        if is_camp:
            camp.append(s)
        else:
            rest = specs[specs.index(s):]
            maps_tree = s
            if "late" in s["title"].lower():  # e.g. "(Late) CoC" listed before "(Early) Slinger"
                maps_tree = next((x for x in rest if "early" in x["title"].lower()), s)
            break
    if maps_tree:
        camp.append(maps_tree)
        others = [x["title"] for x in specs if x not in camp]
        if others:
            info["later_tree"] = "; ".join(others)

    # ---- passives
    prev_main: set[int] = set()
    prev_mast: dict[int, int] = {}
    asc_seen: list[int] = []
    last_act = 1
    for ti, s in enumerate(camp):
        known = {n for n in s["nodes"] if n in tree.nodes}
        main_now = {n for n in known if not tree.is_asc(n) and tree.kind(n) not in ("start", "mastery")}
        add, remove = main_now - prev_main, prev_main - main_now
        cs = tree.class_start(s["classId"])
        chunks, _ = tree.order((main_now & prev_main) | ({cs} if cs else set()), add)
        n_done = len(main_now & prev_main)
        is_maps_tree = s is maps_tree
        bd = bounds(s)
        first_act = None
        for ch in chunks:
            n_done += len(ch)
            act = act_for_level(P.est_level(n_done + len(s["masteries"]), build["bandit"]))
            if bd:
                act = min(max(act, bd[0]), bd[1])
            act = MAPS if is_maps_tree else max(last_act, act)
            first_act = first_act or act
            last_act = act
            big = [n for n in ch if tree.is_big(n)]
            small = [n for n in ch if not tree.is_big(n)]
            c = cards[act]
            if big:
                c["pass"].append(node_chip(tree, big[-1], small, n_done))
            elif act != MAPS:
                c["pass"].append(f'<span class="p small" title="{e(tree.small_summary(small))}">'
                                 f'+{len(small)} small</span>')
            c["new"].extend(ch)
            if not c["old"]:
                c["old"] = set(prev_main & main_now) | (cards[act - 1]["old"] | set(cards[act - 1]["new"])
                                                         if act > 1 else set())
                c["old"] &= main_now | prev_main
        if remove:
            act = first_act or last_act
            big = [tree.name(n) for n in remove if tree.is_big(n)]
            cards[act]["respec"].append(
                f'<span class="p respec" title="Refund {len(remove)} points (Orbs of Regret): '
                f'{e(", ".join(sorted(big)))}">Respec {len(remove)}: {e(", ".join(sorted(big)[:4]))}'
                f'{"…" if len(big) > 4 else ""}</span>')
        for k, v in s["masteries"].items():
            if prev_mast.get(k) != v:
                eff = " / ".join(tree.nodes.get(k, {}).get("masteryEffects", {}).get(str(v), []))
                cards[MAPS if is_maps_tree else last_act]["mast"].append(
                    f'<span class="m" title="{e(eff)}"><b>{e(tree.name(k).replace(" Mastery", ""))}</b> '
                    f'{e(eff[:48])}{"…" if len(eff) > 48 else ""}</span>')
        prev_main, prev_mast = main_now, s["masteries"]
        # ascendancy order (first time each node shows up, in route order)
        asc_now = {n for n in known if tree.is_asc(n) and tree.kind(n) != "ascstart"
                   and not tree.nodes[n].get("isBloodline")}
        prev_asc = set(asc_seen)
        new_asc = asc_now - prev_asc
        if new_asc:
            aname = tree.nodes[next(iter(new_asc))]["ascendancyName"]
            st = tree.asc_start(aname)
            kept = asc_now & prev_asc
            achunks, rest = tree.order(kept | ({st} if st else set()), new_asc)
            pts = len(kept)
            for ch in achunks + ([sorted(rest)] if rest else []):
                for nid in ch:
                    pts += 1
                    if not tree.is_big(nid):
                        continue
                    lab = min((pts + 1) // 2, 4)
                    card = MAPS if is_maps_tree else LAB_ACT[lab]
                    stats = "\n".join(tree.nodes[nid].get("stats", []))
                    when = "Swap to" if prev_asc - asc_now else \
                        ["", "Normal", "Cruel", "Merciless", "Uber"][lab] + " lab:"
                    cards[card]["asc"].append(
                        f'<span class="p asc" title="{e(stats)}">{when} {e(tree.name(nid))}</span>')
        asc_seen = list(asc_now)

    # ---- skill sets: leveling ones go into their act, the first later one into maps
    lev_ids = [i for i, ss in enumerate(build["skill_sets"]) if set_act(ss["title"])]
    if not lev_ids:
        # No leveling gem setups in this PoB: show the first set as the end goal.
        placement = {0: MAPS} if build["skill_sets"] else {}
        info["no_leveling_sets"] = True
    else:
        placement = {i: set_act(build["skill_sets"][i]["title"]) for i in lev_ids}
        later = [i for i in range(len(build["skill_sets"])) if i not in lev_ids]
        if later:
            placement[later[0]] = MAPS
    prev_gems: set[str] = set()
    prev_groups: set[tuple] = set()
    for i in sorted(placement, key=lambda i: (placement[i], i)):
        ss = build["skill_sets"][i]
        rows, singles, now = [], [], set()
        groups_now, kept = set(), 0
        groups = sorted((g for g in ss["groups"] if g["gems"] and g["enabled"]),
                        key=lambda g: -len(g["gems"]))
        for g in groups:
            gems = [x for x in g["gems"] if x["enabled"]]
            names = [x["name"] for x in gems]
            now |= set(names)
            sig = tuple(sorted(names))
            groups_now.add(sig)
            if sig in prev_groups:
                kept += 1
                continue
            chips = [gem_chip(n, gdb.get(gid_for(n, gdb)), n not in prev_gems) for n in names]
            if len(gems) >= 2:
                lbl = f'{len(gems)}L' + (f' <i>{e(g["slot"])}</i>' if g["slot"] else "")
                rows.append(f'<div class="link"><span class="ll">{lbl}</span>{"".join(chips)}</div>')
            else:
                singles.extend(chips)
        if singles:
            rows.append(f'<div class="link"><span class="ll">solo</span>{"".join(singles)}</div>')
        if kept and rows:
            rows.append(f'<div class="link"><span class="ll"></span><span class="q">+ {kept} unchanged</span></div>')
        if rows:
            cards[placement[i]]["links"].append((ss["title"], rows))
        prev_gems, prev_groups = now, groups_now
    info["placement"] = placement
    info["recipes"] = leveling_recipes(leveling_profile(build, gdb, placement))

    # ---- gems by quest (only gems for the sets shown)
    camp_sets = [i for i in placement if placement[i] != MAPS] or list(placement)
    if info.get("no_leveling_sets"):
        maps_only = []
    else:
        maps_only = None
    plan, where, needed = P.gem_acquisition(build, class_name, gems_db, quests_db["quests"],
                                            set_ids=camp_sets)
    # Gems only the maps setup needs: list them in the maps card instead.
    maps_sets = [] if maps_only is not None else \
        [i for i in placement if placement[i] == MAPS and i not in camp_sets]
    if maps_sets:
        _, where2, needed2 = P.gem_acquisition(build, class_name, gems_db, quests_db["quests"], set_ids=maps_sets)
        extra = [n for n in needed2 if n not in needed]
        if extra:
            chips = [gem_chip(n, gdb.get(needed2[n]["gid"]), tip=f"{n}: {where2[n]}") for n in extra]
            cards[MAPS]["gems"].append(("For this setup", "Lilly Roth (Act 6+) sells every quest gem", "", chips))
    for act, qname, npc, take, buys in plan:
        chips = []
        if take:
            chips.append(gem_chip(take, gdb.get(needed[take]["gid"]), note="take",
                                  tip=f"{take} — quest reward: {qname} ({npc}), lvl {gdb.get(needed[take]['gid'], {}).get('lvl', '?')}"))
        for n, vnpc in buys:
            chips.append(gem_chip(n, gdb.get(needed[n]["gid"]),
                                  tip=f"{n} — buy from {vnpc} after {qname}, lvl {gdb.get(needed[n]['gid'], {}).get('lvl', '?')}"))
        cards[act]["gems"].append((qname, npc, buys[0][1] if buys else "", chips))
    info["no_vendor"] = [n for n in needed if not where[n].startswith("Act")]

    # ---- uniques you can use while leveling (first item set + leveling sets)
    seen = set()
    sets = build["item_sets"]
    for k, s in enumerate(sets):
        a = set_act(s["title"])
        if k > 0 and a is None:
            continue
        for slot, item in s["slots"]:
            if item["rarity"] != "UNIQUE" or item["name"] in seen:
                continue
            seen.add(item["name"])
            req = item["levelreq"] or 1
            act = a or act_for_level(req)
            if act == MAPS and k > 0:
                continue
            cards[act]["gear"].append(
                f'<span class="u" title="{e(item["base"])} · {e(slot)} · lvl {req}">{e(item["name"])}'
                f'<small>lvl {req}</small></span>')
    return cards, info


RECIPE_DATA = P.DATA_DIR / "vendor_recipes.json"


def leveling_profile(build: dict, gdb: dict, placement: dict) -> set[str]:
    """Tags of the main skill in each early leveling set (acts 1-5)."""
    ids = [i for i, a in placement.items() if a <= 5] or list(placement)
    tags: set[str] = set()
    for i in ids:
        groups = [g for g in build["skill_sets"][i]["groups"] if g["enabled"] and not g["source"]]
        if not groups:
            continue
        main = max(groups, key=lambda g: len(g["gems"]))
        for gem in main["gems"]:
            entry = gdb.get(gid_for(gem["name"], gdb), {})
            if entry and not entry.get("support"):
                tags |= set(entry.get("tags", []))
                break
    return tags


def leveling_recipes(tags: set[str]) -> list[tuple[str, str, str]]:
    """(label, ingredients, notes) for the vendor recipes that fit the build."""
    if not RECIPE_DATA.exists():
        return []
    import json
    recipes = json.loads(RECIPE_DATA.read_text(encoding="utf-8"))["recipes"]
    elems = [e for e in ("fire", "cold", "lightning", "chaos", "physical") if e in tags]
    wanted = [("boots", r"movement speed", "Move-speed boots"),
              ("ring", r"^Ruby Ring", "Resist rings (Ruby / Topaz / Sapphire)")]
    if "spell" in tags:
        wanted.append(("w", r"increased spell damage", "Spell damage weapon"))
        wanted += [("w", rf"level of all {e} spell skill gems", f"+1 {e.title()} spell gems weapon") for e in elems]
    if "attack" in tags:
        wanted.append(("w", r"increased physical damage", "+% physical damage weapon"))
        wanted.append(("w", r"added physical damage one tier", "Added physical damage weapon"))
        wanted += [("w", rf"added {e} damage one tier", f"Added {e.title()} damage weapon")
                   for e in elems if e != "physical"]
    if "minion" in tags:
        wanted.append(("h", r"minion skill gems", "+1 minion gems helmet"))
    out, seen = [], set()
    for _, pat, label in wanted:
        for r in recipes:
            res = r.get("Result", "")
            if not r.get("_section", "").startswith("Equipment") or not re.search(pat, res, re.I | re.M):
                continue
            if label in seen:
                break
            seen.add(label)
            ing = re.sub(r"\s*\([^)]*\)", "", r.get("Recipes", "")).replace(" / ", " + ")
            if label.startswith("Resist rings"):
                ing = "1x Iron Ring + 1x red / green / blue gem (fire / lightning / cold res)"
            ing = ing.replace(" explicit mod", "").replace("Magic/Rare/Unique ", "any ") \
                     .replace("2 or more quality gems with a combined total of 40% quality & the", "gems totalling 40% quality with the")
            out.append((label, ing, f"{res}\n{r.get('Notes', '')}".strip()))
            break
    return out


def gid_for(name: str, gdb: dict) -> str:
    cache = gid_for.__dict__.setdefault("cache", {})
    if not cache:
        for k, v in gdb.items():
            if "Royale" not in k:
                cache.setdefault(v["name"].lower(), k)
    return cache.get(name.lower(), "")


CSS = """
:root{--bg:#f4f4f1;--surface:#fff;--surface2:#ecece7;--ink:#26282e;--muted:#6b6e78;--line:#d8d8d1;
--gold:#9a7f3f;--str:#b8473f;--dex:#3f8a4a;--int:#3f6fb8;--none:#777;--new:#c99a2e;--red:#b8473f}
@media (prefers-color-scheme:dark){:root{--bg:#17181c;--surface:#1f2126;--surface2:#26282e;--ink:#e7e5dd;
--muted:#9a9da8;--line:#33353c;--gold:#c9ab63;--str:#e0776f;--dex:#6cc27a;--int:#79a3ea;--none:#aaa;--new:#e6bf5c;--red:#e0776f}}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font:14px/1.45 "Segoe UI",system-ui,-apple-system,sans-serif;margin:0;padding:0 16px 60px}
.wrap{max-width:1100px;margin:0 auto}
header{padding:26px 0 10px}
h1{font-family:"Palatino Linotype","Book Antiqua",Palatino,Georgia,serif;font-size:clamp(22px,3.4vw,32px);font-weight:600;margin:0 0 4px}
h1 .rule{color:var(--gold)}
.sub{color:var(--muted);margin:0;font-size:13px}
.legend{font-size:12.5px;color:var(--muted);margin:10px 0 14px;display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center}
.act{display:grid;grid-template-columns:62px 1fr;gap:14px;background:var(--surface);border:1px solid var(--line);
border-radius:10px;padding:14px 16px;margin:0 0 10px}
.an{font-family:"Palatino Linotype",Palatino,Georgia,serif;font-size:30px;font-weight:600;line-height:1;color:var(--gold)}
.an small{display:block;font:600 11px/1.3 "Segoe UI",system-ui,sans-serif;color:var(--muted);margin-top:4px;letter-spacing:.03em}
.body{display:grid;grid-template-columns:1fr 300px;gap:12px 18px;align-items:start}
.body.nomap{grid-template-columns:1fr}
.rows>div{display:flex;flex-wrap:wrap;gap:5px;align-items:center;margin:0 0 7px}
.lab{flex:none;width:58px;font:700 10.5px/1 "Segoe UI",sans-serif;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.q{font-size:11.5px;color:var(--muted);width:128px;flex:none;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.qrow{display:flex;flex-wrap:wrap;gap:4px;align-items:center;margin:0 0 3px}
.g,.p,.u{display:inline-flex;align-items:baseline;gap:4px;font-size:12.5px;padding:2px 8px;border-radius:5px;
border:1px solid var(--line);background:var(--surface2);white-space:nowrap;cursor:default}
.g small,.u small,.p small{font-size:10.5px;color:var(--muted)}
.g{border-left:4px solid var(--none)} .g.str{border-left-color:var(--str)} .g.dex{border-left-color:var(--dex)} .g.int{border-left-color:var(--int)}
.g.sup{border-style:dashed;border-left-style:solid}
.g.old{opacity:.55}
.g small{font-weight:700;color:var(--new);text-transform:uppercase;letter-spacing:.05em}
.link{display:flex;flex-wrap:wrap;gap:4px;align-items:center;margin:0 0 4px}
.ll{font:700 11px/1 Consolas,monospace;color:var(--muted);min-width:34px}
.ll i{font:400 10.5px "Segoe UI",sans-serif}
.setname{font-size:11px;color:var(--muted);margin:2px 0 3px}
.p.notable{border-color:var(--gold);font-weight:600}
.p.keystone{border:2px solid var(--gold);font-weight:700}
.p.jewel{border-style:dashed}
.p.small{color:var(--muted)}
.p.respec{border-color:var(--red);color:var(--red)}
.p.asc{border-color:var(--gold);background:transparent;font-weight:600}
.ms{font-size:11.5px;color:var(--muted);flex:1} .ms b{color:var(--ink);font-weight:600} .m{cursor:default}
.arrow{color:var(--muted);font-size:11px}
.u{border-color:var(--gold);font-weight:600}
svg.map{width:300px;height:210px;background:var(--surface2);border-radius:8px;border:1px solid var(--line)}
svg .eb{stroke:var(--line);stroke-width:1} svg .eo{stroke:var(--muted);stroke-width:1.6} svg .en{stroke:var(--new);stroke-width:2.6}
svg .nb{fill:var(--line)} svg .no{fill:var(--muted)} svg .nn{fill:var(--new)}
svg .nn.big{stroke:var(--ink);stroke-width:1}
svg text{font:600 9.5px "Segoe UI",sans-serif;fill:var(--ink);paint-order:stroke;stroke:var(--surface2);stroke-width:3px}
.tips{font-size:12.5px;flex:1} .tips code{font:12px Consolas,monospace;background:var(--surface2);padding:0 4px;border-radius:3px}
.rc{font-size:12.5px;margin:0 0 2px;cursor:default}
.warn{font-size:12.5px;color:var(--red);margin:0 0 8px}
a{color:var(--gold)}
.foot{font-size:12px;color:var(--muted);margin-top:14px}
@media (max-width:760px){.body{grid-template-columns:1fr}.act{grid-template-columns:1fr}}
"""


def render_html(build: dict, tree: P.Tree, gems_db: dict, quests_db: dict, source: str,
                class_override: str | None = None, keep_order: bool = False, md_name: str = "") -> str:
    P.prepare(build, tree, keep_order, class_override)
    cards, info = build_cards(build, tree, gems_db, quests_db)
    cls = build["_prep"]["class_name"]
    asc = build["ascendClassName"] or cls
    main_skill = ""
    out = ['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width,initial-scale=1">',
           f'<title>Leveling sheet — {e(asc)}</title><style>{CSS}</style></head><body><div class="wrap">',
           f'<header><h1>Leveling sheet <span class="rule">·</span> {e(asc)} <small style="font-size:.55em;color:var(--muted)">({e(cls)})</small></h1>',
           f'<p class="sub">From {link(source)} · made {dt.date.today().isoformat()} · quest data may change in a new league{main_skill}</p></header>',
           '<div class="legend"><span><b>Gems</b>: <span class="g int">int</span> <span class="g dex">dex</span> '
           '<span class="g str">str</span> <span class="g int sup">dashed = support</span> '
           '<span class="g int">Name<small>take</small></span> = pick as quest reward, rest = buy · '
           'faded = already had</span><span><b>Passives</b>: click left → right; '
           '<span class="p small"><small>+3</small>Notable</span> = 3 small nodes on the way. Map: gold = this act.</span>'
           '<span>Hover anything for details.</span></div>']
    for act in range(1, MAPS + 1):
        c = cards[act]
        if act not in TIPS and not any(c[k] for k in ("gems", "links", "pass", "respec", "asc", "gear", "mast")):
            continue
        rows = []
        for title, lrows in c["links"]:
            rows.append(f'<div><span class="lab">Links</span><div style="flex:1">'
                        f'<div class="setname">{e(title)}</div>{"".join(lrows)}</div></div>')
        if c["gems"]:
            parts = []
            for qname, npc, vendor, chips in c["gems"]:
                parts.append(f'<div class="qrow"><span class="q" title="{e(npc)}">{e(qname)}</span>{"".join(chips)}</div>')
            rows.insert(0, f'<div><span class="lab">Gems</span><div style="flex:1">{"".join(parts)}</div></div>')
        if act == MAPS:
            c["pass"] = [x for x in c["pass"] if 'class="p notable' in x or 'class="p keystone' in x]
            if len(c["pass"]) > 12:
                c["pass"] = c["pass"][:12] + [f'<span class="p small">…+{len(c["pass"]) - 12} more</span>']
        if c["pass"] or c["respec"]:
            arrow = '<span class="arrow">→</span>'
            rows.append(f'<div><span class="lab">Passives</span>{"".join(c["respec"])}{arrow.join(c["pass"])}</div>')
        if c["mast"] and act != MAPS:
            rows.append(f'<div><span class="lab">Mastery</span><span class="ms">{" · ".join(c["mast"])}</span></div>')
        if c["asc"]:
            rows.append(f'<div><span class="lab">Ascend</span>{"".join(c["asc"])}</div>')
        if act == 1 and info["recipes"]:
            lines = "".join(f'<div class="rc" title="{e(notes)}"><b>{e(label)}:</b> {e(ing)}</div>'
                            for label, ing, notes in info["recipes"])
            rows.append(f'<div><span class="lab">Recipes</span><div style="flex:1">{lines}</div></div>')
        if act in TIPS:
            kill_all = build["bandit"] in ("None", "", None)
            tips = [t.replace("{bandit}", BANDIT.get(build["bandit"] or "", BANDIT["None"]))
                     .replace("{passives}", "24" if kill_all else "23") for t in TIPS[act]
                    if not (act == 1 and info["recipes"] and t.startswith("<b>Boots:"))]
            rows.append(f'<div><span class="lab">Tips</span><span class="tips">{" · ".join(tips)}</span></div>')
        if c["gear"]:
            rows.append(f'<div><span class="lab">Uniques</span>{"".join(c["gear"])}</div>')
        big_new = {n for n in c["new"] if tree.is_big(n)}
        svg = minimap(tree, c["old"], c["new"], big_new) if act != MAPS else ""
        if act == 1 and info.get("no_leveling_sets"):
            rows.insert(0, '<div class="warn">This PoB has no leveling gem setups. The gems below are for the '
                           'final setup (see Maps), placed where you can first get them.</div>')
        label = "Maps" if act == MAPS else f"A{act}"
        out.append(f'<section class="act"><div class="an">{label}<small>lvl {act_range(act)}</small></div>'
                   f'<div class="body{"" if svg else " nomap"}"><div class="rows">{"".join(rows)}</div>{svg}</div></section>')
    foot = []
    if info["no_vendor"]:
        foot.append("Not sold by vendors (trade / drops / lab): " + ", ".join(info["no_vendor"]) + ".")
    if info["later_tree"]:
        foot.append(f"Other trees in the PoB (endgame variants, not shown): {info['later_tree']}.")
    if md_name:
        foot.append(f'Full detail (every tree, set and item): <a href="{e(md_name)}">{e(md_name)}</a>.')
    out.append(f'<p class="foot">{" ".join(e(x) if not x.startswith("Full") else x for x in foot)}</p>')
    out.append("</div></body></html>")
    return "\n".join(out)
