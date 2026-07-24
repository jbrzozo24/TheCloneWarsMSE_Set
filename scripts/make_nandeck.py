#!/usr/bin/env python3
"""Generate a NanDeck .txt script from a folder of card/token PNGs.

NanDeck expects a very small script for "print these images as cards":

    UNIT=MM
    CARDSIZE=63,88
    IMAGE=1,"C:\\...\\Some Card_v1.png",0,0,63,88
    IMAGE=2,"C:\\...\\Another Card_v1.png",0,0,63,88
    ...

This tool builds that file for you from a directory of images. By default it
picks up every PNG in the folder (sorted). If you only want a subset -- or a
specific ordering -- pass a config file (``--config``) listing the filenames
you want, one per line.

Examples
--------
Whole folder::

    python scripts/make_nandeck.py Export/tokens_v1

Custom output path::

    python scripts/make_nandeck.py Export/tokens_v1 -o nandeck/NanDeckTokensExport.txt

Only the files listed in a config (in that order)::

    python scripts/make_nandeck.py Export/tokens_v1 --config scripts/tokens_v1.cfg

The config format is one filename per line. Blank lines and lines starting
with ``#`` are ignored. Entries may be bare filenames (resolved against the
image folder), relative subpaths, or absolute paths. A missing ``.png``
extension is added automatically if that makes the file resolve.

To include multiple copies of a card, either list it on several lines or add
a trailing ``xN`` / ``*N`` multiplier (handy for tokens)::

    _Clone Trooper_v1.png x8
    _Battle Droid_v1.png *4
    _Droid_v1.png            # one copy
    _Droid_v1.png            # ...and another
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# NanDeck defaults matching the existing exports in nandeck/ (standard MTG card).
DEFAULT_UNIT = "MM"
DEFAULT_CARD_SIZE = (63, 88)
DEFAULT_PATTERN = "*.png"


def parse_card_size(value: str) -> tuple[int, int]:
    """Parse a ``WxH`` or ``W,H`` card size into an ``(width, height)`` pair."""
    separators = ("x", "X", ",")
    for sep in separators:
        if sep in value:
            width, _, height = value.partition(sep)
            try:
                return int(width.strip()), int(height.strip())
            except ValueError:
                break
    raise argparse.ArgumentTypeError(
        f"invalid card size {value!r}; expected 'WxH' or 'W,H' (e.g. 63x88)"
    )


def resolve_entry(entry: str, folder: Path) -> Path:
    """Resolve one config entry to an absolute path (relative to ``folder``).

    Tries the entry as given first, then with a ``.png`` extension appended if
    it has no suffix. Returns the best-guess absolute path even if it does not
    exist so the caller can report a helpful warning.
    """
    candidate = Path(entry)
    if not candidate.is_absolute():
        candidate = folder / candidate

    if candidate.exists():
        return candidate.resolve()

    # Allow listing token names without the ".png" extension.
    if candidate.suffix == "":
        with_ext = candidate.with_suffix(".png")
        if with_ext.exists():
            return with_ext.resolve()

    return candidate.resolve()


# Optional trailing copy multiplier, e.g. "Card_v1.png x8" or "Card_v1.png *4".
# It must be whitespace-separated so it can't be mistaken for part of a name;
# combined with the ".png" that ends real entries, collisions are unlikely.
_COUNT_RE = re.compile(r"^(?P<name>.*\S)\s+[xX*](?P<count>\d+)\s*$")


def parse_config_line(line: str) -> tuple[str, int]:
    """Split a config line into ``(filename, copies)``.

    A trailing ``xN`` / ``*N`` multiplier requests that many copies of the
    card; without one, a single copy is requested. Listing the same file on
    several lines stacks copies too.
    """
    match = _COUNT_RE.match(line)
    if match:
        return match.group("name"), int(match.group("count"))
    return line, 1


def collect_from_config(config_path: Path, folder: Path) -> list[Path]:
    """Read image paths from a config file, preserving the listed order.

    Repeated entries and trailing ``xN`` multipliers both expand into multiple
    copies of the same image.
    """
    images: list[Path] = []
    with open(config_path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            name, copies = parse_config_line(line)
            images.extend([resolve_entry(name, folder)] * copies)
    return images


def collect_from_folder(folder: Path, pattern: str, recursive: bool) -> list[Path]:
    """Return every image in ``folder`` matching ``pattern`` (case-insensitive sort)."""
    globber = folder.rglob if recursive else folder.glob
    images = [path for path in globber(pattern) if path.is_file()]
    # Case-insensitive name sort matches the ordering of the existing exports
    # in nandeck/ (e.g. "Anakins Podracer" before "ARC-170").
    images.sort(key=lambda path: path.name.casefold())
    return [path.resolve() for path in images]


def build_nandeck_lines(
    images: list[Path],
    unit: str,
    card_size: tuple[int, int],
) -> list[str]:
    """Build the NanDeck script lines for the given images."""
    width, height = card_size
    lines = [f"UNIT={unit}", f"CARDSIZE={width},{height}"]
    for index, image in enumerate(images, start=1):
        # NanDeck runs on Windows and wants backslash paths; os.fspath on a
        # resolved WindowsPath already gives that, but normalize to be safe.
        native_path = os.path.normpath(str(image))
        lines.append(f'IMAGE={index},"{native_path}",0,0,{width},{height}')
    return lines


def default_output_path(folder: Path) -> Path:
    """Pick a sensible default output filename derived from the folder name."""
    return Path.cwd() / f"NanDeck_{folder.name}.txt"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a NanDeck .txt script from a folder of PNG images.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "folder",
        type=Path,
        help="Folder containing the PNG images to lay out as cards.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output .txt path (default: NanDeck_<folder>.txt in the current dir).",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=None,
        help="Config file listing the filenames to include, one per line, in order. "
        "Overrides directory scanning. Blank lines and '#' comments are ignored.",
    )
    parser.add_argument(
        "--card-size",
        type=parse_card_size,
        default=DEFAULT_CARD_SIZE,
        metavar="WxH",
        help="Card size in the chosen unit (default: 63x88).",
    )
    parser.add_argument(
        "--unit",
        default=DEFAULT_UNIT,
        help="NanDeck measurement unit (default: MM).",
    )
    parser.add_argument(
        "--pattern",
        default=DEFAULT_PATTERN,
        help="Glob pattern for directory mode (default: *.png). Ignored with --config.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recurse into subfolders in directory mode. Ignored with --config.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    folder: Path = args.folder
    if not folder.is_dir():
        print(f"error: not a folder: {folder}", file=sys.stderr)
        return 2

    if args.config is not None:
        if not args.config.is_file():
            print(f"error: config file not found: {args.config}", file=sys.stderr)
            return 2
        images = collect_from_config(args.config, folder)
        source = f"config {args.config}"
    else:
        images = collect_from_folder(folder, args.pattern, args.recursive)
        source = f"folder {folder} (pattern {args.pattern!r})"

    # Warn once per distinct missing path (an entry may be listed many times).
    missing: list[Path] = []
    for image in images:
        if not image.exists() and image not in missing:
            missing.append(image)
            print(f"warning: file not found, skipping: {image}", file=sys.stderr)
    images = [image for image in images if image.exists()]

    if not images:
        print(f"error: no images found from {source}", file=sys.stderr)
        return 1

    lines = build_nandeck_lines(images, args.unit, args.card_size)

    output_path = args.output or default_output_path(folder)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\r\n") as handle:
        handle.write("\n".join(lines) + "\n")

    print(f"Wrote {len(images)} image(s) to {output_path.resolve()}")
    if missing:
        print(f"({len(missing)} listed file(s) were missing and skipped.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
