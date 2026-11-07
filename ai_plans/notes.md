# Notes I didn't want to pay attention to but didnt want to lose.

## 5. Baseline (v2, before any Pass 3 changes)

Weighted playables per archetype, from `curve_audit.py`:

| Azorius | Golgari | Simic | Rakdos | Gruul | Dimir | Selesnya | Boros | Orzhov | Izzet |
|---|---|---|---|---|---|---|---|---|---|
| 135 | 126 | 117 | 112 | 110 | 107 | 102 | 102 | 100 | 96 |

Average MV runs 3.08–3.34 across all ten; average archetypes per card is 2.07.
The spread is genuinely tight — **this is a well-built first pass, and that
should be said before the criticism.** No archetype is structurally starved of
playables. The problems are in *shape*, not volume.

> **Numbers caveat.** An earlier ad-hoc analysis quoted baselines ~2 higher for
> several archetypes (Azorius 137, Simic 119, Rakdos 114, Gruul 112, Dimir 109)
> because its Izzet hook lacked `prowess` and `noncreature spell`. The script's
> numbers above are canonical. All findings and deltas were unaffected.

---

## 6. Findings and decisions (Pass 3)

Full change list with card codes lives in `CHANGELOG.md`. This section records
**why**.

### 6.1 Simic — the four-drop pileup

Seven of Simic's twelve core creatures cost exactly 4. **Zero cost 2.** Its only
two common creatures cost 4 and 6.

The generalisable insight: *the problem was not "too many fours", it was that
the Light Side engine had no on-ramp.* Nothing generated or spent `L` below four
mana at common, so a drafter reading the signals correctly still had blank
opening turns. Moving 4s to 3s could not fix it alone, because most of the
four-drops are rares, mythics, or really Republic cards — shuffling them down
moves few weighted units and leaves MV 2 at zero.

Decisions: cheapen `CG06` (4→3) and `UZ10` Qui-Gon (4→3, the signpost must land
on curve to signal), and swap in a **payoff** at two rather than another
generator — generation already existed at two in blue, what was missing was a
reason to spend `L` early and a body to spend it on.

Result: creature curve MV 1–6 goes `2/6/4/13/8/7` → `2/8/8/9/6/7`, total
unchanged at 40.

### 6.2 Izzet — fewest playables, and why

Izzet was last at 96. The diagnosis that mattered was the colour split:

| | Blue | Red | Colourless |
|---|---|---|---|
| Cards excluded from Izzet | 16 | **32** | 16 |
| Weighted | 26 | **54** | 23 |

Izzet gets a normal share of blue and **starves on red**. Mono-red designed
cards split Gruul 13 / Boros 11 / Rakdos 8 / Izzet 7, and the other three each
own an exclusive, text-visible mechanic (contract/outlaw/crime, scrap/craft,
Dark Side/sacrifice) that tethers their cards to them.

The sharpest finding: of the set's **12 copy-referencing cards, zero are red and
zero are common.** Four are designed into Azorius.

> **Izzet is a two-colour archetype with a one-colour identity.** Every other
> pair has payoff carriers in both halves.

So the fix is not to move cards into Izzet — it is to put an Izzet hook onto red
and onto common, so red cards *read* as Izzet cards to drafters. Three of the
five changes are text or name edits on existing cards; only two are swaps.

Ledger: Izzet 96→104, Azorius 135→129, Gruul 110→106, Rakdos 112→110. Izzet
moves from last to 7th, **inside** the bottom cluster rather than below it. The
goal was never to make Izzet rich — it was that no archetype is *conspicuously*
starved.

### 6.3 Dimir — the MV-1 hole (not yet specified)

9 weighted one-drops against 28 at two, and almost all non-creature. Same
disease as Simic, one turn earlier: the archetype cannot start. Wants one common
one-drop creature each in U and B with board-relevant text. Needs two same-rarity
cuts, not yet chosen.

### 6.4 Selesnya — strong because nothing answers it (not yet specified)

Thinnest instant/sorcery line in the set: 8 weighted spells across MV 1–3, zero
at MV 5–6. It plays permanents on curve and never interacts — *and neither does
the mirror*, so it out-grinds everything.

The design principle here is worth keeping: **fix Selesnya's strength with cards
its opponents can cast, not by nerfing Selesnya.** A cheap sweeper at common
taxes go-wide directly; conditional removal ("power 3 or greater", "attacking
alone") does not answer it at all.

### 6.5 Structural note — colourless artifact concentration

Azorius carries the most weighted generic pickups in the set, almost all
colourless artifacts, because every colourless artifact reads as an
artifacts-matter card. This is the single largest remaining source of imbalance.
`CA01` Hologram Projector is the obvious candidate to carry a spells-matter
trigger instead, held back only because it also feeds Boros (102), which can't
afford the loss. Revisit if the colourless artifact count is rebalanced.

---