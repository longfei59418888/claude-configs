#!/usr/bin/env python3
"""Resize image assets proportionally to a 2x rendered-width ceiling and encode as WebP."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:  # pragma: no cover - exercised by the CLI environment
    Image = None
    ImageOps = None


EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resize images to at most 2x their rendered width and convert them to WebP."
    )
    parser.add_argument("--input", required=True, type=Path, help="Image file or directory to process")
    parser.add_argument("--output", type=Path, help="Output directory (default: <input>-compressed)")
    parser.add_argument("--width", required=True, type=int, help="Rendered/CSS width in pixels")
    parser.add_argument("--quality", type=int, default=82, help="WebP quality, 0-100 (default: 82)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output files")
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Write beside the source and remove the original after successful conversion",
    )
    return parser.parse_args()


def image_paths(source: Path) -> list[Path]:
    if source.is_file():
        return [source] if source.suffix.lower() in EXTENSIONS else []
    if source.is_dir():
        return sorted(path for path in source.rglob("*") if path.is_file() and path.suffix.lower() in EXTENSIONS)
    raise FileNotFoundError(f"Input does not exist: {source}")


def output_path(source: Path, input_root: Path, output_root: Path) -> Path:
    relative = source.name if input_root.is_file() else source.relative_to(input_root)
    return output_root / Path(relative).with_suffix(".webp")


def compress(source: Path, destination: Path, max_width: int, quality: int) -> tuple[bool, str]:
    with Image.open(source) as opened:
        if getattr(opened, "is_animated", False):
            return False, "animated image skipped"

        image = ImageOps.exif_transpose(opened)
        if image.width > max_width:
            scale = max_width / image.width
            resized_width = max_width
            resized_height = round(image.height * scale)
            # Calculate height from the same scale factor; never stretch either axis.
            image = image.resize((resized_width, resized_height), Image.Resampling.LANCZOS)

        if image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
        image.save(destination, "WEBP", quality=quality, method=6)
        return True, f"{opened.width}x{opened.height} -> {image.width}x{image.height}"


def main() -> int:
    args = parse_args()
    if Image is None:
        print("Pillow is required. Install it with: python3 -m pip install Pillow", file=sys.stderr)
        return 2
    if args.width <= 0 or not 0 <= args.quality <= 100:
        print("--width must be positive and --quality must be between 0 and 100", file=sys.stderr)
        return 2
    if args.in_place and args.output:
        print("--in-place cannot be combined with --output", file=sys.stderr)
        return 2

    source_root = args.input.resolve()
    files = image_paths(source_root)
    if not files:
        print(f"No supported images found under {source_root}")
        return 0

    output_root = source_root.parent / f"{source_root.stem}-compressed" if not args.output else args.output.resolve()
    if args.in_place:
        output_root = source_root.parent if source_root.is_file() else source_root

    converted = skipped = failed = 0
    for source in files:
        destination = output_path(source, source_root, output_root)
        if destination.exists() and not args.overwrite and not args.in_place:
            print(f"SKIP {source}: output exists ({destination})")
            skipped += 1
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        try:
            ok, detail = compress(source, temporary, args.width * 2, args.quality)
            if not ok:
                temporary.unlink(missing_ok=True)
                print(f"SKIP {source}: {detail}")
                skipped += 1
                continue
            temporary.replace(destination)
            if args.in_place and source != destination:
                source.unlink()
            print(f"OK   {source} -> {destination} ({detail})")
            converted += 1
        except Exception as error:  # keep a batch useful when one asset is malformed
            temporary.unlink(missing_ok=True)
            print(f"FAIL {source}: {error}", file=sys.stderr)
            failed += 1

    print(f"Summary: converted={converted}, skipped={skipped}, failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
