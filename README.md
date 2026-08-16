# The Clone Wars MTG Cube

Hi everyone, welcome to the repository for my Star Wars the Clone Wars themed MTG cube. The cube consists of 540 cards (enough for 36 15 card packs). It contains 80 commons printed 2x, 110 uncommons printed 2x, 86 rares, 38 mythic rares, and 36 lands. I am a one man show here. I started this project because I love the Clone Wars and I love Magic the Gathering! If you too like both of these things, you'll be certain to like this set! Many thanks to my friends who have helped me playtest this set numerous times while we tweaked it to get it just right. I'm proud to announce that I am releasing all of the cards for the set free of charge. I hope people enjoy it as much as I have. That said, if you do insist on showing your appreciation, you can buy me a coffee via Venmo. (Don't see my venmo here? Send me an email at `jbrzozo24@gmail.com` with the title `Clone Wars MTG set` and I will get back to you!)

## How do I get the cube?

If you have Magic Set Editor, open up `TheCloneWars.mse-set` and export it however you like. `Tokens.mse-set` contains the relevant tokens as well, if you want the full experience.

No MSE? No problem! The repo contains PDF exports for all of the cards you'll need to create the set. I recommend printing at your local UPS store, and sleeving the cube card with a real MTG card behind it. You will want to buy some draft chaff ;).

## Archetypes

- `{WU} DROID ARTIFACT EFFICIENCY` - Build an efficient army of utility droids that grow stronger together. Create tokens, activate abilities, move counters between droids, and generate value through tight artifact synergies.
- `{WB} CORUSCANT CORRUPTION` - Wield Powerful Nobles who, as a result of their power, enter with a target on their back. Cast above-rate creatures, and stay on the front foot to avoid an opponent reaping the benefits of cashing in on your bounties. Manipulate life totals to gain political advantage. Pay life for powerful effects, then drain opponents to recover. In Coruscant, everything has a price.
- `{UB} SEPARATIST SCHEMING` - Control the war by manipulating battles and committing war crimes. Your band of nobility and outlaws will seek to orchestrate the Clone Wars in your favor. The more you learn, the more you control.
- `{UR} KAMINOAN CLONING` - Cast instants and sorceries to mass-produce clone troopers with prowess. Cast multiple spells in a single turn to bend clones to their genetic programming. Copy spells to make more clones, then use spells to pump your army. Each spell makes you stronger, and gives you more control.
- `{BR} SITH PLOTTING` - Dastardly plots pave the way for massive turns. Commit crimes and expend the weak to fuel the dark side, leading to many abilities that some consider to be... unnatural.
- `{BG} GRAVEYARD SCRAP` - Battle Droids that just keep coming. Sacrifice fodder to build more formidable crafts, and use your graveyard as a means to escape from sticky situations. Every destroyed droid fuels the next wave.
- `{RG} CONTRACTED FURY` - Place bounties on creatures, attack aggressively, and profit when they die. Commit crimes and build a band of outlaws to stake a claim in the outer rim. Generate Treasure tokens to fuel bigger threats. Every death pays dividends.
- `{RW} SCRAP & CRAFT` - Sacrifice artifacts to charge up Crafts and turn them into powerful creatures. Generate Scrap tokens, build crafts from the junk, and reward yourself for every piece of scrap metal you feed into the machine.
- `{GW} REPUBLIC GO WIDE` - "Together We Are Unstoppable" - Deploy legendary Clone commanders alongside Jedi generals. Go wide with Clone Trooper tokens, then use strategic buffs and synergies to overwhelm opponents. Leadership matters.
- `{GU} JEDI CONTROL` - "There is No Emotion, There is Peace" - Master the Force to control the battlefield. Generate Light Side Counters to tap opponent's permanents, untap your own, and manipulate combat. Each Force manipulation builds toward an overwhelming advantage.

## Finding the Card Backside

Some cards are DFCs. Look for the card code in the bottom left of the card to find the matching backside. `UW17` would matchup with something like `UW17B` or `UW17B_0`.

# Developer Instructions

## Set Builder Instructions

You'll need to set up google_auth in mse_set_builder_app/google_auth, follow the readme in mse_set_builder_app.

``` bash
cd $STEM
git clone git@github.com:jbrzozo24/magic_the_gathering_projects.git
cd magic_the_gathering_projects/src/mse_set_builder_app/
./set_builder.py -v # The defaults are correct already
```

## Set Version 3.0
This is the set after the first two draft playtests covering half of the set.