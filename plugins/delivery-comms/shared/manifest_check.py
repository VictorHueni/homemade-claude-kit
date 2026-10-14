"""Small checker for the kit-manifest schema: type, required, properties,
additionalProperties, enum, const and pattern, nothing else. Returns a list of
error strings; an empty list means the manifest is structurally valid."""
import re

KEYWORDS = {"type", "required", "properties", "additionalProperties", "enum", "const", "pattern"}
_TYPES = {"object": dict, "string": str, "array": list, "boolean": bool, "number": (int, float), "integer": int}


def check(value, schema, path="$"):
    errors = []
    kind = schema.get("type")
    if kind and not isinstance(value, _TYPES[kind]):
        return [f"{path}: expected {kind}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: must be {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: must be one of {schema['enum']}")
    if "pattern" in schema and isinstance(value, str) and not re.search(schema["pattern"], value):
        errors.append(f"{path}: {value!r} does not match {schema['pattern']}")
    if isinstance(value, dict):
        props = schema.get("properties", {})
        for name in schema.get("required", []):
            if name not in value:
                errors.append(f"{path}: missing required key {name!r}")
        for name, sub in value.items():
            extra = schema.get("additionalProperties", True)
            if name in props:
                errors += check(sub, props[name], f"{path}.{name}")
            elif extra is False:
                errors.append(f"{path}: unknown key {name!r}")
            elif isinstance(extra, dict):
                errors += check(sub, extra, f"{path}.{name}")
    return errors
