# MSE card reference (The Clone Wars)

Shared by the `edit-mse-mtg-card` and `create-mse-mtg-card` skills. For the full
file format, see `docs/mse-file-formats.md`.

## Contents
1. Where cards live
2. Card file format
3. Fields by stylesheet
4. Writing text: what MSE formats for you
5. Card codes
6. Set conventions
7. The helper script

---

## 1. Where cards live

- Set directory: `TheCloneWars.mse-set/` in the repo root.
- `set` lists the cards in order with `include_file: card <name>` lines, and each
  card is in its own file. **Only files listed in `set` are cards.** The
  directory also has stale `card …` files (old names, `… copy`, `no-name`) that
  MSE ignores. Find cards with `mse_card.py list`, never with `ls`/`grep` over
  the directory.
- MSE 2.6 saves cards *inline* in `set` as `card:` blocks unless
  `save_cards_in_separate_files: true` is set in `~/.magicseteditor/mse.config`.
  `mse_card.py list` shows those as `set:<line>`. Edit them in `set` the same way.
- Card art is `imageN.png` in the set directory, referenced by `image:`.
- `TCW_Tokens.mse-set` (if present) is a separate set for tokens. The helper
  works on it with `MSE_SET_DIR=<path>`.

## 2. Card file format

```
﻿mse_version: 2.5.8          ← file starts with a UTF-8 BOM, then this line
card:
	stylesheet: m15-altered
	stylesheet_version: 2025-10-05
	has_styling: false
	notes:
	time_created: 2026-04-21 21:47:59
	time_modified: 2026-05-05 08:47:30
	extra_data:
		magic-m15-altered:
			vorthos_box: Jack Brzozowski
	name: Clone Trooper Regiment
	casting_cost: W
	rule_text:
		When Clone Trooper Regiment enters, if you control a Jedi, create a 1/1 white Clone Trooper creature token.
		Lifelink. squad 1W.
	...
```

- **Tabs** for indentation, one per level. Spaces break parsing.
- **LF** line endings, UTF-8 with BOM. Edit existing files in place, or copy them
  with `cp`, so the BOM and line endings are kept. Don't recreate a card file
  from scratch with a write tool.
- **Single-line value:** `key: value`. **Multi-line value:** `key:` alone, then
  each line indented one more tab. A value becomes multi-line as soon as it has
  a second line (a second ability, a bullet list).
- Empty fields are written `key: ` or `key:`. Keep the fields the card already
  has, even empty ones.
- `time_modified` / `time_created` use `YYYY-MM-DD HH:MM:SS`.
- **Don't edit `special_text`.** It's computed by a script (export text) and MSE
  regenerates it. Don't add or copy `uid:`, which must be unique per card.

## 3. Fields by stylesheet

`stylesheet` picks the frame. The set default is `m15-altered`.

| Stylesheet | Used for | Text lives in |
|---|---|---|
| `m15-altered` | normal cards (most of the set) | `rule_text`, `flavor_text`, `power`, `toughness` |
| `m15-saga` | sagas **and** class cards | sagas: `chapter_text` (reminder), `level_1_text`…`level_4_text` (one per chapter). classes: `level_1_text` (level 1), `level_2`/`level_3` (labels), `level_9_text`/`level_10_text` (level costs, `<sym-auto>2W</sym-auto>:`), `level_2_text`/`level_3_text` (abilities, wrapped in `<margin:0:0:30>…</margin:0:0:30>`) |
| `m15-mainframe-planeswalker` | planeswalkers | `loyalty` (starting), `loyalty_cost_1..4` (`+2`, `−2`), `level_1_text..level_5_text` (abilities, wrapped in `<margin:130:0:0>…</margin:130:0:0>` when they have a cost) |
| `m15-mainframe-battles` | battles | `rule_text`, `loyalty` (defense), `transformation` |
| `m15-flip` | flip cards | front: `name`, `rule_text`, `power`…; flipped: `name_2`, `rule_text_2`, `power_2`… |
| `m15-split-fusable` | split cards | left: `name`, `casting_cost`, `rule_text`; right: `name_2`, `casting_cost_2`, `rule_text_2` |

Shared fields: `name`, `casting_cost` (`2WU`, `X`, hybrid `W/U`), `super_type`
(`Legendary Creature`, `Artifact`), `sub_type` (`Clone Trooper`), `rarity`
(`common` / `uncommon` / `rare` / `mythic rare`), `image`, `illustrator`,
`card_stamp`, `card_code_text`, `watermark`, `extra_data` (per style).

When unsure, open an existing card with the same stylesheet and mirror it.
`mse_card.py list` shows each card's stylesheet.

**Double-faced (transform) cards are two separate cards** linked only by code:
the back is `<front code>B` or `<front code>B_0` (`UW17` / `UW17B`). Flip and
split cards are one card using the `_2` fields.

## 4. Writing text: what MSE formats for you

MSE re-applies most markup when it loads a card, so write **plain text** and let
MSE add the tags. Tested in this set:

| You write | MSE renders |
|---|---|
| `Flying, vigilance` | keywords (no reminder text for evergreen keywords) |
| `squad 1W` | custom keyword with its reminder text and mana symbols |
| `2W, T: Draw a card.` | a cost before `:` becomes symbols, including `T` (tap) |
| a line per ability | separate paragraphs |
| `Choose one —` then lines starting with `• ` | a bullet list (each `•` must start its own line) |
| `casting_cost: 2WU` | mana symbols |
| `super_type: Creature` | type line (no `<word-list-…>` tags needed) |
| `flavor_text: …` | italic flavor text |

Wrap symbols **in the middle of a sentence** in `<sym>…</sym>`: `Add <sym>G</sym>.`,
`you get <sym>LLLL</sym>`. MSE doesn't reliably detect them otherwise. In
testing `LL` was converted but `OO` was left as letters.

Custom symbols in this set: **`L`** = Light Side, **`O`** = Dark Side
(defined in `magic-mana-small.mse-symbol-font`).

Existing cards contain tags like `<kw-a>`, `<key>`, `<i-auto>`,
`<error-spelling:…>`, `<word-list-type-en>`, `<li><bullet>`. In the parts you
don't change, leave them as they are. In the parts you rewrite, plain text is
fine. Don't copy auto-generated reminder text (`<atom-reminder…>`) into a
value.

## 5. Card codes

`card_code_text` = **rarity** + **color** + **two-digit number**, plus `B`/`B_0` for back faces.

- Rarity: `C` common, `U` uncommon, `R` rare, `M` mythic.
- Color: `W` `U` `B` `R` `G`, `Z` multicolor, `A` artifact/colorless, `L` land.
- Examples: `CW01` (common white), `UZ11` (uncommon multicolor), `RL03` (rare land), `MZ11B` (back face of mythic multicolor 11).

Use `mse_card.py codes <prefix>` to see the codes in use and the next free one.

## 6. Set conventions

Copy these from a sibling card rather than inventing them:

- `illustrator: LUCASFILM` (a few cards credit a real artist)
- `card_stamp: universes beyond`
- `extra_data` → `magic-m15-altered` → `vorthos_box: Jack Brzozowski` (also as a plain `vorthos_box:` field on m15-altered cards)

Design rules (from `CLAUDE.md` §2): the set size is fixed, so a new card replaces
a cut card of the **same rarity**, ideally the same color. Changing an existing
card doesn't need a swap.

The Google Sheet is the other source of truth. After editing MSE, the sheet is
out of date until Jack runs `set_builder`. Don't run it yourself. Say which
cards changed so he can sync.

## 7. The helper script

`python3 ai/scripts/mse_card.py <command>` (run from the repo root):

| Command | Does |
|---|---|
| `list [QUERY]` | cards in set order: file, code, stylesheet, name. QUERY matches name, code or file |
| `codes PREFIX` | codes in use for a prefix, and the next free number |
| `filename "Name"` | an unused per-card file name for a new card |
| `add FILE` | add `include_file: FILE` to `set` (after the last include) |
| `check FILE…` | lint: BOM/header, LF, tabs, one card block, name/rarity, listed in `set` |
| `render CARD… [--out DIR]` | render just these cards to PNG with the Linux MSE build (about 6 s per card). CARD = file, code or exact name. Default output dir `/tmp/mse-card-renders` |

Environment overrides: `MSE_SET_DIR` (another set), `MSE_BIN` (MSE binary).
