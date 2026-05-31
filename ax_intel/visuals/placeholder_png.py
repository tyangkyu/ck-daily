from __future__ import annotations

import struct
import zlib
from pathlib import Path
from typing import Tuple


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunk(kind: bytes, data: bytes) -> bytes:
    checksum = zlib.crc32(kind + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", checksum)


def write_solid_png(path: Path, *, size: Tuple[int, int] = (1600, 900)) -> None:
    width, height = size
    # RGB gradient-like rows: dark executive background with a red signal band.
    rows = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            red_band = 80 if y > int(height * 0.72) else 0
            r = min(255, 18 + red_band + x // 24)
            g = min(255, 24 + y // 28)
            b = min(255, 38 + x // 40 + y // 45)
            row.extend((r, g, b))
        rows.append(bytes(row))

    raw = b"".join(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        PNG_SIGNATURE
        + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + _chunk(b"IDAT", zlib.compress(raw, level=9))
        + _chunk(b"IEND", b"")
    )

