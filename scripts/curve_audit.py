#!/usr/bin/env python3
"""
curve_audit.py - archetype tagging + mana curve audit for The Clone Wars set.

Reads the Cards tab (xlsx or csv), tags every front face with each archetype it
would be *good* in, and writes a self-contained interactive HTML report.

Usage
-----
    python curve_audit.py Custom_Set_Cards.xlsx
    python curve_audit.py cards.csv --out docs/curve-audit.html --tags-out tags.csv
    python curve_audit.py Custom_Set_Cards.xlsx --overrides tag_overrides.csv

Requires: pandas, and openpyxl if the input is .xlsx.

Tagging model
-------------
A card is tagged into an archetype if any of these hold:

  designed   its `Archetype` column names that archetype
  secondary  its `Secondary Archetype` column names that archetype
  generic    the archetype's colours can cast it, AND the card carries no
             mechanical hook belonging to a *different* castable archetype

Hooks are regexes matched against Rules Text + Mechanic + Subtype + Type + Name.
They are the knob most worth tuning as the set evolves - see HOOKS below.
When the heuristic gets a specific card wrong, prefer --overrides over editing
HOOKS, so that human judgement stays visible in version control.

Lands are excluded from the curves (they'd all pile up at MV 0).
Weighting: commons and uncommons count twice, rares and mythics once.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

# --------------------------------------------------------------------------
# configuration
# --------------------------------------------------------------------------

# archetype -> (colour pair, short name)
ARCHETYPES = {
    'Republic - Selesnya':    ('GW', 'Selesnya'),
    'Coruscant - Orzhov':     ('WB', 'Orzhov'),
    'Droids - Azorius':       ('WU', 'Azorius'),
    'Separatist - Dimir':     ('UB', 'Dimir'),
    'Jedi - Simic':           ('GU', 'Simic'),
    'Kamino - Izzet':         ('UR', 'Izzet'),
    'Sith - Rakdos':          ('BR', 'Rakdos'),
    'Geonosis - Golgari':     ('BG', 'Golgari'),
    'Bounty Hunters - Gruul': ('RG', 'Gruul'),
    'Tatooine - Boros':       ('RW', 'Boros'),
}

RARITY_WEIGHT = {'Common': 2, 'Uncommon': 2, 'Rare': 1, 'Mythic Rare': 1, 'Mythic': 1}
DEFAULT_WEIGHT = 1

MAX_MV = 7  # everything at or above this is bucketed into "7+"

# free-text -> canonical archetype, for the messy Secondary Archetype column
ALIASES = {
    'selesnya': 'Republic - Selesnya', 'republic': 'Republic - Selesnya',
    'orzhov': 'Coruscant - Orzhov', 'coruscant': 'Coruscant - Orzhov',
    'azorius': 'Droids - Azorius', 'droids': 'Droids - Azorius',
    'droid': 'Droids - Azorius',
    'dimir': 'Separatist - Dimir', 'separatist': 'Separatist - Dimir',
    'separatists': 'Separatist - Dimir',
    'simic': 'Jedi - Simic', 'jedi': 'Jedi - Simic',
    'izzet': 'Kamino - Izzet', 'kamino': 'Kamino - Izzet',
    'rakdos': 'Sith - Rakdos', 'sith': 'Sith - Rakdos',
    'dark side': 'Sith - Rakdos',
    'golgari': 'Geonosis - Golgari', 'geonosis': 'Geonosis - Golgari',
    'gruul': 'Bounty Hunters - Gruul', 'bounty hunters': 'Bounty Hunters - Gruul',
    'outlaws': 'Bounty Hunters - Gruul',
    'boros': 'Tatooine - Boros', 'tatooine': 'Tatooine - Boros',
    'tatooine scrap': 'Tatooine - Boros',
}

# (regex, archetypes it tethers a card to)
HOOKS = [
    (r'\bsquad\b|clone trooper|\bclones?\b',
     ['Republic - Selesnya', 'Droids - Azorius']),
    (r'gain \d+ life|whenever you gain life|lifelink|\bnoble\b|\bsenator\b',
     ['Coruscant - Orzhov']),
    (r'\bdroid\b|whenever an artifact|another artifact enters|artifacts you control',
     ['Droids - Azorius']),
    (r'\bmills?\b|\binfiltrat|battle droid|from among them',
     ['Separatist - Dimir']),
    (r'\bjedi\b|light side|\bO{1,4}\b',
     ['Jedi - Simic']),
    (r'\bcopy\b|copies|instant or sorcery spell|second spell|noncreature spell|\bprowess\b',
     ['Kamino - Izzet']),
    (r'\bsith\b|dark side|sacrifice a creature',
     ['Sith - Rakdos']),
    (r'when(ever)? .{0,40}dies',
     ['Sith - Rakdos', 'Geonosis - Golgari']),
    (r'graveyard|\bendure\b|\bescape\b|geonosian|\bmorbid\b',
     ['Geonosis - Golgari']),
    (r'\bcontract\b|bounty counter|\boutlaw|commit a crime|treasure',
     ['Bounty Hunters - Gruul']),
    (r'\bscrap\b|charge counter|\bcraft\b|\bequip\b',
     ['Tatooine - Boros']),
]

REQUIRED_COLUMNS = ['Card Code', 'Card Name', 'Status', 'Color', 'Rarity',
                    'Archetype', 'CMC', 'Type']

MANA_HEX = {'W': '#F2E7CE', 'U': '#4FA3D1', 'B': '#8C7C98',
            'R': '#D9553F', 'G': '#5DA05A'}


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------

def load_cards(path, sheet, max_rows):
    if path.suffix.lower() in ('.xlsx', '.xlsm'):
        df = pd.read_excel(path, sheet_name=sheet)
    elif path.suffix.lower() in ('.csv', '.tsv'):
        df = pd.read_csv(path, sep='\t' if path.suffix.lower() == '.tsv' else ',')
    else:
        sys.exit(f'unsupported input type: {path.suffix}')

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        sys.exit(f'missing required column(s): {", ".join(missing)}\n'
                 f'found: {", ".join(map(str, df.columns))}')

    if max_rows:
        df = df.iloc[:max_rows]
    df = df[df['Card Code'].notna()]
    # back faces of DFCs are marked by Status, not reliably by card code suffix
    df = df[df['Status'] != 'Backside']
    return df.copy()


def load_overrides(path):
    """Optional CSV: Card Code,Archetypes  where Archetypes is ';'-separated.

    An override *replaces* the computed tag set for that card. Use it when you
    disagree with the heuristic; an empty Archetypes cell removes all tags.
    """
    if not path:
        return {}
    ov = pd.read_csv(path)
    for col in ('Card Code', 'Archetypes'):
        if col not in ov.columns:
            sys.exit(f'overrides file needs a {col!r} column')
    out = {}
    for _, r in ov.iterrows():
        raw = str(r.get('Archetypes', '') or '')
        if raw.lower() == 'nan':
            raw = ''
        names = []
        for part in raw.split(';'):
            part = part.strip()
            if not part:
                continue
            match = next((a for a, (_, s) in ARCHETYPES.items()
                          if part in (a, s)), None)
            if match is None:
                sys.exit(f'override for {r["Card Code"]}: unknown archetype {part!r}')
            names.append(match)
        out[str(r['Card Code'])] = names
    return out


# --------------------------------------------------------------------------
# tagging
# --------------------------------------------------------------------------

def card_colors(value):
    if not isinstance(value, str) or value.strip().lower() == 'colorless':
        return set()
    return {ch for ch in value.upper() if ch in 'WUBRG'}


def parse_secondary(value):
    if not isinstance(value, str):
        return []
    out = []
    for part in re.split(r'[,/&]| and ', value.lower()):
        part = part.strip(' ?.-')
        if part in ALIASES:
            out.append(ALIASES[part])
    return out


def hooks_for(row):
    blob = ' '.join(
        str(row.get(k, '')) for k in
        ['Rules Text', 'Mechanic', 'Subtype', 'Type', 'Card Name']
    ).lower()
    hits = set()
    for pattern, archs in HOOKS:
        if re.search(pattern, blob):
            hits.update(archs)
    return hits


def type_bucket(type_line):
    t = str(type_line)
    if 'Creature' in t:
        return 'Creature'
    if 'Instant' in t or 'Sorcery' in t:
        return 'Instant/Sorcery'
    if 'Land' in t:
        return 'Land'
    return 'Other'


def tag_cards(df, overrides):
    colors = {a: set(pair) for a, (pair, _) in ARCHETYPES.items()}
    records = []

    for _, row in df.iterrows():
        cols = card_colors(row['Color'])
        tags = set()
        reasons = {}

        primary = row['Archetype'] if isinstance(row['Archetype'], str) else ''
        if primary in ARCHETYPES:
            tags.add(primary)
            reasons[primary] = 'designed'
        for a in parse_secondary(row.get('Secondary Archetype')):
            if a not in tags:
                tags.add(a)
                reasons[a] = 'secondary'

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
            tags.add(a)
            reasons[a] = 'generic'

        code = str(row['Card Code'])
        if code in overrides:
            tags = set(overrides[code])
            reasons = {a: reasons.get(a, 'override') for a in tags}

        rarity = row['Rarity'] if isinstance(row['Rarity'], str) else 'Unknown'
        cmc = int(row['CMC']) if pd.notna(row['CMC']) else 0

        records.append(dict(
            code=code,
            name=row['Card Name'],
            color=row['Color'],
            rarity=rarity,
            weight=RARITY_WEIGHT.get(rarity, DEFAULT_WEIGHT),
            cmc=cmc,
            type=row['Type'],
            bucket=type_bucket(row['Type']),
            tags=sorted(tags),
            reasons=reasons,
        ))

    return pd.DataFrame(records)


# --------------------------------------------------------------------------
# curves
# --------------------------------------------------------------------------

def build_curves(tagged):
    spells = tagged[tagged.bucket != 'Land']
    out = {}

    def curve(frame):
        bars = [0] * (MAX_MV + 1)
        for _, r in frame.iterrows():
            bars[min(int(r.cmc), MAX_MV)] += r.weight
        return bars

    for archetype in ARCHETYPES:
        sub = spells[spells.tags.apply(lambda t: archetype in t)]
        if sub.empty:
            continue
        core = sub[sub.reasons.apply(lambda d: d.get(archetype) != 'generic')]
        weighted = int(sub.weight.sum())
        out[archetype] = dict(
            total=curve(sub),
            Creature=curve(sub[sub.bucket == 'Creature']),
            InstantSorcery=curve(sub[sub.bucket == 'Instant/Sorcery']),
            Other=curve(sub[sub.bucket == 'Other']),
            cards=int(len(sub)),
            core=int(len(core)),
            wtd=weighted,
            avg=round(float((sub.cmc * sub.weight).sum() / weighted), 2) if weighted else 0,
        )
    return out


def print_summary(tagged, curves):
    spells = tagged[tagged.bucket != 'Land']
    print(f'front faces: {len(tagged)}  '
          f'(spells {len(spells)}, lands {len(tagged) - len(spells)})')
    print(f'avg archetypes per card: {tagged.tags.apply(len).mean():.2f}')
    untagged = tagged[tagged.tags.apply(len) == 0]
    if len(untagged):
        print(f'WARNING: {len(untagged)} card(s) matched no archetype: '
              + ', '.join(untagged.code.head(10)))
    print()
    header = (f'{"archetype":<10} {"cards":>5} {"core":>5} '
              f'{"wtd":>5} {"avgMV":>6}   curve 1..7+')
    print(header)
    print('-' * len(header))
    for archetype, data in sorted(curves.items(), key=lambda kv: -kv[1]['wtd']):
        short = ARCHETYPES[archetype][1]
        bars = ' '.join(f'{v:>3}' for v in data['total'][1:])
        print(f'{short:<10} {data["cards"]:>5} {data["core"]:>5} '
              f'{data["wtd"]:>5} {data["avg"]:>6.2f}   {bars}')


# --------------------------------------------------------------------------
# html
# --------------------------------------------------------------------------

HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Curve audit &mdash; archetypes</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700&family=Barlow:wght@400;500&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#0D1316; --panel:#141D21; --panel2:#101819; --rule:#22333A;
  --ink:#EDE6D6; --muted:#7E9299; --dim:#4E6169;
  --creature:#D9A441; --spell:#56B6C2; --other:#9A7FBF;
  --a1:#5DA05A; --a2:#F2E7CE;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:'Barlow',system-ui,sans-serif;-webkit-font-smoothing:antialiased;
  background-image:radial-gradient(ellipse at 12% -10%, #16242a 0%, transparent 55%);}
.wrap{max-width:1120px;margin:0 auto;padding:34px 22px 70px}
.eyebrow{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:.22em;
  text-transform:uppercase;color:var(--dim)}
h1{font-family:'Barlow Condensed',sans-serif;font-weight:700;text-transform:uppercase;
  font-size:clamp(38px,7vw,66px);line-height:.92;margin:8px 0 0}
h1 em{font-style:normal;color:var(--a1);transition:color .4s}
.lede{max-width:60ch;margin:14px 0 0;color:var(--muted);font-size:15px;line-height:1.55}
.lede b{color:var(--ink);font-weight:500}
.rule{height:1px;background:var(--rule);margin:28px 0 20px}
.picker{display:flex;flex-wrap:wrap;gap:7px}
.chip{display:flex;align-items:center;gap:8px;background:transparent;cursor:pointer;
  border:1px solid var(--rule);border-radius:2px;padding:7px 11px 7px 9px;color:var(--muted);
  font-family:'Barlow Condensed',sans-serif;font-weight:600;text-transform:uppercase;
  letter-spacing:.09em;font-size:14px;transition:.18s}
.chip:hover{color:var(--ink);border-color:var(--dim)}
.chip[aria-pressed="true"]{color:#0D1316;background:var(--ink);border-color:var(--ink)}
.chip:focus-visible{outline:2px solid #4FA3D1;outline-offset:2px}
.pips{display:flex;gap:3px}
.pip{width:9px;height:9px;border-radius:50%;box-shadow:inset 0 0 0 1px rgba(0,0,0,.35)}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--rule);
  border:1px solid var(--rule);margin:22px 0 0}
.stat{background:var(--panel2);padding:13px 15px}
.stat .k{font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.16em;
  text-transform:uppercase;color:var(--dim)}
.stat .v{font-family:'Barlow Condensed',sans-serif;font-size:30px;font-weight:700;
  line-height:1.1;margin-top:3px}
.stat .v small{font-size:13px;color:var(--muted);font-weight:400;margin-left:4px}
.panel{background:var(--panel);border:1px solid var(--rule);margin-top:20px;padding:20px 20px 14px}
.phead{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;
  gap:10px;margin-bottom:6px}
.ptitle{font-family:'Barlow Condensed',sans-serif;font-weight:700;text-transform:uppercase;
  letter-spacing:.13em;font-size:15px}
.psub{font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--dim);letter-spacing:.06em}
.legend{display:flex;gap:14px;font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--muted)}
.legend span{display:flex;align-items:center;gap:6px}
.sw{width:16px;height:9px;border-radius:1.5px;display:inline-block}
.chart{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;align-items:end;
  height:250px;margin-top:16px;padding-bottom:2px;border-bottom:1px solid var(--rule)}
.col{display:flex;flex-direction:column;justify-content:flex-end;height:100%;gap:2px}
.blk{border-radius:1.5px;flex:0 0 auto;animation:rise .34s cubic-bezier(.2,.7,.3,1) backwards}
@keyframes rise{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:none}}
.axis{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;margin-top:7px}
.tick{text-align:center;font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--muted)}
.tick b{display:block;font-size:15px;font-weight:600;color:var(--ink)}
.tick i{font-style:normal;display:block;font-size:10px;color:var(--dim);margin-top:1px}
.grid{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;background:var(--rule);
  border:1px solid var(--rule);margin-top:20px}
.cell{background:var(--panel2);padding:12px 11px 10px;cursor:pointer;transition:background .18s;
  border:0;text-align:left;font:inherit;color:inherit}
.cell:hover,.cell[data-on="1"]{background:#1A262B}
.cell:focus-visible{outline:2px solid #4FA3D1;outline-offset:-2px}
.cell h3{font-family:'Barlow Condensed',sans-serif;font-size:14px;font-weight:700;
  text-transform:uppercase;letter-spacing:.09em;margin:0 0 2px;display:flex;align-items:center;gap:6px}
.cell .m{font-family:'IBM Plex Mono',monospace;font-size:9.5px;color:var(--dim);letter-spacing:.05em}
.spark{display:grid;grid-template-columns:repeat(7,1fr);gap:2px;align-items:end;height:46px;margin-top:9px}
.spark div{border-radius:1px;background:var(--dim)}
.cell[data-on="1"] .spark div{background:var(--a1)}
.foot{margin-top:26px;color:var(--dim);font-size:12.5px;line-height:1.6;max-width:70ch}
.foot code{font-family:'IBM Plex Mono',monospace;color:var(--muted)}
@media(max-width:820px){
  .grid{grid-template-columns:repeat(2,1fr)}
  .stats{grid-template-columns:repeat(2,1fr)}
  .chart{height:200px}
}
@media(prefers-reduced-motion:reduce){.blk{animation:none}}
</style>
</head>
<body>
<div class="wrap">
  <div class="eyebrow">__EYEBROW__</div>
  <h1>Mana curve<br>by <em id="h1a">archetype</em></h1>
  <p class="lede">Every front face is tagged with each archetype it would actually be <b>good</b> in &mdash; its designed home, its secondary, plus any archetype that can cast it and has no competing mechanical pull. Commons and uncommons count <b>twice</b>, rares and mythics once, so the bars approximate what a drafter sees rather than what the spreadsheet holds. Lands excluded.</p>

  <div class="rule"></div>
  <div class="picker" id="picker" role="group" aria-label="Choose archetype"></div>
  <div class="stats" id="stats"></div>

  <section class="panel">
    <div class="phead">
      <div class="ptitle">Curve &mdash; all cards</div>
      <div class="psub">one block = one weighted card</div>
    </div>
    <div class="chart" id="c1"></div>
    <div class="axis" id="ax1"></div>
  </section>

  <section class="panel">
    <div class="phead">
      <div class="ptitle">Curve &mdash; by card type</div>
      <div class="legend">
        <span><i class="sw" style="background:var(--creature)"></i>Creature</span>
        <span><i class="sw" style="background:var(--spell)"></i>Instant / Sorcery</span>
        <span><i class="sw" style="background:var(--other)"></i>Other</span>
      </div>
    </div>
    <div class="chart" id="c2"></div>
    <div class="axis" id="ax2"></div>
  </section>

  <div class="grid" id="grid"></div>

  <p class="foot">Weighting: Common &times;2, Uncommon &times;2, Rare &times;1, Mythic &times;1. &ldquo;Other&rdquo; is artifacts, enchantments, battles and planeswalkers. &ldquo;Core&rdquo; counts only cards designed into the archetype (primary or secondary column); the rest are generically castable pickups. Generated by <code>curve_audit.py</code>.</p>
</div>

<script>
const DATA = __DATA__;
const MANA = __MANA__;
const HEX  = __HEX__;
const NAMES=Object.keys(DATA);
const MAXBAR=Math.max(1,...NAMES.map(n=>Math.max(...DATA[n].total)));
let current=NAMES[0];
const el=id=>document.getElementById(id);

el('picker').innerHTML=NAMES.map(n=>{
  const [a,b]=MANA[n];
  return `<button class="chip" data-n="${n}" aria-pressed="false">
    <span class="pips"><i class="pip" style="background:${HEX[a]}"></i><i class="pip" style="background:${HEX[b]}"></i></span>
    ${n.split(' - ')[1]}</button>`;
}).join('');

el('grid').innerHTML=NAMES.map(n=>{
  const d=DATA[n],[a,b]=MANA[n],mx=Math.max(1,...d.total);
  const bars=d.total.slice(1).map(v=>`<div style="height:${Math.max(2,v/mx*100)}%"></div>`).join('');
  return `<button class="cell" data-n="${n}" data-on="0">
    <h3><span class="pips"><i class="pip" style="background:${HEX[a]}"></i><i class="pip" style="background:${HEX[b]}"></i></span>${n.split(' - ')[1]}</h3>
    <div class="m">${d.wtd} wtd &middot; avg ${d.avg}</div>
    <div class="spark">${bars}</div></button>`;
}).join('');

function blocks(vals,colorFn){
  return vals.slice(1).map((v,i)=>{
    const h=100/MAXBAR;
    let inner='';
    for(let k=0;k<v;k++){
      inner+=`<div class="blk" style="height:calc(${h}% - 2px);background:${colorFn(i+1,k)};animation-delay:${(i*26+k*7)}ms"></div>`;
    }
    return `<div class="col">${inner||'<div style="height:2px"></div>'}</div>`;
  }).join('');
}

function render(n){
  current=n;
  const d=DATA[n],[a,b]=MANA[n];
  document.documentElement.style.setProperty('--a1',HEX[a]);
  document.documentElement.style.setProperty('--a2',HEX[b]);
  el('h1a').textContent=n.split(' - ')[1];
  document.querySelectorAll('.chip').forEach(c=>c.setAttribute('aria-pressed',c.dataset.n===n));
  document.querySelectorAll('.cell').forEach(c=>c.dataset.on=c.dataset.n===n?'1':'0');

  el('stats').innerHTML=[
    ['Cards playable',d.cards,''],
    ['Designed in',d.core,'core'],
    ['Weighted count',d.wtd,''],
    ['Average MV',d.avg,'']
  ].map(([k,v,s])=>`<div class="stat"><div class="k">${k}</div><div class="v">${v}${s?`<small>${s}</small>`:''}</div></div>`).join('');

  el('c1').innerHTML=blocks(d.total,(mv,k)=>k%2? HEX[b] : HEX[a]);

  el('c2').innerHTML=d.total.slice(1).map((tot,i)=>{
    const mv=i+1,h=100/MAXBAR;
    const segs=[['Other','var(--other)'],['InstantSorcery','var(--spell)'],['Creature','var(--creature)']];
    let inner='',k=0;
    segs.forEach(([key,col])=>{
      for(let j=0;j<d[key][mv];j++,k++)
        inner+=`<div class="blk" style="height:calc(${h}% - 2px);background:${col};animation-delay:${(i*26+k*7)}ms"></div>`;
    });
    return `<div class="col">${inner||'<div style="height:2px"></div>'}</div>`;
  }).join('');

  const ax=d.total.slice(1).map((v,i)=>
    `<div class="tick"><b>${i+1===7?'7+':i+1}</b>${v}<i>${d.wtd?Math.round(v/d.wtd*100):0}%</i></div>`).join('');
  el('ax1').innerHTML=ax; el('ax2').innerHTML=ax;
}

document.addEventListener('click',e=>{
  const t=e.target.closest('[data-n]');
  if(t) render(t.dataset.n);
});
render(current);
</script>
</body>
</html>
'''


def render_html(curves, tagged, label):
    mana = {a: list(pair) for a, (pair, _) in ARCHETYPES.items() if a in curves}
    spells = len(tagged[tagged.bucket != 'Land'])
    eyebrow = f'{label} &middot; {len(tagged)} front faces &middot; {spells} spells'
    return (HTML_TEMPLATE
            .replace('__DATA__', json.dumps(curves, separators=(',', ':')))
            .replace('__MANA__', json.dumps(mana, separators=(',', ':')))
            .replace('__HEX__', json.dumps(MANA_HEX, separators=(',', ':')))
            .replace('__EYEBROW__', eyebrow))


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description='Tag cards by archetype and render a mana curve report.')
    ap.add_argument('input', type=Path, help='Cards export (.xlsx or .csv)')
    ap.add_argument('--sheet', default='Cards', help='worksheet name (default: Cards)')
    ap.add_argument('--max-rows', type=int, default=421,
                    help='stop reading after N rows; 0 reads all (default: 421)')
    ap.add_argument('--out', type=Path, default=Path('curve-audit.html'),
                    help='HTML report path')
    ap.add_argument('--tags-out', type=Path, default=None,
                    help='also write the per-card tag table to this CSV')
    ap.add_argument('--overrides', type=Path, default=None,
                    help='CSV of manual tag overrides (Card Code,Archetypes)')
    ap.add_argument('--label', default='Clone Wars set',
                    help='text shown above the report title')
    args = ap.parse_args()

    df = load_cards(args.input, args.sheet, args.max_rows)
    tagged = tag_cards(df, load_overrides(args.overrides))
    curves = build_curves(tagged)

    print_summary(tagged, curves)

    if args.out.parent != Path(''):
        args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render_html(curves, tagged, args.label), encoding='utf-8')
    print(f'\nwrote {args.out}')

    if args.tags_out:
        rows = []
        for _, r in tagged.iterrows():
            row = dict(Code=r.code, Name=r['name'], Color=r.color, Rarity=r.rarity,
                       Weight=r.weight, CMC=r.cmc, Type=r.type, Bucket=r.bucket,
                       Archetypes='; '.join(ARCHETYPES[a][1] for a in r.tags),
                       NumArchetypes=len(r.tags))
            for a, (_, short) in ARCHETYPES.items():
                row[short] = r.reasons.get(a, '')
            rows.append(row)
        if args.tags_out.parent != Path(''):
            args.tags_out.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(rows).to_csv(args.tags_out, index=False)
        print(f'wrote {args.tags_out}')


if __name__ == '__main__':
    main()
