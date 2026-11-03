#!/usr/bin/env python3
"""Markdown to PDF converter."""

from __future__ import annotations

import argparse
import re
import struct
import sys
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

PAGE_SIZES = {"a4": (595.28, 841.89), "letter": (612.0, 792.0)}
BACKTICK = chr(96)


def pdf_num(value: float) -> str:
    if abs(value) < 0.0001:
        value = 0.0
    return f"{value:.3f}".rstrip("0").rstrip(".")


def pdf_name(value: str) -> str:
    return "/" + re.sub(r"[^A-Za-z0-9_.-]", "", value)


def pdf_string(value: str) -> bytes:
    value = value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return value.replace("\r", " ").replace("\n", " ").encode("latin-1", "replace")


def cjk_string(value: str) -> bytes:
    safe = "".join(ch if ord(ch) <= 0xFFFF else "?" for ch in value)
    return safe.encode("utf-16-be", "replace")


def is_cjk_char(char: str) -> bool:
    return ord(char) > 0x7F


def text_width(value: str, size: float, style: Optional[Dict[str, bool]] = None) -> float:
    style = style or {}
    latin = 0.60 if style.get("code") else (0.52 if style.get("bold") else 0.50)
    result = 0.0
    for char in value:
        if char == "\t":
            result += size * latin * 4
        elif char == " ":
            result += size * 0.28
        elif char == "\u3000" or is_cjk_char(char):
            result += size
        elif char in "ilI.,'!|:;":
            result += size * 0.28
        elif char in "mwMW@#%&":
            result += size * 0.78
        else:
            result += size * latin
    return result


@dataclass
class Run:
    text: str
    style: Dict[str, bool] = field(default_factory=dict)


@dataclass
class Block:
    kind: str
    text: str = ""
    level: int = 0
    ordered: bool = False
    items: List[str] = field(default_factory=list)
    rows: List[List[str]] = field(default_factory=list)
    image_path: Optional[str] = None
    image_alt: str = ""


def merge_runs(runs: Iterable[Run]) -> List[Run]:
    result: List[Run] = []
    for run in runs:
        if not run.text:
            continue
        if result and result[-1].style == run.style:
            result[-1].text += run.text
        else:
            result.append(Run(run.text, dict(run.style)))
    return result


def parse_inline(value: str) -> List[Run]:
    fence = BACKTICK
    pattern = re.compile(
        r"(!?\[[^\]]*\]\([^)\n]+\)|"
        + re.escape(fence)
        + r"[^"
        + re.escape(fence)
        + r"\n]+"
        + re.escape(fence)
        + r"|\*\*[^\*\n]+\*\*|__[^_\n]+__|~~[^~\n]+~~|\*[^*\n]+\*|_[^_\n]+_)"
    )
    result: List[Run] = []
    cursor = 0
    for match in pattern.finditer(value):
        if match.start() > cursor:
            result.append(Run(value[cursor : match.start()]))
        token = match.group(0)
        if token.startswith("!["):
            parsed = re.match(r"!\[([^\]]*)\]\(([^)\n]+)\)", token)
            result.append(Run(f"[Image: {parsed.group(1) if parsed else token}]", {"italic": True}))
        elif token.startswith("["):
            parsed = re.match(r"\[([^\]]*)\]\(([^)\n]+)\)", token)
            result.append(Run(parsed.group(1) if parsed else token, {"link": True}))
        elif token.startswith(fence):
            result.append(Run(token[1:-1], {"code": True}))
        elif token.startswith("**") or token.startswith("__"):
            result.append(Run(token[2:-2], {"bold": True}))
        elif token.startswith("~~"):
            result.append(Run(token[2:-2], {"strike": True}))
        else:
            result.append(Run(token[1:-1], {"italic": True}))
        cursor = match.end()
    if cursor < len(value):
        result.append(Run(value[cursor:]))
    return merge_runs(result)


def split_table_row(line: str) -> List[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    result, current, escaped = [], [], False
    for char in line:
        if char == "|" and not escaped:
            result.append("".join(current).replace("\\|", "|").strip())
            current = []
        else:
            current.append(char)
        escaped = char == "\\" and not escaped
        if char != "\\":
            escaped = False
    result.append("".join(current).replace("\\|", "|").strip())
    return result


TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")
HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
UL_ITEM = re.compile(r"^(\s*)[-+*]\s+(.+)$")
OL_ITEM = re.compile(r"^(\s*)\d+[.)]\s+(.+)$")
IMAGE_ONLY = re.compile(r"^\s*!\[([^\]]*)\]\(([^)\n]+)\)\s*$")
THEMATIC_BREAK = re.compile(r"^\s{0,3}[-*_](?:\s*[-*_]){2,}\s*$")


def is_block_start(lines: Sequence[str], index: int) -> bool:
    line = lines[index]
    return bool(
        HEADING.match(line)
        or line.strip().startswith(BACKTICK * 3)
        or THEMATIC_BREAK.match(line)
        or UL_ITEM.match(line)
        or OL_ITEM.match(line)
        or line.lstrip().startswith(">")
        or IMAGE_ONLY.match(line)
        or (index + 1 < len(lines) and "|" in line and TABLE_SEPARATOR.match(lines[index + 1]))
    )


def parse_markdown(markdown: str, source_dir: Path, warnings: List[str]) -> Tuple[List[Block], str]:
    lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    blocks: List[Block] = []
    title = ""
    index = 0
    if lines and lines[0].strip() == "---":
        end = next((n for n in range(1, len(lines)) if lines[n].strip() == "---"), None)
        if end is not None:
            for metadata_line in lines[1:end]:
                key, separator, value = metadata_line.partition(":")
                if separator and key.strip().lower() == "title":
                    title = value.strip().strip("\"'")
            index = end + 1

    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        heading = HEADING.match(line)
        if heading:
            text = heading.group(2).strip()
            blocks.append(Block("heading", text, len(heading.group(1))))
            if not title and len(heading.group(1)) == 1:
                title = re.sub(r"[*_]", "", text).replace(BACKTICK, "")
            index += 1
            continue
        if line.strip().startswith(BACKTICK * 3):
            code: List[str] = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith(BACKTICK * 3):
                code.append(lines[index])
                index += 1
            if index < len(lines):
                index += 1
            blocks.append(Block("code", "\n".join(code)))
            continue
        image = IMAGE_ONLY.match(line)
        if image:
            raw_path = image.group(2).strip().strip("<>")
            path = Path(raw_path)
            if not path.is_absolute():
                path = source_dir / path
            if path.is_file():
                blocks.append(Block("image", image_path=str(path), image_alt=image.group(1).strip()))
            else:
                warnings.append(f"Image not found, rendered as alt text: {raw_path}")
                blocks.append(Block("paragraph", f"[Image: {image.group(1).strip()}]"))
            index += 1
            continue
        if index + 1 < len(lines) and "|" in line and TABLE_SEPARATOR.match(lines[index + 1]):
            rows = [split_table_row(line)]
            index += 2
            while index < len(lines) and lines[index].strip() and "|" in lines[index]:
                rows.append(split_table_row(lines[index]))
                index += 1
            columns = max(len(row) for row in rows)
            blocks.append(Block("table", rows=[row + [""] * (columns - len(row)) for row in rows]))
            continue
        if THEMATIC_BREAK.match(line):
            blocks.append(Block("rule"))
            index += 1
            continue
        list_match = UL_ITEM.match(line) or OL_ITEM.match(line)
        if list_match:
            ordered = bool(OL_ITEM.match(line))
            items: List[str] = []
            while index < len(lines):
                match = (OL_ITEM if ordered else UL_ITEM).match(lines[index])
                if match:
                    items.append(match.group(2).strip())
                    index += 1
                elif lines[index].strip() and (lines[index].startswith("  ") or lines[index].startswith("\t")):
                    if items:
                        items[-1] += " " + lines[index].strip()
                    index += 1
                else:
                    break
            blocks.append(Block("list", ordered=ordered, items=items))
            continue
        if line.lstrip().startswith(">"):
            quote: List[str] = []
            while index < len(lines) and lines[index].lstrip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[index]))
                index += 1
            blocks.append(Block("quote", "\n".join(quote)))
            continue
        paragraph = [line]
        index += 1
        while index < len(lines) and lines[index].strip() and not is_block_start(lines, index):
            paragraph.append(lines[index])
            index += 1
        blocks.append(Block("paragraph", " ".join(part.strip() for part in paragraph)))
    return blocks, title


def jpeg_dimensions(data: bytes) -> Tuple[int, int, int]:
    if not data.startswith(b"\xff\xd8"):
        raise ValueError("invalid JPEG header")
    offset = 2
    while offset + 9 < len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        marker = data[offset + 1]
        offset += 2
        if marker in (0xD8, 0xD9):
            continue
        if offset + 2 > len(data):
            break
        length = struct.unpack(">H", data[offset : offset + 2])[0]
        if marker in set(range(0xC0, 0xC4)) | set(range(0xC5, 0xC8)) | set(range(0xC9, 0xCC)) | set(range(0xCD, 0xD0)):
            if offset + 8 > len(data):
                break
            height, width, components = struct.unpack(">HHB", data[offset + 3 : offset + 8])
            return width, height, components
        offset += length
    raise ValueError("could not determine JPEG dimensions")


def png_data(data: bytes) -> Tuple[int, int, int, bytes, Optional[bytes]]:
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("invalid PNG header")
    offset = 8
    width = height = bit_depth = color_type = 0
    idat: List[bytes] = []
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        chunk = data[offset + 8 : offset + 8 + length]
        offset += 12 + length
        if kind == b"IHDR":
            width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", chunk)
            if bit_depth != 8 or interlace != 0 or compression != 0 or filtering != 0:
                raise ValueError("only non-interlaced 8-bit PNGs are supported")
        elif kind == b"IDAT":
            idat.append(chunk)
        elif kind == b"IEND":
            break
    channels = {0: 1, 2: 3, 4: 2, 6: 4}.get(color_type)
    if not width or not height or not idat or channels is None:
        raise ValueError("unsupported or empty PNG")
    raw = zlib.decompress(b"".join(idat))
    row_size = width * channels
    if len(raw) != (row_size + 1) * height:
        raise ValueError("PNG data length does not match dimensions")
    rows: List[bytes] = []
    previous = bytearray(row_size)
    cursor = 0
    for _ in range(height):
        filter_type = raw[cursor]
        row = bytearray(raw[cursor + 1 : cursor + 1 + row_size])
        cursor += row_size + 1
        for pos in range(row_size):
            left = row[pos - channels] if pos >= channels else 0
            up = previous[pos]
            upper_left = previous[pos - channels] if pos >= channels else 0
            if filter_type == 1:
                row[pos] = (row[pos] + left) & 255
            elif filter_type == 2:
                row[pos] = (row[pos] + up) & 255
            elif filter_type == 3:
                row[pos] = (row[pos] + (left + up) // 2) & 255
            elif filter_type == 4:
                predictor = left + up - upper_left
                pa, pb, pc = abs(predictor - left), abs(predictor - up), abs(predictor - upper_left)
                estimate = left if pa <= pb and pa <= pc else up if pb <= pc else upper_left
                row[pos] = (row[pos] + estimate) & 255
            elif filter_type != 0:
                raise ValueError(f"unsupported PNG filter: {filter_type}")
        rows.append(bytes(row))
        previous = row
    if color_type in (4, 6):
        color_channels = 1 if color_type == 4 else 3
        stride = 2 if color_type == 4 else 4
        colors = [b"".join(row[pos : pos + color_channels] for pos in range(0, len(row), stride)) for row in rows]
        alphas = [row[1::2] if color_type == 4 else row[3::4] for row in rows]
        return width, height, color_channels, zlib.compress(b"".join(colors), 9), zlib.compress(b"".join(alphas), 9)
    predicted = b"".join(b"\x00" + row for row in rows)
    return width, height, channels, zlib.compress(predicted, 9), None


def tokenize_for_wrap(runs: Sequence[Run]) -> Iterable[Tuple[str, Optional[Run]]]:
    for run in runs:
        current: List[str] = []
        for char in run.text:
            if char == "\n":
                if current:
                    yield "".join(current), run
                    current = []
                yield "\n", None
            elif char.isspace():
                if current:
                    yield "".join(current), run
                    current = []
                yield char, run
            elif is_cjk_char(char):
                if current:
                    yield "".join(current), run
                    current = []
                yield char, run
            else:
                current.append(char)
        if current:
            yield "".join(current), run


def wrap_runs(runs: Sequence[Run], max_width: float, size: float) -> List[List[Run]]:
    lines: List[List[Run]] = [[]]
    current_width = 0.0

    def append(text: str, style: Dict[str, bool]) -> None:
        nonlocal current_width
        if text:
            lines[-1].append(Run(text, style))
            current_width += text_width(text, size, style)

    for token, run in tokenize_for_wrap(runs):
        if token == "\n":
            lines[-1] = merge_runs(lines[-1])
            lines.append([])
            current_width = 0.0
            continue
        if run is None:
            continue
        style = run.style
        width = text_width(token, size, style)
        if token.isspace() and not lines[-1]:
            continue
        if current_width + width <= max_width or not lines[-1]:
            if width <= max_width or len(token) == 1:
                append(token, style)
                continue
        if token.isspace():
            lines[-1] = merge_runs(lines[-1])
            continue
        if lines[-1]:
            lines[-1] = merge_runs(lines[-1])
            lines.append([])
            current_width = 0.0
        for char in token:
            char_width = text_width(char, size, style)
            if current_width + char_width > max_width and lines[-1]:
                lines[-1] = merge_runs(lines[-1])
                lines.append([])
                current_width = 0.0
            append(char, style)
    lines[-1] = merge_runs(lines[-1])
    return lines


class PDFDocument:
    def __init__(self, title: str) -> None:
        self.objects: List[Optional[bytes]] = [None]
        self.fonts: Dict[str, int] = {}
        self.image_counter = 0
        self.title = title
        self._init_fonts()

    def add_object(self, value: bytes) -> int:
        self.objects.append(value)
        return len(self.objects) - 1

    def set_object(self, object_id: int, value: bytes) -> None:
        self.objects[object_id] = value

    def _init_fonts(self) -> None:
        for name, base in (
            ("body", "Helvetica"),
            ("bold", "Helvetica-Bold"),
            ("italic", "Helvetica-Oblique"),
            ("code", "Courier"),
        ):
            self.fonts[name] = self.add_object(
                f"<< /Type /Font /Subtype /Type1 /BaseFont /{base} /Encoding /WinAnsiEncoding >>".encode("ascii")
            )
        cid = self.add_object(
            b"<< /Type /Font /Subtype /CIDFontType0 /BaseFont /STSong-Light "
            b"/CIDSystemInfo << /Registry (Adobe) /Ordering (GB1) /Supplement 4 >> /DW 1000 >>"
        )
        self.fonts["cjk"] = self.add_object(
            b"<< /Type /Font /Subtype /Type0 /BaseFont /STSong-Light /Encoding /UniGB-UCS2-H /DescendantFonts ["
            + str(cid).encode("ascii")
            + b" 0 R] >>"
        )

    def add_image(self, path: Path) -> Tuple[str, int, int, int]:
        data = path.read_bytes()
        suffix = path.suffix.lower()
        if suffix in (".jpg", ".jpeg"):
            width, height, components = jpeg_dimensions(data)
            colorspace = b"/DeviceGray" if components == 1 else b"/DeviceRGB"
            image = (
                b"<< /Type /XObject /Subtype /Image "
                + f"/Width {width} /Height {height} /ColorSpace ".encode("ascii")
                + colorspace
                + b" /BitsPerComponent 8 /Filter /DCTDecode "
                + f"/Length {len(data)} >>\nstream\n".encode("ascii")
                + data
                + b"\nendstream"
            )
        elif suffix == ".png":
            width, height, components, compressed, alpha = png_data(data)
            alpha_id = 0
            if alpha is not None:
                alpha_id = self.add_object(
                    b"<< /Type /XObject /Subtype /Image "
                    + f"/Width {width} /Height {height} /ColorSpace /DeviceGray /BitsPerComponent 8 /Filter /FlateDecode /Length {len(alpha)} >>\nstream\n".encode("ascii")
                    + alpha
                    + b"\nendstream"
                )
            smask = f" /SMask {alpha_id}".encode("ascii") if alpha_id else b""
            colorspace = b"/DeviceGray" if components == 1 else b"/DeviceRGB"
            image = (
                b"<< /Type /XObject /Subtype /Image "
                + f"/Width {width} /Height {height} /ColorSpace ".encode("ascii")
                + colorspace
                + b" /BitsPerComponent 8 /Filter /FlateDecode "
                + f"/DecodeParms << /Predictor 15 /Colors {components} /BitsPerComponent 8 /Columns {width} >>".encode("ascii")
                + smask
                + f" /Length {len(compressed)} >>\nstream\n".encode("ascii")
                + compressed
                + b"\nendstream"
            )
        else:
            raise ValueError(f"unsupported image type: {path.name}")
        object_id = self.add_object(image)
        self.image_counter += 1
        return f"Im{self.image_counter}", object_id, width, height

    def write(self, pages: List[Tuple[bytes, Dict[str, object]]], path: Path) -> None:
        pages_id = self.add_object(b"")
        page_ids: List[int] = []
        for content, resources in pages:
            content_id = self.add_object(
                b"<< /Length " + str(len(content)).encode("ascii") + b" >>\nstream\n" + content + b"\nendstream"
            )
            fonts = b" ".join(
                pdf_name(name).encode("ascii") + b" " + str(object_id).encode("ascii") + b" 0 R"
                for name, object_id in self.fonts.items()
            )
            images = b" ".join(
                pdf_name(name).encode("ascii") + b" " + str(value[1]).encode("ascii") + b" 0 R"
                for name, value in resources.items()
                if name != "_page"
            )
            resource = b"<< /Font << " + fonts + b" >>"
            if images:
                resource += b" /XObject << " + images + b" >>"
            resource += b" >>"
            page_width, page_height = resources["_page"]  # type: ignore[misc]
            page_ids.append(
                self.add_object(
                    b"<< /Type /Page /Parent " + str(pages_id).encode("ascii") + b" 0 R /MediaBox [0 0 "
                    + pdf_num(page_width).encode("ascii") + b" " + pdf_num(page_height).encode("ascii")
                    + b"] /Resources " + resource + b" /Contents " + str(content_id).encode("ascii") + b" 0 R >>"
                )
            )
        kids = b" ".join(str(page_id).encode("ascii") + b" 0 R" for page_id in page_ids)
        self.set_object(
            pages_id,
            b"<< /Type /Pages /Kids [" + kids + b"] /Count " + str(len(page_ids)).encode("ascii") + b" >>",
        )
        info_id = self.add_object(
            b"<< /Title (" + pdf_string(self.title) + b") /Producer (md-to-pdf standard-library renderer) >>"
        )
        catalog_id = self.add_object(
            b"<< /Type /Catalog /Pages " + str(pages_id).encode("ascii") + b" 0 R >>"
        )
        output = bytearray(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for object_id in range(1, len(self.objects)):
            offsets.append(len(output))
            output.extend(f"{object_id} 0 obj\n".encode("ascii"))
            output.extend(self.objects[object_id] or b"")
            output.extend(b"\nendobj\n")
        xref_offset = len(output)
        output.extend(f"xref\n0 {len(self.objects)}\n0000000000 65535 f \n".encode("ascii"))
        for offset in offsets[1:]:
            output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
        output.extend(
            b"trailer\n<< /Size " + str(len(self.objects)).encode("ascii") + b" /Root "
            + str(catalog_id).encode("ascii") + b" 0 R /Info " + str(info_id).encode("ascii")
            + b" 0 R >>\nstartxref\n" + str(xref_offset).encode("ascii") + b"\n%%EOF\n"
        )
        path.write_bytes(output)


class Renderer:
    def __init__(
        self,
        document: PDFDocument,
        page_size: Tuple[float, float],
        margin: float,
        footer: bool,
        warnings: List[str],
    ) -> None:
        self.document = document
        self.page_width, self.page_height = page_size
        self.margin, self.footer, self.warnings = margin, footer, warnings
        self.pages: List[Dict[str, object]] = []
        self.new_page()

    @property
    def content_width(self) -> float:
        return self.page_width - self.margin * 2

    @property
    def bottom(self) -> float:
        return self.margin + (20 if self.footer else 0)

    def new_page(self) -> None:
        self.pages.append({"commands": [], "resources": {}})
        self.x, self.y = self.margin, self.page_height - self.margin
        self.resources = self.pages[-1]["resources"]  # type: ignore[assignment]

    def add(self, command: str) -> None:
        self.pages[-1]["commands"].append(command)  # type: ignore[union-attr]

    def ensure_height(self, height: float) -> None:
        if self.y - height < self.bottom:
            self.new_page()

    def draw_text(self, runs: Sequence[Run], x: float, baseline: float, size: float) -> None:
        cursor = x
        for run in runs:
            style, parts, current = run.style, [], []
            current_font = ""
            for char in run.text:
                if is_cjk_char(char):
                    font = "cjk"
                elif style.get("code"):
                    font = "code"
                elif style.get("bold"):
                    font = "bold"
                elif style.get("italic"):
                    font = "italic"
                else:
                    font = "body"
                if current_font != font and current:
                    parts.append(("".join(current), current_font))
                    current = []
                current_font = font
                current.append(char)
            if current:
                parts.append(("".join(current), current_font))
            for text, font in parts:
                width = text_width(text, size, style)
                if style.get("code"):
                    self.add(
                        f"q 0.92 0.93 0.95 rg {pdf_num(cursor - 2)} {pdf_num(baseline - 3)} "
                        f"{pdf_num(width + 4)} {pdf_num(size + 5)} re f Q"
                    )
                encoded = (
                    "<" + cjk_string(text).hex().upper() + "> Tj"
                    if font == "cjk"
                    else "(" + pdf_string(text).decode("latin-1") + ") Tj"
                )
                self.add(
                    f"BT /{font} {pdf_num(size)} Tf 0.12 0.12 0.15 rg "
                    f"{pdf_num(cursor)} {pdf_num(baseline)} Td {encoded} ET"
                )
                if style.get("link") or style.get("strike"):
                    y = baseline - 1.5 if style.get("link") else baseline + size * 0.30
                    color = "0.10 0.32 0.68" if style.get("link") else "0.12 0.12 0.15"
                    self.add(f"{color} RG 0.6 w {pdf_num(cursor)} {pdf_num(y)} {pdf_num(width)} 0 m S")
                cursor += width

    def draw_wrapped(
        self,
        runs: Sequence[Run],
        size: float,
        line_height: float,
        x: Optional[float] = None,
        width: Optional[float] = None,
    ) -> None:
        lines = wrap_runs(runs, width or self.content_width, size) or [[]]
        for line in lines:
            self.ensure_height(line_height)
            self.draw_text(line, self.margin if x is None else x, self.y - size, size)
            self.y -= line_height

    def render_heading(self, block: Block) -> None:
        size = {1: 25, 2: 20, 3: 16, 4: 14, 5: 12, 6: 11}.get(block.level, 12)
        before = 18 if block.level <= 2 else 12
        self.ensure_height(before + size + 8)
        self.y -= before
        self.draw_wrapped([Run(block.text, {"bold": True})], size, size * 1.35)
        self.y -= 8

    def render_paragraph(self, text: str, size: float = 10.5, line_height: float = 16) -> None:
        self.draw_wrapped(parse_inline(text), size, line_height)
        self.y -= 7

    def render_quote(self, text: str) -> None:
        lines = wrap_runs(parse_inline(text), self.content_width - 24, 10.5) or [[]]
        self.ensure_height(len(lines) * 16 + 8)
        self.y -= 3
        for line in lines:
            self.ensure_height(16)
            self.add(f"0.55 0.58 0.63 RG 2.2 w {pdf_num(self.margin + 6)} {pdf_num(self.y - 11)} 0 16 m S")
            self.draw_text(line, self.margin + 18, self.y - 10.5, 10.5)
            self.y -= 16
        self.y -= 7

    def render_list(self, block: Block) -> None:
        for number, item in enumerate(block.items, 1):
            prefix = f"{number}. " if block.ordered else "- "
            lines = wrap_runs(parse_inline(item), self.content_width - 18, 10.5) or [[]]
            for line_number, line in enumerate(lines):
                self.ensure_height(16)
                x = self.margin
                if line_number == 0:
                    self.draw_text([Run(prefix)], x, self.y - 10.5, 10.5)
                    x += text_width(prefix, 10.5)
                self.draw_text(line, x, self.y - 10.5, 10.5)
                self.y -= 16
        self.y -= 6

    def render_code(self, block: Block) -> None:
        self.ensure_height(20)
        self.y -= 3
        for raw_line in block.text.split("\n") or [""]:
            lines = wrap_runs([Run(raw_line.expandtabs(4), {"code": True})], self.content_width - 12, 9) or [[]]
            for line in lines:
                self.ensure_height(15)
                line_text = "".join(run.text for run in line)
                width = min(self.content_width, text_width(line_text, 9, {"code": True}) + 12)
                self.add(f"0.95 0.96 0.97 rg {pdf_num(self.margin)} {pdf_num(self.y - 3)} {pdf_num(width)} 14 re f")
                self.draw_text(line, self.margin + 6, self.y - 10, 9)
                self.y -= 14
        self.y -= 8

    def render_table(self, block: Block) -> None:
        if not block.rows:
            return
        size, columns = 9.2, len(block.rows[0])
        widths = [
            max(48.0, min(180.0, max((text_width(row[col], size) for row in block.rows), default=0) + 14))
            for col in range(columns)
        ]
        if sum(widths) > self.content_width:
            scale = self.content_width / sum(widths)
            widths = [width * scale for width in widths]
        for row_number, row in enumerate(block.rows):
            cell_lines = [
                wrap_runs(parse_inline(cell), max(20, widths[col] - 10), size) or [[]]
                for col, cell in enumerate(row)
            ]
            row_height = max(len(lines) for lines in cell_lines) * 13 + 8
            self.ensure_height(row_height)
            top, total = self.y, sum(widths)
            if row_number == 0:
                self.add(
                    f"0.90 0.92 0.95 rg {pdf_num(self.margin)} {pdf_num(top - row_height)} "
                    f"{pdf_num(total)} {pdf_num(row_height)} re f"
                )
            self.add(
                f"0.70 0.72 0.75 RG 0.5 w {pdf_num(self.margin)} {pdf_num(top - row_height)} "
                f"{pdf_num(total)} {pdf_num(row_height)} re S"
            )
            x = self.margin
            for col, lines in enumerate(cell_lines):
                if col:
                    self.add(
                        f"0.80 0.82 0.84 RG 0.4 w {pdf_num(x)} {pdf_num(top - row_height)} "
                        f"0 {pdf_num(row_height)} m S"
                    )
                style = {"bold": True} if row_number == 0 else {}
                for line_number, line in enumerate(lines):
                    styled = [Run(run.text, {**run.style, **style}) for run in line]
                    self.draw_text(styled, x + 5, top - 12 - line_number * 13, size)
                x += widths[col]
            self.y = top - row_height
        self.y -= 8

    def render_image(self, block: Block) -> None:
        path = Path(block.image_path or "")
        try:
            name, object_id, width, height = self.document.add_image(path)
        except (OSError, ValueError) as error:
            self.warnings.append(f"Could not embed image {path.name}: {error}")
            self.render_paragraph(f"[Image: {block.image_alt or path.name}]")
            return
        self.resources[name] = (name, object_id)
        scale = min(self.content_width / width, (self.page_height - self.margin * 2 - 30) / height, 1.0)
        draw_width, draw_height = width * scale, height * scale
        self.ensure_height(draw_height + 12)
        x, y = self.margin + (self.content_width - draw_width) / 2, self.y - draw_height
        self.add(
            f"q {pdf_num(draw_width)} 0 0 {pdf_num(draw_height)} {pdf_num(x)} {pdf_num(y)} cm /{name} Do Q"
        )
        self.y = y - 12
        if block.image_alt:
            self.draw_text([Run(block.image_alt, {"italic": True})], x, self.y - 9, 8.5)
            self.y -= 15

    def finish(self) -> List[Tuple[bytes, Dict[str, object]]]:
        total = len(self.pages)
        for number, page in enumerate(self.pages, 1):
            if self.footer:
                page["commands"].append(
                    f"0.45 0.47 0.50 rg BT /body 8 Tf "
                    f"{pdf_num(self.page_width - self.margin - 40)} 18 Td ({number} / {total}) Tj ET"
                )
            page["resources"]["_page"] = (self.page_width, self.page_height)
        return [
            ("\n".join(page["commands"]).encode("latin-1", "replace"), page["resources"])
            for page in self.pages
        ]


def convert(
    markdown: str,
    input_path: Path,
    output_path: Path,
    page_size: str,
    margin: float,
    footer: bool,
    title: Optional[str],
) -> List[str]:
    warnings: List[str] = []
    blocks, detected_title = parse_markdown(markdown, input_path.parent, warnings)
    document = PDFDocument(title or detected_title or input_path.stem)
    renderer = Renderer(document, PAGE_SIZES[page_size], margin, footer, warnings)
    for block in blocks:
        if block.kind == "heading":
            renderer.render_heading(block)
        elif block.kind == "paragraph":
            renderer.render_paragraph(block.text)
        elif block.kind == "quote":
            renderer.render_quote(block.text)
        elif block.kind == "list":
            renderer.render_list(block)
        elif block.kind == "code":
            renderer.render_code(block)
        elif block.kind == "table":
            renderer.render_table(block)
        elif block.kind == "rule":
            renderer.ensure_height(18)
            renderer.add(
                f"0.75 0.77 0.80 RG 0.7 w {pdf_num(margin)} "
                f"{pdf_num(renderer.y - 8)} {pdf_num(renderer.content_width)} 0 m S"
            )
            renderer.y -= 18
        elif block.kind == "image":
            renderer.render_image(block)
    document.write(renderer.finish(), output_path)
    return warnings


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert Markdown to PDF with no third-party runtime dependencies."
    )
    parser.add_argument("input", type=Path, help="Markdown source file")
    parser.add_argument("-o", "--output", type=Path, help="Output PDF path")
    parser.add_argument("--page-size", choices=sorted(PAGE_SIZES), default="a4")
    parser.add_argument("--margin", type=float, default=54, help="Page margin in points")
    parser.add_argument("--title", help="PDF document title")
    parser.add_argument("--no-footer", action="store_true", help="Do not add page numbers")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing an existing PDF")
    args = parser.parse_args(argv)
    input_path = args.input.expanduser().resolve()
    output_path = args.output.expanduser().resolve() if args.output else input_path.with_suffix(".pdf")
    if not input_path.is_file():
        parser.error(f"input file does not exist: {input_path}")
    if input_path == output_path:
        parser.error("output must be different from input")
    if args.margin < 24 or args.margin * 2 >= min(PAGE_SIZES[args.page_size]):
        parser.error("margin must leave usable space on the selected page size")
    if output_path.exists() and not args.overwrite:
        parser.error(f"output already exists (use --overwrite): {output_path}")
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        warnings = convert(
            input_path.read_text(encoding="utf-8-sig"),
            input_path,
            output_path,
            args.page_size,
            args.margin,
            not args.no_footer,
            args.title,
        )
    except (OSError, UnicodeError, ValueError, zlib.error) as error:
        print(f"md-to-pdf: error: {error}", file=sys.stderr)
        return 1
    print(f"Created {output_path}")
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
