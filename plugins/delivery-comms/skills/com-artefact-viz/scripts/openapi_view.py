"""
openapi_view.py — an OpenAPI document as an HTML viewer in the design's roles.

One card per operation (method, path, summary, request body, responses, each with its schema table and its
examples), then the document itself with a copy control. It follows local `$ref`. What it does not render
(parameters, composed schemas) is said on the operation, never dropped silently.

The markup uses classes only; the view's stylesheet colours them with contract roles. Standard library only
for a JSON document; a YAML document needs PyYAML.
"""

import html
import json
import os

NAMES = ("openapi.json", "openapi.yaml", "openapi.yml")
COMPOSED = ("allOf", "oneOf", "anyOf")
METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")


class OpenApiError(Exception):
    """The document is missing or cannot be read; the message says what to do."""


def load(folder):
    """(document, its source text, its file name) for the OpenAPI document of `folder`; JSON first."""
    for name in NAMES:
        path = os.path.join(folder, name)
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8") as fh:
            source = fh.read()
        if name.endswith(".json"):
            try:
                return json.loads(source), source, name
            except json.JSONDecodeError as exc:
                raise OpenApiError(f"{name} is not valid JSON: {exc}")
        try:
            import yaml
        except ImportError:
            raise OpenApiError(f"{name} is YAML and PyYAML is not installed: install it (pip install pyyaml), "
                               "or give the document as openapi.json")
        try:
            return yaml.safe_load(source), source, name
        except yaml.YAMLError as exc:
            raise OpenApiError(f"{name} is not valid YAML: {exc}")
    raise OpenApiError("the OpenAPI slot needs a document in the slice folder: openapi.json, or openapi.yaml "
                       "with PyYAML installed")


def esc(value):
    return html.escape(str(value), quote=True)


def resolve(doc, schema):
    """Follow a local $ref to its schema; a reference that leads nowhere resolves to an empty schema."""
    seen = set()
    while isinstance(schema, dict) and "$ref" in schema and schema["$ref"] not in seen:
        seen.add(schema["$ref"])
        node = doc
        for part in schema["$ref"].removeprefix("#/").split("/"):
            node = node.get(part, {}) if isinstance(node, dict) else {}
        schema = node
    return schema if isinstance(schema, dict) else {}


def schema_rows(doc, schema, prefix="", depth=0):
    """One row per property, nested objects flattened with dotted names."""
    schema = resolve(doc, schema)
    rows = []
    if depth > 6:   # a schema that refers to itself
        return rows
    for name, prop in schema.get("properties", {}).items():
        prop = resolve(doc, prop)
        kind = prop.get("type", "object")
        if "enum" in prop:
            kind = f"{kind}, one of " + ", ".join(str(v) for v in prop["enum"])
        required = "yes" if name in schema.get("required", []) else "no"
        rows.append((prefix + name, kind, required, prop.get("description", "")))
        rows.extend(schema_rows(doc, prop, prefix + name + ".", depth + 1))
    return rows


def composed(doc, schema, depth=0):
    """True when the schema, or one it reaches, is an allOf, oneOf or anyOf composition."""
    schema = resolve(doc, schema)
    if depth > 6:
        return False
    if any(key in schema for key in COMPOSED):
        return True
    children = list(schema.get("properties", {}).values()) + ([schema["items"]] if "items" in schema else [])
    return any(composed(doc, child, depth + 1) for child in children)


def content_html(doc, content):
    """The schema table and the examples of each media type of a body."""
    out = []
    for media, body in (content or {}).items():
        out.append(f'<span class="chip ref">{esc(media)}</span>')
        rows = schema_rows(doc, body.get("schema", {}))
        if rows:
            cells = "".join(
                f'<tr><td class="key">{esc(n)}</td><td class="mono">{esc(k)}</td><td>{esc(r)}</td><td>{esc(d)}</td></tr>'
                for n, k, r, d in rows)
            out.append('<div class="scroll"><table><thead><tr><th>Field</th><th>Type</th><th>Required</th>'
                       f"<th>Description</th></tr></thead><tbody>{cells}</tbody></table></div>")
        for example in body.get("examples", {}).values():
            if example.get("summary"):
                out.append(f'<p class="note">{esc(example["summary"])}</p>')
            out.append(f"<pre>{esc(json.dumps(example.get('value'), indent=2))}</pre>")
    return "".join(out)


def not_shown(doc, item, op):
    """What this viewer leaves out of an operation, as a sentence, or '' when it renders all of it."""
    missing = []
    if item.get("parameters") or op.get("parameters"):
        missing.append("parameters")
    bodies = [op.get("requestBody", {})] + list(op.get("responses", {}).values())
    schemas = [media.get("schema", {}) for body in bodies if isinstance(body, dict)
               for media in body.get("content", {}).values()]
    if any(composed(doc, schema) for schema in schemas):
        missing.append("composed schemas (allOf, oneOf, anyOf)")
    return "Not shown: " + "; ".join(missing) + ". Read them in the document below." if missing else ""


def render(doc, source, name):
    """The viewer: a head, one card per operation, then the document itself."""
    info = doc.get("info", {})
    out = ['<div class="oas">',
           f'<div class="oas-head"><span class="chip ref">OpenAPI {esc(doc.get("openapi", ""))}</span>'
           f'<span>{esc(info.get("title", ""))} · version {esc(info.get("version", ""))}</span></div>']
    if info.get("description"):
        out.append(f'<p class="note">{esc(info["description"])}</p>')
    for path, item in doc.get("paths", {}).items():
        for method, op in item.items():
            if method not in METHODS:
                continue
            out.append(f'<details class="op" open><summary><span class="method">{esc(method.upper())}</span>'
                       f'<span class="path">{esc(path)}</span><span class="op-sum">{esc(op.get("summary", ""))}</span>'
                       '</summary><div class="op-body">')
            if op.get("description"):
                out.append(f"<p>{esc(op['description'])}</p>")
            left_out = not_shown(doc, item, op)
            if left_out:
                out.append(f'<p class="note">{esc(left_out)}</p>')
            body = op.get("requestBody")
            if body:
                need = "required" if body.get("required") else "optional"
                out.append(f'<div class="op-part"><h4>Request body<span class="op-sum">{need}</span></h4>'
                           f'{content_html(doc, body.get("content"))}</div>')
            out.append('<div class="op-part"><h4>Responses</h4>')
            for status, response in op.get("responses", {}).items():
                out.append(f'<div class="resp"><p><span class="status">{esc(status)}</span> '
                           f'{esc(response.get("description", ""))}</p>{content_html(doc, response.get("content"))}</div>')
            out.append("</div></div></details>")
    out.append(f'<details class="raw"><summary><span class="path">{esc(name)}</span>'
               '<span class="op-sum">The document itself</span></summary><div class="op-body">'
               '<button class="copy" type="button" data-copy="openapi-source">Copy the document</button>'
               f'<pre id="openapi-source">{esc(source)}</pre></div></details></div>')
    return "".join(out)
