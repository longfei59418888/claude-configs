---
name: md-to-pdf
description: Convert Markdown files to readable PDFs with bundled, dependency-free tooling. Use when the user asks to export, render, or convert a .md/.markdown document to PDF.
---

# Markdown to PDF

Use the bundled script at scripts/md_to_pdf.py. It runs with Python 3 and
uses only the Python standard library; do not ask the user to install Pandoc,
ReportLab, wkhtmltopdf, a browser, Pillow, or another PDF dependency.

## Basic workflow

1. Resolve the input Markdown file and the requested output path. If no output
   path is given, use the input basename with a .pdf extension.
2. Run:

   ~~~bash
   python3 skills/md-to-pdf/scripts/md_to_pdf.py path/to/document.md \
     --output path/to/document.pdf
   ~~~

3. If the output already exists, add --overwrite only when replacing it is
   explicitly requested.
4. Report the created PDF path and any warnings printed by the script.

When the command is run from outside the repository, use the installed skill's
absolute path to scripts/md_to_pdf.py.

## Options

- --page-size a4|letter (default a4)
- --margin POINTS (default 54)
- --title TITLE to override the document title
- --no-footer to omit page numbers
- --overwrite to allow replacing an existing PDF

The renderer supports ATX headings, paragraphs, inline bold/italic/strike/code
and links, ordered and unordered lists, blockquotes, fenced code blocks,
GitHub-style tables, YAML-front-matter title, and standalone local PNG/JPEG
images. Chinese text is encoded through PDF's standard STSong-Light CJK
mapping, so no font download is needed. Missing or unsupported standalone
images are reported as warnings and represented by alt text; remote image URLs
are not downloaded.
