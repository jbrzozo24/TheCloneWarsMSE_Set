## Utility Scripts for Set Management and Design Iteration

### curve_audit.py

Generate an HTML pages showing mana curve for each archetype based on heuristic card tagging

```bash
# Create a venv
python -m venv .venv
source .venv/Scripts/activate
pip install uv
uv pip install pandas
uv pip install openpyxl

# Copy an exported xlsx into the scripts directory
# Named Custom_Set_Cards.xlsx
# Then, run the script
cd scripts
python curve_audit.py Custom_Set_Cards.xlsx --out ../docs/curve-audit.html
```

### Loading idiom

```python
import pandas as pd

df = pd.read_excel('Custom_Set_Cards.xlsx', sheet_name='Cards').iloc[:421]
df = df[df['Card Code'].notna()]
df = df[df['Status'] != 'Backside']   # 335 front faces
```

### Traps — read before writing any script

- **`.iloc[:421]` isolates rows 2–422** of the sheet (the header row is consumed
  by `header=0`). Rows past that are scratch space.
- **Back faces of DFCs are identified by `Status == 'Backside'`, not by card
  code.** Code suffixes are inconsistent: `UW17B`, `UZ11B_0`, etc. Never filter
  on the code.
- **`O` in rules text means a Dark Side counter.** To detect it without matching
  the letter O inside names and flavour text, use
  `(?<![A-Za-z])O{1,4}(?![A-Za-z])`.
- **`Secondary Archetype` is free text** with ~44 distinct spellings ("Sith",
  "Dark Side", "Tatooine scrap", "Outlaws"…). Always normalise through an alias
  map; never compare raw strings.
- **`P/T` is unreliable** — some rows have it as a date. Use the separate `P`
  and `T` columns.
- **Rarity values** are `Common`, `Uncommon`, `Rare`, `Mythic Rare`.
- **Google Drive access is unreliable for this workbook.**
  `download_file_content` returns "No approval received";
  `read_file_content` silently truncates each tab partway through (yielded only
  ~116 of 335 cards). **Do not analyse from a Drive read — ask Jack to upload
  the file directly.**

Current composition (v1, front faces only): **335 cards** — 80 Common,
110 Uncommon, 96 Rare, 49 Mythic Rare; 314 spells + 21 lands.

---

## 4. Tooling — `curve_audit.py`

Self-contained script: tags every front face by archetype, prints a summary
table, and writes an interactive HTML curve report.

```bash
python curve_audit.py Custom_Set_Cards.xlsx \
    --out docs/curve-audit.html \
    --tags-out docs/archetype-tags.csv \
    --overrides tag_overrides.csv
```

Flags: `--sheet` (default `Cards`), `--max-rows` (default 421, `0` = all),
`--out`, `--tags-out`, `--overrides`, `--label`.
Deps: `pandas`, plus `openpyxl` for `.xlsx`. Accepts `.xlsx`/`.xlsm`/`.csv`/`.tsv`
— verified to give identical numbers from either format.

### The tagging model

A card is tagged into an archetype for one of three reasons, recorded per-card
so the output is auditable:

| Reason | Meaning |
|---|---|
| `designed` | the `Archetype` column names that archetype |
| `secondary` | the `Secondary Archetype` column names it (after alias normalisation) |
| `generic` | the archetype's colours can cast it AND it carries no mechanical hook belonging to a *different* castable archetype |
| `override` | set manually in `tag_overrides.csv` |

Core of the algorithm:

```python
castable = [a for a in ARCHETYPES if cols <= colors[a]]
if not castable:
    # 3+ colour card: any guild fully inside its colour identity may splash it
    castable = [a for a in ARCHETYPES if colors[a] <= cols]

hooks = hooks_for(row)
# a hook only tethers a card away from an archetype if the hooked
# archetype could actually cast the card in the first place
live_hooks = hooks & set(castable)
for a in castable:
    if a in tags:
        continue
    if live_hooks and a not in live_hooks:
        continue
    tags.add(a); reasons[a] = 'generic'
```

That `live_hooks` intersection is load-bearing. An earlier version compared
against all hooks, so a mono-blue card hooked to (say) Orzhov was excluded from
*every* blue archetype and ended up untagged. If cards start showing up in the
"matched no archetype" warning, suspect this logic first.

### Hooks

Regexes matched against `Rules Text + Mechanic + Subtype + Type + Card Name`,
lowercased. This is the knob most worth tuning as the set evolves.

| Archetype | Hook signals |
|---|---|
| Selesnya + Azorius | `squad`, `clone trooper`, `clone(s)` |
| Orzhov | `gain N life`, `whenever you gain life`, `lifelink`, `noble`, `senator` |
| Azorius | `droid`, `whenever an artifact`, `another artifact enters`, `artifacts you control` |
| Dimir | `mill(s)`, `infiltrat…`, `battle droid`, `from among them` |
| Simic | `jedi`, `light side`, `O{1,4}` |
| Izzet | `copy`, `copies`, `instant or sorcery spell`, `second spell`, `noncreature spell`, `prowess` |
| Rakdos | `sith`, `dark side`, `sacrifice a creature` |
| Rakdos + Golgari | `when(ever) … dies` |
| Golgari | `graveyard`, `endure`, `escape`, `geonosian`, `morbid` |
| Gruul | `contract`, `bounty counter`, `outlaw`, `commit a crime`, `treasure` |
| Boros | `scrap`, `charge counter`, `craft`, `equip` |

Deliberately **not** hooks: `artifact creature` (a type line, not an
artifacts-matter payoff — including it wrongly pulled every artifact creature
into Azorius).

### Overrides

When the heuristic gets a card wrong, fix it in `tag_overrides.csv`, **not** by
editing `HOOKS`. Editing hooks silently changes every card; an override records
one human judgement in a diffable file.

```csv
Card Code,Archetypes
CG07,Selesnya; Gruul
CU06,
```

An override *replaces* the computed tag set. An empty cell removes all tags (and
triggers the untagged warning, which is intended).