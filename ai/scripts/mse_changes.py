#!/usr/bin/env python3
"""Report card changes in TheCloneWars.mse-set between git and the working tree.

  mse_changes.py                 working tree vs the index (unstaged changes)
  mse_changes.py --base HEAD     working tree vs a commit (staged + unstaged)
  mse_changes.py --raw           also list fields whose only change is MSE markup
  mse_changes.py --out FILE      write the report to FILE instead
  mse_changes.py --stdout        print the report instead of writing a file

Writes a Markdown report to ai/reports/card-changes-YYYY-MM-DD_HHMMSS.md grouped by card: cards swapped into a slot in `set`,
cards added or removed, and field-by-field changes to the rest. Values are
shown with MSE tags stripped; bookkeeping fields (time_modified, …) are ignored.
Changed image files are attributed to the card whose `image` field uses them.
"""

import argparse
import difflib
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mse_card import REPO, SET_DIR, split_inline_cards, strip_tags  # noqa: E402

REPORTS_DIR = REPO / "ai" / "reports"
SET_REL = SET_DIR.relative_to(REPO).as_posix()
IGNORED = {"time_created", "time_modified", "stylesheet_version", "has_styling", "extra_data", "styling_data",
           "card_color", "card_color_2",  # frame colour metadata, not card text
           "uid",  # MSE 2.6 gives every card a random uid on save
           "vorthos_box"}  # designer credit; MSE 2.6 moved it out of extra_data, same value
LABELS = {
  "name": "Name", "casting_cost": "Mana cost", "type": "Type line", "rarity": "Rarity",
  "rule_text": "Rules text", "flavor_text": "Flavor text", "power": "Power", "toughness": "Toughness",
  "loyalty": "Loyalty", "card_code_text": "Code", "image": "Art", "stylesheet": "Frame",
  "notes": "Notes", "illustrator": "Illustrator", "watermark": "Watermark",
}
FIELD_ORDER = list(LABELS)


def git(*args, check=True) -> str:
  result = subprocess.run(["git", "-c", "core.safecrlf=false", *args], cwd=REPO,
                          capture_output=True, text=True, encoding="utf-8")
  if check and result.returncode != 0:
    sys.exit(result.stderr.strip())
  return result.stdout if result.returncode == 0 else None


def clean(text):
  return None if text is None else text.replace("\r", "").lstrip("﻿")


def base_text(base: str, rel: str):
  spec = f":{SET_REL}/{rel}" if base == ":" else f"{base}:{SET_REL}/{rel}"
  return clean(git("show", spec, check=False))


def work_text(rel: str):
  path = SET_DIR / rel
  return clean(path.read_text(encoding="utf-8")) if path.is_file() else None


def parse_card(text):
  """All top-level fields of the first card block, multi-line values joined."""
  if not text:
    return {}
  blocks = split_inline_cards(text)
  if not blocks:
    return {}
  fields, key = {}, None
  for line in blocks[0][1].splitlines()[1:]:
    m = re.match(r"^\t([a-z0-9_]+):\s?(.*)$", line)
    if m:
      key = m.group(1)
      fields[key] = m.group(2)
    elif key and line.startswith("\t\t"):
      fields[key] = (fields[key] + "\n" + line[2:]).lstrip("\n")
  return fields


def type_line(f: dict, suffix: str) -> str:
  supers = [strip_tags(f.get(f"super_type{s}", "")).strip() for s in ([suffix] if suffix else ["", "_2", "_3", "_4"])]
  supers = " ".join(s for s in supers if s) if not suffix else supers[0]
  sub = strip_tags(f.get(f"sub_type{suffix}", "")).strip()
  return f"{supers} — {sub}" if sub else supers


LEVEL_FRAMES = {"m15-saga", "m15-mainframe-planeswalker"}
REMINDER_RE = re.compile(r"<(atom-reminder[\w-]*)>.*?</\1>", re.S)


def without_reminders(value: str) -> str:
  """Drop MSE's auto-generated reminder text, which some files have baked in and others don't."""
  return REMINDER_RE.sub("", value or "")


def norm(value: str) -> str:
  """Comparison form: straight quotes, single spaces, no trailing whitespace."""
  value = value.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
  return re.sub(r"\s+", " ", value).strip()  # line breaks too: re-flowing text isn't a change


def display_fields(f: dict, reminders: bool = True) -> dict:
  """Tag-stripped values, with super/sub types folded into a type line per face."""
  out = {}
  for key, value in f.items():
    if key in IGNORED or re.match(r"(super|sub)_type", key):
      continue
    out[key] = strip_tags(value if reminders else without_reminders(value)).strip()
  if f:
    out["type"] = type_line(f, "")
    if f.get("name_2"):
      out["type_2"] = type_line(f, "_2")
  if f.get("stylesheet") in LEVEL_FRAMES:
    # Sagas, classes and planeswalkers show level_N_text; their rule_text is unused and often stale.
    out.pop("rule_text", None)
  # special_text is MSE's export copy of the whole text box. It repeats level_N_text and
  # loyalty costs, and is only regenerated when MSE saves, so it can be stale. Report the real fields.
  out.pop("special_text", None)
  return {k: v for k, v in out.items() if v}


def label(key: str) -> str:
  base, _, face = key.partition("_2") if key.endswith("_2") else (key, "", "")
  text = LABELS.get(base, base.replace("_", " ").capitalize())
  return text + (" (back)" if key.endswith("_2") else "")


def order(keys):
  def rank(k):
    base = k[:-2] if k.endswith("_2") else k
    return (k.endswith("_2"), FIELD_ORDER.index(base) if base in FIELD_ORDER else len(FIELD_ORDER), k)
  return sorted(keys, key=rank)


def heading(f: dict, fallback: str) -> str:
  d = display_fields(f)
  parts = [d.get("card_code_text"), d.get("name") or fallback]
  extra = ", ".join(x for x in (d.get("casting_cost"), d.get("rarity")) if x)
  return " · ".join(p for p in parts if p) + (f" ({extra})" if extra else "")


def summary(f: dict) -> list:
  d = display_fields(f)
  out = []
  for key in ("casting_cost", "type", "rarity"):
    if d.get(key):
      out.append(f"- **{label(key)}:** {d[key]}")
  if d.get("power") or d.get("toughness"):
    out.append(f"- **P/T:** {d.get('power', '')}/{d.get('toughness', '')}")
  if d.get("rule_text"):
    out.append("- **Rules text:**\n" + "\n".join(f"  > {line}" for line in d["rule_text"].splitlines()))
  return out


def field_changes(old: dict, new: dict, raw_old: dict, raw_new: dict, show_raw: bool) -> list:
  a, b = display_fields(old, reminders=False), display_fields(new, reminders=False)
  ra, rb = display_fields(old), display_fields(new)
  lines, cosmetic = [], []
  for key in order(set(a) | set(b) | set(ra) | set(rb)):
    before, after = a.get(key, ""), b.get(key, "")
    if norm(before) == norm(after):
      if ra.get(key, "") != rb.get(key, ""):
        cosmetic.append(key)
      continue
    if "\n" in before or "\n" in after or key == "rule_text":
      diff = difflib.ndiff(before.splitlines(), after.splitlines())
      body = [f"  {l}" for l in diff if not l.startswith("?")]
      lines.append(f"- **{label(key)}:**\n  ```diff\n" + "\n".join(body) + "\n  ```")
    else:
      lines.append(f"- **{label(key)}:** {before or '_(empty)_'} → {after or '_(empty)_'}")
  if show_raw and cosmetic:
    lines.append(f"- _Formatting only (reminder text, quotes, spacing):_ {', '.join(cosmetic)}")
  if show_raw:
    markup = [k for k in set(raw_old) | set(raw_new)
              if k not in IGNORED and (raw_old.get(k) or "") != (raw_new.get(k) or "")
              and strip_tags(raw_old.get(k, "")).strip() == strip_tags(raw_new.get(k, "")).strip()]
    if markup:
      lines.append(f"- _Markup only:_ {', '.join(sorted(markup))}")
  return lines


def includes(text) -> list:
  return re.findall(r"^include_file: (.+)$", text or "", flags=re.M)


def parse_block(block: str) -> dict:
  """All top-level fields of one `card:` block, multi-line values joined."""
  fields, key = {}, None
  for line in block.splitlines()[1:]:
    m = re.match(r"^\t([a-z0-9_]+):\s?(.*)$", line)
    if m:
      key = m.group(1)
      fields[key] = m.group(2)
    elif key and line.startswith("\t\t"):
      fields[key] = (fields[key] + "\n" + line[2:]).lstrip("\n")
  return fields


def name_of(card) -> str:
  return strip_tags(card["fields"].get("name", "")).strip()


def code_of(card) -> str:
  return strip_tags(card["fields"].get("card_code_text", "")).strip()


def load_side(get_text) -> list:
  """Every card one side's `set` references, whatever the layout: inline `card:` blocks,
  one file per card, or a single file holding many cards (as the unzip utility writes).
  Each card gets a key from its name, so the two sides can be matched card by card."""
  set_text = get_text("set") or ""
  sources = [("set", set_text)] + [(rel, get_text(rel) or "") for rel in includes(set_text)]
  cards, seen = [], {}
  for src, text in sources:
    for _, block in split_inline_cards(text):
      fields = parse_block(block)
      key = re.sub(r"[^a-z0-9]+", " ", strip_tags(fields.get("name", "")).lower()).strip() or src
      seen[key] = seen.get(key, 0) + 1
      if seen[key] > 1:
        key = f"{key} #{seen[key]}"
      cards.append({"key": key, "src": src, "fields": fields})
  return cards


def changed_images(base: str) -> set:
  args = ["diff", "--name-only"] + ([] if base == ":" else [base]) + ["--", SET_REL]
  tracked = git(*args).splitlines()
  untracked = git("ls-files", "--others", "--exclude-standard", "--", SET_REL).splitlines()
  return {Path(p).name for p in tracked + untracked if p.endswith((".png", ".jpg", ".jpeg"))}


def main():
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("--base", default=":", help="git ref to compare against (default: the index)")
  parser.add_argument("--raw", action="store_true", help="note fields whose only change is MSE markup")
  parser.add_argument("--out", help="report file (default: ai/reports/card-changes-<timestamp>.md)")
  parser.add_argument("--stdout", action="store_true", help="print the report instead of writing a file")
  args = parser.parse_args()
  report = []
  emit = report.append

  old_cards = load_side(lambda rel: base_text(args.base, rel))
  new_cards = load_side(work_text)
  old_by, new_by = {c["key"]: c for c in old_cards}, {c["key"]: c for c in new_cards}

  # Pair cards: same name first; then, among the rest, the same card code is either a
  # rename (similar name) or a swap (a different card took that code's slot).
  matched = [(old_by[c["key"]], c) for c in new_cards if c["key"] in old_by]
  old_left = [c for c in old_cards if c["key"] not in new_by]
  new_left = [c for c in new_cards if c["key"] not in old_by]
  swaps, added, removed = [], [], []
  old_by_code = {}
  for c in old_left:
    old_by_code.setdefault(code_of(c), []).append(c)
  for c in new_left:
    candidates = old_by_code.get(code_of(c)) if code_of(c) else None
    if candidates:
      old = candidates.pop(0)
      ratio = difflib.SequenceMatcher(a=name_of(old).lower(), b=name_of(c).lower()).ratio()
      (matched if ratio >= 0.6 else swaps).append((old, c))
    else:
      added.append(c)
  paired = {id(o) for o, _ in matched + swaps}
  removed = [c for c in old_left if id(c) not in paired]

  images = changed_images(args.base)

  def art_note(f: dict) -> list:
    img = f.get("image", "")
    return [f"- **Art:** image file `{img}` changed"] if img and img in images else []

  sections = []

  if swaps:
    out = []
    for old, new in swaps:
      out.append(f"### {heading(new['fields'], new['src'])}\n_replaces_ **{heading(old['fields'], old['src'])}**\n")
      out += summary(new["fields"])
      before = summary(old["fields"])
      if before:
        out.append("\n<details><summary>Replaced card</summary>\n\n" + "\n".join(before) + "\n\n</details>")
      out.append("")
    sections.append(("Swapped cards", out))

  if added:
    out = []
    for c in added:
      out.append(f"### {heading(c['fields'], c['src'])}\n_new card_ (`{c['src']}`)\n")
      out += summary(c["fields"]) + [""]
    sections.append(("Added cards", out))

  modified = []
  for old, new in matched:
    old_f, new_f = old["fields"], new["fields"]
    lines = field_changes(old_f, new_f, old_f, new_f, args.raw) if old_f != new_f else []
    if old_f.get("image") == new_f.get("image"):
      lines += art_note(new_f)
    if lines:
      modified.append((display_fields(new_f).get("card_code_text", "~"), heading(new_f, new["src"]), lines))
  if modified:
    out = []
    for _, head, lines in sorted(modified):
      out += [f"### {head}"] + lines + [""]
    sections.append(("Modified cards", out))

  if removed:
    out = []
    for c in removed:
      out.append(f"- **{heading(c['fields'], c['src'])}** (no longer in `set`)")
    sections.append(("Removed cards", out + [""]))

  if not sections:
    print("No card changes.")
    return
  base_name = "the index" if args.base == ":" else args.base
  counts = ", ".join(f"{len(out_cards)} {name.split()[0].lower()}" for name, out_cards in
                     (("Swapped", swaps), ("Added", added), ("Modified", modified), ("Removed", removed)) if out_cards)
  stamp = datetime.now()
  emit(f"# Card changes vs {base_name}\n\n_{stamp:%Y-%m-%d %H:%M}_ · {counts}\n")
  for title, out in sections:
    emit(f"## {title}\n")
    emit("\n".join(out))
  text = "\n".join(report) + "\n"
  if args.stdout:
    print(text, end="")
    return
  path = Path(args.out) if args.out else REPORTS_DIR / f"card-changes-{stamp:%Y-%m-%d_%H%M%S}.md"
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(text, encoding="utf-8")
  print(f"{counts}\nwrote {path.resolve().relative_to(REPO) if path.resolve().is_relative_to(REPO) else path}")


if __name__ == "__main__":
  main()
