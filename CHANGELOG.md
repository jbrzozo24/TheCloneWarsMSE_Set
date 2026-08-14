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

Rationale for 2.2: a signpost uncommon at 4 can't signal during the game. The
draw trigger *is* the signpost; the untap/tap mode is a second card's worth of
text. Once-per-turn is not optional at 3 mana.

Alternative to 2.3 if the Bantha stays: cut `CG03` Gungan Operative instead
(Glue two-drop, curve-neutral swap, costs some land fixing).

**Weighted Simic creature curve, MV 1–6:** `2 / 6 / 4 / 13 / 8 / 7` →
`2 / 8 / 8 / 9 / 6 / 7`. Total unchanged at 40.

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

**Balance ledger (weighted playables):**

| Change | Izzet | Azorius | Gruul | Rakdos |
|---|---|---|---|---|
| 2.5 Lone Raider → Izzet | +2 | | −2 | −2 |
| 2.6 Medical Droid retheme | +2 | −2 | | |
| 2.7 Now There Are Two Of Them! | — | −2 | | |
| 2.8/2.9 blue common swap | +2 | −2 | | |
| 2.10/2.11 red common swap | +2 | | −2 | |
| **Net** | **+8** | **−6** | **−4** | **−2** |
| **Before → after** | 96 → **104** | 137 → **131** | 112 → **108** | 114 → **112** |

Izzet moves from last to 7th of ten, inside the bottom cluster
(Boros 102, Selesnya 102, Orzhov 100) rather than below it.

### Not yet specified

Directional findings from the same pass, no cards drafted yet:

- **Dimir one-drops.** 9 weighted at MV 1 against 30 at MV 2, and almost all
  non-creature. Wants one common one-drop creature each in U and B with
  board-relevant text. Needs two same-rarity cuts.
- **Selesnya interaction.** Thinnest instant/sorcery line in the set — 8 weighted
  spells across MV 1–3, zero at MV 5–6. Fix via the planned removal commons,
  weighted so *opponents* can answer a wide board (a cheap sweeper at common
  taxes Selesnya without nerfing it directly).
- **Simic MV 6.** Now the second-tallest bar at 7 weighted; `CU07` Kamino
  Stormcaller is a common 5/5 for six. Revisit if Simic still feels clunky.
- **Colorless artifact concentration.** Azorius carries 78 weighted generic
  pickups, the most in the set, almost all colorless artifacts. `CA01` Hologram
  Projector is the obvious candidate to carry a spells-matter trigger, held back
  because it currently feeds Boros (102), which can't afford the loss.

---

## Pass 1 — post-draft design document

- Add ~5 removal commons (removal is ~6 of 79 commons vs. a healthy 12–15%).
- Consolidate Rakdos around one Plot/Dark Side → payoff loop; cut sacrifice,
  crime, Morbid and Sith tribal gating.
- Double scrap fodder-making commons (4 → 8); cap scrap costs at 2/3/4 by rarity.
- Address Selesnya's strength via removal additions rather than direct nerfs.
- Concentrate copy-referencing cards into Izzet; add copy-themed commons.
  *(Changes 2.7, 2.9, 2.11 begin this.)*