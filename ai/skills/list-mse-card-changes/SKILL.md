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

Cards are matched by name (and by card code for renames and swaps), so the two
sides can use different layouts: one file per card, inline `card:` blocks in
`set`, or one `cards` file holding every card (what `main` uses).

Ignored, so a card MSE merely re-saved doesn't show up: bookkeeping fields
(`time_modified`, styling data, frame colour), MSE's auto reminder text,
straight vs curly quotes, whitespace and line breaks, and the unused
`rule_text` on saga/class/planeswalker frames. Add `--raw` to list those
formatting-only and markup-only (spelling/symbol tag) differences too.

The report is written to `ai/reports/card-changes-YYYY-MM-DD_HHMMSS.md` and the
script prints the counts and the path. Use `--out FILE` for another location or
`--stdout` to print it without writing a file. Read the written file to show it.

The report is Markdown:

- **Swapped cards**: a different card now holds an old card's code (a new card
  taking its slot). Shows the new card in full and the replaced one collapsed.
- **Added / Removed cards**: cards that entered or left `set`.
- **Modified cards**: field-by-field changes, sorted by card code. Rules text
  and class/planeswalker text boxes are shown as line diffs; changed image files
  are attributed to the card that uses them.

Pick the base from what the user asked: "unstaged" → the default, "uncommitted"
or "since my last commit" → `--base HEAD`. Show the report to the user as is
(it's already grouped by card) and give them the path to the file. If it's long, lead with the counts line and
offer to summarize, but don't drop cards. Apart from the report file, don't write
anything; this skill doesn't change cards.
