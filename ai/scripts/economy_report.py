#!/usr/bin/env python3
"""Report the Light Side (L) or Dark Side (O) economy of TheCloneWars.mse-set.

  economy_report.py L              write ai/reports/l-economy-YYYY-MM-DD_HHMMSS.md
  economy_report.py O              write ai/reports/o-economy-YYYY-MM-DD_HHMMSS.md
  economy_report.py L --out FILE   write the report to FILE instead
  economy_report.py L --stdout     print the report instead of writing a file

Reads card text from the MSE set (only cards `set` references) and finds every
line with the symbol. Each line is classed as:

  source     gives you the symbol ("you get LL", "you get L for each Clone")
  spender    spends it (an `LL:` / `1G, L:` cost, "pay LL", kicker OO)
  threshold  cares how much you have ("three or more O", "the number of L you have")
  trigger    cares that you got or spent it ("whenever you spend one or more L")

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
SYMBOLS = {"L": "Light Side", "O": "Dark Side"}
COPIES = {"common": 2, "uncommon": 2, "rare": 1, "mythic rare": 1}
RARITY_ORDER = ["common", "uncommon", "rare", "mythic rare"]
COLOURS = "WUBRG"
ARCHETYPES = ["Republic", "Coruscant", "Droids", "Separatist", "Jedi", "Kamino",
              "Sith", "Geonosis", "Bounty Hunters", "Tatooine", "Glue"]
GUILDS = {"Selesnya": "Republic", "Orzhov": "Coruscant", "Azorius": "Droids", "Dimir": "Separatist",
          "Simic": "Jedi", "Izzet": "Kamino", "Rakdos": "Sith", "Golgari": "Geonosis",
          "Gruul": "Bounty Hunters", "Boros": "Tatooine", "Separatists": "Separatist"}
NUMBERS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}
NUM = r"(\d+|" + "|".join(NUMBERS) + r")"
# Frames whose rules live in level_N_text; their rule_text is unused and can be stale.
LEVEL_FRAMES = {"m15-saga", "m15-mainframe-planeswalker"}
CLASSES = ["source", "spender", "threshold", "trigger"]
PAYOFFS = {"spender", "threshold", "trigger"}


class Economy:
  """Regexes for one symbol (L or O)."""

  def __init__(self, s: str):
    self.s = s
    self.token = rf"\b\d*{s}+\b"
    self.source = re.compile(rf"\b(you get|get|add)\s+(?:{NUM}\s+)?\d*({s}+)\b(\s+for each)?", re.I)
    self.amplify = re.compile(rf"if you would get one or more {s}\b", re.I)
    self.trigger = re.compile(rf"\b(?:whenever you (?:get|spend)|if you spent)\b[^.]*?\b(?:one or more\s+)?{s}+\b", re.I)
    self.threshold = re.compile(rf"(?:have|has)\s+{NUM}\s+or more\s+{s}\b|number of {s}\b,? you have"
                                rf"|for each\s+{s}+\s+you have", re.I)

  def count(self, token: str) -> int:
    return token.count(self.s)

  def given(self, line: str):
    """(amount, repeatable) for the first "you get …" on the line, skipping trigger conditions."""
    for m in self.source.finditer(line):
      if re.search(r"\b(whenever|if you would)\s*$", line[:m.start()], re.I):
        continue
      word = re.match(rf"\s*{NUM}\s", line[m.start() + len(m.group(1)):], re.I)
      if m.group(4):
        amount = "scales"
      elif word:
        amount = int(word.group(1)) if word.group(1).isdigit() else NUMBERS[word.group(1).lower()]
      else:
        amount = self.count(m.group(3))
      repeat = bool(re.search(r"\b(whenever|at the beginning)\b", line, re.I)) or self.activated(line[:m.start()])
      return amount, repeat
    return None

  @staticmethod
  def costs(text: str):
    """Activated-ability costs in text: the part before each `:` that is only cost pieces (2, 1G, T, LL, Exhaust —)."""
    for m in re.finditer(r"(?:^|[.•]\s*)([^.:•]*?):", text):
      cost = re.sub(r"^\s*(exhaust\s*—|kicker)\s*", "", m.group(1), flags=re.I)
      parts = [p.strip() for p in cost.split(",")]
      if all(re.fullmatch(r"\d*[WUBRGCXLO]*|T|Q|pay \d+ life|sacrifice .*|discard .*", p, re.I) and p for p in parts):
        yield parts

  def activated(self, before: str) -> bool:
    return any(True for _ in self.costs(before))

  def spent(self, line: str):
    """O/L paid on the line: an activated cost before `:` or a "pay LL" / "kicker OO"."""
    for parts in self.costs(line):
      for part in parts:
        if re.fullmatch(rf"\d*{self.s}+", part):
          return self.count(part)
    m = re.search(rf"\b(?:pay|kicker)\s+(\d*{self.s}+)\b", line, re.I)
    return self.count(m.group(1)) if m else None

  def threshold_value(self, line: str):
    m = re.search(rf"(?:have|has)\s+{NUM}\s+or more\s+{self.s}\b", line, re.I)
    if not m:
      return None
    w = m.group(1)
    return int(w) if w.isdigit() else NUMBERS[w.lower()]

  def classify(self, line: str) -> dict:
    out = {}
    if self.amplify.search(line):
      out["source"] = {"amount": "+1 per trigger", "repeat": True}
    else:
      given = self.given(line)
      if given:
        out["source"] = {"amount": given[0], "repeat": given[1]}
    spent = self.spent(line)
    if spent is not None:
      out["spender"] = {"amount": spent}
    if self.threshold.search(line):
      out["threshold"] = {"amount": self.threshold_value(line)}
    m = self.trigger.search(line)
    if m:
      out["trigger"] = {"amount": "on spend" if re.search(r"spen[dt]", m.group(0), re.I) else "on get"}
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


def colours_of(cost) -> str:
  return "".join(c for c in COLOURS if c in (cost or ""))


def archetypes(value: str) -> list:
  """Sheet archetype cell -> archetype names ("Sith - Rakdos", "Gruul, Sith" -> ["Bounty Hunters", "Sith"])."""
  out = []
  for part in re.split(r"\s*,\s*|\s*/\s*", value or ""):
    name = GUILDS.get(part.split(" - ")[0].strip(), part.split(" - ")[0].strip())
    if name and name not in out:
      out.append(name)
  return out


def load_dump() -> dict:
  if not DUMP.is_file():
    return {}
  return {str(row["Card Code"]): row for row in json.loads(DUMP.read_text(encoding="utf-8"))}


def collect(eco: Economy):
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
        if re.search(eco.token, line):
          classes = eco.classify(line)
          if classes:
            hits.append({"field": key, "line": line, "classes": classes})
    if not hits:
      continue
    base = base_code(code)
    row, front = sheet.get(code) or {}, sheet.get(base) or {}
    name = strip_tags(f.get("name", "")).strip()
    if any(h["field"].endswith("_2") for h in hits) and f.get("name_2"):
      name = f"{name} // {strip_tags(f['name_2']).strip()}"
    rarity = f.get("rarity", "").strip()
    arch_row = row if row.get("Archetype") else front
    primary = (archetypes(arch_row.get("Archetype", "")) or [""])[0]
    sheet_name = (arch_row.get("Card Name") or "").strip()
    stale = arch_row is row and bool(row) and sheet_name.lower() != strip_tags(f.get("name", "")).strip().lower()
    entry = cards.setdefault(base or code, {
      "code": base or code, "name": name, "cost": strip_tags(f.get("casting_cost", "")).strip(),
      "rarity": rarity, "copies": COPIES.get(rarity, 1),
      "colour": colours_of(f.get("casting_cost")) or colours_of(row.get("Color")) or colours_of(front.get("Color")),
      "archetype": primary,
      "secondary": [a for a in archetypes(arch_row.get("Secondary Archetype", "")) if a != primary],
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
  parts = []
  for v in (h["classes"][cls] for h in card["hits"] if cls in h["classes"]):
    a = v.get("amount")
    if cls == "source":
      parts.append(f"{a}{' (repeatable)' if v.get('repeat') else ''}")
    elif cls == "threshold":
      parts.append(f"{a}+" if a is not None else "scales")
    else:
      parts.append(str(a))
  return ", ".join(parts)


def card_row(card, cls) -> str:
  arch = card["archetype"] or "—"
  if card["secondary"]:
    arch += " / " + ", ".join(card["secondary"])
  if card["stale_sheet"]:
    arch += " †"
  text = "<br>".join((f"_{h['face']}:_ " if h.get("face") else "") + h["line"].replace("|", "\\|")
                     for h in card["hits"] if cls in h["classes"])
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
  out = [f"| {label} | Sources | Spenders | Thresholds | Triggers | Any |", "|---|---|---|---|---|---|"]
  for key in keys:
    g = groups.get(key, {})
    if not any(g.values()):
      continue
    cells = [f"{len(g.get(c, []))} ({weighted(g.get(c, []))})" for c in CLASSES + ["any"]]
    out.append(f"| {key} | " + " | ".join(cells) + " |")
  return out


def counted(values) -> str:
  return ", ".join(f"{n}×{k}" for k, n in sorted(Counter(values).items()))


def render(eco: Economy, cards) -> str:
  s = eco.s
  by_class = {c: [x for x in cards if c in classes_of(x)] for c in CLASSES}
  payoffs = [x for x in cards if classes_of(x) & PAYOFFS]
  pure_sources = [x for x in by_class["source"] if not classes_of(x) & PAYOFFS]
  pure_payoffs = [x for x in payoffs if "source" not in classes_of(x)]
  both = [x for x in by_class["source"] if classes_of(x) & PAYOFFS]

  def row(label, group):
    return f"| {label} | {len(group)} | {weighted(group)} |"

  stamp = datetime.now()
  out = [f"# {SYMBOLS[s]} ({s}) economy\n",
         f"_{stamp:%Y-%m-%d %H:%M}_ · from `TheCloneWars.mse-set`, archetypes from the sheet dump\n",
         "Counts are **cards (copies in the set)**: commons and uncommons count twice, rares and mythics once.\n",
         "## Summary\n", "| | Cards | Copies |", "|---|---|---|",
         row(f"Cards that mention {s}", cards),
         row(f"**Sources** (give {s})", by_class["source"]),
         row(f"**Payoffs** (spend {s} or care about it)", payoffs),
         row(f"↳ Spenders (pay {s})", by_class["spender"]),
         row(f"↳ Thresholds (care how much {s} you have)", by_class["threshold"]),
         row(f"↳ Triggers (care that you got or spent {s})", by_class["trigger"]),
         row("Source only", pure_sources), row("Payoff only", pure_payoffs),
         row("Source and payoff on one card", both), ""]

  given = [h["classes"]["source"] for c in by_class["source"] for h in c["hits"] if "source" in h["classes"]]
  repeat = sum(1 for g in given if g.get("repeat"))
  numeric = [g["amount"] for g in given if isinstance(g["amount"], int)]
  other = Counter(g["amount"] for g in given if not isinstance(g["amount"], int))
  spent = [h["classes"]["spender"]["amount"] for c in by_class["spender"] for h in c["hits"] if "spender" in h["classes"]]
  thresholds = Counter(h["classes"]["threshold"]["amount"] for c in by_class["threshold"] for h in c["hits"]
                       if "threshold" in h["classes"])
  triggers = Counter(h["classes"]["trigger"]["amount"] for c in by_class["trigger"] for h in c["hits"]
                     if "trigger" in h["classes"])
  out += ["## Amounts\n",
          f"- **Source abilities:** {len(given)}, of which {repeat} repeatable (whenever / each turn / activated) "
          f"and {len(given) - repeat} one-shot (ETB, spell, chapter).",
          f"- **{s} per source ability:** {counted(numeric)}"
          + (f", plus {', '.join(f'{n}× {k}' for k, n in other.items())}" if other else "")
          + (f" (average {sum(numeric) / len(numeric):.1f})" if numeric else ""),
          f"- **{s} per spend:** {counted(spent)}" + (f" (average {sum(spent) / len(spent):.1f})" if spent else ""),
          "- **Thresholds:** " + (", ".join(f"{k if k is not None else 'scales'}: {n}" for k, n in
                                            sorted(thresholds.items(), key=lambda kv: (kv[0] is None, kv[0] or 0))) or "none"),
          "- **Triggers:** " + (", ".join(f"{k}: {n}" for k, n in sorted(triggers.items())) or "none"), ""]

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
  out += ["## By archetype\n", "Primary archetype from the sheet; secondary archetypes count too.\n"]
  extra = sorted({a for c in cards for a in [c["archetype"], *c["secondary"]] if a and a not in ARCHETYPES})
  out += breakdown(group(lambda c: [a for a in [c["archetype"], *c["secondary"]] if a] or ["—"]),
                   ARCHETYPES + extra + ["—"], "Archetype") + [""]
  out += ["## By rarity\n"]
  out += breakdown(group(lambda c: [c["rarity"]]), RARITY_ORDER, "Rarity") + [""]

  out += ["## Sources\n", f"Amount is {s} per ability; _repeatable_ means it can happen more than once; "
          "_scales_ means \"for each …\".\n"]
  out += table(by_class["source"], "source", f"{s} given") + [""]
  out += [f"## Payoffs: spend {s}\n"] + table(by_class["spender"], "spender", f"{s} spent") + [""]
  out += [f"## Payoffs: care how much {s} you have\n"] + table(by_class["threshold"], "threshold", "Needs") + [""]
  out += [f"## Payoffs: care that you got or spent {s}\n"] + table(by_class["trigger"], "trigger", "Triggers") + [""]

  stale = [c for c in cards if c["stale_sheet"]]
  if stale:
    out += ["---\n", "† The sheet row for this code is still the card it replaced, so its archetype may be out of date: " +
            "; ".join(f"{c['code']} {c['name']} (sheet: {c['stale_sheet']})" for c in stale) + ".\n"]
  return "\n".join(out) + "\n"


def main():
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("symbol", choices=sorted(SYMBOLS), help="L (Light Side) or O (Dark Side)")
  parser.add_argument("--out", help="report file (default: ai/reports/<symbol>-economy-<timestamp>.md)")
  parser.add_argument("--stdout", action="store_true", help="print the report instead of writing a file")
  args = parser.parse_args()
  eco = Economy(args.symbol)
  text = render(eco, collect(eco))
  if args.stdout:
    print(text, end="")
    return
  path = Path(args.out) if args.out else REPORTS_DIR / f"{args.symbol.lower()}-economy-{datetime.now():%Y-%m-%d_%H%M%S}.md"
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(text, encoding="utf-8")
  print(f"wrote {path.resolve().relative_to(REPO) if path.resolve().is_relative_to(REPO) else path}")


if __name__ == "__main__":
  main()
