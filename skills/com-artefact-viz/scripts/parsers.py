"""
parsers.py — canonical Markdown -> normalized model (com-artefact-viz).

Each parser reads exactly the Markdown shape its source skill emits and returns
a plain dict ("the model"). Renderers consume the model and never touch raw
Markdown. When a source skill's output template evolves, only the matching
parser here changes — the renderer and templates stay put.

Source shapes (see references/parsing-contract.md for the full contract):
  capability map  -> business-capability-map  (docs/business/03a-capability-map.md)
  fbs             -> spec-functional-breakdown-structure (docs/product-specs/07a-fbs.md)
  delivery roadmap-> spec-delivery-roadmap     (docs/product-specs/08a-delivery-roadmap.md)
  bmc / lean      -> business-model-canvas      (docs/business/02a-bmc.md | 02a-lean-canvas.md)

Standard library only.
"""

import re

# --------------------------------------------------------------------------- #
# Shared helpers
# --------------------------------------------------------------------------- #

CAP_ID = re.compile(r"\bC\d+(?:\.\d+)*\b")
FUNC_ID = re.compile(r"\bC\d+(?:\.\d+)+\.F\d+\b")
EPIC_ID = re.compile(r"\bE-\d+\b")

STATUS_MAP = {"✅": "shipped", "🔄": "planned", "⬜": "backlog"}


def strip_frontmatter(text):
    """Drop a leading YAML frontmatter block (--- ... ---) if present."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            nl = text.find("\n", end + 1)
            return text[nl + 1 :] if nl != -1 else ""
    return text


def doc_title(text):
    """First level-1 heading, with the artefact-type suffix kept verbatim."""
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled"


def is_placeholder(value):
    """True for scaffold placeholders the renderer should treat as empty."""
    if value is None:
        return True
    v = value.strip()
    if not v:
        return True
    low = v.lower()
    return (
        v == "_TODO_"
        or low in ("_todo_", "tbd", "_tbd_")
        or (v.startswith("[") and v.endswith("]"))
        or (v.startswith("{{") and v.endswith("}}"))
    )


def clean(value):
    """Strip markdown emphasis/link syntax for plain-text display."""
    if value is None:
        return ""
    v = value.strip()
    v = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", v)  # [text](url) -> text
    v = v.replace("**", "").replace("`", "")
    v = v.strip(" _*")
    return v


def split_h2(text):
    """Return {heading_text: body} for every level-2 (## ) section."""
    out = {}
    cur = None
    buf = []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.*\S)\s*$", line)
        if m and not line.startswith("###"):
            if cur is not None:
                out[cur] = "\n".join(buf)
            cur = m.group(1).strip()
            buf = []
        else:
            if cur is not None:
                buf.append(line)
    if cur is not None:
        out[cur] = "\n".join(buf)
    return out


def find_section(sections, *keywords):
    """First section whose heading contains all keywords (case-insensitive)."""
    for head, body in sections.items():
        low = head.lower()
        if all(k.lower() in low for k in keywords):
            return body
    return None


def first_code_block(body):
    """Contents of the first fenced ``` block in a section body."""
    if body is None:
        return None
    m = re.search(r"```[^\n]*\n(.*?)```", body, re.DOTALL)
    return m.group(1) if m else None


def parse_table(body):
    """
    Parse the first GFM table in `body`. Returns (headers, rows) where each row
    is a list of cell strings aligned to headers. Header/separator rows excluded.
    """
    if not body:
        return [], []
    lines = [l for l in body.splitlines() if l.strip().startswith("|")]
    if len(lines) < 2:
        return [], []

    def cells(line):
        parts = line.strip().strip("|").split("|")
        return [c.strip() for c in parts]

    headers = cells(lines[0])
    rows = []
    for line in lines[2:]:  # skip header + separator
        if re.match(r"^\s*\|[\s:|-]+\|?\s*$", line):  # stray separator
            continue
        c = cells(line)
        if any(cell.strip() for cell in c):
            rows.append(c)
    return headers, rows


def row_dict(headers, row):
    """Zip a row to its headers (tolerating short/long rows)."""
    d = {}
    for i, h in enumerate(headers):
        d[h] = row[i] if i < len(row) else ""
    return d


def first_status_symbol(text):
    for sym, name in STATUS_MAP.items():
        if sym in text:
            return name
    return None


# --------------------------------------------------------------------------- #
# Tree from the "Global overview" ASCII block (capability map + FBS share it)
# --------------------------------------------------------------------------- #

def parse_overview_tree(code, strip_after=None):
    """
    Parse the ASCII overview block into a nested tree keyed by capability ID.
    Nesting is derived from the ID's dot-depth (C1 -> C1.1 -> C1.1.1), which is
    far more robust than counting box-drawing indentation.

    Returns a list of root nodes: {id, label, level, children: [...]}.
    `strip_after` truncates the label at that substring (FBS appends counts).
    """
    if not code:
        return []
    by_id = {}
    order = []
    for raw in code.splitlines():
        m = CAP_ID.search(raw)
        if not m:
            continue
        cid = m.group(0)
        # Label = text after the ID, minus a leading "· " separator.
        tail = raw[m.end():]
        tail = re.sub(r"^[\s·–-]+", "", tail)
        if strip_after and strip_after in tail:
            tail = tail.split(strip_after)[0]
        label = clean(tail)
        if cid in by_id:  # ignore duplicate appearances
            continue
        node = {
            "id": cid,
            "label": "" if is_placeholder(label) else label,
            "level": cid.count("."),
            "children": [],
        }
        by_id[cid] = node
        order.append(cid)

    roots = []
    for cid in order:
        node = by_id[cid]
        parent_id = cid.rsplit(".", 1)[0] if "." in cid else None
        if parent_id and parent_id in by_id:
            by_id[parent_id]["children"].append(node)
        else:
            roots.append(node)
    return roots


# --------------------------------------------------------------------------- #
# Capability map
# --------------------------------------------------------------------------- #

def parse_capability_map(text):
    text = strip_frontmatter(text)
    sections = split_h2(text)
    title = doc_title(text)

    # L0 axis label -> default left-axis arrow text (project-overridable later).
    axis = None
    m = re.search(r"\*\*Chosen axis:\*\*\s*(.+)", text)
    if m:
        axis = clean(m.group(1))
        if is_placeholder(axis):
            axis = None

    tree = parse_overview_tree(first_code_block(find_section(sections, "global", "overview")))

    # Enrich each node from the "Capability index" table.
    index = {}
    headers, rows = parse_table(find_section(sections, "capability", "index") or "")
    if headers:
        hmap = {h.lower(): i for i, h in enumerate(headers)}
        id_i = hmap.get("id", 0)
        name_i = hmap.get("name", 1)
        imp_i = next((i for h, i in hmap.items() if "importance" in h), None)
        def_i = next((i for h, i in hmap.items() if "definition" in h), None)
        for row in rows:
            rid_m = CAP_ID.search(row[id_i] if id_i < len(row) else "")
            if not rid_m:
                continue
            rid = rid_m.group(0)
            importance = None
            if imp_i is not None and imp_i < len(row):
                raw_imp = row[imp_i].lower()
                if "/" not in raw_imp and not is_placeholder(row[imp_i]):
                    for kw in ("differentiator", "necessary", "commodity"):
                        if kw in raw_imp:
                            importance = kw
                            break
            definition = ""
            if def_i is not None and def_i < len(row) and not is_placeholder(row[def_i]):
                definition = clean(row[def_i])
            index[rid] = {
                "name": clean(row[name_i]) if name_i < len(row) else "",
                "importance": importance,
                "definition": definition,
            }

    def enrich(node):
        meta = index.get(node["id"])
        if meta:
            if not node["label"] and meta["name"]:
                node["label"] = meta["name"]
            node["importance"] = meta.get("importance")
            node["definition"] = meta.get("definition", "")
        else:
            node.setdefault("importance", None)
            node.setdefault("definition", "")
        for ch in node["children"]:
            enrich(ch)

    for n in tree:
        enrich(n)

    return {
        "kind": "capability-map",
        "title": title,
        "left_axis_label": axis,
        "tree": tree,
    }


# --------------------------------------------------------------------------- #
# Functional Breakdown Structure
# --------------------------------------------------------------------------- #

def parse_fbs(text):
    text = strip_frontmatter(text)
    sections = split_h2(text)
    title = doc_title(text)

    axis = None
    m = re.search(r"\*\*Chosen axis:\*\*\s*(.+)", text)
    if m:
        axis = clean(re.sub(r"\*\(inherited.*?\)\*", "", m.group(1)))
        if is_placeholder(axis):
            axis = None

    tree = parse_overview_tree(
        first_code_block(find_section(sections, "global", "overview")),
        strip_after="(functionalities",
    )

    # Functionalities live in per-capability tables anywhere in the doc.
    funcs_by_cap = {}
    for body in sections.values():
        headers, rows = parse_table(body)
        if not headers:
            continue
        lower = [h.lower() for h in headers]
        if "id" not in lower or not any("functional" in h for h in lower):
            continue
        id_i = lower.index("id")
        name_i = next((i for i, h in enumerate(lower) if "functional" in h), 1)
        status_i = next((i for i, h in enumerate(lower) if "status" in h), None)
        vs_i = next((i for i, h in enumerate(lower) if "vs" in h or "stage" in h), None)
        for row in rows:
            fid_m = FUNC_ID.search(row[id_i] if id_i < len(row) else "")
            if not fid_m:
                continue
            fid = fid_m.group(0)
            cap_id = fid.rsplit(".F", 1)[0]
            status = None
            if status_i is not None and status_i < len(row):
                status = first_status_symbol(row[status_i])
            vs = ""
            if vs_i is not None and vs_i < len(row) and not is_placeholder(row[vs_i]):
                vs = clean(row[vs_i])
            funcs_by_cap.setdefault(cap_id, []).append({
                "id": fid,
                "label": clean(row[name_i]) if name_i < len(row) else "",
                "status": status or "backlog",
                "vs": vs,
            })

    # Attach functionalities to their leaf capability nodes.
    def attach(node):
        for ch in node["children"]:
            attach(ch)
        node["functionalities"] = funcs_by_cap.get(node["id"], [])

    for n in tree:
        attach(n)

    counts = {"shipped": 0, "planned": 0, "backlog": 0}
    for flist in funcs_by_cap.values():
        for f in flist:
            counts[f["status"]] = counts.get(f["status"], 0) + 1

    return {
        "kind": "fbs",
        "title": title,
        "left_axis_label": axis,
        "tree": tree,
        "counts": counts,
    }


# --------------------------------------------------------------------------- #
# Delivery roadmap
# --------------------------------------------------------------------------- #

def _pain_level(text):
    low = (text or "").lower()
    for level in ("critical", "high", "medium", "low"):
        if level in low:
            return level
    return None


def parse_roadmap(text):
    text = strip_frontmatter(text)
    sections = split_h2(text)
    title = doc_title(text)

    # Walking skeleton -------------------------------------------------------
    ws_body = find_section(sections, "walking", "skeleton") or ""
    ws = {"hypothesis": "", "value_stream": "", "can": [], "cannot": []}
    m = re.search(r"\*\*Hypothesis[^:]*:\*\*\s*(.+)", ws_body)
    if m and not is_placeholder(m.group(1)):
        ws["hypothesis"] = clean(m.group(1))
    m = re.search(r"\*\*Value stream[^:]*:\*\*\s*(.+)", ws_body)
    if m and not is_placeholder(m.group(1)):
        ws["value_stream"] = clean(m.group(1))
    # "can" / "cannot yet" bullet lists
    can_mode = None
    for line in ws_body.splitlines():
        cl = line.strip()
        if "can:" in cl.lower() and "cannot" not in cl.lower():
            can_mode = "can"
            continue
        if "cannot" in cl.lower():
            can_mode = "cannot"
            continue
        bullet = re.match(r"^(?:[-*]|\d+\.)\s+(.*)", cl)
        if bullet and can_mode and not is_placeholder(bullet.group(1)):
            ws[can_mode].append(clean(bullet.group(1)))

    # Phase plan -------------------------------------------------------------
    phases = []
    headers, rows = parse_table(find_section(sections, "phase", "plan") or "")
    if headers:
        lower = [h.lower() for h in headers]
        p_i = 0
        e_i = next((i for i, h in enumerate(lower) if "epic" in h), 1)
        vs_i = next((i for i, h in enumerate(lower) if "value stream" in h or "operational" in h), None)
        g_i = next((i for i, h in enumerate(lower) if "goal" in h), None)
        for row in rows:
            name = clean(row[p_i]) if p_i < len(row) else ""
            if is_placeholder(name):
                continue
            phases.append({
                "name": name,
                "epics_raw": clean(row[e_i]) if e_i < len(row) else "",
                "vs_operational": clean(row[vs_i]) if vs_i is not None and vs_i < len(row) else "",
                "goal": clean(row[g_i]) if g_i is not None and g_i < len(row) else "",
                "epics": [],
            })

    # Epic table -------------------------------------------------------------
    epics = []
    epic_by_id = {}
    headers, rows = parse_table(find_section(sections, "epic", "table") or "")
    if headers:
        lower = [h.lower() for h in headers]
        def col(*names):
            for i, h in enumerate(lower):
                if any(n in h for n in names):
                    return i
            return None
        c_id = col("id")
        c_name = col("epic name", "name")
        c_vs = col("vs anchor", "anchor")
        c_pain = col("pain")
        c_pers = col("persona")
        c_caps = col("capabilit")
        c_phase = col("phase")
        c_prd = col("prd")
        c_status = col("status")
        for row in rows:
            d = row_dict(headers, row)
            eid_m = EPIC_ID.search(row[c_id]) if c_id is not None and c_id < len(row) else None
            if not eid_m:
                continue
            eid = eid_m.group(0)
            def g(i):
                return clean(row[i]) if i is not None and i < len(row) and not is_placeholder(row[i]) else ""
            epic = {
                "id": eid,
                "name": g(c_name),
                "vs_anchor": g(c_vs),
                "pain": _pain_level(row[c_pain]) if c_pain is not None and c_pain < len(row) else None,
                "personas": g(c_pers),
                "capabilities": g(c_caps),
                "phase": g(c_phase),
                "prd": g(c_prd),
                "status": first_status_symbol(row[c_status]) if c_status is not None and c_status < len(row) else None,
                "value_statement": "",
                "fbs_scope": [],
            }
            epics.append(epic)
            epic_by_id[eid] = epic

    # Per-epic sections (### E-NN) -> value statement + FBS scope -------------
    epic_sections = re.split(r"^###\s+", find_section(sections, "epics") or "", flags=re.MULTILINE)
    for chunk in epic_sections:
        eid_m = EPIC_ID.search(chunk[:40])
        if not eid_m:
            continue
        epic = epic_by_id.get(eid_m.group(0))
        if not epic:
            continue
        m = re.search(r"\*\*Value statement:\*\*\s*(.+)", chunk)
        if m and not is_placeholder(m.group(1)):
            epic["value_statement"] = clean(m.group(1))
        _, frows = parse_table(chunk)
        for r in frows:
            fid_m = FUNC_ID.search(" ".join(r))
            if not fid_m:
                continue
            epic["fbs_scope"].append({
                "id": fid_m.group(0),
                "label": clean(r[1]) if len(r) > 1 else "",
                "status": first_status_symbol(" ".join(r)) or "backlog",
            })

    # Bucket epics into phases. Prefer the epic's own Phase column; fall back to
    # matching epic IDs named in the phase-plan row.
    def phase_key(name):
        m = re.search(r"(mvp|phase\s*\d+|\d+)", name.lower())
        return m.group(0).replace(" ", "") if m else name.lower()

    if phases:
        index = {phase_key(p["name"]): p for p in phases}
        for epic in epics:
            placed = False
            pk = phase_key(epic["phase"]) if epic["phase"] else None
            if pk and pk in index:
                index[pk]["epics"].append(epic)
                placed = True
            if not placed:
                for p in phases:
                    if epic["id"] in p["epics_raw"]:
                        p["epics"].append(epic)
                        placed = True
                        break
            if not placed and phases:
                phases[0]["epics"].append(epic)
    else:
        # No phase plan: synthesize columns from distinct Phase values.
        seen = {}
        for epic in epics:
            key = epic["phase"] or "Unscheduled"
            if key not in seen:
                seen[key] = {"name": key, "epics": [], "vs_operational": "", "goal": "", "epics_raw": ""}
                phases.append(seen[key])
            seen[key]["epics"].append(epic)

    return {
        "kind": "delivery-roadmap",
        "title": title,
        "walking_skeleton": ws,
        "phases": phases,
        "epic_count": len(epics),
    }


# --------------------------------------------------------------------------- #
# Business Model Canvas / Lean Canvas
# --------------------------------------------------------------------------- #

# grid-area name per canonical block key, for each variant.
BMC_AREAS = {
    "8": "kp", "7": "ka", "6": "kr", "2": "vp", "4": "cr",
    "3": "ch", "1": "cs", "9": "cost", "5": "rev",
}
LEAN_AREAS = {
    "8'": "prob", "7'": "sol", "6'": "metrics", "2": "uvp", "4'": "adv",
    "3": "ch", "1": "cs", "9": "cost", "5": "rev",
}


def parse_bmc(text):
    text = strip_frontmatter(text)
    title = doc_title(text)

    variant = "BMC"
    m = re.search(r"\*\*Variant chosen:\*\*\s*(.+)", text)
    if m and "lean" in m.group(1).lower():
        variant = "Lean Canvas"
    elif "lean canvas" in title.lower():
        variant = "Lean Canvas"

    # Only parse blocks before the deep-dives / VPC template sections.
    cut = len(text)
    for marker in ("## Value Proposition Deep-dives", "## Inter-block", "# VPC Companion"):
        idx = text.find(marker)
        if idx != -1:
            cut = min(cut, idx)
    body = text[:cut]

    blocks = []
    # Block headings look like "### 1 · Customer Segments" or "### 4' · Unfair Advantage".
    parts = re.split(r"^###\s+", body, flags=re.MULTILINE)
    for chunk in parts[1:]:
        head_line = chunk.splitlines()[0]
        hm = re.match(r"(\d+'?)\s*·\s*(.+)", head_line.strip())
        if not hm:
            continue
        key = hm.group(1)
        name = clean(re.sub(r"\*\(.*?\)\*", "", hm.group(2)))
        # Bullets (skip blockquote notes and italics-only guidance lines).
        bullets = []
        for line in chunk.splitlines()[1:]:
            bm = re.match(r"^\s*[-*]\s+(.*)", line)
            if not bm:
                continue
            val = bm.group(1).strip()
            if is_placeholder(val):
                continue
            bullets.append(clean(val))
        confidence = None
        cm = re.search(r"\*\*Confidence:\*\*\s*(\w+)", chunk)
        if cm:
            confidence = cm.group(1).strip().lower()
        areas = LEAN_AREAS if variant == "Lean Canvas" else BMC_AREAS
        blocks.append({
            "key": key,
            "name": name,
            "bullets": bullets,
            "confidence": confidence,
            "area": areas.get(key),
        })

    # Keep only blocks that belong to the chosen variant's grid (drop the
    # alternate variant's blocks, e.g. Lean's 4'/6'/7'/8' in a BMC doc).
    blocks = [b for b in blocks if b["area"]]

    return {
        "kind": "bmc",
        "title": title,
        "variant": variant,
        "blocks": blocks,
    }


# --------------------------------------------------------------------------- #
# Dispatch by source path / content
# --------------------------------------------------------------------------- #

PARSERS = {
    "capability-map": parse_capability_map,
    "fbs": parse_fbs,
    "delivery-roadmap": parse_roadmap,
    "bmc": parse_bmc,
}


def detect_kind(path, text):
    """Guess the artefact type from filename, then from content headings."""
    p = path.lower()
    if "capability-map" in p or "capability_map" in p:
        return "capability-map"
    if "fbs" in p or "functional-breakdown" in p:
        return "fbs"
    if "roadmap" in p:
        return "delivery-roadmap"
    if "lean-canvas" in p or "bmc" in p or "canvas" in p:
        return "bmc"
    head = text[:4000].lower()
    if "business capability map" in head:
        return "capability-map"
    if "functional breakdown structure" in head:
        return "fbs"
    if "delivery roadmap" in head:
        return "delivery-roadmap"
    if "business model canvas" in head or "lean canvas" in head:
        return "bmc"
    return None
