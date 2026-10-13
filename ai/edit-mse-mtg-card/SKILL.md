---
name: edit-mse-mtg-card
description: Edit an existing card in The Clone Wars Magic Set Editor set (TheCloneWars.mse-set). Changes rules text, mana cost, P/T, type line, name, rarity, flavor text, art, frame/stylesheet, or saga/class/planeswalker abilities in the card's MSE file, then renders the card to check it. Use this whenever the user wants to change, fix, tweak, reword, buff, nerf, rename or recost a card in the set, even if they only give the card's name or code (e.g. "make CW01 cost 1W", "change Watto's -2", "fix the typo on The Clone Wars") and don't mention MSE or files.
---

# Edit an MSE card

Edit one or more existing cards in `TheCloneWars.mse-set/`, keeping the rest of
the file exactly as MSE wrote it, then render the card so the user can see the
result.

Before starting, read `ai/references/mse-card-reference.md` (in the repo root).
It covers the file format, the fields for each frame type, which plain text MSE
formats automatically, and the card codes. The commands below use the helper
script `ai/scripts/mse_card.py`. Run everything from the repo root.

## 1. Make sure MSE won't overwrite the edit

MSE keeps the open set in memory and writes all of it when the user saves. An
edit made while the set is open in MSE gets overwritten, or overwrites the
user's unsaved work. Ask the user to close the set in MSE (or confirm it isn't
open) before you write, and to reopen it afterwards.

Also run `git status --short TheCloneWars.mse-set/` (with `-c core.autocrlf=true`
if the output lists every file). If the card you're editing already has
uncommitted changes, say so. You'll be building on top of them.

## 2. Find the card

```bash
python3 ai/scripts/mse_card.py list "<name or code>"
```

This lists only the cards that `set` references. The directory also has stale
card files that MSE ignores, so don't pick a file with `ls` or `grep`. If several
cards match, ask which one is meant. Check:

- **Double-faced cards** are two cards, `UW17` (front) and `UW17B` / `UW17B_0`
  (back). If the change affects both faces (e.g. a name shared between them, or
  transform conditions), edit both.
- **Source column `set:<line>`** means the card is stored inline in `set`
  (saved by MSE 2.6 without per-card files). Edit the `card:` block at that line
  in `set`.

Render the card **before** editing, so you have something to compare against:

```bash
python3 ai/scripts/mse_card.py render <CODE or file> --out /tmp/mse-card-renders/before
```

## 3. Make the edit

Read the whole card file, then change only the fields the request needs, using
exact-match edits. Everything you don't touch (tags, empty fields, `extra_data`,
styling) should stay exactly as it was, so the git diff shows only the real
change and MSE keeps its formatting.

- Find the right field for the frame type in the reference's "Fields by
  stylesheet" table. For example, saga chapters live in `level_N_text`, not
  `rule_text`.
- Write new text as plain text. MSE adds keyword, mana and bullet markup when it
  loads the card. Wrap mana symbols in the middle of a sentence in `<sym>…</sym>`
  (`Add <sym>G</sym>.`, `you get <sym>OO</sym>`), because MSE doesn't reliably
  detect them there.
- When rewriting a value that contains MSE tags, replace the whole value with
  clean plain text. Don't try to keep half the tags. Leave values you're not
  changing alone.
- Multi-line values go on the lines after `key:`, indented one more tab than
  the key. Use tabs only.
- Mention the card's own name in its rules text the way the card already does
  (full name, or the short name for legends).
- Set `time_modified` to the current time (`date '+%Y-%m-%d %H:%M:%S'`).
- Don't edit `special_text` (MSE regenerates it) or `card_code_text` unless asked.
- If the change makes another field wrong, fix that too and say so. For
  example, a rarity change also changes the code's first letter, and adding a
  colour changes `W` to `Z`. Ask before changing a code, because the spreadsheet
  and DFC back faces use it to match cards.

Changing the frame (`stylesheet:`) is a bigger change: the new frame may use
different fields (see the table). Copy the field layout from an existing card
with that stylesheet, and move the text into its fields.

## 4. Check and render

```bash
python3 ai/scripts/mse_card.py check "<card file>"
python3 ai/scripts/mse_card.py render <CODE or file> --out /tmp/mse-card-renders/after
```

Look at the rendered PNG with the Read tool and compare it with the "before"
image. Check that the text fits and isn't shrunk to unreadable, that symbols
render as symbols (not letters), that bullets are on separate lines, and that the
right frame and colours are shown. If something is off, fix it and render again.

## 5. Report

Tell the user:
- which card(s) and fields changed, as before → after text
- where the rendered image is (show it with the Read tool if they want to see it)
- that the Google Sheet is now behind for these cards, so the next `set_builder`
  sync will show them as changed. Don't run `set_builder`; Jack runs syncs.
- if MSE was open: reopen the set to see the change.

Don't commit unless asked. If asked, commit just the edited card file(s).
