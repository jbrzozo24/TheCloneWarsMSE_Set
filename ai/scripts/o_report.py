#!/usr/bin/env python3
"""Report the Dark Side (O) economy of TheCloneWars.mse-set.

  o_report.py              write ai/reports/o-economy-YYYY-MM-DD_HHMMSS.md
  o_report.py --out FILE   write the report to FILE instead
  o_report.py --stdout     print the report instead of writing a file

Reads card text from the MSE set (only cards `set` references) and finds every
line with an O symbol. Each line is classed as:

  source     gives you O ("you get OO", "add O")
  spender    spends O (an `OO:` cost, "pay OO", kicker OO)
  threshold  cares how much O you have ("three or more O", "for each OO you have")

A card can be in several classes. Archetype and colour come from the sheet dump
(scripts/Cards_dump.json), matched by card code; back faces use the front's row.
Copies follow CLAUDE.md: common/uncommon x2, rare/mythic x1.
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mse_card import REPO, SET_DIR, load_cards, read_text, strip_tags  # noqa: E402
from mse_changes import parse_card  # noqa: E402

DUMP = REPO / "scripts" / "Cards_dump.json"
REPORTS_DIR = REPO / "ai" / "reports"
COPIES = {"common": 2, "uncommon": 2, "rare": 1, "mythic rare": 1}
RARITY_ORDER = ["common", "uncommon", "rare", "mythic rare"]
COLOURS = "WUBRG"
ARCHETYPES = ["Republic", "Coruscant", "Droids", "Separatist", "Jedi", "Kamino",
              "Sith", "Geonosis", "Bounty Hunters", "Tatooine", "Glue"]
NUMBERS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}
# Frames whose rules live in level_N_text; their rule_text is unused and can be stale.
LEVEL_FRAMES = {"m15-saga", "m15-mainframe-planeswalker"}

O_TOKEN = r"\b\d*O+\b"
NUM = r"(\d+|" + "|".join(NUMBERS) + r")"
SOURCE_RE = re.compile(rf"\b(you get|get|add)\s+(?:{NUM}\s+)?{O_TOKEN}", re.I)
AMPLIFY_RE = re.compile(r"if you would get one or more O", re.I)
THRESHOLD_RE = re.compile(rf"(?:have|has)\s+{NUM}\s+or more\s+O\b|number of O you have|for each\s+O+\s+you have", re.I)
REPEAT_RE = re.compile(r"\b(whenever|at the beginning)\b|^\s*T\b|\bT:", re.I)


def o_count(token: str) -> int:
  return token.count("O")


def amount_given(line: str):
  m = SOURCE_RE.search(line)
  if not m:
    return None
  word = m.group(2)
  tokens = re.findall(O_TOKEN, line[m.start():m.end()])
  n = o_count(tokens[-1]) if tokens else 1
  if word:
    n = int(word) if word.isdigit() else NUMBERS[word.lower()]
  return n


def amount_spent(line: str):
  m = re.search(r"(?:^|[.•]\s*)\d*(O+)(?:,[^:.]*)?:", line)
  if m:
    return o_count(m.group(1))
  m = re.search(rf"\b(?:pay|Kicker)\s+({O_TOKEN})", line, re.I)
  if m:
    return o_count(m.group(1))
  return None


def threshold_value(line: str):
  m = re.search(rf"(?:have|has)\s+{NUM}\s+or more\s+O\b", line, re.I)
  if m:
    w = m.group(1)
    return int(w) if w.isdigit() else NUMBERS[w.lower()]
  return None


def classify(line: str) -> dict:
  """Which classes an O line belongs to, with the amounts involved."""
  out = {}
  if AMPLIFY_RE.search(line):
    out["source"] = {"amount": "+1 per trigger", "repeat": True}
  elif SOURCE_RE.search(line):
    out["source"] = {"amount": amount_given(line), "repeat": bool(REPEAT_RE.search(line))}
  spent = amount_spent(line)
  if spent is not None:
    out["spender"] = {"amount": spent}
  if THRESHOLD_RE.search(line):
    out["threshold"] = {"amount": threshold_value(line)}
  return out


def text_fields(f: dict) -> list:
  keys = []
  for key in f:
    if re.fullmatch(r"level_\d+_text", key):
      keys.append(key)
    elif re.fullmatch(r"rule_text(_2)?", key) and not (key == "rule_text" and f.get("stylesheet") in LEVEL_FRAMES):
      keys.append(key)
  return keys


def base_code(code: str) -> str:
  return re.sub(r"B(_\d+)?$", "", code or "")


def colours_of(cost: str) -> str:
  return "".join(c for c in COLOURS if c in (cost or ""))


GUILDS = {"Selesnya": "Republic", "Orzhov": "Coruscant", "Azorius": "Droids", "Dimir": "Separatist",
          "Simic": "Jedi", "Izzet": "Kamino", "Rakdos": "Sith", "Golgari": "Geonosis",
          "Gruul": "Bounty Hunters", "Boros": "Tatooine", "Separatists": "Separatist"}


def archetypes(value: str) -> list:
  """Sheet archetype cell -> archetype names ("Sith - Rakdos", "Gruul, Sith" -> ["Bounty Hunters", "Sith"])."""
  out = []
  for part in re.split(r"\s*,\s*", value or ""):
    name = part.split(" - ")[0].strip()
    name = GUILDS.get(name, name)
    if name and name not in out:
      out.append(name)
  return out


def load_dump() -> dict:
  if not DUMP.is_file():
    return {}
  return {str(row["Card Code"]): row for row in json.loads(DUMP.read_text(encoding="utf-8"))}


def collect():
  sheet = load_dump()
  cards = {}
  for card in load_cards():
    if not card["file"]:
      continue
    f = parse_card(read_text(SET_DIR / card["file"]))
    code = strip_tags(f.get("card_code_text", "")).strip()
    hits = []
    for key in text_fields(f):
      for line in strip_tags(f[key]).splitlines():
        line = line.strip()
        if re.search(O_TOKEN, line):
          classes = classify(line)
          if classes:
            hits.append({"field": key, "line": line, "classes": classes})
    if not hits:
      continue
    base = base_code(code)
    row = sheet.get(code) or {}
    front = sheet.get(base) or {}
    name = strip_tags(f.get("name", "")).strip()
    if any(h["field"].endswith("_2") for h in hits) and f.get("name_2"):
      name = f"{name} // {strip_tags(f['name_2']).strip()}"
    rarity = f.get("rarity", "").strip()
    colour = colours_of(f.get("casting_cost", "")) or colours_of(row.get("Color")) or colours_of(front.get("Color"))
    arch_row = row if row.get("Archetype") else front
    sheet_name = (arch_row.get("Card Name") or "").strip()
    stale = bool(arch_row) and sheet_name.lower() != strip_tags(f.get("name", "")).strip().lower() and arch_row is row
    entry = cards.setdefault(base or code, {
      "code": base or code, "name": name, "cost": strip_tags(f.get("casting_cost", "")).strip(),
      "rarity": rarity, "copies": COPIES.get(rarity, 1), "colour": colour,
      "archetype": (archetypes(arch_row.get("Archetype", "")) or [""])[0],
      "secondary": [a for a in archetypes(arch_row.get("Secondary Archetype", ""))
                    if a != (archetypes(arch_row.get("Archetype", "")) or [""])[0]],
      "stale_sheet": sheet_name if stale else "", "hits": [],
    })
    for h in hits:
      if h["field"].endswith("_2") and f.get("name_2"):
        h["face"] = strip_tags(f["name_2"]).strip()
      elif code != entry["code"]:
        h["face"] = f"{code} {strip_tags(f.get('name', '')).strip()}"
    entry["hits"] += hits
  return list(cards.values())


def classes_of(card) -> set:
  return {c for h in card["hits"] for c in h["classes"]}


def fmt_amount(card, cls) -> str:
  vals = [h["classes"][cls] for h in card["hits"] if cls in h["classes"]]
  parts = []
  for v in vals:
    a = v.get("amount")
    if cls == "source":
      parts.append(f"{a}{' (repeatable)' if v.get('repeat') else ''}" if a is not None else "?")
    elif cls == "spender":
      parts.append(f"{a}" if a is not None else "?")
    else:
      parts.append(f"{a}+" if a is not None else "scales")
  return ", ".join(parts)


def card_row(card, cls) -> str:
  arch = card["archetype"] or "—"
  if card["secondary"]:
    arch += " / " + ", ".join(card["secondary"])
  if card["stale_sheet"]:
    arch += " †"
  lines = [h for h in card["hits"] if cls in h["classes"]]
  text = "<br>".join((f"_{h['face']}:_ " if h.get("face") else "") + h["line"].replace("|", "\\|") for h in lines)
  return (f"| {card['code']} | {card['name']} | {card['cost'] or '—'} | {card['rarity']} ×{card['copies']} "
          f"| {card['colour'] or 'C'} | {arch} | {fmt_amount(card, cls)} | {text} |")


def table(cards, cls, amount_label) -> list:
  rows = sorted(cards, key=lambda c: (RARITY_ORDER.index(c["rarity"]) if c["rarity"] in RARITY_ORDER else 9, c["code"]))
  out = [f"| Code | Card | Cost | Rarity | Colour | Archetype | {amount_label} | Text |",
         "|---|---|---|---|---|---|---|---|"]
  return out + [card_row(c, cls) for c in rows]


def weighted(cards) -> int:
  return sum(c["copies"] for c in cards)


def breakdown(groups: dict, keys: list, label: str) -> list:
  out = [f"| {label} | Sources | Spenders | Thresholds | Any O card |", "|---|---|---|---|---|"]
  for key in keys:
    g = groups.get(key, {})
    if not any(g.values()):
      continue
    cells = [f"{len(g.get(c, []))} ({weighted(g.get(c, []))})" for c in ("source", "spender", "threshold", "any")]
    out.append(f"| {key} | " + " | ".join(cells) + " |")
  return out


def render(cards) -> str:
  by_class = {c: [x for x in cards if c in classes_of(x)] for c in ("source", "spender", "threshold")}
  payoffs = [x for x in cards if classes_of(x) & {"spender", "threshold"}]
  pure_sources = [x for x in by_class["source"] if not classes_of(x) & {"spender", "threshold"}]
  pure_payoffs = [x for x in payoffs if "source" not in classes_of(x)]
  both = [x for x in by_class["source"] if classes_of(x) & {"spender", "threshold"}]

  stamp = datetime.now()
  out = [f"# Dark Side (O) economy\n",
         f"_{stamp:%Y-%m-%d %H:%M}_ · from `TheCloneWars.mse-set`, archetypes from the sheet dump\n",
         "Counts are **cards (copies in the set)**: commons and uncommons count twice, rares and mythics once.\n",
         "## Summary\n",
         "| | Cards | Copies |", "|---|---|---|",
         f"| Cards that mention O | {len(cards)} | {weighted(cards)} |",
         f"| **Sources** (give O) | {len(by_class['source'])} | {weighted(by_class['source'])} |",
         f"| **Payoffs** (spend or count O) | {len(payoffs)} | {weighted(payoffs)} |",
         f"| ↳ Spenders (pay O) | {len(by_class['spender'])} | {weighted(by_class['spender'])} |",
         f"| ↳ Thresholds (care how much O you have) | {len(by_class['threshold'])} | {weighted(by_class['threshold'])} |",
         f"| Source only | {len(pure_sources)} | {weighted(pure_sources)} |",
         f"| Payoff only | {len(pure_payoffs)} | {weighted(pure_payoffs)} |",
         f"| Source and payoff on one card | {len(both)} | {weighted(both)} |", ""]

  given = [h["classes"]["source"] for c in by_class["source"] for h in c["hits"] if "source" in h["classes"]]
  repeat = sum(1 for g in given if g.get("repeat"))
  numeric = [g["amount"] for g in given if isinstance(g["amount"], int)]
  spent = [h["classes"]["spender"]["amount"] for c in by_class["spender"] for h in c["hits"]
           if "spender" in h["classes"] and isinstance(h["classes"]["spender"]["amount"], int)]
  thresholds = Counter(h["classes"]["threshold"]["amount"] for c in by_class["threshold"] for h in c["hits"]
                       if "threshold" in h["classes"])
  out += ["## Amounts\n",
          f"- **Source abilities:** {len(given)}, of which {repeat} repeatable (whenever / each turn / tap) "
          f"and {len(given) - repeat} one-shot (ETB, spell, chapter).",
          f"- **O per source ability:** " + ", ".join(f"{n}×{k}" for k, n in sorted(Counter(numeric).items())) +
          (f" (average {sum(numeric) / len(numeric):.1f})" if numeric else ""),
          f"- **O per spend:** " + ", ".join(f"{n}×{k}" for k, n in sorted(Counter(spent).items())) +
          (f" (average {sum(spent) / len(spent):.1f})" if spent else ""),
          f"- **Thresholds:** " + ", ".join(f"{k if k is not None else 'scales with O'}: {n}"
                                             for k, n in sorted(thresholds.items(), key=lambda kv: (kv[0] is None, kv[0] or 0))),
          ""]

  def group(key_fn):
    groups = defaultdict(lambda: defaultdict(list))
    for c in cards:
      for k in key_fn(c):
        for cls in classes_of(c):
          groups[k][cls].append(c)
        groups[k]["any"].append(c)
    return groups

  out += ["## By colour\n", "A multicolour card counts under each of its colours. Back faces take the front's colour from the sheet.\n"]
  out += breakdown(group(lambda c: list(c["colour"]) or ["Colourless"]), list(COLOURS) + ["Colourless"], "Colour") + [""]
  out += ["## By archetype\n", "Primary archetype from the sheet; a secondary archetype counts too.\n"]
  arch_keys = ARCHETYPES + sorted({a for c in cards for a in [c["archetype"], *c["secondary"]] if a and a not in ARCHETYPES}) + ["—"]
  out += breakdown(group(lambda c: [a for a in [c["archetype"], *c["secondary"]] if a] or ["—"]), arch_keys, "Archetype") + [""]
  out += ["## By rarity\n"]
  out += breakdown(group(lambda c: [c["rarity"]]), RARITY_ORDER, "Rarity") + [""]

  out += ["## Sources\n", "Amount is O per ability; _repeatable_ means it can trigger more than once.\n"]
  out += table(by_class["source"], "source", "O given") + [""]
  out += ["## Payoffs: spend O\n"]
  out += table(by_class["spender"], "spender", "O spent") + [""]
  out += ["## Payoffs: care how much O you have\n"]
  out += table(by_class["threshold"], "threshold", "Needs") + [""]

  stale = [c for c in cards if c["stale_sheet"]]
  if stale:
    out += ["---\n", "† The sheet row for this code is still the card it replaced, so its archetype may be out of date: " +
            "; ".join(f"{c['code']} {c['name']} (sheet: {c['stale_sheet']})" for c in stale) + ".\n"]
  return "\n".join(out) + "\n"


def main():
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("--out", help="report file (default: ai/reports/o-economy-<timestamp>.md)")
  parser.add_argument("--stdout", action="store_true", help="print the report instead of writing a file")
  args = parser.parse_args()
  text = render(collect())
  if args.stdout:
    print(text, end="")
    return
  path = Path(args.out) if args.out else REPORTS_DIR / f"o-economy-{datetime.now():%Y-%m-%d_%H%M%S}.md"
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(text, encoding="utf-8")
  print(f"wrote {path.resolve().relative_to(REPO) if path.resolve().is_relative_to(REPO) else path}")


if __name__ == "__main__":
  main()
