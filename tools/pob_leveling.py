#!/usr/bin/env python3
"""Turn a Path of Building (PoB) export into a markdown leveling plan.

Give it a PoB code, a pobb.in / pastebin / poe.ninja link, or a file that holds
a code or the raw XML. It decodes the build and writes out only the leveling
pieces:

    - every passive tree in the PoB, in order, with the points to add between
      trees (grouped as "path to this notable"), respecs, masteries and the
      ascendancy order
    - every skill set (gem setup), with what changed from the previous one
    - when and where to get each gem for your class: which quest reward to
      take and what to buy from which vendor, act by act
    - item sets and the uniques the guide uses, with level requirements
    - the guide author's PoB notes

No third-party packages needed (Python 3.9+).

Usage:
    python tools/pob_leveling.py https://pobb.in/XXXXXXXX -o builds/leveling/my-build.md
    python tools/pob_leveling.py https://mobalytics.gg/poe/builds/<guide>   # guide page with a PoB
    python tools/pob_leveling.py build.txt              # file with a code or XML
    python tools/pob_leveling.py - < code.txt           # code on stdin
    python tools/pob_leveling.py URL --class Witch      # override class for gem rewards
    python tools/pob_leveling.py URL --save-xml build.xml
    python tools/pob_leveling.py --update-data          # refresh tree / gem / quest data

pobb.in, pastebin and poe.ninja are blocked from Claude's cloud sessions, so
fetch links on a normal PC. A PoB code pasted into chat works anywhere: copy it
in PoB with Import/Export Build -> "Generate" -> "Copy".

Data (tools/pob_data/, refreshed with --update-data):
    tree.json    trimmed from GGG's skilltree-export (github.com/grindinggear/skilltree-export)
    gems.json    gem names and level requirements  (github.com/HeartofPhos/exile-leveling)
    quests.json  quest rewards and vendor gems per class (same source)
Quest rewards can change in a new league; re-run --update-data once those
repos update for it.
"""
from __future__ import annotations

import argparse
import base64
import collections
import datetime as dt
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "pob_data"
UA = "pob-leveling-extractor/1.0 (+https://github.com/kruppenb/PathOfExile)"

TREE_URL = "https://raw.githubusercontent.com/grindinggear/skilltree-export/master/data.json"
GEMS_URL = "https://raw.githubusercontent.com/HeartofPhos/exile-leveling/main/common/data/json/gems.json"
QUESTS_URL = "https://raw.githubusercontent.com/HeartofPhos/exile-leveling/main/common/data/json/quests.json"

CLASS_NAMES = ["Scion", "Marauder", "Ranger", "Witch", "Duelist", "Templar", "Shadow"]

# Passive points from quests, cumulative at the end of each act, and the
# rough level people finish each act at. Used only to guess a level for trees
# whose title doesn't say one. Bandits add 2 more if you kill all three.
ACT_END = [  # (act, typical level at end, cumulative quest points)
    (1, 12, 2), (2, 22, 3), (3, 32, 5), (4, 40, 6), (5, 45, 8),
    (6, 50, 11), (7, 55, 14), (8, 60, 17), (9, 63, 19), (10, 67, 22),
]
# Ascendancy points: 2 per Labyrinth, so lab N unlocks points 2N-1 and 2N.
LABS = ["Normal Lab (~lvl 33, act 3)", "Cruel Lab (~lvl 55, act 7)",
        "Merciless Lab (~lvl 68, after act 10)", "Uber Lab (maps)"]


# --------------------------------------------------------------------------- input

def http_get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def raw_urls(url: str) -> list[str]:
    """Candidate 'raw code' URLs for a build-sharing link, best first."""
    url = url.strip()
    m = re.match(r"https?://(?:www\.)?pobb\.in/(?:u/[^/]+/)?([A-Za-z0-9_-]+)", url)
    if m:
        return [f"https://pobb.in/{m.group(1)}/raw"]
    m = re.match(r"https?://(?:www\.)?pastebin\.com/(?:raw/)?([A-Za-z0-9]+)", url)
    if m:
        return [f"https://pastebin.com/raw/{m.group(1)}"]
    m = re.match(r"https?://(?:www\.)?poe\.ninja/pob/(?:raw/)?([A-Za-z0-9_-]+)", url)
    if m:
        return [f"https://poe.ninja/pob/raw/{m.group(1)}"]
    m = re.match(r"https?://(?:www\.)?maxroll\.gg/poe/pob/([A-Za-z0-9_-]+)", url)
    if m:
        return [f"https://maxroll.gg/poe/api/pob/{m.group(1)}"]
    m = re.match(r"https?://(?:www\.)?pob\.codes/(?:raw/)?([A-Za-z0-9_-]+)", url)
    if m:
        return [f"https://pob.codes/raw/{m.group(1)}", url]
    return [url.rstrip("/") + "/raw", url]


def decode_code(code: str) -> str:
    code = re.sub(r"\s+", "", code)
    code = code.replace("-", "+").replace("_", "/")
    code += "=" * (-len(code) % 4)
    return zlib.decompress(base64.b64decode(code)).decode("utf-8", "replace")


def load_build_xml(src: str, depth: int = 0) -> tuple[str, str]:
    """Return (xml_text, source_label)."""
    if src == "-":
        text = sys.stdin.read()
        label = "stdin"
    elif re.match(r"https?://", src):
        last_err: Exception | None = None
        for u in raw_urls(src):
            try:
                text = http_get(u)
            except Exception as e:  # noqa: BLE001
                last_err = e
                continue
            text = text.strip()
            if text.startswith("<") and "<PathOfBuilding" not in text[:500]:
                # A guide page (e.g. mobalytics): look for an embedded code, then a PoB link.
                m = re.search(r'"pobCode"\s*:\s*"(eN[A-Za-z0-9+/=_-]{200,})"', text) or \
                    re.search(r'\b(eN[A-Za-z0-9_-]{2000,}={0,2})', text)
                if m:
                    return to_xml(m.group(1)), src
                links = re.findall(r"https?://(?:pobb\.in|pastebin\.com|poe\.ninja/pob|maxroll\.gg/poe/pob)/[A-Za-z0-9_/-]+", text)
                if links and depth == 0:
                    print(f"Using the first PoB link on the page: {links[0]} "
                          f"(others: {', '.join(sorted(set(links[1:]))) or 'none'})", file=sys.stderr)
                    return load_build_xml(links[0], depth=1)
                continue
            return to_xml(text), src
        sys.exit(f"Couldn't fetch a PoB code from {src} ({last_err or 'got a web page, not a code'}).\n"
                 "If this runs in the cloud, pobb.in/pastebin are blocked: run it on your PC, or "
                 "paste the code into a file and pass the file.")
    elif Path(src).exists():
        text = Path(src).read_text(encoding="utf-8", errors="replace")
        label = Path(src).name
    else:
        text = src
        label = "PoB code"
    return to_xml(text.strip()), label


def to_xml(text: str) -> str:
    text = text.strip().lstrip("﻿")
    if text.startswith("<"):
        return text
    try:
        return decode_code(text)
    except Exception as e:  # noqa: BLE001
        sys.exit(f"That doesn't look like a PoB code or PoB XML ({e}).")


# --------------------------------------------------------------------------- data

# Angles (degrees, clockwise from 12 o'clock) PoB uses for the uneven orbits.
ORBIT_ANGLES = {
    16: [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330],
    40: [0, 10, 20, 30, 40, 45, 50, 60, 70, 80, 90, 100, 110, 120, 130, 135, 140, 150, 160, 170,
         180, 190, 200, 210, 220, 225, 230, 240, 250, 260, 270, 280, 290, 300, 310, 315, 320, 330, 340, 350],
}


def node_xy(tree: dict, n: dict) -> list[int] | None:
    import math
    g = tree["groups"].get(str(n.get("group")))
    if not g:
        return None
    orbit, idx = n.get("orbit", 0), n.get("orbitIndex", 0)
    r = tree["constants"]["orbitRadii"][orbit]
    count = tree["constants"]["skillsPerOrbit"][orbit]
    ang = ORBIT_ANGLES[count][idx] if count in ORBIT_ANGLES else 360 * idx / count
    a = math.radians(ang)
    return [round(g["x"] + r * math.sin(a)), round(g["y"] - r * math.cos(a))]


def update_data() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    today = dt.date.today().isoformat()
    print("Downloading passive tree ...", file=sys.stderr)
    tree = json.loads(http_get(TREE_URL))
    keep = ("name", "stats", "isNotable", "isKeystone", "isMastery", "isJewelSocket",
            "ascendancyName", "isAscendancyStart", "classStartIndex", "isMultipleChoiceOption",
            "isBloodline")
    nodes = {}
    for nid, n in tree["nodes"].items():
        if nid == "root":
            continue
        t = {k: n[k] for k in keep if k in n and n[k] not in (None, False, [])}
        nb = sorted(set(n.get("out", [])) | set(n.get("in", [])))
        if nb:
            t["nb"] = [int(x) for x in nb if x != "root"]
        if n.get("masteryEffects"):
            t["masteryEffects"] = {str(e["effect"]): e["stats"] for e in n["masteryEffects"]}
        pos = node_xy(tree, n)
        if pos:
            t["xy"] = pos
        nodes[nid] = t
    classes = [{"name": c["name"], "ascendancies": [a["id"] for a in c["ascendancies"]]}
               for c in tree["classes"]]
    alt = [a.get("id") for a in tree.get("alternate_ascendancies", [])]
    out = {"_source": TREE_URL, "_fetched": today, "tree": tree.get("tree"),
           "classes": classes, "alternate_ascendancies": alt, "nodes": nodes}
    (DATA_DIR / "tree.json").write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")

    print("Downloading gems and quests ...", file=sys.stderr)
    gems = json.loads(http_get(GEMS_URL))
    gems_out = {"_source": GEMS_URL, "_fetched": today,
                "gems": {k: {"name": g["name"], "lvl": g.get("required_level", 1),
                             "attr": g.get("primary_attribute"), "support": g.get("is_support", False)}
                         for k, g in gems.items()}}
    (DATA_DIR / "gems.json").write_text(json.dumps(gems_out, separators=(",", ":")), encoding="utf-8")

    quests = json.loads(http_get(QUESTS_URL))
    q_out = []
    for qid, q in quests.items():
        try:
            act = int(q["act"])
        except ValueError:
            continue
        if not 1 <= act <= 10:
            continue
        offers = []
        for o in q["reward_offers"].values():
            reward = {g: v["classes"] for g, v in o.get("quest", {}).items() if "/Gems/" in g}
            vendor = {g: [v["classes"], v.get("npc", "")] for g, v in o.get("vendor", {}).items()
                      if "/Gems/" in g}
            if reward or vendor:
                offers.append({"npc": o.get("quest_npc", ""), "reward": reward, "vendor": vendor})
        if offers:
            q_out.append({"id": qid, "name": q["name"], "act": act, "offers": offers})
    q_out.sort(key=lambda q: q["act"])  # stable: keeps the route order within an act
    (DATA_DIR / "quests.json").write_text(
        json.dumps({"_source": QUESTS_URL, "_fetched": today, "quests": q_out}, separators=(",", ":")),
        encoding="utf-8")
    print(f"Saved to {DATA_DIR}", file=sys.stderr)


def load_data():
    if not (DATA_DIR / "tree.json").exists():
        update_data()
    tree = json.loads((DATA_DIR / "tree.json").read_text(encoding="utf-8"))
    gems = json.loads((DATA_DIR / "gems.json").read_text(encoding="utf-8"))
    quests = json.loads((DATA_DIR / "quests.json").read_text(encoding="utf-8"))
    return tree, gems, quests


# --------------------------------------------------------------------------- parsing

COLOR_RE = re.compile(r"\^(x[0-9A-Fa-f]{6}|\d)")


def clean(s: str | None) -> str:
    return COLOR_RE.sub("", s or "").strip()


def level_from_title(title: str) -> str | None:
    """Level (or level range) a guide wrote in a tree / skill-set title."""
    t = title.lower()
    m = re.search(r"\b(?:lvl|level|lv)\s*\.?\s*(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?", t)
    if m:
        return m.group(1) + (f"–{m.group(2)}" if m.group(2) else "")
    m = re.match(r"\s*(\d{1,3})\s*(?:[-–]\s*(\d{1,3})|(\+))", t)  # "1-12 | Cobra", "29+"
    if m and int(m.group(1)) <= 100:
        return m.group(1) + (f"–{m.group(2)}" if m.group(2) else "+")
    return None


def act_from_title(title: str) -> str | None:
    """'Act 3', 'Act1', 'Ato 4 e 5' (Portuguese), 'Akt 2' -> '3', '1', '4–5'."""
    m = re.search(r"\b(?:act|ato|akt|acto)\s*(\d{1,2})(?:\s*(?:-|–|e|and|&|to)\s*(\d{1,2}))?", title.lower())
    if not m:
        return None
    return m.group(1) + (f"–{m.group(2)}" if m.group(2) else "")


def parse_item(text: str) -> dict:
    lines = [ln.strip() for ln in clean(text).splitlines() if ln.strip()]
    item = {"rarity": "", "name": "", "base": "", "levelreq": None, "text": lines}
    i = 0
    if lines and lines[0].lower().startswith("rarity:"):
        item["rarity"] = lines[0].split(":", 1)[1].strip().upper()
        i = 1
    if i < len(lines):
        item["name"] = lines[i]
    if item["rarity"] in ("UNIQUE", "RARE", "RELIC") and i + 1 < len(lines):
        item["base"] = lines[i + 1]
    else:
        item["base"] = item["name"]
    item["mods"], item["sockets"] = [], ""
    imp_at = None
    for j, ln in enumerate(lines):
        m = re.match(r"(?:LevelReq|Requires Level):?\s*(\d+)", ln, re.I)
        if m:
            item["levelreq"] = int(m.group(1))
        if ln.startswith("Sockets:"):
            item["sockets"] = ln.split(":", 1)[1].strip()
        if re.match(r"Implicits:\s*\d+", ln):
            imp_at = j
    if imp_at is not None:
        for ln in lines[imp_at + 1:]:
            ln = re.sub(r"\{[^}]*\}", "", ln).strip()
            if ln and ln not in ("Fractured Item", "Corrupted", "Mirrored", "Synthesised Item",
                                 "Shaper Item", "Elder Item", "Split"):
                item["mods"].append(ln)
    return item


def to_int(v, default: int | None = 0) -> int | None:
    """PoB writes Lua's "nil" for unset numbers."""
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def parse_build(xml_text: str) -> dict:
    root = ET.fromstring(xml_text)
    b = root.find("Build")
    build = {
        "level": to_int(b.get("level"), 1) if b is not None else 1,
        "className": b.get("className", "") if b is not None else "",
        "ascendClassName": b.get("ascendClassName", "") if b is not None else "",
        "bandit": b.get("bandit", "") if b is not None else "",
        "mainSocketGroup": b.get("mainSocketGroup") if b is not None else None,
        "targetVersion": b.get("targetVersion", "") if b is not None else "",
    }

    # Trees
    specs = []
    tree = root.find("Tree")
    if tree is not None:
        for i, s in enumerate(tree.findall("Spec"), 1):
            nodes = [int(x) for x in (s.get("nodes") or "").split(",") if x.strip().isdigit()]
            masteries = {}
            for a, e in re.findall(r"\{(\d+),(\d+)\}", s.get("masteryEffects") or ""):
                masteries[int(a)] = int(e)
            url_el = s.find("URL")
            specs.append({
                "title": clean(s.get("title")) or f"Tree {i}",
                "nodes": nodes,
                "classId": to_int(s.get("classId"), None),
                "ascendClassId": to_int(s.get("ascendClassId")),
                "secondaryAscendClassId": to_int(s.get("secondaryAscendClassId")),
                "treeVersion": s.get("treeVersion", ""),
                "masteries": masteries,
                "url": (url_el.text or "").strip() if url_el is not None else "",
            })
        build["activeSpec"] = tree.get("activeSpec")

    # Skills
    skill_sets = []
    skills = root.find("Skills")
    if skills is not None:
        sets = skills.findall("SkillSet") or [skills]
        for i, ss in enumerate(sets, 1):
            groups = []
            for sk in ss.findall("Skill"):
                gems = []
                for g in sk.findall("Gem"):
                    gems.append({
                        "name": clean(g.get("nameSpec") or g.get("skillId") or "?"),
                        "gemId": g.get("gemId") or "",
                        "level": g.get("level"),
                        "quality": g.get("quality"),
                        "enabled": g.get("enabled", "true") != "false",
                    })
                groups.append({
                    "label": clean(sk.get("label")),
                    "slot": sk.get("slot") or "",
                    "enabled": sk.get("enabled", "true") != "false",
                    "source": sk.get("source") or "",
                    "gems": gems,
                })
            skill_sets.append({"title": clean(ss.get("title")) or f"Skill set {i}", "groups": groups})

    # Items
    items, item_sets = {}, []
    it = root.find("Items")
    if it is not None:
        for el in it.findall("Item"):
            items[el.get("id")] = parse_item(el.text or "")
        sets = it.findall("ItemSet")
        for i, s in enumerate(sets, 1):
            slots = []
            for sl in s.findall("Slot"):
                iid = sl.get("itemId", "0")
                if iid and iid != "0" and iid in items:
                    slots.append((sl.get("name", ""), items[iid]))
            item_sets.append({"title": clean(s.get("title")) or f"Item set {i}", "slots": slots})

    notes = root.find("Notes")
    build.update(specs=specs, skill_sets=skill_sets, item_sets=item_sets,
                 notes=clean(notes.text) if notes is not None and notes.text else "")
    return build


# --------------------------------------------------------------------------- tree logic

class Tree:
    def __init__(self, data: dict):
        self.nodes = {int(k): v for k, v in data["nodes"].items()}
        self.classes = data["classes"]
        self.version = data.get("tree", "")
        self.fetched = data.get("_fetched", "")

    def name(self, nid: int) -> str:
        return self.nodes.get(nid, {}).get("name", f"#{nid}")

    def kind(self, nid: int) -> str:
        n = self.nodes.get(nid)
        if n is None:
            return "unknown"
        if "classStartIndex" in n:
            return "start"
        if n.get("isAscendancyStart"):
            return "ascstart"
        if n.get("isMastery"):
            return "mastery"
        if n.get("isKeystone"):
            return "keystone"
        if n.get("isJewelSocket"):
            return "jewel"
        if n.get("isNotable"):
            return "notable"
        return "small"

    def is_asc(self, nid: int) -> bool:
        return "ascendancyName" in self.nodes.get(nid, {})

    def class_start(self, class_id: int) -> int | None:
        for nid, n in self.nodes.items():
            if n.get("classStartIndex") == class_id:
                return nid
        return None

    def asc_start(self, asc_name: str) -> int | None:
        for nid, n in self.nodes.items():
            if n.get("isAscendancyStart") and n.get("ascendancyName") == asc_name:
                return nid
        return None

    def asc_name(self, class_id: int, asc_id: int) -> str:
        try:
            return self.classes[class_id]["ascendancies"][asc_id - 1] if asc_id else ""
        except IndexError:
            return ""

    def is_big(self, nid: int) -> bool:
        return self.kind(nid) in ("notable", "keystone", "jewel")

    def label(self, nid: int) -> str:
        k = self.kind(nid)
        nm = self.name(nid)
        if k == "keystone":
            return f"**{nm}** (keystone)"
        if k == "jewel":
            return "**Jewel socket**"
        if k == "notable":
            return f"**{nm}**"
        return nm

    def small_summary(self, nids: list[int]) -> str:
        c = collections.Counter("; ".join(self.nodes.get(n, {}).get("stats", [])) or self.name(n)
                                for n in nids)
        return ", ".join(f"{s} ×{k}" if k > 1 else s for s, k in c.items())

    def order(self, start: set[int], targets: set[int]) -> tuple[list[list[int]], set[int]]:
        """Order `targets` as connected chunks, each ending on the nearest notable.

        Walks only through target nodes, starting from the already-allocated
        `start` set. Returns (chunks, unreachable)."""
        have = set(start)
        todo = set(targets) - have
        chunks: list[list[int]] = []
        while todo:
            # BFS from everything we have, through todo nodes only.
            parent: dict[int, int | None] = {}
            frontier = collections.deque()
            for h in have:
                for nb in self.nodes.get(h, {}).get("nb", []):
                    if nb in todo and nb not in parent:
                        parent[nb] = None
                        frontier.append(nb)
            seen_order = []
            while frontier:
                cur = frontier.popleft()
                seen_order.append(cur)
                for nb in self.nodes.get(cur, {}).get("nb", []):
                    if nb in todo and nb not in parent:
                        parent[nb] = cur
                        frontier.append(nb)
            if not seen_order:
                break
            target = next((n for n in seen_order if self.is_big(n)), None)
            if target is None:
                chunk = seen_order  # only small nodes left
            else:
                chunk = []
                cur: int | None = target
                while cur is not None:
                    chunk.append(cur)
                    cur = parent[cur]
                chunk.reverse()
            chunks.append(chunk)
            have |= set(chunk)
            todo -= set(chunk)
        return chunks, todo


def est_level(points: int, bandit: str) -> int:
    """Guess character level from main-tree points (quest points included)."""
    for lvl in range(1, 101):
        qp = 0
        for act, end_lvl, cum in ACT_END:
            if lvl >= end_lvl:
                qp = cum + (2 if act >= 2 and bandit in ("None", "", None) else 0)
        if lvl - 1 + qp >= points:
            return lvl
    return 100


# --------------------------------------------------------------------------- gem logic

def gem_main_id(gids: set[str]) -> str:
    """Pick the normal gem id when the data has variants (Royale etc.)."""
    good = sorted((g for g in gids if "Royale" not in g), key=len)
    return good[0] if good else (sorted(gids)[0] if gids else "")


def is_vaal(name: str) -> bool:
    return name.lower().startswith("vaal ")


def gem_acquisition(build: dict, class_name: str, gems_db: dict, quests: list,
                    set_ids: list[int] | None = None) -> tuple[list, dict, list]:
    """Return (act_plan, where, unobtainable).

    act_plan: [(act, quest name, npc, take_reward or None, [buy (gem, npc)])]
    where[gem name] = short text on how to get it."""
    gdb = gems_db["gems"]
    by_name: dict[str, set[str]] = collections.defaultdict(set)
    for k, v in gdb.items():
        by_name[v["name"].lower()].add(k)

    # Gems the build needs, with the first skill set that uses them.
    needed: dict[str, dict] = {}
    for si, ss in enumerate(build["skill_sets"]):
        if set_ids is not None and si not in set_ids:
            continue
        for grp in ss["groups"]:
            if grp["source"]:  # granted by an item
                continue
            for g in grp["gems"]:
                gids = by_name.get(g["name"].lower(), set()) | ({g["gemId"]} if g["gemId"] in gdb else set())
                key = g["name"]
                if key not in needed:
                    main = gem_main_id(gids)
                    needed[key] = {"gid": main, "gids": gids, "first_set": si,
                                   "support": gdb.get(main, {}).get("support", "support" in g["gemId"].lower()),
                                   "enabled": False}
                needed[key]["enabled"] |= g["enabled"] and grp["enabled"]

    def ok(classes: list) -> bool:
        return not classes or class_name in classes

    remaining = {k for k, v in needed.items() if v["gid"]}
    where: dict[str, str] = {}
    plan = []
    for q in quests:
        rewards, buys = [], []
        for o in q["offers"]:
            for gname in sorted(remaining):
                for gid in needed[gname]["gids"]:
                    if gid in o["reward"] and ok(o["reward"][gid]):
                        rewards.append(gname)
                    if gid in o["vendor"] and ok(o["vendor"][gid][0]):
                        buys.append((gname, o["vendor"][gid][1]))
        if not rewards and not buys:
            continue
        rewards = sorted(set(rewards), key=lambda n: (needed[n]["first_set"], needed[n]["support"], n))
        take = rewards[0] if rewards else None
        got = set()
        if take:
            got.add(take)
            where[take] = f"Act {q['act']} — quest reward for *{q['name']}*"
        real_buys = []
        for n, npc in buys:
            if n in got:
                continue
            real_buys.append((n, npc))
            got.add(n)
            where[n] = f"Act {q['act']} — buy from {npc} after *{q['name']}*"
        remaining -= got
        if take or real_buys:
            plan.append((q["act"], q["name"], q["offers"][0]["npc"], take,
                         sorted(real_buys, key=lambda x: (needed[x[0]]["first_set"], x[0]))))
    unobtainable = []
    for n, v in needed.items():
        if n in where:
            continue
        if is_vaal(n):
            why = "Vaal gem: drops / corrupt the normal gem / trade"
        elif not v["gid"] and " of " in n:
            why = "Transfigured gem: Divine Font in the Labyrinth, or trade"
        elif not v["gid"]:
            why = "Not in the gem data (new or renamed gem?) — check poewiki"
        else:
            why = "Not sold by quest vendors (drop-only / exceptional support): trade"
        where[n] = why
        unobtainable.append(n)
    return plan, where, needed


# --------------------------------------------------------------------------- output

def md_escape(s: str) -> str:
    return s.replace("|", "\\|")


def stage_key(title: str) -> float | None:
    lv = level_from_title(title)
    if lv:
        return float(re.match(r"\d+", lv).group(0))
    act = act_from_title(title)
    if act:
        return ACT_END[min(int(re.match(r"\d+", act).group(0)), 10) - 1][1] - 5
    return None


def leveling_first(sets: list[dict]) -> bool:
    """If the first set isn't a leveling one but later ones are (endgame-first
    PoBs), move the sets with a level/act in the title to the front, in level
    order. Returns True if it reordered."""
    keys = [stage_key(x["title"]) for x in sets]
    if not sets or keys[0] is not None or all(k is None for k in keys):
        return False
    def phase(t: str) -> int:  # for the untitled-by-level rest: early < mid < late/endgame
        t = t.lower()
        return 0 if "early" in t else 2 if ("late" in t or "end" in t) else 1
    order = sorted(range(len(sets)), key=lambda i: (keys[i] is None, keys[i] or 0,
                                                    phase(sets[i]["title"]) if keys[i] is None else 0, i))
    sets[:] = [sets[i] for i in order]
    return True


def prepare(build: dict, tree: "Tree", keep_order: bool = False, class_override: str | None = None) -> dict:
    """Shared prep for both outputs: class, points/levels per tree, and
    leveling-first ordering of trees and sets. Safe to call twice."""
    if build.get("_prep"):
        return build["_prep"]
    specs = build["specs"]
    class_name = class_override or build["className"] or CLASS_NAMES[(specs[0]["classId"] or 0) if specs else 0]
    for s in specs:
        if s["classId"] is None:
            s["classId"] = CLASS_NAMES.index(build["className"]) if build["className"] in CLASS_NAMES else 0
    for s in specs:
        main = [n for n in s["nodes"] if n in tree.nodes and not tree.is_asc(n) and tree.kind(n) not in ("start", "mastery")]
        ascn = [n for n in s["nodes"] if tree.is_asc(n) and tree.kind(n) != "ascstart"
                and not tree.nodes[n].get("isBloodline")]
        s["_points"], s["_asc"] = len(main), len(ascn)
        lvl = level_from_title(s["title"])
        guess = est_level(len(main) + len(s["masteries"]), build["bandit"])
        s["_lvl"] = (lvl, True) if lvl else (f"≈{guess}", False)
        s["_act"] = act_from_title(s["title"])
    # Guides often put the endgame tree first. If a tree has clearly more
    # points than a later one, show them sorted by points instead.
    reordered = False
    if not keep_order and any(a["_points"] > b["_points"] + 10
                              for i, a in enumerate(specs) for b in specs[i + 1:]):
        specs.sort(key=lambda s: s["_points"])
        reordered = True
    moved = [name for name, key in (("skill sets", "skill_sets"), ("item sets", "item_sets"))
             if not keep_order and leveling_first(build[key])]
    build["_prep"] = {"class_name": class_name, "reordered": reordered, "moved": moved}
    return build["_prep"]


def render(build: dict, tree: Tree, gems_db: dict, quests_db: dict, source: str,
           class_override: str | None, keep_order: bool = False) -> str:
    out: list[str] = []
    w = out.append
    specs = build["specs"]
    prep = prepare(build, tree, keep_order, class_override)
    class_name, reordered, moved = prep["class_name"], prep["reordered"], prep["moved"]
    asc = build["ascendClassName"]
    gdb = gems_db["gems"]

    w(f"# Leveling plan: {asc or class_name} ({class_name})")
    w("")
    w(f"Generated {dt.date.today().isoformat()} by `tools/pob_leveling.py` from {source}. "
      f"PoB character level {build['level']}, bandit: {build['bandit'] or 'None (kill all, +2 points)'}.")
    w(f"Tree data: GGG export ({tree.fetched}); gem/quest data: exile-leveling ({gems_db.get('_fetched', '?')}). "
      "**Quest rewards and gems can change in a new league — check the patch notes.**")
    w("")
    w(f"Contents: {len(specs)} passive trees · {len(build['skill_sets'])} skill sets · "
      f"{len(build['item_sets'])} item sets")
    w("")

    if specs:
        w("## Trees at a glance")
        w("")
        w("| # | Tree (PoB title) | Passive points | Level | Ascendancy points |")
        w("|---|---|---|---|---|")
        for i, s in enumerate(specs, 1):
            lvl = s["_lvl"][0] + (f" (end of act {s['_act']})" if s["_act"] else "")
            w(f"| {i} | {md_escape(s['title'])} | {s['_points']} | {lvl} | {s['_asc']} |")
        w("")
        w("Level comes from the tree title when it has one, otherwise it's estimated from points "
          "(`≈`, assumes you do the quests that give passive points).")
        if reordered:
            w("**Trees are sorted by points here**: the PoB lists them in a different order "
              "(usually endgame first). Use `--keep-order` to keep the PoB's order.")
        w("")

    # ---- gem plan
    if moved:
        w(f"*Leveling {' and '.join(moved)} (titles with a level or act) are listed first; "
          "the PoB has them after the endgame ones.*")
        w("")
    plan, where, needed = gem_acquisition(build, class_name, gems_db, quests_db["quests"])
    if needed:
        w(f"## Gems: what to take and buy, act by act ({class_name})")
        w("")
        w("Quest reward = pick it from the quest's reward list (one per quest). "
          "Buy = from that act's gem vendor once the quest is done (cheap: Wisdom / Transmute / Alteration).")
        w("")
        cur_act = None
        for act, qname, npc, take, buys in plan:
            if act != cur_act:
                if cur_act is not None:
                    w("")
                w(f"**Act {act}**")
                w("")
                cur_act = act
            bits = []
            if take:
                lv = gdb.get(needed[take]["gid"], {}).get("lvl", 1)
                bits.append(f"take **{take}** (lvl {lv})")
            if buys:
                bits.append("buy " + ", ".join(
                    f"{n} (lvl {gdb.get(needed[n]['gid'], {}).get('lvl', 1)})" for n, _ in buys)
                    + f" from {buys[0][1]}")
            first = min(needed[n]["first_set"] for n in ([take] if take else []) + [n for n, _ in buys])
            w(f"- *{qname}*: " + "; ".join(bits) + f" — needed from *{build['skill_sets'][first]['title']}*")
        w("")
        other = [n for n in needed if not where[n].startswith("Act")]
        if other:
            w("**Not from quests or vendors:**")
            w("")
            for n in other:
                w(f"- {n}: {where[n]}")
            w("")

        w("### Every gem, by first use")
        w("")
        w("| Gem | Req. level | First used in | Get it |")
        w("|---|---|---|---|")
        for n, v in sorted(needed.items(), key=lambda x: (x[1]["first_set"], x[1]["support"], x[0])):
            lv = gdb.get(v["gid"], {}).get("lvl", "?")
            first = build["skill_sets"][v["first_set"]]["title"]
            flag = "" if v["enabled"] else " (disabled in PoB)"
            w(f"| {n}{flag} | {lv} | {md_escape(first)} | {where[n]} |")
        w("")

    # ---- skill sets
    if build["skill_sets"]:
        w("## Skill sets (gem links)")
        w("")
        prev: set[str] = set()
        for i, ss in enumerate(build["skill_sets"], 1):
            w(f"### {i}. {ss['title']}")
            w("")
            names_now: set[str] = set()
            for grp in ss["groups"]:
                gems = [g for g in grp["gems"]]
                if not gems:
                    continue
                parts = []
                for g in gems:
                    n = g["name"]
                    names_now.add(n)
                    t = n if n in prev else f"**{n}**"
                    if not g["enabled"]:
                        t = f"~~{n}~~"
                    parts.append(t)
                where_txt = grp["label"] or grp["slot"] or ""
                extra = []
                if grp["slot"] and grp["label"]:
                    extra.append(grp["slot"])
                if not grp["enabled"]:
                    extra.append("disabled")
                if grp["source"]:
                    extra.append("from item")
                tag = f" ({', '.join(extra)})" if extra else ""
                link = f"{len(gems)}L" if len(gems) > 1 else "1"
                w(f"- {link}{': ' + md_escape(where_txt) if where_txt else ''}{tag} — " + " – ".join(parts))
            dropped = sorted(prev - names_now)
            if dropped and i > 1:
                w(f"- *Dropped:* {', '.join(dropped)}")
            w("")
            prev = names_now
        w("**Bold** = new since the previous set. ~~Struck~~ = disabled in PoB.")
        w("")

    # ---- trees
    if specs:
        w("## Passive tree progression")
        w("")
        w("Each step is a connected path ending on a notable, in the order to take them. "
          "Small nodes on the way are summarised.")
        w("")
        prev_nodes: set[int] = set()
        prev_mast: dict[int, int] = {}
        asc_have: set[int] = set()
        for i, s in enumerate(specs, 1):
            nodes = set(s["nodes"])
            known = {n for n in nodes if n in tree.nodes}
            unknown = nodes - known
            cs = tree.class_start(s["classId"])
            ascname = tree.asc_name(s["classId"], s["ascendClassId"])
            main_now = {n for n in known if not tree.is_asc(n) and tree.kind(n) not in ("start", "mastery")}
            main_prev = {n for n in prev_nodes if n in tree.nodes and not tree.is_asc(n)
                         and tree.kind(n) not in ("start", "mastery")}
            add = main_now - main_prev
            remove = main_prev - main_now
            lvl, from_title = s["_lvl"]
            w(f"### Tree {i}: {s['title']}")
            w("")
            w(f"{s['_points']} points (level {lvl.lstrip('≈') if from_title else lvl})"
              + (f" · {ascname}" if ascname else "")
              + (f" · tree {s['treeVersion']}" if s["treeVersion"] else "")
              + (f" · [open tree]({s['url']})" if s["url"].startswith("http") else ""))
            w("")
            if remove:
                big = [tree.label(n) for n in sorted(remove, key=tree.name) if tree.is_big(n)]
                w(f"**Respec {len(remove)} points** (Orbs of Regret): "
                  + (", ".join(big) + (f" + {len(remove) - len(big)} small" if len(remove) > len(big) else "")
                     if big else f"{len(remove)} small nodes"))
                w("")
            start = (main_now & main_prev) | ({cs} if cs else set())
            chunks, unreach = tree.order(start, add)
            if chunks:
                w(f"Allocate {len(add)} points:" if i > 1 else f"Allocate {len(add)} points from the class start:")
                w("")
                n_done = len(main_prev & main_now)
                for chunk in chunks:
                    big = [n for n in chunk if tree.is_big(n)]
                    small = [n for n in chunk if not tree.is_big(n)]
                    n_done += len(chunk)
                    if big:
                        head = tree.label(big[-1])
                        stats = "; ".join(tree.nodes[big[-1]].get("stats", [])).replace("\n", " ")
                        stats = f" *({stats})*" if stats else ""
                        via = f" — via {len(small)}: {tree.small_summary(small)}" if small else ""
                        w(f"1. {head}{stats}{via} `[{n_done}]`")
                    else:
                        w(f"1. {len(small)} small: {tree.small_summary(small)} `[{n_done}]`")
                w("")
                w("`[n]` = points spent once this step is done.")
                w("")
            if unreach:
                w(f"*Not connected to the rest of the tree ({len(unreach)}), usually taken through a jewel such as "
                  "Thread of Hope / Impossible Escape / Intuitive Leap, or an anoint:* "
                  + ", ".join(tree.label(n) for n in sorted(unreach)))
                w("")
            if unknown:
                w(f"*{len(unknown)} node ids not in the tree data (cluster-jewel nodes or a different tree version).*")
                w("")
            # masteries
            mast_new = {k: v for k, v in s["masteries"].items() if prev_mast.get(k) != v}
            if mast_new:
                w("Masteries: " + "; ".join(
                    f"{tree.name(k)}: *{' / '.join(tree.nodes.get(k, {}).get('masteryEffects', {}).get(str(v), ['effect ' + str(v)]))}*"
                    for k, v in mast_new.items()))
                w("")
            # ascendancy (and bloodline / secondary ascendancy, counted separately)
            asc_now = {n for n in known if tree.is_asc(n) and tree.kind(n) != "ascstart"}
            asc_add = asc_now - asc_have
            groups = collections.defaultdict(set)
            for n in asc_add:
                groups[tree.nodes[n]["ascendancyName"]].add(n)
            for aname, add_n in sorted(groups.items(), key=lambda g: tree.nodes[next(iter(g[1]))].get("isBloodline", False)):
                bloodline = any(tree.nodes[n].get("isBloodline") for n in add_n)
                had = {n for n in asc_now & asc_have if tree.nodes[n]["ascendancyName"] == aname}
                ast = tree.asc_start(aname)
                achunks, rest = tree.order(had | ({ast} if ast else set()), add_n)
                if rest:
                    achunks.append(sorted(rest))
                pts = len(had)
                steps = []
                for ch in achunks:
                    pts += len(ch)
                    where_ = "" if bloodline else ", " + LABS[min((pts - 1) // 2, 3)].split(" (")[0]
                    big = [n for n in ch if tree.is_big(n)]
                    steps.append(f"{', '.join(tree.label(n) for n in big) or tree.small_summary(ch)} "
                                 f"({pts} pts{where_})")
                w(("Bloodline / secondary ascendancy " if bloodline else "Ascendancy ")
                  + f"({aname}): " + " → ".join(steps))
                w("")
            if asc_have - asc_now:
                w("Ascendancy respec: " + ", ".join(tree.label(n) for n in asc_have - asc_now if tree.is_big(n)))
                w("")
            prev_nodes, prev_mast, asc_have = nodes, s["masteries"], asc_now

    # ---- items
    if build["item_sets"]:
        w("## Item sets")
        w("")
        uniques: dict[str, dict] = {}
        for i, s in enumerate(build["item_sets"], 1):
            for slot, item in s["slots"]:
                if item["rarity"] == "UNIQUE" and item["name"] not in uniques:
                    uniques[item["name"]] = {"base": item["base"], "slot": slot, "set": s["title"],
                                             "req": item["levelreq"]}
        if uniques:
            w("### Uniques the guide uses (first item set they appear in)")
            w("")
            w("| Unique | Base | Slot | Level req | First set |")
            w("|---|---|---|---|---|")
            for n, u in uniques.items():
                w(f"| {n} | {u['base']} | {u['slot']} | {u['req'] or '?'} | {md_escape(u['set'])} |")
            w("")
            w("Price them on poe.ninja / trade before committing.")
            w("")
        w("Each set lists only the slots that changed from the previous set. "
          "Rares show the mods the guide aims for (its stat targets, not an exact item).")
        w("")
        prev_items: dict[str, str] = {}
        for i, s in enumerate(build["item_sets"], 1):
            cur = {slot: "\n".join(item["text"]) for slot, item in s["slots"]}
            changed = [(slot, item) for slot, item in s["slots"] if prev_items.get(slot) != cur[slot]]
            gone = [slot for slot in prev_items if slot not in cur]
            prev_items = cur
            if not changed and not gone:
                continue
            w(f"### {i}. {s['title']}")
            w("")
            for slot, item in changed:
                req = f"lvl {item['levelreq']}" if item["levelreq"] else ""
                sock = item["sockets"]
                meta = ", ".join(x for x in (req, sock and f"sockets {sock}") if x)
                if item["rarity"] == "UNIQUE":
                    w(f"- {slot}: **{item['name']}** ({item['base']}{', ' + meta if meta else ''})")
                else:
                    mods = "; ".join(item["mods"][:8]) + (" …" if len(item["mods"]) > 8 else "")
                    w(f"- {slot}: {item['rarity'].title() or '?'} {item['base']}"
                      f"{' (' + meta + ')' if meta else ''}{' — ' + mods if mods else ''}")
            if gone:
                w(f"- *Removed:* {', '.join(gone)}")
            w("")

    if build["notes"]:
        w("## Author's PoB notes")
        w("")
        w("```text")
        w(build["notes"])
        w("```")
        w("")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", nargs="?", help="PoB code, pobb.in/pastebin/poe.ninja link, file, or - for stdin")
    ap.add_argument("-o", "--out", help="write here: .md = full plan, .html = one-page glance sheet (default: print markdown)")
    ap.add_argument("--save-xml", help="also save the decoded PoB XML here")
    ap.add_argument("--class", dest="cls", choices=CLASS_NAMES, help="class for gem rewards (default: from PoB)")
    ap.add_argument("--label", help="how to name the source in the output (e.g. the guide URL)")
    ap.add_argument("--keep-order", action="store_true", help="keep the PoB's tree order (default: sort by points if it's jumbled)")
    ap.add_argument("--update-data", action="store_true", help="re-download tree / gem / quest data")
    a = ap.parse_args()
    if a.update_data:
        update_data()
        if not a.source:
            return
    if not a.source:
        ap.error("give a PoB code, link or file")
    xml_text, label = load_build_xml(a.source)
    label = a.label or label
    if a.save_xml:
        Path(a.save_xml).write_text(xml_text, encoding="utf-8")
    tree_data, gems, quests = load_data()
    build, tree = parse_build(xml_text), Tree(tree_data)
    if a.out and a.out.lower().endswith(".html"):
        sys.path.insert(0, str(HERE))
        import pob_sheet
        md_name = Path(a.out).with_suffix(".md").name if Path(a.out).with_suffix(".md").exists() else ""
        page = pob_sheet.render_html(build, tree, gems, quests, label, a.cls, a.keep_order, md_name)
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(page, encoding="utf-8")
        print(f"Wrote {a.out}", file=sys.stderr)
        return
    md = render(build, tree, gems, quests, label, a.cls, a.keep_order)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(md + "\n", encoding="utf-8")
        print(f"Wrote {a.out}", file=sys.stderr)
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(md)


if __name__ == "__main__":
    main()
