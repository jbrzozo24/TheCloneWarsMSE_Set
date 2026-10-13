#!/usr/bin/env python3
"""Helpers for editing cards in an unzipped MSE set (TheCloneWars.mse-set).

Used by the edit-mse-mtg-card and create-mse-mtg-card skills.

  list    [QUERY]            cards in set order: source, code, stylesheet, name
  codes   PREFIX             codes in use for a prefix (e.g. CW, UZ, RL) and the next free one
  filename "CARD NAME"       per-card file name for a new card (MSE style, not yet used)
  add     CARD_FILE          append `include_file: CARD_FILE` to the set manifest
  check   CARD_FILE...       lint card files (header, tabs, set membership)
  render  CARD...            render only these cards to PNG (CARD = file name, code or name)

Cards are only the ones the `set` file references (include_file lines or inline
`card:` blocks). Other `card …` files in the directory are stale and ignored by MSE.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SET_DIR = Path(os.environ.get("MSE_SET_DIR", REPO / "TheCloneWars.mse-set"))
MSE_BIN = os.environ.get(
  "MSE_BIN",
  "/mnt/c/Users/jbrzo/Desktop/workroot/magic_set_editor_from_src/MagicSetEditor2/build/magicseteditor",
)
BOM = "﻿"


def read_text(path: Path) -> str:
  return path.read_text(encoding="utf-8-sig")


def card_fields(block: str) -> dict:
  """Top-level `key: value` fields of one card block (multi-line values are not joined)."""
  fields = {}
  for line in block.splitlines():
    m = re.match(r"^\t([a-z0-9_]+):\s?(.*)$", line)
    if m and m.group(1) not in fields:
      fields[m.group(1)] = m.group(2)
  return fields


def split_inline_cards(set_text: str) -> list:
  """Return (start_line, block_text) for every inline `card:` block in the set file."""
  lines = set_text.splitlines()
  blocks, i = [], 0
  while i < len(lines):
    if lines[i] == "card:":
      start, i = i, i + 1
      while i < len(lines) and (lines[i] == "" or lines[i][0] in "\t "):
        i += 1
      blocks.append((start + 1, "\n".join(lines[start:i])))
    else:
      i += 1
  return blocks


def load_cards() -> list:
  """All cards the set references, in order: dicts with source, file, fields."""
  set_text = read_text(SET_DIR / "set")
  cards = []
  for line_no, block in split_inline_cards(set_text):
    cards.append({"source": f"set:{line_no}", "file": None, "fields": card_fields(block)})
  for target in re.findall(r"^include_file: (.+)$", set_text, flags=re.M):
    path = SET_DIR / target
    if not path.is_file():
      cards.append({"source": f"MISSING {target}", "file": target, "fields": {}})
      continue
    for _, block in split_inline_cards(read_text(path)):
      cards.append({"source": target, "file": target, "fields": card_fields(block)})
  return cards


def strip_tags(text: str) -> str:
  return re.sub(r"<[^>]*>", "", text or "")


def cmd_list(args):
  query = (args.query or "").lower()
  for card in load_cards():
    f = card["fields"]
    name, code = strip_tags(f.get("name", "")), f.get("card_code_text", "")
    if query and query not in name.lower() and query not in code.lower() and query not in card["source"].lower():
      continue
    print(f"{card['source']}\t{code or '-'}\t{f.get('stylesheet', '') or '(set default)'}\t{name}")


def cmd_codes(args):
  prefix = args.prefix.upper()
  codes = sorted(
    c for c in (card["fields"].get("card_code_text", "") for card in load_cards())
    if c.upper().startswith(prefix)
  )
  print(" ".join(codes) if codes else f"(no codes start with {prefix})")
  numbers = [int(m.group(1)) for c in codes if (m := re.fullmatch(re.escape(prefix) + r"(\d+)", c, flags=re.I))]
  print(f"next: {prefix}{(max(numbers) + 1 if numbers else 1):02d}")


def mse_filename(name: str) -> str:
  cleaned = re.sub(r"[^a-z0-9 \-]", "", strip_tags(name).lower()).strip(" .")
  return f"card {cleaned or 'no-name'}"


def cmd_filename(args):
  base = mse_filename(args.name)
  candidate, n = base, 0
  while (SET_DIR / candidate).exists():
    n += 1
    candidate = f"{base}.{n}"
  print(candidate)


def cmd_add(args):
  target = args.card_file
  if not (SET_DIR / target).is_file():
    sys.exit(f"{SET_DIR / target} does not exist; write the card file first")
  set_path = SET_DIR / "set"
  raw = set_path.read_text(encoding="utf-8")
  if re.search(rf"^include_file: {re.escape(target)}$", raw, flags=re.M):
    print(f"already included: {target}")
    return
  lines = raw.split("\n")
  includes = [i for i, line in enumerate(lines) if line.startswith("include_file: ")]
  if not includes:
    sys.exit("set has no include_file lines (cards are stored inline); add the card as an inline `card:` block instead")
  lines.insert(includes[-1] + 1, f"include_file: {target}")
  set_path.write_text("\n".join(lines), encoding="utf-8")
  print(f"added include_file: {target} (after line {includes[-1] + 1})")


def cmd_check(args):
  set_text = read_text(SET_DIR / "set")
  included = set(re.findall(r"^include_file: (.+)$", set_text, flags=re.M))
  problems = 0
  for name in args.card_files:
    path = SET_DIR / name
    raw = path.read_bytes().decode("utf-8")
    issues = []
    if not raw.startswith(BOM + "mse_version: "):
      issues.append("must start with a UTF-8 BOM and an `mse_version:` line")
    if "\r" in raw:
      issues.append("contains CR characters; MSE writes LF line endings")
    if "\ncard:\n" not in raw:
      issues.append("no top-level `card:` line")
    for no, line in enumerate(raw.lstrip(BOM).split("\n"), 1):
      if line.startswith(" "):
        issues.append(f"line {no} is indented with spaces; MSE needs tabs")
    blocks = split_inline_cards(raw.lstrip(BOM))
    if len(blocks) != 1:
      issues.append(f"expected exactly one card block, found {len(blocks)}")
    else:
      f = card_fields(blocks[0][1])
      for key in ("name", "rarity"):
        if not f.get(key):
          issues.append(f"missing `{key}`")
      if f.get("rarity") and f["rarity"] not in ("common", "uncommon", "rare", "mythic rare", "special"):
        issues.append(f"unknown rarity {f['rarity']!r}")
    if name not in included:
      issues.append("not referenced by `set` (MSE will ignore it); run `add`")
    problems += len(issues)
    print(f"{name}: " + ("ok" if not issues else "\n  - " + "\n  - ".join(issues)))
  sys.exit(1 if problems else 0)


def resolve(selector: str, cards: list) -> dict:
  sel = selector.lower()
  for key in ("file", "code", "name"):
    hits = []
    for card in cards:
      value = {"file": card["file"] or "", "code": card["fields"].get("card_code_text", ""),
               "name": strip_tags(card["fields"].get("name", ""))}[key]
      if value.lower() == sel:
        hits.append(card)
    if len(hits) == 1:
      return hits[0]
    if len(hits) > 1:
      sys.exit(f"{selector!r} matches {len(hits)} cards by {key}; use the file name")
  sys.exit(f"no card matches {selector!r}; try `list {selector}`")


def cmd_render(args):
  cards = load_cards()
  chosen = [resolve(s, cards) for s in args.cards]
  out_dir = Path(args.out).resolve()
  out_dir.mkdir(parents=True, exist_ok=True)
  set_text = read_text(SET_DIR / "set")
  lines = set_text.splitlines()
  first_card = next((i for i, l in enumerate(lines) if l == "card:" or l.startswith("include_file: ")), len(lines))
  header = lines[:first_card]
  inline = dict(split_inline_cards(set_text))
  for card in chosen:
    with tempfile.TemporaryDirectory(prefix="mse-render-") as tmp:
      tmp_set = Path(tmp) / "Render.mse-set"
      tmp_set.mkdir()
      for entry in SET_DIR.iterdir():
        if entry.name != "set":
          (tmp_set / entry.name).symlink_to(entry)
      if card["file"]:
        body = [f"include_file: {card['file']}"]
      else:
        body = inline[int(card["source"].split(":")[1])].splitlines()
      (tmp_set / "set").write_text(BOM + "\n".join(header + body) + "\n", encoding="utf-8")
      name = strip_tags(card["fields"].get("name", "card"))
      label = card["fields"].get("card_code_text") or re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")
      target = out_dir / f"{label}.png"
      result = subprocess.run(
        [MSE_BIN, "--export-images", str(tmp_set), str(target)],
        capture_output=True, text=True, timeout=300,
      )
      if result.returncode != 0 or not target.exists():
        sys.exit(f"render failed for {name}:\n{result.stdout}\n{result.stderr}")
      print(target)


def main():
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  sub = parser.add_subparsers(dest="command", required=True)
  p = sub.add_parser("list"); p.add_argument("query", nargs="?"); p.set_defaults(func=cmd_list)
  p = sub.add_parser("codes"); p.add_argument("prefix"); p.set_defaults(func=cmd_codes)
  p = sub.add_parser("filename"); p.add_argument("name"); p.set_defaults(func=cmd_filename)
  p = sub.add_parser("add"); p.add_argument("card_file"); p.set_defaults(func=cmd_add)
  p = sub.add_parser("check"); p.add_argument("card_files", nargs="+"); p.set_defaults(func=cmd_check)
  p = sub.add_parser("render"); p.add_argument("cards", nargs="+")
  p.add_argument("--out", default=str(Path(tempfile.gettempdir()) / "mse-card-renders"))
  p.set_defaults(func=cmd_render)
  args = parser.parse_args()
  args.func(args)


if __name__ == "__main__":
  main()
