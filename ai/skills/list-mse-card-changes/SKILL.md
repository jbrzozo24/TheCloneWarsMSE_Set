---
name: list-mse-card-changes
description: List the card changes in The Clone Wars MSE set (TheCloneWars.mse-set) that aren't committed yet, as a report organized by card — swapped, added, modified and removed cards, with old → new mana cost, rules text, P/T, art and so on. Use this whenever the user asks what they changed, what's in their unstaged/uncommitted/working changes, what to sync, for a changelog or summary of recent card edits, or for a diff of the set against a commit or branch, even if they don't mention git or MSE.
---

# List MSE card changes

Run from the repo root:

```bash
python3 ai/scripts/mse_changes.py              # unstaged: working tree vs the index
python3 ai/scripts/mse_changes.py --base HEAD  # everything uncommitted
python3 ai/scripts/mse_changes.py --base main  # vs another commit or branch
```

Add `--raw` to also note fields whose only change is MSE markup (spelling
tags, symbol tags). Bookkeeping fields (`time_modified`, styling data) are
always ignored, so a card that MSE merely re-saved doesn't show up.

The report is written to `ai/reports/card-changes-YYYY-MM-DD_HHMMSS.md` and the
script prints the counts and the path. Use `--out FILE` for another location or
`--stdout` to print it without writing a file. Read the written file to show it.

The report is Markdown:

- **Swapped cards**: an `include_file` line in `set` replaced in place, i.e.
  a new card taking an old card's slot. Shows the new card in full and the
  replaced one collapsed.
- **Added / Removed cards**: cards that entered or left `set`.
- **Modified cards**: field-by-field changes, sorted by card code. Rules text
  and class/planeswalker text boxes are shown as line diffs; changed image files
  are attributed to the card that uses them.

Pick the base from what the user asked: "unstaged" → the default, "uncommitted"
or "since my last commit" → `--base HEAD`. Show the report to the user as is
(it's already grouped by card) and give them the path to the file. If it's long, lead with the counts line and
offer to summarize, but don't drop cards. Apart from the report file, don't write
anything; this skill doesn't change cards.
