#!/usr/bin/env python3
"""Stamp a Chromium PDF with the source date instead of the render time, without moving a byte.

Chromium's PDF backend (Skia) writes the wall-clock render time into the document Info dictionary as
`/CreationDate (D:YYYYMMDDHHmmSS+00'00')` and the same `/ModDate`; nothing else in its output depends on the
clock (no document /ID, no XMP metadata). `normalise` rewrites both values in place with the date from
shared/source_date.py, in the same 23-byte form, so every byte offset and the cross-reference table stay
valid. Anything else (a missing date, another shape, an /ID or XMP) is refused rather than resized or left
to vary: the render would no longer be reproducible and must say so.
"""
import datetime
import os
import re
from pathlib import Path

_DATE = re.compile(rb"(/(CreationDate|ModDate)\s*\()(D:[^)]*)\)")
_SHAPE = re.compile(rb"D:\d{14}[+-]\d{2}'\d{2}'")


class PdfDateError(ValueError):
    """The PDF does not carry the two Info dates in the shape Skia writes, or carries more that varies."""


def pdf_date(when):
    """`when` (an aware datetime) in the PDF date form Skia writes, in UTC."""
    return when.astimezone(datetime.timezone.utc).strftime("D:%Y%m%d%H%M%S+00'00'").encode("ascii")


def normalise_bytes(data, when):
    """Return `data` with /CreationDate and /ModDate set to `when`; same length, nothing else touched."""
    if re.search(rb"/ID\s*\[", data) or b"/Metadata" in data:
        raise PdfDateError("the PDF carries a document /ID or XMP metadata; only the Info dates are normalised")
    found = [(m.group(2), m.group(3)) for m in _DATE.finditer(data)]
    names = sorted(name for name, _ in found)
    if names != [b"CreationDate", b"ModDate"]:
        raise PdfDateError(f"expected one /CreationDate and one /ModDate, found {[n.decode() for n in names]}")
    stamp = pdf_date(when)
    for name, value in found:
        if not _SHAPE.fullmatch(value) or len(value) != len(stamp):
            raise PdfDateError(f"/{name.decode()} {value.decode(errors='replace')!r} is not the D:YYYYMMDDHHmmSS+HH'mm' "
                               "form; it cannot be rewritten in place")
    out = _DATE.sub(lambda m: m.group(1) + stamp + b")", data)
    assert len(out) == len(data)
    return out


def normalise(path, when):
    """Rewrite the PDF at `path` in place (temp file, then rename) with the Info dates set to `when`."""
    path = Path(path)
    data = normalise_bytes(path.read_bytes(), when)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)
