#!/usr/bin/env python3
"""Minimal PNG and ICO writers -- standard library only.

The site has no third-party build dependencies, and a favicon is sixteen
coloured squares. `zlib` and `struct` are enough.

A real `/favicon.ico` matters more than it sounds. A 404 there is one of
the small roughnesses that makes a brand-new domain look shabbier to
automated filters and proxies than it needs to, and it is the one thing
on the page a corporate gateway reliably checks for.

Public API:

    encode_png(size, rgba)                 -> bytes
    encode_ico([(size, png), ...])          -> bytes
    raster_grid(cells, grid, size, colour,
                background=None, ss=4)       -> bytes (RGBA)

`cells` is a set of (col, row) pairs on a `grid` x `grid` lattice, the
same construction the SVG favicon uses, so the ICO and the SVG are the
same mark at different fidelities rather than two drawings.
"""

import math
import struct
import zlib


# --------------------------------------------------------------------------
# PNG
# --------------------------------------------------------------------------

def _chunk(tag, data):
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def encode_png(size, rgba):
    """Encode a square RGBA buffer as a PNG.

    `rgba` is `size * size * 4` bytes, row-major, 8 bits per channel.
    """
    stride = size * 4
    if len(rgba) != stride * size:
        raise ValueError("rgba buffer is the wrong size for this image")

    raw = bytearray()
    for y in range(size):
        raw.append(0)  # filter type 0 (none) -- keeps the output stable
        raw += rgba[y * stride:(y + 1) * stride]

    return b"".join([
        b"\x89PNG\r\n\x1a\n",
        _chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)),
        _chunk(b"IDAT", zlib.compress(bytes(raw), 9)),
        _chunk(b"IEND", b""),
    ])


# --------------------------------------------------------------------------
# ICO
# --------------------------------------------------------------------------

def encode_ico(images):
    """Wrap PNG-encoded images in an ICO container.

    `images` is a list of (size, png_bytes). PNG-in-ICO is understood by
    every browser that has mattered for years, and it keeps the bytes
    identical to the PNG we already build.
    """
    count = len(images)
    if not count:
        raise ValueError("an ICO needs at least one image")

    header = struct.pack("<HHH", 0, 1, count)
    offset = 6 + 16 * count
    entries = bytearray()
    blobs = bytearray()

    for size, png in images:
        dim = 0 if size >= 256 else size  # 0 means 256 in the ICO format
        entries += struct.pack(
            "<BBBBHHII", dim, dim, 0, 0, 1, 32, len(png), offset
        )
        blobs += png
        offset += len(png)

    return bytes(header + entries + blobs)


# --------------------------------------------------------------------------
# Rasterising
# --------------------------------------------------------------------------

# The SVG favicon is a 64x64 box with 2px of margin, 10px cells and 2px
# gaps. Expressed as ratios so every raster size is the same drawing.
MARGIN_RATIO = 2 / 64
CELL_RATIO = 10 / 11.6  # cell width as a fraction of the lattice pitch


def raster_grid(cells, grid, size, colour, background=None, ss=4):
    """Rasterise a lattice of cells into an RGBA buffer.

    `cells` is a set of (col, row) pairs. `grid` is the lattice size.
    `colour` is an (r, g, b) tuple. `background` is an optional (r, g, b)
    tuple -- when given, the result is fully opaque and the cells are
    blended over it, which is what iOS wants from a touch icon.

    Coverage is computed analytically per pixel rather than by sampling,
    so the edges are clean and the build is deterministic.
    """
    margin = size * MARGIN_RATIO
    content = size - 2 * margin
    pitch = content / grid
    cell_w = pitch * CELL_RATIO
    cell_h = pitch * CELL_RATIO

    by_row = {}
    for col, row in cells:
        by_row.setdefault(row, []).append(col)

    out = bytearray()
    for py in range(size):
        # Coverage per output pixel on this row.
        cov = [0.0] * size

        for sy in range(ss):
            y = py + (sy + 0.5) / ss
            fy = y - margin
            if fy < 0 or fy >= content:
                continue
            row = int(fy / pitch)
            if (fy - row * pitch) >= cell_h:
                continue  # in the gap

            for col in by_row.get(row, ()):
                x0 = margin + col * pitch
                x1 = x0 + cell_w
                first = max(0, int(x0))
                last = min(size - 1, int(x1) + 1)
                for px in range(first, last + 1):
                    # How many of this pixel's ss sample points fall
                    # inside [x0, x1)?
                    lo = math.ceil(x0 * ss - 0.5 - px * ss)
                    hi = math.ceil(x1 * ss - 0.5 - px * ss)
                    lo = max(lo, 0)
                    hi = min(hi, ss)
                    if hi > lo:
                        cov[px] += (hi - lo) / (ss * ss)

        for px in range(size):
            a = cov[px]
            if background is None:
                out += bytes((colour[0], colour[1], colour[2],
                              int(round(a * 255))))
            else:
                out += bytes((
                    int(round(background[0] + (colour[0] - background[0]) * a)),
                    int(round(background[1] + (colour[1] - background[1]) * a)),
                    int(round(background[2] + (colour[2] - background[2]) * a)),
                    255,
                ))

    return bytes(out)


def hex_rgb(value):
    """'#FD447E' -> (253, 68, 126)"""
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
