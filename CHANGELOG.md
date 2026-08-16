# Set Changelog

Loose running log of design changes. Entries are grouped by review pass.
Status values: **Proposed** (agreed in review, not yet in MSE/Sheets) →
**Applied** (live in the set files) → **Tested** (survived a draft).

Set size is fixed. Every addition must name a removal of the same rarity,
unless the change is a modification to an existing card.

---

## Pass 2 — v1 draft data review (2 six-player drafts)

Analysis basis: all 335 front faces tagged by archetype, curves weighted
Common/Uncommon ×2, Rare/Mythic ×1. Regenerate with `curve_audit.py`.

### Jedi — Simic: four-drop pileup

**Finding.** Seven of Simic's twelve core creatures cost exactly 4. Zero cost 2.
Its only two common creatures cost 4 and 6, so the Light Side engine cannot start
before turn four at common.

| # | Card | Change | Status |
|---|---|---|---|
| 2.1 | `CG06` Jedi Youngling Initiate | **Modify.** `3G` 3/4 → `2G` 2/3. ETB `LLL` → `LL`. "Untap up to two creatures" → "Untap target creature you control." | Proposed |
| 2.2 | `UZ10` Qui-Gon Jinn, Jedi Wanderer | **Modify.** `2GU` 2/3 → `1GU` 2/2. ETB `LLL` → `LL`. Drop the `LLL: Untap target permanent, then tap…` ability entirely. Add "This ability triggers only once each turn" to the draw trigger. | Proposed |
| 2.3 | `CG07` Meandering Bantha | **Cut** (Common, R... green). A 10/6 for `2GGG` is far outside the common power band and its `5: You get LL` is never activated. | Proposed |
| 2.4 | *Sparring Padawan* (new) | **Add** (Common, green) — replaces 2.3. `1G` 2/2 Creature — Human Jedi. "When Sparring Padawan enters, you get L. Whenever you spend one or more L, Sparring Padawan gets +1/+1 until end of turn." | Proposed |

### Kamino — Izzet: fewest playables in the set

**Finding.** Izzet has 96 weighted playables, last of ten, 41 behind Azorius.
The shortfall is red-side: 54 weighted red cards are excluded vs. 26 blue.
Mono-red splits Gruul 13 / Boros 11 / Rakdos 8 / Izzet 7, and the other three
each own an exclusive mechanic that tethers their cards. Of the set's 12
copy-referencing cards, **zero are red and zero are common** — Izzet is a
two-colour archetype with a one-colour identity.

| # | Card | Change | Status |
|---|---|---|---|
| 2.5 | `CR01` Lone Raider | **Modify.** `R` 1/1 "dies → Treasure" → `R` 1/2 Creature — Rogue Citizen, **Prowess**. Removes a Gruul currency from a Glue card; fills Izzet's empty MV-1 creature slot. | Proposed |
| 2.6 | `CU05` Medical Droid | **Retheme only**, no rules change. Rename to *Kaminoan Recall Technician*, retype Creature — Kaminoan Scientist. The word "Droid" is the only thing making an Izzet tempo card read as Azorius. | Proposed |
| 2.7 | `UU06` Now There Are Two Of Them! | **Modify.** Drop the artifact rider: "Create a token that's a copy of target creature. If you've cast another spell this turn, put a +1/+1 counter on it and draw a card." Identity only — adds no playables. | Proposed |
| 2.8 | `CU06` Astromech Investigator | **Cut** (Common, blue). Five-mana common flier with a symmetrical "each player draws"; Azorius is the deepest pool in the set. | Proposed |
| 2.9 | *Accelerated Decanting* (new) | **Add** (Common, blue) — replaces 2.8. `1U` Instant. "Create a token that's a copy of target creature you control. Sacrifice it at the beginning of the next end step." First copy card at common. | Proposed |
| 2.10 | `CR15` Twin Blaster Showdown | **Cut** (Common, red). Six-mana common referencing outlaws, scrapping *and* contract on one card — the identity-crisis problem in miniature. | Proposed |
| 2.11 | *Double Blaster Volley* (new) | **Add** (Common, red) — replaces 2.10. `1R` Instant. "Deals 2 damage to any target. If you've cast another spell this turn, copy this spell. You may choose new targets for the copy." Red copy card + spells payoff + one more removal common. | Proposed |

---

## Pass 3 — v3 MSE application (2026-08-16)

### Pass 2 proposals now applied

| # | Card | Change | Status |
|---|---|---|---|
| 3.1 | `CG06` Jedi Youngling Initiate | **Applied as proposed (2.1).** `3G` 3/4 → `2G` 2/3. ETB `LLL` → `LL`. "Untap up to two creatures" → "`LL`: Untap target creature you control." | Applied |
| 3.2 | `UZ10` Qui-Gon Jinn, Jedi Wanderer | **Applied, deviates from 2.2.** `2GU` 2/3 → `1GU` 2/2. ETB `LLL` → `LL`. Draw trigger now reads "This ability triggers only once each turn." **The `LLL` untap/tap ability was kept**, narrowed to "Untap target permanent *you control*." 2.2 called for deleting it as a second card's worth of text; it is still there at a lower mana cost. | Applied |
| 3.3 | `CG07` Meandering Bantha → *Sparring Padawan* | **Applied, deviates from 2.3/2.4.** In-place rename of the same common green slot. `2GGG` 10/6 Beast → `1G` **1/3** Human Jedi with vigilance: "Whenever Sparring Padawan attacks, you get `L`. Whenever you spend one or more `L`, Sparring Padawan gets +1/+1 until end of turn." 2.4 specified a 2/2 with an **ETB** `L`; the shipped card is a 1/3 whose `L` is gated behind attacking, which is slower to turn on than the proposal intended. New art `image245.png`. | Applied |
| 3.4 | `CR01` Lone Raider → *Unmodified Template* | **Applied, deviates from 2.5.** Renamed; Rogue Citizen → Human Clone; gains **haste and prowess**. But `R` **1/1** (2.5 asked for 1/2) and **the "dies → create a Treasure" trigger was kept**. The point of 2.5 was to strip a Gruul currency off a Glue card; that currency is still on it, so the Izzet/Gruul ledger line for 2.5 no longer holds. New art `image249.png`. | Applied |
| 3.5 | `CU05` Medical Droid → *Repair Technician* | **Applied, deviates from 2.6.** Renamed and given an Izzet guild watermark. **The type line was not changed — still Creature — Droid Artificer.** 2.6's whole argument was that the word "Droid" is what makes an Izzet tempo card read as Azorius; the watermark signals Izzet to the drafter but the Droid type still feeds every Azorius artifact/droid payoff. Rules text unchanged apart from the name. | Applied |
| 3.6 | `UU06` Now There Are Two Of Them! | **Applied, redesigned from 2.7.** Artifact rider dropped as proposed. The spells payoff moved from a rider onto the cost instead: "This spell costs `2` less to cast if you've cast an instant or sorcery spell this turn. Create a token that's a copy of target creature." Cost stays `3UU`, so it's effectively `1UU` in the Izzet deck and unplayable elsewhere — a sharper archetype signal than 2.7's version. New art `image282.png`. | Applied |

### New changes, not from Pass 2

| # | Card | Change | Status |
|---|---|---|---|
| 3.7 | `UR04` Clone Deserter | **Modify.** Sacrifice-a-Clone additional cost removed. Modes are now "Create a 2/2 red Clone creature token that's tapped and attacking, sacrifice it at the beginning of your next end step" or "Create a Treasure." Also `+2/+0` and menace mode dropped. Subtype Clone Trooper Citizen → Clone Citizen. `2R` 2/3 unchanged. | Applied |
| 3.8 | `UR15` Discard the Defective | **Modify.** "As an additional cost, sacrifice a creature" removed. Adds "If this is the second spell you've cast this turn, copy it, you may choose new targets for the copy." Both existing modes unchanged. Second Izzet copy/spells-matter card in this batch. | Applied |
| 3.9 | `CG05` Gamorrean Guard | **Modify.** Rarity **uncommon → common**. No cost, stat or text change. ⚠ This is the one change in the batch that breaks a fixed budget: nothing moved common → uncommon to balance it, so the set is now 81 commons / 109 uncommons against the fixed 80/110. Needs a paired demotion or promotion before the next export. | Applied |
| 3.10 | `CG08` Leader of Kashyyyk | **Modify.** `4GG` → `3GG`. | Applied |
| 3.11 | `MZ07` Jango Fett, Master Bounty Hunter | **Modify.** Crime trigger gated to once per turn: "Whenever you commit a crime **for the first time each turn**, contract 2." Flying/haste, the `RR` unblockable attack trigger and Escape `5RG` unchanged. | Applied |
| 3.12 | `UB08` Maul, Broken by Hatred | **Modify.** Template fix, no design change: "Whenever a creature you commit a crime" → "Whenever a creature **you control commits** a crime." The Sith sacrifice cost and the `1BR` halving ability are unchanged — note this leaves Rakdos Sith tribal gating in place, which Pass 1 wanted cut. | Applied |
| 3.13 | `UB10` Rebuild the Legion | **Modify.** The returned artifact creature now **gains haste**. Finality counter and the `OO` double strike rider unchanged. | Applied |