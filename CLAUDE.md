# CONTEXT.md — The Clone Wars (TCW) custom Magic set

Context for AI assistants working in this repo. Covers the project shape, the
hard constraints, the data model and its traps, the analysis tooling, and the
design decisions made so far *with their rationale* — the rationale matters more
than the conclusions, because the conclusions will change and the reasoning is
what makes the next round of changes consistent with the last.

---

## 1. Project

A custom Magic: The Gathering draft set themed on Star Wars: The Clone Wars,
designed by Jack (`jbrzozo24`). It is a **540-card draft set** built around ten
two-colour archetypes mapped onto MTG's guild pairs.

| Archetype | Guild | Colours |
|---|---|---|
| Republic | Selesnya | GW |
| Coruscant | Orzhov | WB |
| Droids | Azorius | WU |
| Separatist | Dimir | UB |
| Jedi | Simic | GU |
| Kamino | Izzet | UR |
| Sith | Rakdos | BR |
| Geonosis | Golgari | BG |
| Bounty Hunters | Gruul | RG |
| Tatooine | Boros | RW |

**Repos**
- Set files (MSE + analysis): `https://github.com/jbrzozo24/TheCloneWarsMSE_Set`
- Sync tooling: `https://github.com/jbrzozo24/magic_the_gathering_projects` (`set_builder`)

---

## 2. Hard constraints

These are non-negotiable and apply to every suggestion:

1. **The set size is fixed.** Any proposed addition must name a corresponding
   card to cut. Do not propose "add X" without "cut Y".
2. **Swaps must be same-rarity.** A new common replaces a common. In practice
   also match colour where possible, since colour balance is a separate budget.
3. **Modifications are free.** Changing an existing card's cost, stats, text,
   name or type does not require a swap. Prefer modification over swap when it
   achieves the same goal — it's cheaper and less disruptive.
4. **There should be a healthy balance of cards playable in multiple archetypes** 
   If a card is only good in one archetype, then anyone drafting that archetype
   always gets the same cards. Some cards should be designed with some utility
   overlap to help drafts feel different each time. It is okay for a card to be
   designed for a single archetype too, but there should be a healthy balance.
4. **Custom mechanics have owners.** Don't spread a mechanic across archetypes
   casually; the archetype identity problem (see §6) is caused by exactly that. 
   Mechanics should touch as many archetypes as it makes sense to, but it should
   be done with care.

---

## 3. Data model

### Source of truth

The card database lives in **Google Sheets**. Jack works in both 
**Magic Set Editor** and Sheets, syncing via the `set_builder` tool
with manual conflict resolution. Either side may be authoritative at a
given moment — tooling should accept both `.xlsx` and `.csv`.

**Editing cards.** Claude may edit and create cards in the MSE set, but only
through the `edit-mse-mtg-card` and `create-mse-mtg-card` skills (`ai/`,
linked from `.claude/skills/`). They keep the MSE file format intact, render
the card to check it, and respect the constraints in §2. Don't hand-edit card
files outside these skills, and don't edit the Google Sheet. **Jack does the
syncs:** never run `set_builder`. After an edit, say which cards changed so he
can sync them. For design discussion, describing old/new card text in prose is
still the default; only edit files when asked.
`tcw_cfg.yaml` is passed to the `set_builder` tool, and should likely also be used to build a simple set_reader/writer tool which can read the google sheet the same way set_builder does.

### `Cards` tab columns

```
Card Code, Card Name, Status, Color, Rarity, Archetype, Secondary Archetype,
CMC, Mana Cost, Type, Subtype, P, T, P/T, Mechanic, Rules Text, Category,
Flavor Text, Reference Card, Playtest Notes, Picture Ideas, Tag
```

### Weighting

**Common ×2, Uncommon ×2, Rare ×1, Mythic ×1.** Rationale: the question being
answered is "what does a drafter see", not "what does the spreadsheet hold".
Commons and uncommons appear twice in the set, rares and mythics only have a
single copy, so an archetype propped up by rares is not actually supported. 
**Lands are excluded** from curves — they'd
all pile at MV 0 and drown the signal. `7+` is the top bucket.