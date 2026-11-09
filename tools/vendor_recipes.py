#!/usr/bin/env python3
"""Pull the vendor recipe list from poewiki into tools/pob_data/vendor_recipes.json.

poewiki is blocked from Claude's cloud sessions, so run this on a normal PC
(Nick's desktop, or a Claude Remote Control session on it):

    python tools/vendor_recipes.py                  # refresh the data file
    python tools/vendor_recipes.py --raw page.json  # also keep the raw API answer
    python tools/vendor_recipes.py --show leveling  # print recipes whose text matches a word

The leveling sheet (pob_sheet.py) reads the data file and puts the recipes
that fit the build (move speed, weapon damage for its element / attack or
spell) on the Act 1-2 cards. Re-run after a league launch: GGG adds and
changes recipes now and then.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

PAGE = "Vendor_recipe_system"
APIS = ["https://www.poewiki.net/w/api.php", "https://www.poewiki.net/api.php"]
OUT = Path(__file__).resolve().parent / "pob_data" / "vendor_recipes.json"
UA = "pob-leveling-extractor/1.0 (+https://github.com/kruppenb/PathOfExile)"


def fetch() -> tuple[dict, str]:
    q = urllib.parse.urlencode({"action": "parse", "page": PAGE, "prop": "text|wikitext",
                                "format": "json", "formatversion": "2", "redirects": "1"})
    err = None
    for api in APIS:
        try:
            req = urllib.request.Request(f"{api}?{q}", headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode("utf-8"))
            if "parse" in data:
                return data, api
            err = data.get("error")
        except Exception as e:  # noqa: BLE001
            err = e
    sys.exit(f"Couldn't read poewiki ({err}). It's blocked from the cloud: run this on your PC.")


class Tables(HTMLParser):
    """Collect (heading path, table rows) from the rendered page."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.heads: list[str] = ["", "", "", ""]  # h2..h5
        self.in_head = None
        self.head_text = ""
        self.tables: list[dict] = []
        self.stack: list[dict] = []  # nested tables
        self.cell = None
        self.skip: list = []  # [tag, depth] while inside style/script/footnotes/item tooltips

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.skip:
            if tag == self.skip[0]:
                self.skip[1] += 1
            return
        cls = a.get("class") or ""
        if tag in ("style", "script") or (tag == "sup" and "reference" in cls) or \
                (tag == "span" and "hoverbox__display" in cls):
            self.skip = [tag, 1]
            return
        if tag in ("h2", "h3", "h4", "h5"):
            self.in_head, self.head_text = int(tag[1]), ""
        elif tag == "table":
            self.stack.append({"heading": " › ".join(h for h in self.heads if h), "rows": []})
        elif tag == "tr" and self.stack:
            self.stack[-1]["rows"].append([])
        elif tag in ("td", "th") and self.stack and self.stack[-1]["rows"]:
            self.cell = {"th": tag == "th", "text": ""}
        elif tag == "br" and self.cell is not None:
            self.cell["text"] += " / "
        elif tag == "img" and self.cell is not None and a.get("alt"):
            self.cell["text"] += f" {a['alt']} "
        elif tag == "li" and self.cell is not None:
            self.cell["text"] += " / "

    def handle_endtag(self, tag):
        if self.skip:
            if tag == self.skip[0]:
                self.skip[1] -= 1
                if not self.skip[1]:
                    self.skip = []
            return
        if tag in ("h2", "h3", "h4", "h5") and self.in_head:
            lvl = self.in_head - 2
            self.heads[lvl] = re.sub(r"\s*\[edit\]\s*$", "", self.head_text.strip())
            for i in range(lvl + 1, 4):
                self.heads[i] = ""
            self.in_head = None
        elif tag in ("td", "th") and self.cell is not None and self.stack:
            t = re.sub(r"\s+", " ", self.cell["text"]).strip(" /")
            self.stack[-1]["rows"][-1].append((self.cell["th"], t))
            self.cell = None
        elif tag == "table" and self.stack:
            self.tables.append(self.stack.pop())

    def handle_data(self, data):
        if self.skip:
            return
        if self.in_head:
            self.head_text += data
        elif self.cell is not None:
            self.cell["text"] += data


def to_recipes(tables: list[dict]) -> list[dict]:
    out = []
    for t in tables:
        header = None
        for row in t["rows"]:
            if row and all(th for th, _ in row):
                header = [c for _, c in row]
                continue
            cells = [c for _, c in row]
            if not cells or not any(cells):
                continue
            if header and len(cells) <= len(header):  # shorter rows: a rowspan'd Notes cell
                rec = dict(zip(header, cells))
            else:
                rec = {f"col{i}": c for i, c in enumerate(cells)}
            rec["_section"] = t["heading"]
            out.append(rec)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", help="also save the raw API answer (JSON) here")
    ap.add_argument("--show", help="print recipes containing this word (after refreshing)")
    ap.add_argument("--offline", action="store_true", help="don't fetch; use the saved data file")
    ap.add_argument("--from-raw", help="parse a raw API answer saved earlier with --raw instead of fetching")
    a = ap.parse_args()
    if a.from_raw:
        data, api = json.loads(Path(a.from_raw).read_text(encoding="utf-8")), APIS[0]
    if a.from_raw or not a.offline:
        if not a.from_raw:
            data, api = fetch()
        if a.raw:
            Path(a.raw).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        p = Tables()
        p.feed(data["parse"]["text"])
        recipes = to_recipes(p.tables)
        OUT.parent.mkdir(exist_ok=True)
        OUT.write_text(json.dumps({"_source": f"https://www.poewiki.net/wiki/{PAGE}", "_fetched": dt.date.today().isoformat(),
                                   "recipes": recipes}, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Saved {len(recipes)} recipes from {len(p.tables)} tables to {OUT}", file=sys.stderr)
    if a.show:
        recipes = json.loads(OUT.read_text(encoding="utf-8"))["recipes"]
        w = a.show.lower()
        for r in recipes:
            text = " | ".join(f"{k}: {v}" for k, v in r.items())
            if w in text.lower():
                print(html.unescape(text))


if __name__ == "__main__":
    main()
