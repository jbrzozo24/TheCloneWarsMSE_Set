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

The set is in **active v2 → v3 iteration**. Two six-player drafts have been
played; the decks and sideboards were photographed and reviewed. Changes are
tracked in `CHANGELOG.md`.

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
given moment. Given how finicky it is to keep these two in sync,
let Jack make the actual edits and do the syncs. You can make change decisions in
text describing the old/new card/rules text etc. Either side may be
authoritative at a given moment — tooling should accept both `.xlsx` and `.csv`.
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

---

## 7. Carried over from Pass 2 (post-draft design doc)

- Removal is shallow: ~6 of 80 commons. Target 12–15%.
- **Rakdos** has an identity crisis — consolidate around one
  Plot/Crime → Dark Side → payoff loop; cut sacrifice, Morbid and Sith tribal
  gating.
- **Scrap** is too hard to enable, sacrifiing artifacts to scrap feels quite
  bad in practice, need to make it feel more worth the sacrifice.
- **Dimir** is poorly positioned. Interacting with battles just is not strong enough.
  Siege's need more board affecting ETBs. Potentially more problems too.
- **Izzet** lacks identity — concentrate copy cards there, and prowess triggers, 
  add copy commons.
  (Pass 2 changes 2.7 / 2.9 / 2.11 begin this.)
- **Gruul's** v2 strong performance may reflect player skill rather than archetype
  strength — flagged for controlled v3 testing. Do not "fix" Gruul on v2 data.
- **Selesnya's** v2 strong performance may reflect shallow removal problem.

---

## 8. Working agreements

How Jack wants collaboration to go:

- **Be constructively critical, don't sugar-coat.** Name structural problems
  directly. Also name what's working — the tight weighted spread and the
  well-built Light Side engine are real accomplishments and saying so is not
  padding.
- **Every problem statement comes with a proposed fix** — a redesigned card or
  cards, plus the logic for *how* it fixes the problem.
- **Every addition names its cut**, same rarity. Show the balance ledger when
  changes move weight between archetypes.
- **Stay scoped.** Answer the question asked; don't try to solve the whole set
  at once. Findings outside the question go in a short "not yet specified"
  note, not a full treatment.
- **Playtest observation beats model output.** Jack's firsthand read that Simic
  had a four-drop pileup matched the data exactly. When they conflict, dig into
  why rather than trusting the script.
- **State the model's limits.** The `generic` tagging pass is a heuristic doing
  real work (it's the difference between 34 core and 135 weighted for Azorius).
  Ledgers built on it are directionally right, not precise. Say so.

---

## 9. Open threads

- v3 playtests to validate the Pass 3 changes — specifically Izzet identity and
  whether Gruul's strength is archetype or player.
- Pick cuts for the Dimir one-drops and the Selesnya-answering removal commons.
- Simic MV 6 becomes the second-tallest creature bar after 2.1–2.4; `CU07`
  Kamino Stormcaller is a common 5/5 for six.
- Consider whether `Secondary Archetype` should be normalised at source in the
  sheet, which would let the alias map shrink.
