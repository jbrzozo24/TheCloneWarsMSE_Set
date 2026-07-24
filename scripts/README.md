# scripts

Helper scripts for this set.

## make_nandeck.py

Generates a [NanDeck](https://www.nandeck.com/) `.txt` script from a folder of
card/token PNGs, so you can lay them out and export a print sheet / PDF. It
reproduces the format of the existing exports in `../nandeck/` (e.g.
`NanDeckUncommonExport.txt`):

```
UNIT=MM
CARDSIZE=63,88
IMAGE=1,"C:\...\Some Card_v1.png",0,0,63,88
IMAGE=2,"C:\...\Another Card_v1.png",0,0,63,88
...
```

### Usage

Whole folder (every PNG, sorted), writing `NanDeck_tokens_v1.txt` in the
current directory:

```bash
python scripts/make_nandeck.py Export/tokens_v1
```

Choose the output path:

```bash
python scripts/make_nandeck.py Export/tokens_v1 -o nandeck/NanDeckTokensExport.txt
```

Only the files listed in a config, in that order (see
`tokens_v1.example.cfg`):

```bash
python scripts/make_nandeck.py Export/tokens_v1 \
    --config scripts/tokens_v1.example.cfg \
    -o nandeck/NanDeckTokensExport.txt
```

### Options

| Option | Description |
| --- | --- |
| `folder` | Folder of PNGs to include (positional, required). |
| `-o, --output` | Output `.txt` path. Default: `NanDeck_<folder>.txt` in the current dir. |
| `-c, --config` | Config file listing filenames to include, one per line, in order. Overrides directory scanning. |
| `--card-size WxH` | Card size in the chosen unit. Default: `63x88`. |
| `--unit` | NanDeck measurement unit. Default: `MM`. |
| `--pattern` | Glob for directory mode. Default: `*.png`. Ignored with `--config`. |
| `--recursive` | Recurse into subfolders in directory mode. Ignored with `--config`. |

### Config file format

One filename per line. Blank lines and lines starting with `#` are ignored.
Bare filenames are resolved against the image `folder`; relative subpaths and
absolute paths also work. A missing `.png` extension is added automatically
when that makes the file resolve. Files that cannot be found are reported as
warnings and skipped.

To include **multiple copies** of a card, add a trailing `xN` / `*N`
multiplier, or list the card on several lines — both stack:

```
_Clone Trooper_v1.png x8
_Battle Droid_v1.png *4
_Rebel_v1.png              # one copy...
_Rebel_v1.png              # ...and another
```

The multiplier must be whitespace-separated (e.g. `... x8`). Since real
entries end in `.png`, this won't be mistaken for part of a filename.
