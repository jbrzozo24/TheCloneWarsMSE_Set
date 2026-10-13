# Proposed Changelog — Pass 4: Rakdos rebuild, Dimir repositioning

Status values follow `CHANGELOG.md`: **Proposed** → **Applied** → **Tested**.
Everything below is **Proposed**. Nothing here has been written to MSE or Sheets.

Analysis basis: `scripts/Cards_dump.json` (337 front faces, 2026-08-16).
Weighting Common/Uncommon ×2, Rare/Mythic ×1 per `curve_audit.py` convention.

---

## 0. The two diagnoses

Both archetypes fail for the *same shape* of reason, and neither is a
power-level problem. In each case the archetype's payoff half and its enabler
half were built at different rarities, so a drafter who reads the signals
correctly still assembles a deck that cannot execute its plan.

**Rakdos** — the Dark Side counter (`O`) economy has **6 generators at common
and 0 payoffs at common.** A Rakdos deck built out of commons banks a resource
it is physically unable to use.

| Rarity | `O` generators | `O` payoffs |
|---|---|---|
| Common | 6 | **0** |
| Uncommon | 6 | 4 |
| Rare | 7 | 5 |
| Mythic | 4 | 5 |

Three supporting findings:

- **9 of 17 `O` generators trigger on a creature dying** (`CB01`, `CB13`,
  `CB14`, `CR02`, `CR07`, `UB01`, `RB08`, `MZ12`, plus Morbid riders). The
  aristocrats theme isn't just *on* the cards, it's welded into the resource.
- **Rakdos doesn't own crime.** 5 of 9 crime cards belong to Gruul, Golgari and
  Boros. `UG18` Clan Viszla is a *green* card that mints `O`.
- **"Rule of Two" is anti-synergy.** `CB03`, `UB05`, `UB08` all read "if you
  control two or more Sith, sacrifice a Sith/creature" — the card gets worse the
  better your board is, and it's a hidden additional cost that makes drafters
  misprice it in the pack. Delete, don't retune.

**Dimir** — **18 of 29 Dimir cards reference battles, 5 of its 7 commons among
them, and there are 0 battles at common in the entire set** (11 uncommon, 11
rare, 2 mythic). `CU01` and `CU04` are *blank* without a battle in play — a
vanilla 1/1 and a vanilla 1/3.

- **Battles aren't Dimir's, they're the set's.** Only 2 of 24 are designed into
  Dimir, and each of the 10 Duels is a *different* guild's signpost. Dimir's
  payoffs trigger off cards the Dimir drafter is by definition not being passed.
- **Supply is ~2 cards per draft.** A mono-U/B deck can cast 5 battles set-wide
  (`UU17`, `UB17`, `UZ12`, `RU10`, `RB10`) — weighted 8 units across a six-player pod.
- **Strip the battle text and a real archetype is already underneath it:**
  surveil, targeted hand attack, evasive creatures. That's the README's own
  *"the more you learn, the more you control."*

---

## 1. Design thesis

The previous draft of this document solved Rakdos by printing *"Whenever you
commit a crime for the first time each turn, you get `O`"* on eight cards. That
makes the archetype legible and makes every card mono-purpose — good only in
Rakdos, and identical to its neighbours in the pack. It fails §2.4 rather than
serving it. This version replaces that with two structural ideas.

### 1.1 The Dark Side is a track you descend, not a currency you spend

Most `O` cards should **check** your corruption, not consume it. `MB03` Jedi
Blindness already does this — *"as long as you have two or more `O`… as long as
you have four or more `O`…"* — and it is the best-designed `O` card in the set.
This pass makes it the template.

Why this fixes the overlap problem *by construction*: a threshold card is a
**complete, castable card with no `O` at all**, that gets better in the deck
that has some. `CB13` at `1B` for -2/-2 is a card every black deck plays. At
three `O` it's -5/-5. A Golgari or Orzhov drafter takes it for the floor; the
Rakdos drafter takes it for the ceiling. Neither is wrong.

It also creates real gameplay tension the spend-only version never had: **the
few dedicated sinks compete with your thresholds.** Do I dump four `O` into a
removal spell now, or hold at four and keep my whole team turned on? That
decision is the archetype.

Rough shape of the intended mix: **thresholds ≈ half, generators ≈ a third,
dedicated sinks ≈ a sixth**, with sinks concentrated at uncommon and above where
a drafter has actually committed — plus a small number of *hard-gated* cards
that are uncastable without `O` at all. Those are the exception, and §1.3 is
what earns them.

### 1.2 Plot cost is a design lever, not a number to normalise

Plot cost **above** mana cost is correct when the card *scales* — you pre-pay a
premium to buy the option of casting it at its maximum, on a turn when your
mana is doing something else. Plot cost **at** mana cost is for neutral cards
you're plotting purely for mana smoothing. Plot cost **below** mana cost is for
cards that are weak or situational, where you want to bribe the drafter into
plotting at all.

The previous draft got this backwards and proposed flattening four plot costs
down to match mana cost. Worst of those: it flagged **`MZ14` Order 66's
`Plot 7WB` on a `5WB` card as a tax to fix.** Order 66 deals X damage where X is
the opponent's non-legendary creature count and then pairs them off to fight —
it is the single most board-scaling card in the set. Plotting it turn 7 and
cashing it when their board is widest is *exactly* the right play, and the
premium is what you pay for that option. **`MZ14` is now the exemplar this pass
designs toward, and its cost is unchanged.**

The Rakdos plot suite is therefore built as a ladder, not a flat rate:

| Card | Mana | Plot | Why |
|---|---|---|---|
| `UB16` Palpatine's Revelation | `3BB` | `2BB` | *below* — mana smoothing on a situational card. Unchanged. |
| `CR05` Warmonger's Fodder | `2R` | `2RR` | *above* — the exile-cast ETB is the payoff |
| `UR05` Asajj Ventress | `2R` | `3R` | *above* — damage scales with `O` banked while she waits |
| `UB05` Jar Jar Binks, Sith Lord? | `2B` | `4B` | *far above* — commit to the bit, get a removal spell |
| `MZ14` Order 66 | `5WB` | `7WB` | *far above* — scales with their board. Unchanged. |

### 1.3 The Dark Side breaks the colour pie

This is the reason the resource exists, and the previous draft missed it
entirely — it treated `O` as a way to get bigger numbers on cards black and red
could already have.

**`MB03` Jedi Blindness already does this.** At two or more `O` your permanents
have hexproof; at four or more you cast spells as though they had flash. Those
are blue effects on a card with no blue requirement to *use* them. It is the
second thing that card gets right and the second reason it's the best-designed
`O` card in the set.

So the third rung: **the deepest `O` payoffs should let black and red do things
black and red cannot do.** That gives corruption a flavour justification —
"abilities that some consider to be… unnatural" is the archetype's own pitch —
and it gives the drafter a reason to go deep beyond incremental value.

This is a **deliberate exception to §1.1**: a pie-break card should be *hard*
gated, not a threshold. If the off-colour effect is available without paying,
it isn't a break, it's just a black card doing a white thing. Two cards in this
pass are gated this way (`UB14`, and `UB05`'s artifact/enchantment destruction);
everything else stays optional-or-threshold.

### 1.4 Dimir gets a track too, and that's the seam

Dimir's parallel to corruption is **the opponent's hand**: cards check "an
opponent has two or fewer cards in hand" or "an opponent discarded a card this
turn." Same structural benefit — every one is a complete card at floor.

That makes the black overlap fall out naturally instead of being engineered:
**Rakdos tracks its own corruption, Dimir tracks the opponent's emptiness, and
the cheap black interaction that feeds both is the contested middle.** `CB13`
and `CB10` are deliberately parallel two-mana black removal commons — one
scales off `O`, one cantrips off discard — and a BR or UB drafter is happy with
either. That's the overlap the previous draft tried to force with a shared
trigger word.

---

## 2. Rakdos — Sith Plotting

### 2.1 Commons

Goal: a Rakdos deck made only of commons can complete the loop, and **five of
the seven are cards a non-Rakdos black or red deck would still play.**

| # | Card | Change | `O` role | Status |
|---|---|---|---|---|
| 4.1 | `CB01` Sith Acolyte | **Modify.** `B` 1/1 Creature — Human Sith Acolyte. Drop Rule of Two, the sacrifice ETB, the death trigger. "When Sith Acolyte enters, you get `O`. / As long as you have three or more `O`, Sith Acolyte gets +2/+1 and has menace." | burst + threshold | Proposed |
| 4.2 | `CB03` Apprentice of the Dark Side | **Modify.** `1B` 2/2 Creature — Human Sith Witch. Drop the Rule of Two additional cost and the sacrifice pump. "`OO`: Put a +1/+1 counter on Apprentice of the Dark Side. It gains deathtouch until end of turn. Activate only once each turn." The archetype's mana sink — a 2/2 for 2 anywhere, a growing deathtouch threat in Rakdos. *Reference card: Longtusk Cub.* | sink | Proposed |
| 4.3 | `CB12` Intercept Beacon Transmissions | **Modify.** `3B` → `1B` Sorcery. Drop plot, the sacrifice kicker and the draw-2/lose-3. "Target opponent reveals their hand. You choose a nonland card from it. That player discards that card. If it was a creature card, you get `OO`." Conditional payout rewards hitting the card that mattered. | conditional burst | Proposed |
| 4.4 | `CB13` Drain the Living Force | **Modify.** `2B` → `1B` Instant. Drop Morbid and the exile replacement. "Target creature gets -2/-2 until end of turn. If you have three or more `O`, it gets -5/-5 until end of turn instead." | threshold | Proposed |
| 4.5 | `CR05` Warmonger's Fodder | **Modify.** `2R` 2/2 → `2R` 3/2 Creature — Human Sith Warrior, **haste**. **Plot `2RR`.** Drop the token generation and the sacrifice-for-`RRR`. "Haste. / When Warmonger's Fodder enters, if it was cast from exile, you get `OO` and it deals 2 damage to target creature an opponent controls." A 3/2 haste for 3 in any red deck; the plot premium buys the ETB. | plot burst | Proposed |
| 4.6 | `CR07` Coruscanti Protestor | **Modify.** `2RR` 4/3 → `2R` 3/3 Creature — Human Rogue, **menace**. Drop the sacrifice-for-pump. "Menace. / As long as you have four or more `O`, Coruscanti Protestor gets +2/+0 and has trample." Threshold set one higher than 4.1/4.4 so the two turn on at different points in the game. | threshold | Proposed |
| 4.7 | `CR13` Separatist Bombardment | **Modify — kept, not cut.** The previous draft cut this; it's the set's token-management common and that role is load-bearing. `4R` Instant, cost unchanged. Drop the death-triggered `O` (one of the 9 in §0) and make the token half scale: "Choose one. If you have three or more `O`, choose both instead. / • Separatist Bombardment deals 6 damage to target creature. / • Separatist Bombardment deals 2 damage to each creature token your opponents control." Its floor is now *better* than the printed card — a modal 6-damage removal spell **or** a token sweeper, rather than 6 damage plus a single 2-damage ping — and its ceiling is a genuine Selesnya/Republic answer (`notes.md` §6.4). | threshold | Proposed |
| 4.8 | *Vent Your Anger* (new) | **Add** (Common, red) — **replaces `CR02` Immoral General** (Common, red, Glue), which is **cut**. `1R` Instant. "As an additional cost to cast this spell, you may pay any amount of `O`. Vent Your Anger deals 2 damage to target creature or planeswalker, plus 1 damage for each `O` paid this way." A 2-mana Shock-plus in any red deck; the corruption dump in Rakdos. Same colour, same mana value, same Glue role — see §4.5 for why `CR02` is the cut. | scaling sink | Proposed |

**Common `O` payoffs 0 → 5** (three thresholds, two sinks). Rakdos's common
removal goes 2 cards (at 3 and 5 mana) → 4 cards (`CB13` and *Vent Your Anger*
at 2 mana, `CR13` at 5, plus `CB12`'s hand attack), which also pays into the
set-wide removal-depth problem and `notes.md` §6.4.

Rakdos's common count goes 7 → 8, absorbing a slot from Glue. That is
deliberate — Rakdos is one of the two weakest archetypes in the set and this is
the pass meant to fix it — and it is recorded in §4.5 rather than buried.

**Playable outside Rakdos:** `CB03` (any black), `CB12` (any black — Dimir,
Orzhov, Golgari all want cheap targeted discard), `CB13` (any black),
`CR05` (any red), `CR07` (any red), `CR13` (any red), *Vent Your Anger* (any
red). Seven of eight.

### 2.2 Uncommons — nine cards, nine different mechanisms

| # | Card | Change | `O` role | Status |
|---|---|---|---|---|
| 4.9 | `UB01` Nightsister Initiate | **Modify.** `1B` 2/1 first strike. Drop Morbid and the sacrifice ability. "First strike. / When Nightsister Initiate enters, you may pay 3 life. If you do, you get `OOO`." Life-as-a-cost makes it an Orzhov and Coruscant pickup too. | life → `O` | Proposed |
| 4.10 | `UB05` Jar Jar Binks, Sith Lord? | **Modify.** `3B` → `2B` 1/3 Legendary Creature — Gungan Sith. Drop the Rule of Two cost and the Morbid end-step trigger. **Plot `4B`.** "When Jar Jar enters, if he was cast from exile, destroy target creature an opponent controls and you get `OOO`. / Whenever Jar Jar attacks, if you have five or more `O`, he gets +4/+0 and gains menace until end of turn." The gag made mechanical: a laughable 1/3 unless you commit to the bit early, then he's a removal spell stapled to a threat. Also the second pie-break (§1.3) — unconditional artifact/enchantment destruction is white and green's job, and here it's gated behind casting him from exile. | plot burst + threshold + pie break | Proposed |
| 4.11 | `UB08` Maul, Broken by Hatred | **Modify.** `3BB` 4/5, drop the Rule of Two additional cost and the crime trigger. "Whenever a creature an opponent controls dies, you get `O`. / `1BR`: Choose target creature. Its base power and toughness become half its current power and toughness, rounded down." The anti-aristocrats death trigger — it rewards *killing things*, which is what removal-heavy Rakdos does. Keeps the halving ability, which is genuinely unique in the set. | opposing death → `O` | Proposed |
| 4.12 | `UB14` Is that legal? | **Redesign — the pie-break card (§1.3).** The previous draft turned this into a threshold counterspell, which missed the point: the `OO` cost is there so the Dark Side lets black do what black can't. A counterspell in black is the *smallest* available break and the least interesting. `BB` → `2BB` **Instant**. "As an additional cost to cast this spell, pay `OO`. Destroy all creatures." **Two breaks on one card** — mass destruction (Damnation's famous pie-break) *and* instant speed, which effectively no colour gets. Instant speed is also what preserves the card's identity: "Is that legal?" was a gotcha card and it still is, just a far bigger one. Answers Selesnya (`notes.md` §6.4) and the token problem, and only the corrupted deck gets it. ⚠ Power flag in §6. | hard gate / pie break | Proposed |
| 4.13 | `UR05` Asajj Ventress, Sith's Apprentice | **Modify.** `2R` 3/2 flying haste, **Plot `3R` retained** — the premium is the design. Death trigger → "When Asajj Ventress enters, if she was cast from exile, she deals damage equal to the number of `O` you have to target creature." Plot her turn 4, bank corruption, cash her on the turn she snipes a fatty *and* leaves a 3/2 flier behind. | `O` count as X | Proposed |
| 4.14 | `UR08` Savage, Manipulated Brute | **Modify.** `3RR` 6/2 → same stats, drop the sacrifice-a-Sith cost and the "add `RR`" ability. "Savage, Manipulated Brute costs `2` less to cast if you have three or more `O`. / Menace, haste." A 5-mana 6/2 menace haste in any red deck; a 3-mana one in Rakdos. The Rule-of-Two tax becomes a corruption discount. | threshold (cost) | Proposed |
| 4.15 | `UR09` Army of the Dead | **Cut** (Uncommon, red). Sacrifice additional cost plus death-triggered token generation — aristocrats with nothing salvageable underneath. | — | Proposed |
| 4.16 | *The Plan Unfolds* (new) | **Add** (Uncommon, red) — replaces 4.15. `2R` Enchantment. "When The Plan Unfolds enters, you may plot a card from your hand. / Whenever you cast a spell from exile, you get `OO`." Note the trigger is **cast-from-exile**, not "whenever you plot" — so it also pays off Escape (`MR01`, `MZ07`), impulse draw (`RZ05`, `MZ06`) and Gruul's exile-cast cards. Enables *and* rewards, and reads as playable to three archetypes. | exile-cast → `O` | Proposed |
| 4.17 | `UR18` Sith Apprentice's Talent | **Modify.** `2R` Class. ETB unchanged (2 damage to any target). Level 2 `2R` → `1R`: "Creatures you control have haste." Level 3 `2RR` → `3RR`: "When this class becomes level 3, if you have four or more `O`, there is an additional combat phase after this phase, followed by an additional main phase." Drop the self-sacrifice clause. Deliberately, **Level 2 touches `O` not at all** — not every line needs the resource. | threshold (capstone) | Proposed |
| 4.18 | `UZ05` Shadow Collective Commando | **Redesign — the BR signpost, which currently says nothing about the archetype.** `1BR` 1/2 double strike + anthem + death-ping → `1BR` 2/2 Creature — Human Sith Warrior, menace. "If you would get one or more `O`, you get that much plus one instead. / `OOOO`: Shadow Collective Commando gets +3/+0 and gains deathtouch and lifelink until end of turn." A replacement effect that makes *every other `O` card in the set better* — which is what a signpost is for — plus a sink for the surplus it creates. | doubler + sink | Proposed |

### 2.3 Rares and mythics

Light touch. Mythics aren't what teaches a drafter an archetype, so these remove
dead tribal gating and aristocrats text rather than rebuilding.

| # | Card | Change | Status |
|---|---|---|---|
| 4.19 | `RB07` Hateful Tutor | **Cut** (Rare, black). Sith tribal gating — the thing this pass removes — and a tutor makes draft games same-y at rare. | Proposed |
| 4.20 | *The Dark Side Clouds Everything* (new) | **Add** (Rare, black) — replaces 4.19. `2B` Enchantment. "`1B`: You get `O`. Activate only as a sorcery, and only once each turn. / At the beginning of your end step, if you have five or more `O`, each opponent loses 2 life and you draw a card." The engine that makes *hoarding* a strategy — its payoff actively punishes you for dumping corruption into 4.2 or 4.8. This is the tension in §1.1 printed on one card. | Proposed |
| 4.21 | `RB08` Sith Lord's Talent | **Modify.** `1B` Class. Base: "When Sith Lord's Talent enters, you get `OO`." Level 2 `B` → `1B`, drop the Sith gating: "As long as you have four or more `O`, creatures you control have menace and deathtouch." Level 3 `4B`: "`OOOO`: Destroy target creature. Its controller loses 2 life." Burst, threshold and sink on one card — appropriate complexity at rare, and no line duplicates another card. | Proposed |
| 4.22 | `RA01` Ancient Sith Holocron | **Modify.** Drop the Sith gating: "When Ancient Sith Holocron enters, you get `OO`. / `T`, Sacrifice Ancient Sith Holocron: Add `BR`. Draw a card if you have four or more `O`." **Stays colourless** — reversing the previous draft, which recoloured it to `1B` to de-feed Azorius. A colourless `O` source is exactly the kind of card any deck splashing into Rakdos should be able to take, and §2.4 says that's a feature. | Proposed |
| 4.23 | `RB02` Sith Amulet | **Modify.** Add one line: "As long as you have four or more `O`, equipped creature also has deathtouch." Equip cost and existing text unchanged. | Proposed |
| 4.24 | `RZ22` Throne Room Massacre | **Modify.** The "4 damage to another target battle" clause is dead once §3 ships. "When this card enters, choose one — • It deals 3 damage to any target • You get `OOO`." Tempo or fuel, your call. | Proposed |
| 4.25 | `MB01` Darth Sidious, Lord of the Sith | **Modify, minimally.** `[+1]` "Draw a card and you lose 1 life" → "Draw a card, you lose 1 life, and you get `O`." The plot-everything static is the best plot payoff in the set and is untouched. ⚠ Separately, `[+2]` "Target opponent **may** Contract 1" is broken templating — the opponent choosing whether to be bountied makes the ability optional for them. Needs a rewrite regardless of this pass. | Proposed |
| 4.26 | `MZ06` Darth Tyranus, Patient Orchestrator | **Modify.** Replace the sacrifice activation with "`OOO`: Each opponent loses 3 life and you gain 3 life. Then exile the top three cards of your library. You may play them until the end of your next turn." Keeps drain-plus-impulse, drops the aristocrats cost. Plot `2BR` unchanged. | Proposed |
| 4.27 | `MR01` Darth Vader, Twisted By Fear | **No change.** Plot → `O`, `OO` to trigger the attack ability, Escape. Already exactly the card this pass is designing toward. | Proposed |
| 4.28 | `MB03` Jedi Blindness | **No change.** Pure threshold design at two tiers — the model for §1.1. Recorded so its absence from the change list reads as deliberate. | Proposed |
| 4.29 | `MB04` Tragedy of Darth Plagueis | **No change — deliberate exception.** Chapter II is death-matters and survives the purge. The card is *about* Plagueis cheating death; the flavour is load-bearing and one mythic saga doesn't teach drafters that Rakdos is an aristocrats deck. | Proposed |
| 4.30 | `MZ14` Order 66 | **Retag only.** `5WB` with no Sith mechanic — primary Sith → Coruscant-Orzhov, secondary Sith. **`Plot 7WB` unchanged** (see §1.2). | Proposed |
| 4.31 | `RZ16` Revival | **Retag only.** `BRG` reanimation saga is Golgari's mechanic; swap primary/secondary to Geonosis primary, Sith secondary. It stays a genuine bridge card — this only fixes which budget it counts against. | Proposed |

### 2.4 Containment — keeping `O` in black and red

| # | Card | Change | Status |
|---|---|---|---|
| 4.32 | `UG18` Clan Viszla | **Modify** (Uncommon, green, Gruul). "…you may pay `1G`, when you do, add `O`…" → "…when you do, create a Treasure token. If you control another outlaw, Contract 1 and put a +1/+1 counter on target outlaw you control." A green card shouldn't *mint* the Sith resource; Gruul already owns Treasure and Contract. | Proposed |
| 4.33 | `CR02` Immoral General | **Withdrawn — superseded by 4.8, which cuts the card outright.** Number retained so the rest of the list doesn't shift. | Withdrawn |
| 4.34 | `CB14` Galactic Disturbance | **Modify** (Common, black, Glue). Second mode "Sacrifice a creature, then create a 2/2 Battle Droid…" → "Target opponent discards a card, then create a 2/2 black Battle Droid artifact creature token and you get `OO`." Removes the last sacrifice cost at common, and makes the mode a card both Rakdos and Dimir want. | Proposed |

`MZ05` Darth Maul (Golgari mythic) *spends* `O` and is left alone. Spending
across archetypes is healthy overlap; minting in a third colour is not.

---

## 3. Dimir — Separatist Scheming

### 3.1 The reposition

> **Dimir keeps "committing war crimes" and "the more you learn, the more you
> control." It drops "manipulating battles."**

Battles stay in the set as the ten-guild Duel signpost cycle plus the Sieges —
they work fine in that role. What changes is that **no Dimir common depends on
one**, and the archetype stops advertising battles as its plan.

I'm not proposing battles at common. Your playtest read was that battles don't
affect the board enough; printing more of them at the rarity that defines the
format treats the symptom's symptom. The alternative pass is in §5 if you'd
rather keep the battle plan.

### 3.2 Commons

| # | Card | Change | Track role | Status |
|---|---|---|---|---|
| 4.35 | `CU01` Techno Service Droid | **Modify.** `U` 1/1 Creature — Droid Spy. Drop the defense-counter ETB (100% dead text). "Techno Service Droid can't be blocked as long as defending player has two or fewer cards in hand." Fills the blue half of the MV-1 hole (`notes.md` §6.3) with a body that gets *better* as the game goes long even without the discard plan. Stays a Droid — Azorius bridge. | threshold | Proposed |
| 4.36 | `CU03` Separatist Infiltrators | **Modify.** `1U` 1/1 Creature — Droid Spy. Strip "or battle". "Separatist Infiltrators can't be blocked. / Whenever Separatist Infiltrators deals combat damage to a player, that player discards a card." Unblockable so a 1/1 actually connects; the payoff feeds every threshold below. | enabler | Proposed |
| 4.37 | `CU04` Trade Federation Officer | **Modify.** `2U` 1/3 → 2/3 Creature — Neimoidian Rogue, vigilance. Drop the dig-for-a-battle ETB (100% dead text). "Vigilance. / When Trade Federation Officer enters, look at target opponent's hand. You may put a card from it on the bottom of their library." Deliberately **not** discard — it denies Golgari and Geonosis the graveyard, so it's a different card in a different matchup. | enabler | Proposed |
| 4.38 | `CB04` Weequay Pirate | **Modify.** `2B` 2/2 → 3/2 Creature — Pirate Rogue, menace. Drop the end-step Treasure trigger (Treasure is Gruul's currency) and "or battle". "Menace. / As long as an opponent has two or fewer cards in hand, Weequay Pirate gets +1/+1 and has deathtouch." | threshold | Proposed |
| 4.39 | `CB10` Sabotage Mission | **Modify.** `2B` Instant, drop the battle cost-reduction. "Target creature gets -3/-3 until end of turn. If an opponent discarded a card this turn, draw a card." The intentional parallel to 4.4 — two 2-mana black removal commons, one scaling off `O` and one off discard, both playable in either archetype. | threshold | Proposed |
| 4.40 | `CB08` Banking Clan Enforcer | **Modify.** `3BB` 4/5 → `3B` 4/4 Creature — Alien Noble. "When Banking Clan Enforcer enters, target opponent discards a card. / Cycling `2`." ⚠ Also fixes a data error: this card's `Mechanic` column reads **Contract** and the rules text contains no contract. | enabler | Proposed |
| 4.41 | `CA02` Credit Vault | **Cut** (Common, colourless). Tagged Dimir, but its trigger is lifegain (Orzhov) and its payoff is Contract (Gruul) — two other archetypes' mechanics and zero Dimir text. Also a generic colourless artifact feeding Azorius per `notes.md` §6.5. | — | Proposed |
| 4.42 | *Pyke Informant* (new) | **Add** (Common, **black**) — replaces 4.41. `B` 1/1 Creature — Human Rogue. "Deathtouch. / When Pyke Informant enters, look at target opponent's hand." Fills the black half of the MV-1 hole with a body that's board-relevant on turn one and turn ten (a 1/1 deathtouch trades with anything), and is a fine pickup for any black deck. ⚠ **Colour deviation:** moves a slot colourless → black rather than matching. Justified by §6.5 but flagged, not hidden. | enabler | Proposed |

### 3.3 Uncommons

| # | Card | Change | Status |
|---|---|---|---|
| 4.43 | `UZ03` Nute Gunray, Trade Viceroy | **Redesign — the UB signpost, and both its abilities are battle-only.** `2UB` 2/3 Legendary Creature — Neimoidian Noble. "Whenever an opponent discards a card, that player loses 1 life and you get `O`. This ability triggers only once each turn. / As long as an opponent has one or fewer cards in hand, creatures you control can't be blocked." A real win condition on the signpost: empty their hand, your team goes unanswerable. It also mints `O` off Dimir's plan, which is the seam. ⚠ Power flag — "can't be blocked" for the whole team is a big grant; the "one or fewer" gate is what holds it, and that gate should be tested before it ships. | Proposed |
| 4.44 | `UU05` Separatist Saboteur | **Cut** (Uncommon, blue). "Move two defense counters from one battle to another" — blank unless *two* battles are on the table. Unsalvageable. | Proposed |
| 4.45 | *Separatist Spy Network* (new) | **Add** (Uncommon, blue) — replaces 4.44. `2U` Enchantment. "Whenever a creature you control deals combat damage to a player, that player discards a card. This ability triggers only once each turn. / As long as an opponent has two or fewer cards in hand, creatures you control get +1/+1." Converts the unblockable bodies into a clock and closes the loop from evasion → discard → bigger evasion. | Proposed |
| 4.46 | `UU11` Trade Federation Blockade | **Modify.** `2U` Enchantment, drop the battle-transformed trigger and the +0/+1. "Creatures you control can't be blocked by creatures with power 3 or greater. / Whenever an opponent discards a card, put a +1/+1 counter on target creature you control. This ability triggers only once each turn." Turns a defensive card into the aggressive evasion anthem the archetype actually wants. | Proposed |
| 4.47 | `UU14` Tactical Retreat | **Modify.** `1U` Instant. "Return target battle or craft to its owner's hand" — both nouns dead or another guild's. "Return target creature to its owner's hand. If its controller has four or more cards in hand, they discard a card." A 2-mana bounce in any blue deck; a punisher for hoarding in Dimir. | Proposed |
| 4.48 | `UB07` IG-100 MagnaGuard | **Modify.** `2BB` 3/2 → `2B` 3/2 Artifact Creature — Droid Warrior. Both battle clauses removed. "Menace. / When IG-100 MagnaGuard enters, target opponent discards a card. Then if that player has one or fewer cards in hand, destroy target creature they control." This is the direct answer to "the deck didn't impact the board enough" — real removal, gated behind the archetype's own plan. Stays a Droid for the Azorius bridge. | Proposed |
| 4.49 | `UB12` Separatist Intelligence Network | **Modify — the Rakdos seam card.** `1B` Enchantment. "Whenever an opponent discards a card, you get `O`. This ability triggers only once each turn. / `2B`, Sacrifice Separatist Intelligence Network: Target opponent reveals their hand. You choose a nonland card from it. Exile that card." Mints Rakdos's resource off Dimir's plan and cashes out as a hand strip. One card doing the overlap, rather than a trigger word stamped on twelve. | Proposed |
| 4.50 | `UB15` Dooku's Manipulation | **Modify.** `4BB` → `3B` Sorcery. "Return target battle or craft from a graveyard" → "Return target creature card or artifact card from **a** graveyard to the battlefield under your control. You get `OO`." Stealing from *any* graveyard is flavour-perfect for Dooku, and makes it a Golgari and Geonosis pickup as well. | Proposed |
| 4.51 | `UB18` Separatist's Talent | **Modify.** `1B` Class. Base unchanged. Level 2 `1B`: "Whenever an opponent discards a card, that player loses 2 life. This ability triggers only once each turn." Level 3 `4BB` → `3BB`: "At the beginning of your upkeep, target opponent reveals their hand. You choose a nonland card from it. That player discards that card." | Proposed |
| 4.52 | `UB16` Palpatine's Revelation | **No change.** Its `Plot 2BB` on a `3BB` card is the *below-cost* rung of the §1.2 ladder — a situational card bribed into being plotted for mana smoothing. Correct as printed. | Proposed |
| 4.53 | `UU17` Battle of Anaxes / `UZ12` Revelation of the Sith | **No change.** Dimir keeps its two battles as flavour anchors. They're now simply good cards rather than engine pieces nothing else can find. | Proposed |

### 3.4 Rares and mythics

| # | Card | Change | Status |
|---|---|---|---|
| 4.54 | `RB03` Count Dooku, Separatist Leader | **Redesign.** Currently `1B` **3/4** whose every ability is battle-gated — an oversized two-drop that does nothing. `1B` 2/3 Legendary Creature — Human Sith Noble. "Ward—Discard a card. / `OO`: Target opponent discards a card. Activate only as a sorcery." Deliberately a **pure `O` sink that mints none** — he's the card that makes a UB drafter want a Rakdos partner, and he's typed Sith Noble already. | Proposed |
| 4.55 | `MZ03` Admiral Trench, Cunning General | **Modify.** Combat-damage modes → "choose one — • That player discards a card • Draw a card • Target creature gets -3/-3 until end of turn". Removes "or battle" and the defense-counter mode. Deathtouch, lifelink and the surveil trigger unchanged. | Proposed |
| 4.56 | `RU03` Jedi Temple Guard | **Retheme only**, no rules change. A card named *Jedi Temple Guard*, typed Creature — Jedi Soldier, tagged Dimir, reads as Simic or Selesnya in the pack whatever its text says. Rename to *Separatist Sleeper Agent*, retype Creature — Human Rogue. Same argument as Pass 2's 2.6 — and note 2.6 was applied without the type-line change (`CHANGELOG` 3.5), which is exactly why it didn't work. **Change the type line this time.** | Proposed |
| 4.57 | `RB05` Vulture Class Starfighter | **Retag only.** Craft with `scrap 2` — Golgari/Boros mechanics — tagged Dimir primary. Swap to Geonosis-Golgari primary, Separatist secondary. | Proposed |
| 4.58 | `RZ14` / `RZ19` (`WUB`) | **Retag only.** Three-colour Esper cards tagged Dimir primary; neither is castable in a two-colour Dimir deck. Retag primary Coruscant-Orzhov, secondary Separatist. This is a measurement fix — they currently inflate Dimir's weighted playable count with cards Dimir cannot cast. | Proposed |
| 4.59 | `RZ03` Invisible Hand / `MB02` Trade Federation Battleship | **No change.** Both are scrap/craft cards in Dimir, mechanically Golgari's. Left alone because the Separatist flagships are non-negotiable flavour and two rare/mythic bridges don't distort a drafter's read. Recorded so the inconsistency is deliberate. | Proposed |

---

## 4. Ledger

### 4.1 Swaps (all same rarity)

| Rarity | Cut | Add | Colour |
|---|---|---|---|
| Common | `CR02` Immoral General (R) | *Vent Your Anger* (R) | matched |
| Common | `CA02` Credit Vault (colourless) | *Pyke Informant* (B) | ⚠ colourless → black |
| Uncommon | `UR09` Army of the Dead (R) | *The Plan Unfolds* (R) | matched |
| Uncommon | `UU05` Separatist Saboteur (U) | *Separatist Spy Network* (U) | matched |
| Rare | `RB07` Hateful Tutor (B) | *The Dark Side Clouds Everything* (B) | matched |

Set size unchanged: 2 common, 2 uncommon, 1 rare. Everything else is a
modification, retag or retheme — free under §2.3.

`CR13` Separatist Bombardment is **no longer a cut** (4.7) — it is the set's
token-management common and is retained via modification.

**Practical note for the MSE/Sheets sync:** the `CR02` → *Vent Your Anger* swap
can be executed as an in-place rename and retype of the `CR02` slot rather than
a delete-plus-create, the way `CHANGELOG` 3.3 handled Meandering Bantha →
Sparring Padawan. Same for `CA02` → *Pyke Informant*. Given how finicky the two
sides are to reconcile, that's the lower-risk path.

### 4.2 Mechanic movement

| | Before | After |
|---|---|---|
| Rule of Two | 4 cards | **0 — retired** |
| Morbid | 4 riders | **0 — retired** (3 rewritten, 1 cut with `CR02`) |
| Sacrifice as a cost, Rakdos | 8 cards | 0 at common, 0 at uncommon |
| `O` payoffs at common | **0** | **5** (3 threshold, 2 sink) |
| `O` minted outside B/R | 1 (`UG18`, green) | **0** |
| Colour-pie breaks gated on `O` | 1 (`MB03`, mythic only) | 3 (`MB03`, `UB14`, `UB05`) |
| Mono-coloured non-legendary Jedi | 1 (`CR02`, red, common) | **0** |
| Death-triggered `O` | 9 of 17 | 1 (`UB08`), re-pointed to *opponents'* creatures dying |
| Dimir cards needing a battle | 18 of 29 | 2 (`UU17`, `UZ12` — both *are* battles) |
| Battles at common | 0 | 0 (unchanged — deliberately) |

### 4.3 Design-repetition check

The failure mode of the previous draft, measured. No `O` or discard interaction
appears more than twice across the 30 redesigned cards:

| Mechanism | Cards |
|---|---|
| ETB / one-shot `O` burst | `CB01`, `RA01`, `RB08` |
| Conditional burst on what you hit | `CB12` |
| Life → `O` | `UB01` |
| Opponent's creature dies → `O` | `UB08` |
| Cast-from-exile → `O` | *The Plan Unfolds* |
| Plot-cash burst | `CR05`, `UB05`, `UR05` |
| Opponent discards → `O` | `UB12`, `UZ03` |
| Repeatable slow faucet | *The Dark Side Clouds Everything* |
| `O` doubler | `UZ05` |
| Threshold → stats | `CB01`, `CR07`, `CB04` |
| Threshold → modal escalation | `CR13` |
| Threshold → effect scaling | `CB13` |
| Hard gate → colour-pie break | `UB14`, `UB05`, (`MB03`, unchanged) |
| Threshold → cost reduction | `UR08` |
| Threshold → keyword grant | `RB02`, `RB08` L2, `CU01`, `UB07` |
| Threshold → extra combat | `UR18` L3 |
| Threshold → hold-at-five payoff | *The Dark Side Clouds Everything* |
| Sink → grow a creature | `CB03` |
| Sink → X damage | *Vent Your Anger* |
| Sink → repeatable removal / discard | `RB08` L3, `RB03` |
| `O` count as X | `UR05` |

### 4.4 Multi-archetype reach

Cards from this pass a **non-Rakdos, non-Dimir** drafter would still play:

| Card | Also wanted by |
|---|---|
| `CB03` Apprentice of the Dark Side | any black deck (2-drop with a mana sink) |
| `CB12` Intercept Beacon Transmissions | Dimir, Orzhov, Golgari |
| `CB13` Drain the Living Force | any black deck |
| `CR05` Warmonger's Fodder | any red deck (3/2 haste for 3) |
| `CR07` Coruscanti Protestor | any red deck (3/3 menace for 3) |
| `CR13` Separatist Bombardment | any red deck; the modal token sweep is a Selesnya/Republic answer |
| *Vent Your Anger* | any red deck (2-mana Shock-plus) — it inherits `CR02`'s Glue role |
| `UB14` Is that legal? | any black deck willing to splash the `OO` — a wrath is a wrath |
| `UB01` Nightsister Initiate | Orzhov, Coruscant (life as a cost) |
| `UB08` Maul, Broken by Hatred | any black deck (4/5 for 5 + unique removal) |
| `UB15` Dooku's Manipulation | Golgari, Geonosis (steals from any graveyard) |
| *The Plan Unfolds* | Gruul, Golgari (Escape and impulse draw) |
| `RA01` Ancient Sith Holocron | any deck splashing (kept colourless) |
| `CU01` / `CU03` / `UB07` | Azorius (all still Droids) |
| `CU04` Trade Federation Officer | any blue deck; specifically anti-Golgari |
| `CB10` Sabotage Mission | any black deck |
| *Pyke Informant* | any black deck |

⚠ **State the model's limit.** These are directional. The archetype tagging —
especially `Secondary Archetype`, which is un-normalised per `CLAUDE.md` §2.9 —
is a heuristic, and 4.57/4.58 exist precisely because tagging errors were
inflating Dimir's count with uncastable cards. Re-run `curve_audit.py` after
applying; don't trust the deltas to the unit.

### 4.5 Finding a home for *Vent Your Anger*

The set has 15 red commons. Most are unavailable as cuts for good reasons:

| Cards | Why not |
|---|---|
| `CR05`, `CR07`, `CR13` | Rakdos — load-bearing in §2.1, and `CR13` is the token answer |
| `CR06`, `CR12`, `CR14` | Izzet — the most starved archetype in the set (`notes.md` §6.2) |
| `CR09`, `CR10` | Boros — `CR09` is a Craft, `CR10` is the set's common artifact removal |
| `CR03`, `CR04`, `CR08`, `CR11` | Gruul — `CLAUDE.md` §7 says don't touch Gruul on v2 data |
| `CR15` | Gruul, but already slated for cutting by Pass 2's **2.10** |
| `CR01` | Glue — renamed and re-arted one pass ago (`CHANGELOG` 3.4), and it's Izzet's MV-1 prowess body from Pass 2's **2.5** |
| **`CR02`** | **Glue — the cut** |

**Why `CR02` Immoral General.** `1R` 2/2 Creature — Rogue Jedi, menace, *"When
Immoral General enters, if a creature died this turn, you get `O`."*

1. **Its only text is a Morbid rider**, and Morbid is one of the two mechanics
   this pass retires outright. Cutting it makes the retirement a clean removal
   rather than a rewrite — and it lets 4.33 be withdrawn, so the pass gets
   *smaller*.
2. **The type line misfires, and it's the only one that does.** `CR02` is the
   set's **only mono-coloured, non-legendary Jedi**. Every other off-colour Jedi
   is a legendary character where the type is real flavour work — Obi-Wan,
   Ahsoka, Yoda, Mace Windu, Qui-Gon. `CR02` is a *common*, so it's ×2 in the
   pool, and Selesnya's Jedi-matters cards count it: `CW01` Clone Trooper
   Regiment (common), `UG06` Clone Lieutenant Waxer, `RZ17`, `RR10`. A red
   common quietly propping up Selesnya's tribal count is the same bug class as
   Pass 2's **2.6** and 4.56 in this pass.
3. **No archetype loses a designed card.** Archetype is Glue, Secondary is
   blank. And the Glue *function* survives — every red deck plays a 2-mana
   Shock-plus, so the "everyone takes it" slot is preserved, just as removal
   rather than as a body.
4. **It moves the set toward its own stated target.** `CLAUDE.md` §7 wants
   common removal at 12–15% and it currently sits near 7%. Trading a 2/2 menace
   for a scaling removal spell is exactly that direction. Trading the *fish* for
   it would not have been — that swap cost the set its only red mana creature
   and bought no extra body.
5. **Same colour, same mana value, no curve movement.** `1R` → `1R`.

**`CR03` Patrolian Robot Fish is retained**, unchanged. Nothing else in the pass
moves as a result of this — 4.7 (`CR13` kept via modification) and every other
item stand exactly as written.

⚠ **One interaction still worth watching**, unrelated to this cut. Pass 2's
**2.10 / 2.11** — cut `CR15` Twin Blaster Showdown, add *Double Blaster Volley*
— are still **Proposed** and were not in the Pass 3 applied list; `CR15` is
still in the dump. If 2.10 lands, Gruul's red common count goes 5 → 4, since
2.11's replacement is an Izzet card. That's survivable, but it is the only
remaining pressure on Gruul's red half and the two proposals are easier to judge
together than in sequence.

---

## 5. What this pass deliberately does *not* do

- **No battles at common.** If you'd rather keep the battle plan, the
  alternative is: cut two Dimir uncommons for two common Sieges with
  board-affecting ETBs, and accept that Dimir still competes with nine other
  archetypes for the Duel cycle. I don't recommend it.
- **No Gruul changes beyond `UG18`.** `CLAUDE.md` §7 says don't "fix" Gruul on
  v2 data; `UG18` moves only because it mints `O` in green.
- **Selesnya's answering-removal question is now partly answered, but not
  closed.** Three cheap black/red removal commons (4.4, 4.8, 4.39) plus `CR13`'s
  modal token sweep (4.7) plus `UB14`'s wrath (4.12) all push the right way —
  but every one of those lives in black or red. `notes.md` §6.4's ask for a
  common sweeper that *any* deck can cast still needs its own cut picked.
- **No renames or re-art** except 4.56, where the name and type line *are* the bug.

---

## 6. Open questions for Jack

1. **4.43 `UZ03`** — "as long as an opponent has one or fewer cards in hand,
   creatures you control can't be blocked" is the biggest swing in the batch.
   Is an empty-hand gate enough of a brake, or should it be menace instead of
   unblockable?
2. **4.18 `UZ05`** — an `O` doubler on an uncommon signpost makes every other
   `O` card better, which is the point, but it's also the card most likely to be
   a first-pick-and-force. Worth watching in the first v3 draft.
3. **4.42** — is the colourless → black common swap acceptable, or would you
   rather keep `CA02` as a colourless artifact (modified to have actual Dimir
   text) and fix the black MV-1 hole from a different slot?
4. **Threshold numbers.** I've used 3 and 4 as the two tiers, with two cards at
   5 (`UB05`, *The Dark Side Clouds Everything*). If v3 shows corruption
   accumulating faster than expected, the lever is to raise tiers rather than to
   weaken the payoffs — raising a number is a one-cell edit in Sheets,
   redesigning a payoff isn't.
5. **4.12 `UB14` power dial.** An instant-speed wrath at `2BB` + `OO` is the
   strongest card in this batch. If it warps games, **raise the gate to `OOO`
   before raising the mana cost.** Raising the gate keeps it a card only a
   committed Rakdos deck can cast, which is the design intent; raising the mana
   cost just makes it worse for everyone and pushes it out of the format.
6. **Where else should the pie break?** §1.3 is your idea and it generalises
   further than this pass uses it. `MB03` (hexproof + flash) and now `UB14`
   (instant wrath) and `UB05` (artifact/enchantment destruction) are all black.
   The obvious unclaimed one is **red**: unconditional destruction or exile,
   rather than damage, gated on `O` — red can't kill an indestructible or
   high-toughness creature and the Dark Side is a good reason it suddenly can.
   Deliberately not designed here to stay scoped; flagging it as the next
   place to look.
