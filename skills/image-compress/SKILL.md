---
name: image-compress
description: Resize project images to no more than twice their rendered CSS width and convert non-WebP images to WebP. Use when the user asks to optimize, compress, resize, or WebP-convert image assets in a project.
---

# Compress project images

Use the bundled script for deterministic batch processing. It supports PNG, JPEG, GIF, BMP, TIFF, and WebP input and requires Pillow (`python3 -m pip install Pillow` if it is not already available).

## Workflow

1. Determine the image's rendered/project width from the relevant component, stylesheet, design spec, or the user's instruction. If several images have different rendered widths, run the script once per width/group.
2. Use `--width` with that rendered width in CSS pixels. The script sets the maximum source width to `2 * --width`; images already at or below that limit are not enlarged.
3. Run from the project root, preferably writing to a separate output directory first:

   ```bash
   python3 skills/image-compress/scripts/compress_images.py \
     --input path/to/images \
     --output path/to/compressed-images \
     --width 300
   ```

4. Review the printed summary and replace project references only after checking the generated files. Every output is WebP, with the same relative path and filename stem as the input.

## Important behavior

- Non-WebP inputs are converted to `.webp`; WebP inputs remain `.webp`.
- Images wider than `2 * --width` are scaled down proportionally: width and height use the same scale factor, so the original aspect ratio is always preserved. Smaller images are never upscaled.
- JPEG/WebP encoding uses the configurable lossy `--quality` (default `82`); PNG/GIF transparency is retained as WebP alpha.
- The default mode never overwrites source files. Use `--in-place` only when explicitly requested, and make a backup or use version control first.
- Animated images are skipped with an error because converting only the first frame would silently change the asset.
- Use `--overwrite` to replace files already present in the output directory.

Read the script's `--help` output for filtering and in-place options. Report skipped files and any missing Pillow dependency instead of claiming the batch succeeded.
