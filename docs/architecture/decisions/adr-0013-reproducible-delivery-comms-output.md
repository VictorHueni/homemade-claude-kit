---
title: Reproducible delivery-comms Output, Dated from the Source
status: active
owner: Victor Hueni
last_reviewed: 2026-10-14
review_interval: 180d
---

# Reproducible delivery-comms Output, Dated from the Source

Date: 2026-10-14

## Context and Problem Statement

The delivery-comms renderers (`com-slide-deck`, `com-release-note`, `com-artefact-viz`) produced different bytes on every render of an unchanged source. Chromium stamps its render time into the PDF `/CreationDate` and `/ModDate`, the release note printed today's date, and the printed source path depended on the folder the render ran from (issue #106).

`util-provenance` timestamps the SHA-256 digest of exact bytes. An idle re-render therefore leaves a token that proves a file which no longer exists, and the new file carries no proof. Re-timestamping cannot repair this: a new token carries today's date, and the value of the record was the original date.

## Decision Drivers

- Re-rendering an unchanged source is an idempotent act and must not void evidence.
- A consumer must be able to tell whether a committed PDF is current by re-rendering and comparing bytes.
- A date in the output still says something true about the content.

## Considered Options

1. **Fixed stamp:** normalise the PDF dates to a constant. Reproducible, but the date says nothing.
2. **Stamp derived from the source** (chosen): every date a renderer prints or embeds comes from `SOURCE_DATE_EPOCH` when set, else the last commit date of the source files, else their newest modification time.
3. **Document the constraint only:** leaves the trap live but named.
4. **Do nothing.**

## Decision Outcome

Chosen option 2, shipped in delivery-comms 2.0.0 (Plan-0005 increment 10).

1. `shared/source_date.py` gives the date; `shared/pdf_dates.py` rewrites the PDF `/CreationDate` and `/ModDate` in place with a same-length value, and refuses a PDF that varies in any other way (an `/ID`, XMP metadata, another date shape).
2. A printed source path is relative to the source's git repository root, else the file name alone (`shared/source_path.py`).
3. Two renders of the same source and design give byte-identical HTML, PDF and provenance files.

### Cutover for existing provenance records

Adopting 2.0.0 changes the bytes of every PDF a delivery-comms renderer has produced once, so a `util-provenance` token over a PDF rendered before 2.0.0 does not match the next render.

1. **Such tokens are superseded, not invalid.** A token still proves that the exact bytes it names existed at its date. Keep those bytes: the record's git blob OID anchors them in history, or keep the timestamped file itself.
2. **Do not re-render over a timestamped file** without keeping its bytes. Re-timestamp the new render if proof of the new copy is needed, and note in the old record that the new one supersedes it.
3. **Each consumer repository** handles its own records in its 2.0 migration; the kit does not touch them. The 2.0.0 release notes name this cutover.

### Positive Consequences

- An idle rebuild changes no byte, so a timestamp taken after 2.0.0 stays valid across rebuilds.
- A CI check can re-render and compare bytes to prove a committed PDF is current.
- Git stores no new blob for an unchanged PDF.

### Negative Consequences

- Every existing PDF changes bytes once at adoption, so existing tokens need the cutover above.
- A Chromium release that starts writing an `/ID` or XMP metadata fails the render until `pdf_dates.py` normalises it too.
- The output date is the source's last commit, not the render date; a render of an old source carries the old date.
