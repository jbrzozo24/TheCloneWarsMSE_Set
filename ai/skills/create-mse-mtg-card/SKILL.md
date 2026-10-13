---
name: create-mse-mtg-card
description: Create a new card in The Clone Wars Magic Set Editor set (TheCloneWars.mse-set). Builds the card's MSE file from an existing card of the same frame type, gives it the next card code, registers it in the set, and renders it to check. Use this whenever the user wants to add, design, mock up or make a new card, replace or swap a card with a new one, or add a back face or token to the set, even if they only describe the card ("make a common white 2-drop clone with squad") and don't mention MSE or files.
---

# Create an MSE card

Add a new card to `TheCloneWars.mse-set/` by copying an existing card of the
same frame type and filling in the new card's fields, then render it.

Before starting, read `ai/references/mse-card-reference.md` (in the repo root).
It covers the file format, fields for each frame type, which plain text MSE
formats automatically, card codes, and set conventions. The commands below use
`ai/scripts/mse_card.py`. Run everything from the repo root.

## 1. Settle the design questions first

The set has a fixed size (`CLAUDE.md` §2): **a new card replaces a cut card of
the same rarity** (ideally the same colour). Unless the user has already said
what the card replaces, or that it's an extra (a token, a back face, a test
card), ask which card it replaces before creating anything. Don't remove the cut
card unless the user confirms it.

Make sure you know: name, mana cost, type line, rarity, rules text, P/T (or
loyalty/defense), and flavor text if any. If the user gave a rough idea rather
than a finished card, propose the full card text and get a yes before writing
files. Suggesting a design is useful, but the user decides.

As with edits, the set must not be open in MSE while you write. Ask the user to
close it, and to reopen it afterwards.

## 2. Pick a template card

Choose an existing card that's as close as possible: same stylesheet (frame
type), and ideally the same card type and colour.

```bash
python3 ai/scripts/mse_card.py list            # all cards with code + stylesheet
python3 ai/scripts/mse_card.py list "<query>"  # narrow it down
```

Copying a real card keeps everything MSE expects (BOM, header, field order,
`extra_data`, `card_stamp`, `illustrator`, styling) without anyone having to
remember it.

## 3. Choose the code and file name

```bash
python3 ai/scripts/mse_card.py codes <PREFIX>        # e.g. CW, UZ, RL; prints next free code
python3 ai/scripts/mse_card.py filename "<Card Name>"
```

- New card: use the next free code for its rarity + colour.
- Replacing a cut card: ask whether to reuse the cut card's code. That's
  usually what keeps the spreadsheet row and numbering stable.
- Back face of a double-faced card: front code + `B` (follow the pattern
  the front's other back faces use, e.g. `B_0`).

## 4. Create the file

```bash
cp "TheCloneWars.mse-set/<template file>" "TheCloneWars.mse-set/<new file>"
```

Then edit the copy, field by field:

- Replace every card-specific field: `name`, `casting_cost`, `super_type`,
  `sub_type`, `rarity`, the text fields for the frame type, `power` /
  `toughness` / `loyalty`, `flavor_text`, `card_code_text`.
- **Clear what belongs to the template card:** `image:` (leave empty unless the
  user gives art), `notes:`, any `_2` / `level_N` fields the new card doesn't
  use. **Delete** any `uid:` line and `linked_card_N` / `linked_relation_N`
  lines, because those must be unique per card. Delete `special_text` too
  (MSE regenerates it).
- Set `time_created` and `time_modified` to now (`date '+%Y-%m-%d %H:%M:%S'`).
- Keep `stylesheet`, `stylesheet_version`, `extra_data`, `card_stamp`,
  `illustrator` and styling fields from the template.
- Write text as plain text. MSE adds keyword, mana and bullet markup on load.
  Wrap symbols in the middle of a sentence in `<sym>…</sym>`.

Art: if the user provides an image, copy it into the set directory as the next
unused `imageN.png` and set `image:` to it. Otherwise leave `image:` empty; the
user can add art in MSE.

## 5. Register, check and render

```bash
python3 ai/scripts/mse_card.py add "<new file>"
python3 ai/scripts/mse_card.py check "<new file>"
python3 ai/scripts/mse_card.py render <CODE> --out /tmp/mse-card-renders
```

`add` puts the new card at the end of the set's card list. If `set` stores
cards inline (no `include_file:` lines), `add` refuses. In that case, paste the
card block (without the `mse_version` header) into `set` after the last
`card:` block.

Look at the PNG with the Read tool. Check that the frame and colours match the
card's colours, the text fits, symbols render, and the rarity/code at the bottom
left is right. Fix and re-render as needed.

If the user confirmed a cut, remove the cut card's `include_file:` line from
`set` (leave its file; MSE deletes unreferenced card files on its next save).

## 6. Report

Tell the user:
- the new card's code, file name, and full text
- where the render is (and show it)
- which card was cut, if any, or that the set is now one card over size
- that the Google Sheet doesn't have this card yet. Don't run `set_builder`
  yourself; Jack runs syncs.

Don't commit unless asked. If asked, commit the new card file, `set`, and any
new image.
