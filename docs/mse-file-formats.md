# MSE file formats: `.mse-game`, `.mse-style`, `.mse-set`

Reference for how Magic Set Editor (MSE) stores games, templates and sets, written
for working on The Clone Wars set from code (git, `set_builder`) instead of
only through the MSE GUI.

Sources: the MSE 2.6 source (`G-e-n-e-v-e-n-s-i-S/MagicSetEditor2`, mainly
`src/data/{game,stylesheet,set,card}.cpp` and `src/util/io/{reader.hpp,package.cpp}`),
the Full Magic Pack 4.0.1 templates, and this repo's `TheCloneWars.mse-set`.

---

## 1. The big picture

```
magic.mse-game                      defines WHAT a card is (its fields)
   ▲          ▲
   │ game:    │ game:
magic-m15-altered.mse-style   ...  define HOW a card is drawn (one per frame type)
   ▲
   │ stylesheet:   (set default, overridable per card)
TheCloneWars.mse-set                holds the DATA (cards, set info, settings)
```

| Kind | Example | Owns |
|---|---|---|
| Game | `magic.mse-game` | Card fields (name, casting cost, type, rule text, P/T…), set fields, keywords, word lists, statistics, auto-replace, scripts |
| Style (stylesheet) | `magic-m15-altered.mse-style` | Card size/DPI, frame images, position and font of every field, **styling fields** (options in the Style tab), **extra card fields** (style-only per-card fields) |
| Set | `TheCloneWars.mse-set` | Values for the game's card and set fields, which style is used (set-wide and per card), styling choices, style-specific extra data, images |
| Include | `magic-modules.mse-include` | Shared scripts/images that games and styles depend on |
| Symbol font | `magic-mana-small.mse-symbol-font` | The images used for `{W}`, `{2}` etc. inside text |
| Locale | `en.mse-locale` | UI translations |
| Export template | `magic-forum.mse-export-template` | HTML/text exporters |

**Rule of thumb:** card *content* belongs to the game, so it survives a style
change. Anything about *appearance* belongs to the style and is stored per style.

---

## 2. Packages: the common container

Every `.mse-*` thing is a **package**: either a zip file or a plain directory
with that extension. MSE reads both. The directory form is what we keep in git.

- The package has one **main file** named after its type: `game` in a
  `.mse-game`, `style` in a `.mse-style`, `set` in a `.mse-set`, `include` in
  a `.mse-include`, `locale` in a `.mse-locale`, and so on.
- Every other file in the directory is a resource: images, extra script files,
  per-card files.
- Inside scripts and `include file:` lines, `/other-package.mse-include/path`
  refers to a file in *another* installed package.

### Header fields shared by all packages (`Packaged`)

```
mse version:     2.6.0                 # app version the file was written for
short name:      M15 Main              # shown in pickers
full name:       also Leveler
icon:            card-sample.png
position hint:   000000                # sort order in pickers
installer group: magic/M15 Frames/Standard/M15 Main
version:         2026-09-13            # the package's own version (a date)
depends on:                            # repeatable
	package: magic.mse-game
	version: 2026-09-06                # minimum version required
```

`version` is what the set records as `game_version` / `stylesheet_version`.
When a newer package is installed, MSE silently uses it. If the package ships an
`update cards script` for that version jump, MSE also migrates the card data
(see §6).

---

## 3. The text format (all main files)

Every main file uses the same indentation-based key/value format.

```
key: value
key:
	nested_key: value
	another: value
multi_line_key:
	first line of the value
	second line of the value
repeated_key:            # a list is just the same key repeated
	...
repeated_key:
	...
# comment (only in game/style/include files; MSE does not write comments)
```

- **Indentation is tabs.** One tab per nesting level.
- **Spaces and underscores in keys are the same.** Templates are written as
  `card field:` / `short name:` and sets are saved as `card_field` / `short_name`.
  MSE converts spaces to underscores when reading keys (`canonical_name_form`).
- **Multi-line values:** the key ends at `:` and the value is the following
  lines, indented one deeper. Example from a set:
  ```
  	rule_text:
  		When Clone Trooper Regiment enters, if you control a Jedi, ...
  		Lifelink. squad 1W.
  ```
- **`include file: <path>`** splices another file in at that point. It works
  in every file type. `include localized file:` adds `_<locale>`, and
  `include dark file:` adds `_dark` in dark mode.
- Files written by MSE start with a UTF-8 BOM (`﻿`) and an
  `mse_version:` line.
- **Script values** (in games and styles) are MSE's own scripting language,
  either inline after `script:` or as an indented block.

### Tagged text in values

Rich text fields are stored with inline tags that the GUI hides:

| Tag | Meaning |
|---|---|
| `<sym>2W</sym>`, `<sym-auto>…</sym-auto>` | Render with the mana symbol font |
| `<kw-A>…</kw-A>`, `<kw-a>` | Keyword match (reminder text shown / hidden) |
| `<key>Battalion</key>` | The keyword itself |
| `<i>`, `<b>`, `<i-flavor>`, `<i-auto>` | Italic/bold (manual or automatic) |
| `<nospellcheck>`, `<error-spelling:en_US:…>` | Spell-checker state |
| `<word-list-type-en>Creature</word-list-type-en>` | Value chosen from a word list (dropdown) |
| `<soft>`, `<atom-sep>` | Generated separators (removed when the value is edited) |
| `<margin:0:0:30>` | Layout hints used by styles |

`set_builder` strips these to compare against the spreadsheet (see
`MSE_NORMALIZATION_PLAN.md` in the builder app). Reading a value as "what you
see on the card" means removing every `<…>` tag.

---

## 4. `.mse-game`: what a card is

Main file `game`. Pack location: `~/.magicseteditor/data/magic.mse-game/`.
The Magic game splits itself into many files using `include file:`:

```
mse version:  2.6.0
short name:   Magic
version:      2026-09-24
depends on: ...

init script: include file: script     # global script functions
include file: game_script
include file: card_fields             # card field: blocks
include file: card_links
include file: set_fields              # set field: blocks
...                                   # keywords_en, word_lists, statistics, auto_replace, pack types ...
```

Main sections (from `Game` in `game.cpp`):

| Key | Purpose |
|---|---|
| `init script` | Functions available to every script |
| `set field:` | Fields in the Set Info tab (title, set code, copyright, symbol…) |
| `default set style:` | Default styling for set-info fields |
| `card field:` | **Every per-card field.** The names here are the keys in the set file |
| `card links:` | Relations between linked cards (front/back, meld…) |
| `card list color script` | Row color in the card list |
| `statistics dimension:` / `statistics category:` | Stats tab |
| `pack type:` | Booster definitions |
| `has keywords`, `keyword mode:`, `keyword parameter type:`, `keyword:` | Keyword system (reminder text, `squad`, etc.) |
| `word list:` | Dropdown values (`type-en`, `enchantment` …) |
| `add cards script:` | "Add multiple cards" menu items |
| `update cards script:` | Card-data migrations run when the game version changes |
| `auto replace:` | Typing shortcuts (`--` → `—`) |
| `json paths` | Field mapping for JSON import/export |

A `card field:` looks like:

```
card field:
	type: text                 # text | choice | multiple choice | boolean | image | symbol | color | info | package choice
	name: rule text            # saved as rule_text in sets
	description: ...
	save value: true           # false = computed by script and not stored in the set
	editable: true
	show statistics: false
	card list column: 1610
	script: ...                # optional: computes/normalizes the value
```

The `_2`, `_3`, `_4` suffixed fields in our set (`super_type_2`, `image_2`,
`card_code_text_2`…) are separate game fields for the other faces of
multi-face frames (flip, split, transform, adventure). Every card stores all of
them, even when the style doesn't draw them.

---

## 5. `.mse-style`: how a card is drawn

Main file `style`. One style draws one family of frames for one game.

```
mse version:   2.6.0
game:          magic                 # which game this draws
short name:    M15 Main
version:       2026-09-13
depends on: ...                      # game, symbol fonts, includes

card width:    375
card height:   523
card dpi:      150                   # exports are rendered at card dpi × zoom

update cards script: ...             # migrations (see §6)
init script: ...                     # style-local functions (frame choice, etc.)

set info style: ...                  # look of the Set Info tab
styling field: ...                   # options in the Style tab (dropdowns/toggles)
styling style: ...                   # how those options look in the GUI
card style:                          # one entry per GAME card field
	name:
		left: 32  top: 30  width: 311  height: 23
		font: name: Beleren Bold  size: 16 ...
		z index: 10
	casting cost: ...
	rule text: ...
extra card field: ...                # per-card fields that ONLY this style has
extra card style: ...                # how those extra fields are drawn
```

Key points:

- **`card style:`** gives a position, font and visibility to each game field.
  A style doesn't have to draw every field, which is how one game supports
  sagas, battles, planeswalkers and so on.
- **`styling field:`** options are per style. In a set they are saved under
  `styling:` → `magic-<style name>:` (set-wide) or on a card with
  `has_styling: true` (per card).
- **`extra card field:`** values are saved on each card under
  `extra_data:` → `magic-<style name>:`. Switching to another style hides them
  but does not delete them.
- Fonts are referenced **by family name** (`Beleren Bold`, `MPlantin`) and must
  be installed system-wide. On Linux that means `~/.local/share/fonts`, then
  `fc-cache -f`. A missing font silently falls back to a default font.

---

## 6. `.mse-set`: the project

### Layout of `TheCloneWars.mse-set/` (directory form)

```
TheCloneWars.mse-set/
  set                      # main file (header, set info, styling, cards)
  card <name>              # per-card files (2.5.8 directory save; see "Card storage")
  cards                    # set_builder output (one file, many card: blocks)
  image123.png …           # card art, referenced by `image: image123.png`
  symbol4.mse-symbol       # set symbol, referenced by set_info.symbol
```

A zipped `.mse-set` is the same files in a zip archive. MSE can open either form.

### `set` main file

```
﻿mse_version: 2.0.2
game: magic
game_version: 2025-06-14              # game version it was last saved with
stylesheet: m15-altered               # set-wide default style (short form of magic-m15-altered.mse-style)
stylesheet_version: 2025-10-05
set_info:                             # values for the game's `set field`s
	title: The Clone Wars
	copyright: 101
	set_code: TCW
	symbol: symbol4.mse-symbol
	automatic_card_numbers: no
	card_number_style: 0001
styling:                              # set-wide Style tab choices, ONE BLOCK PER STYLE ever used
	magic-m15-altered:
		other_options: avoid covering devoid, auto vehicles, ...
		text_box_mana_symbols: magic-mana-small.mse-symbol-font
	magic-m15-saga: ...
	magic-DayNight: ...               # stale blocks for styles tried once remain here; harmless
card: ...                             # or include_file: lines (see below)
keyword: ...                          # custom keywords defined in this set (squad, etc.)
pack_type: ...
version_control: ...
apprentice_code: ...
```

`stylesheet: m15-altered` is the short form: MSE adds the game name prefix and
`.mse-style` suffix to get `magic-m15-altered.mse-style`.

### A card

```
card:
	stylesheet: m15-saga                  # per-card override (omitted/empty = use set default)
	stylesheet_version: 2024-09-23
	has_styling: false                    # true = this card has its own Style tab choices
	styling_data: ...                     # only when has_styling is true
	notes:
	uid: ...                              # stable id (added by 2.6 templates' migration scripts)
	linked_card_1: … linked_relation_1: … # card links (DFC backs etc.)
	time_created: 2026-04-21 21:47:59
	time_modified: 2026-07-18 17:17:14
	extra_data:                           # style-only fields, grouped by style
		magic-m15-altered:
			vorthos_box: Jack Brzozowski
	name: 212th Battalion                 # ── from here on: the game's card fields ──
	casting_cost: 2W
	image: image107.png
	super_type: <word-list-type-en>Enchantment</word-list-type-en>
	sub_type: <word-list-enchantment>Class</word-list-enchantment>…
	rarity: uncommon
	rule_text: …
	level_1_text: …                       # saga/class fields the game defines
	card_code_text: UW04
```

Order matters only for readability. MSE writes the fixed card keys first, then
the game fields in the order the game defines them. Fields with
`save value: false` are never written.

### Card storage: inline vs `include_file`

There are two ways the cards can sit in a set:

1. **Inline:** `card:` blocks directly inside `set`. This is what zipped sets
   and **MSE 2.6.x** write. The fork disabled per-card files in commit
   `595a548a` ("stop exporting each card to separate file in directory",
   July 2026).
2. **`include_file:` manifest:** `set` contains `include_file: card <name>`
   lines, and each card lives in its own file. **MSE 2.5.8** writes this when
   saving to a directory. Our current `set` uses this form (365 entries), and
   `set_builder` rewrites it to a single `include_file: cards`.

The reader accepts `include_file:` anywhere, so 2.6 opens both forms. By
default, **a save from 2.6 writes form 1**: all cards go inside `set`, and the
`card <name>` files are deleted on save because nothing references them.

**Keeping per-card files (recommended for this repo).** Our local MSE build
(branch `save-cards-in-separate-files` of the MSE fork) adds a setting that
brings back form 2 for sets saved as a directory. Set it in
`~/.magicseteditor/mse.config` while MSE is closed:

```
save_cards_in_separate_files: true
```

`set_builder` handles both forms (branch `mse-2.6-inline-cards-and-saga-bullets`):
it reads inline cards as well as included files, and consolidated mode removes
inline cards when it writes `include_file: cards`. `in_place` mode needs
per-card files, so it stops with an explanation if the set has inline cards.

### Versions and migrations

When the set is opened with newer packages than its recorded
`game_version` / `stylesheet_version`, MSE runs any `update cards script:` whose
`before version` is newer than the recorded version. For this set, moving from
Full Magic Pack 3.1.0 to 4.0.1 triggers:

| Package | Old → new | Migration |
|---|---|---|
| `magic.mse-game` | 2025-06-14 → 2026-09-24 | none |
| `magic-m15-altered` | 2025-10-05 → 2026-09-13 | *Migrate vorthos box*: copies `vorthos_box` into the new field format and gives each card a `uid` |
| `magic-m15-saga` | 2024-09-23 → 2026-10-06 | *Update coordinates to offsets* |
| `magic-m15-mainframe-planeswalker` | 2024-09-01 → 2026-09-15 | *Update to loyalty module* |
| `magic-m15-split-fusable` | 2024-09-03 → 2026-09-06 | *Updates styling fields* |
| `magic-m15-mainframe-battles` | 2025-01-21 → 2026-09-13 | none |
| `magic-m15-flip` | 2024-06-06 → 2024-06-06 | unchanged |

Expect the first 2.6 save to produce a large diff: card storage switches to
inline, cards get `uid`s, and the migrations above run. Make that save its own
commit, with no content edits mixed in.

Hardcoded versions in `set_builder` (`utl_card_defines.py: CardStyleSheets`,
`utl_mse_card_models.py`) are the 3.1.0-pack versions. MSE upgrades them on
open, but the builder will keep writing the old values until they're updated.

---

## 7. Changing a set's style (e.g. to a different CST frame)

- **Kept:** every game field (name, cost, types, rules/flavor text, P/T,
  rarity, art, card codes, keywords).
- **Reset to the new style's defaults:** styling options. The old style's block
  under `styling:` stays in the file.
- **Hidden but kept:** the old style's `extra_data:` block. It comes back if you
  switch back.
- **Not changed by switching the set default:** cards with their own
  `stylesheet:` (in this set: 21 saga/class, 24 battles, 7 planeswalkers,
  6 flip, 6 split). Change those separately.
- **Check by eye:** art crop (a different art box), text fitting, and fonts.

Moving from 3.1.0 to 4.0.1 alone doesn't change any style: all six styles this
set uses still exist under the same names.

---

## 8. Where things live on Linux (this machine)

| What | Path |
|---|---|
| MSE binary (built from source) | `…/magic_set_editor_from_src/MagicSetEditor2/build/magicseteditor` |
| User data dir (packages) | `~/.magicseteditor/data` → symlink to `~/mse-packs/Full-Magic-Pack/data` |
| UI resources | `~/.magicseteditor/resource` |
| Settings | `~/.magicseteditor/mse.config` |
| Template fonts | `~/.local/share/fonts/mse-full-magic-pack/` |
| Global data dir (unused) | `/usr/local/share/magicseteditor` |

| Font name aliases | `~/.config/fontconfig/conf.d/50-mse-font-aliases.conf` |

**Custom symbols.** The set's `L` (light side) and `O` (dark side) mana symbols
are local additions to `magic-mana-small.mse-symbol-font`: two `symbol:` entries
after `C`, plus `LightSideTulip.png` and `DarkSideInverted-removebg-preview.png`.
They live on the local branch `tcw-custom-symbols` of the pack clone.

**Font aliases.** The templates request `Beleren Bold` and
`Beleren Small Caps Bold` (the Windows names). On Linux these fonts are family
`Beleren` / `Beleren Small Caps` with style Bold, so the fontconfig file above
maps one name to the other.

Update templates (this keeps the custom symbols branch on top):

```bash
git -C ~/mse-packs/Full-Magic-Pack pull --rebase origin main
```

Then copy any new fonts into `~/.local/share/fonts/mse-full-magic-pack/`, run
`fc-cache -f`, and restart MSE.

Render every card without the GUI (useful as a smoke test, or for diffing renders):

```bash
magicseteditor --export-images TheCloneWars.mse-set "out/{card.card_code_text}.png"
```
