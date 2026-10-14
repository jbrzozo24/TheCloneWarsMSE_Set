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
IGNORED = {"time_created", "time_modified", "stylesheet_version", "has_styling", "extra_data", "styling_data"}
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


def display_fields(f: dict) -> dict:
  """Tag-stripped values, with super/sub types folded into a type line per face."""
  out = {}
  for key, value in f.items():
    if key in IGNORED or re.match(r"(super|sub)_type", key):
      continue
    out[key] = strip_tags(value).strip()
  if f:
    out["type"] = type_line(f, "")
    if f.get("name_2"):
      out["type_2"] = type_line(f, "_2")
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
  a, b = display_fields(old), display_fields(new)
  lines = []
  for key in order(set(a) | set(b)):
    before, after = a.get(key, ""), b.get(key, "")
    if before == after:
      continue
    if "\n" in before or "\n" in after or key == "rule_text":
      diff = difflib.ndiff(before.splitlines(), after.splitlines())
      body = [f"  {l}" for l in diff if not l.startswith("?")]
      lines.append(f"- **{label(key)}:**\n  ```diff\n" + "\n".join(body) + "\n  ```")
    else:
      lines.append(f"- **{label(key)}:** {before or '_(empty)_'} → {after or '_(empty)_'}")
  if show_raw:
    markup = [k for k in set(raw_old) | set(raw_new)
              if k not in IGNORED and raw_old.get(k) != raw_new.get(k)
              and strip_tags(raw_old.get(k, "")).strip() == strip_tags(raw_new.get(k, "")).strip()]
    if markup:
      lines.append(f"- _Markup only:_ {', '.join(sorted(markup))}")
  return lines


def includes(text) -> list:
  return re.findall(r"^include_file: (.+)$", text or "", flags=re.M)


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

  old_set, new_set = base_text(args.base, "set") or "", work_text("set") or ""
  old_inc, new_inc = includes(old_set), includes(new_set)
  if split_inline_cards(new_set) or split_inline_cards(old_set):
    emit("_Note: `set` has inline `card:` blocks; this report only covers include_file cards._\n")

  swaps, added, removed = [], [], []
  matcher = difflib.SequenceMatcher(a=old_inc, b=new_inc, autojunk=False)
  for op, i1, i2, j1, j2 in matcher.get_opcodes():
    olds, news = old_inc[i1:i2], new_inc[j1:j2]
    if op == "replace":
      pairs = min(len(olds), len(news))
      swaps += list(zip(olds[:pairs], news[:pairs]))
      removed += olds[pairs:]
      added += news[pairs:]
    elif op == "delete":
      removed += olds
    elif op == "insert":
      added += news
  # A card moved elsewhere in `set` isn't added or removed.
  moved = set(added) & set(removed)
  added = [c for c in added if c not in moved]
  removed = [c for c in removed if c not in moved]

  images = changed_images(args.base)
  cards = {}
  for rel in dict.fromkeys(old_inc + new_inc):
    old_raw, new_raw = base_text(args.base, rel), work_text(rel)
    cards[rel] = (parse_card(old_raw), parse_card(new_raw), old_raw != new_raw)

  def art_note(f: dict) -> list:
    img = f.get("image", "")
    return [f"- **Art:** image file `{img}` changed"] if img and img in images else []

  sections = []

  if swaps:
    out = []
    for old_rel, new_rel in swaps:
      old_f, new_f = cards[old_rel][1] or cards[old_rel][0], cards[new_rel][1]
      out.append(f"### {heading(new_f, new_rel)}\n_replaces_ **{heading(old_f, old_rel)}**\n")
      out += summary(new_f)
      before = summary(old_f)
      if before:
        out.append("\n<details><summary>Replaced card</summary>\n\n" + "\n".join(before) + "\n\n</details>")
      out.append("")
    sections.append(("Swapped cards", out))

  if added:
    out = []
    for rel in added:
      new_f = cards[rel][1]
      out.append(f"### {heading(new_f, rel)}\n_new card_ (`{rel}`)\n")
      out += summary(new_f) + [""]
    sections.append(("Added cards", out))

  modified = []
  for rel in dict.fromkeys(new_inc):
    if rel in added or rel in (n for _, n in swaps):
      continue
    old_f, new_f, file_changed = cards[rel]
    lines = field_changes(old_f, new_f, old_f, new_f, args.raw) if file_changed else []
    if old_f.get("image") == new_f.get("image"):
      lines += art_note(new_f)
    if lines:
      modified.append((display_fields(new_f).get("card_code_text", "~"), heading(new_f, rel), lines))
  if modified:
    out = []
    for _, head, lines in sorted(modified):
      out += [f"### {head}"] + lines + [""]
    sections.append(("Modified cards", out))

  if removed:
    out = []
    for rel in removed:
      f = cards[rel][1] or cards[rel][0]
      out.append(f"- **{heading(f, rel)}** (`{rel}` no longer in `set`)")
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
