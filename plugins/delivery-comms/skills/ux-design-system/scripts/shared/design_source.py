#!/usr/bin/env python3
"""Resolve the design a render uses: a pinned design-system package, a local folder, or the base theme.

Resolution order: an explicit folder, then the `docs/ux/package.json` pin found by walking up from the
source (at most 8 levels), then the kit's base theme. A legacy token file with no pin is refused. The
pinned version is downloaded from the npm registry (no npm, no node_modules), verified against npm's
`dist.integrity`, extracted with the tar `data` filter and cached per machine.

Text on a fill: a contract pair whose `fg` is a list passes when any of its roles reaches WCAG AA on the fill.
For each such pair the resolver appends `--kit-on-<fill>: var(<first role in list order that passes>)` to the
CSS of the module that owns the fill role, so renderers paint that text with `var(--kit-on-<fill>)`.

As a command, for generators outside the kit:
    design_source.py css [--module core,dataviz] [--design-system DIR | --from DIR]
    design_source.py fonts | provenance  [same selection]
"""
import argparse
import base64
import hashlib
import json
import mimetypes
import os
import re
import shutil
import sys
import tarfile
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import manifest_check  # noqa: E402
from source_path import display_path  # noqa: E402  (provenance names a folder the same on every machine)

MAX_LEVELS = 8
LEGACY = ("docs/ux/tokens.css", "docs/design/tokens.css")
DEFAULT_REGISTRY = "https://registry.npmjs.org"
AA = 4.5
MIME = {".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf", ".otf": "font/otf", ".svg": "image/svg+xml"}


class DesignError(Exception):
    """A refusal the user must act on; `code` is the process exit code."""

    def __init__(self, message, code=2):
        super().__init__(message)
        self.code = code


@dataclass
class Design:
    css: dict            # module -> assembled CSS (base first, then the package)
    fonts: list          # @font-face rules from the provided modules, url() inlined
    brand: dict          # brand role -> CSS value, assets inlined
    exceptions: dict     # named local exceptions a document may declare -> reason
    provenance: dict     # which module came from where; printed and written next to the output
    root: Optional[Path] = None  # package folder, None for the base theme


def _contract_file(name):
    """The contract JSON beside this file in a skill's copy, else in the canonical contract/ folder."""
    beside = HERE / name
    return beside if beside.is_file() else HERE.parent / "contract" / name


def _contract():
    return json.loads(_contract_file("modules.json").read_text(encoding="utf-8"))


def dark_mirror(contract):
    """{light role: its --dark- twin} for every role of the modules the `dark` module mirrors, in contract order."""
    mirror = contract["modules"]["dark"]["mirror"]
    return {role: "--dark-" + role[2:] for module in mirror["modules"]
            for role in contract["modules"][module]["roles"] if role not in mirror["except"]}


def _legacy_message(path):
    return (f"{path} is a legacy token file (core only) and is no longer read. Move to a design system with one of:\n"
            "  ux-design-system point               pin a published design-system package in docs/ux/package.json\n"
            "  ux-design-system subset              author a subset design for this project\n"
            "  ux-design-system subset --from-legacy   turn this file into a validated subset")


def _read_json(path, what):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DesignError(f"cannot read {what} {path}: {exc}")


# --- finding the source ---------------------------------------------------------------------------

def _find_source(start):
    """Return (pin_file, legacy_file) of the nearest folder level that has either, else (None, None)."""
    here = start if start.is_dir() else start.parent
    here = here.resolve()
    for level in [here, *here.parents][: MAX_LEVELS + 1]:
        pin = level / "docs/ux/package.json"
        legacy = next((level / rel for rel in LEGACY if (level / rel).is_file()), None)
        if pin.is_file() or legacy:
            return (pin if pin.is_file() else None), legacy
    return None, None


def _pin_target(pin_file):
    deps = _read_json(pin_file, "pin").get("dependencies", {})
    if len(deps) != 1:
        raise DesignError(f"{pin_file} must declare exactly one dependency, the design system (found {len(deps)})")
    name, spec = next(iter(deps.items()))
    if spec.startswith("file:"):
        return name, (pin_file.parent / spec[5:]).resolve(), None
    if not re.fullmatch(r"\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?", spec):
        raise DesignError(f"{pin_file}: pin {name} to an exact version (got {spec!r}); a range lets installs drift "
                          "and Dependabot cannot propose bumps")
    return name, None, spec


# --- registry, integrity, cache -------------------------------------------------------------------

def _get(url):
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read()
    except (urllib.error.URLError, OSError) as exc:
        raise DesignError(f"cannot fetch {url}: {exc}")


def _integrity(data):
    return "sha512-" + base64.b64encode(hashlib.sha512(data).digest()).decode()


def _cache_root():
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "delivery-comms" / "design-systems"


def _fetch_package(name, version):
    folder = _cache_root() / f"{name}@{version}"
    kept, sealed = folder / "package.tgz", folder / "integrity"
    if folder.is_dir():
        if _integrity(kept.read_bytes()) != sealed.read_text().strip():
            raise DesignError(f"integrity check failed for the cached {name}@{version} ({kept}); delete {folder}")
        return _package_root(folder / "package")
    registry = os.environ.get("DELIVERY_COMMS_NPM_REGISTRY", DEFAULT_REGISTRY).rstrip("/")
    try:
        meta = json.loads(_get(f"{registry}/{name}/{version}"))
        tarball_url, expected = meta["dist"]["tarball"], meta["dist"]["integrity"]
    except (ValueError, KeyError):
        raise DesignError(f"the registry has no usable {name}@{version} (no dist.tarball or dist.integrity)")
    if not expected.startswith("sha512-"):
        raise DesignError(f"{name}@{version}: registry integrity {expected!r} is not sha512")
    data = _get(tarball_url)
    if _integrity(data) != expected:
        raise DesignError(f"integrity check failed for {name}@{version}: the tarball does not match the registry's "
                          "dist.integrity; nothing was cached")
    folder.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".staging-", dir=folder.parent))
    try:
        (staging / "package.tgz").write_bytes(data)
        (staging / "integrity").write_text(expected)
        try:
            with tarfile.open(staging / "package.tgz", "r:gz") as tf:
                tf.extractall(staging / "package", filter="data")
        except (tarfile.TarError, OSError) as exc:
            raise DesignError(f"refusing {name}@{version}: unsafe or unreadable tarball ({exc})")
        try:
            os.rename(staging, folder)
        except OSError:
            if not folder.is_dir():
                raise
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    return _package_root(folder / "package")


def _package_root(extracted):
    top = [p for p in extracted.iterdir()]
    return top[0] if len(top) == 1 and top[0].is_dir() else extracted


# --- package contents -----------------------------------------------------------------------------

def _export_path(root, exports, key):
    """Map a package export name (`./css/type.css`) to a file, exact or through a `*` pattern."""
    target = exports.get(key)
    if target is None:
        for pattern, value in exports.items():
            if "*" in pattern:
                head, _, tail = pattern.partition("*")
                if key.startswith(head) and key.endswith(tail) and len(key) >= len(head) + len(tail):
                    target = value.replace("*", key[len(head): len(key) - len(tail)])
                    break
    if not isinstance(target, str):
        raise DesignError(f"{key} is not in the package's exports; the kit reads only published export names")
    return _inside(root, root / target)


def _inside(root, path):
    path = path.resolve()
    if root.resolve() not in path.parents:
        raise DesignError(f"{path} lies outside the design-system package")
    if path.is_dir():
        raise DesignError(f"{path.relative_to(root.resolve())} is a folder; an export names one file (contract/README.md)")
    if not path.is_file():
        raise DesignError(f"{path.relative_to(root.resolve())} is missing from the design-system package")
    return path


def _data_uri(path):
    mime = MIME.get(path.suffix.lower()) or mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


_URL = re.compile(r"url\(\s*(['\"]?)([^'\")]+)\1\s*\)")
_FACE = re.compile(r"@font-face\s*\{[^}]*\}", re.S)


def _split_faces(css, module_file, root):
    """Take the @font-face rules out of a module's CSS; inline their url()s (relative to the module file)."""
    faces = []

    def inline(match):
        ref = match.group(2)
        if ref.startswith("data:"):
            return match.group(0)
        return f'url("{_data_uri(_inside(root, module_file.parent / ref))}")'

    for face in _FACE.findall(css):
        faces.append(_URL.sub(inline, face))
    return _FACE.sub("", css).strip() + "\n", faces


def _inline_brand_value(value, root, exports):
    """Inline the package export path a brand value names in url()."""
    return _URL.sub(lambda m: f'url("{_data_uri(_export_path(root, exports, m.group(2)))}")', value)


def _inline_brand(css, root, exports):
    """Inline the export paths a brand module names in its `--brand-*` url() values."""
    return re.sub(r"(--brand-[\w-]+\s*:\s*)([^;}]*)", lambda m: m.group(1) + _inline_brand_value(m.group(2), root, exports), css)


# --- contrast -------------------------------------------------------------------------------------

def _luminance(hex_colour):
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    channels = [int(h[i: i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(fg, bg):
    hi, lo = sorted((_luminance(fg), _luminance(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def role_values(css):
    """Last declared value of each custom property in `css`."""
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;}]+)", css)}


_HEX = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})")
KIT_ON = "--kit-on-"


def text_roles(pair):
    """The text roles of a contract pair: one role, or a list where any role that reaches AA will do."""
    return list(pair["fg"]) if isinstance(pair["fg"], list) else [pair["fg"]]


def pair_ratios(values, pair):
    """[(text role, contrast on the pair's fill)] in list order, or None when a value is not a hex colour."""
    bg = values.get(pair["bg"], "")
    fgs = [(role, values.get(role, "")) for role in text_roles(pair)]
    if not _HEX.fullmatch(bg) or not all(_HEX.fullmatch(value) for _, value in fgs):
        return None
    return [(role, contrast(value, bg)) for role, value in fgs]


def failing_pairs(css, pairs):
    """(tried, bg, use) for every contract pair whose roles are hex colours and none of whose text roles
    reaches AA; `tried` is [(text role, ratio)] in list order."""
    values, failed = role_values(css), []
    for pair in pairs:
        tried = pair_ratios(values, pair)
        if tried and all(ratio < AA for _, ratio in tried):
            failed.append((tried, pair["bg"], pair["use"]))
    return failed


def describe_failure(tried, bg, use):
    """One line naming every text role tried on `bg` with its ratio."""
    if len(tried) == 1:
        (fg, ratio), = tried
        return f"{fg} on {bg} ({use}): contrast {ratio:.2f}, below WCAG AA {AA}"
    roles = " or ".join(f"{fg} (contrast {ratio:.2f})" for fg, ratio in tried)
    return f"{roles} on {bg} ({use}): no text role reaches WCAG AA {AA}"


def kit_on(fill):
    """The renderer property that holds the text role chosen for `fill`: --success -> --kit-on-success."""
    return KIT_ON + fill.lstrip("-")


def fill_text(css, pairs):
    """{fill: text role} for every list pair: the first role in list order that reaches AA on the fill, else
    (a value that is not a hex colour, or no role passing) the first role of the list."""
    values, chosen = role_values(css), {}
    for pair in pairs:
        if not isinstance(pair["fg"], list):
            continue
        tried = pair_ratios(values, pair) or []
        chosen[pair["bg"]] = next((role for role, ratio in tried if ratio >= AA), text_roles(pair)[0])
    return chosen


def fill_text_css(chosen):
    """A `:root` block declaring --kit-on-<fill>: var(<role>) for each entry of `chosen`, or "" when empty."""
    if not chosen:
        return ""
    return ":root {\n" + "".join(f"  {kit_on(fill)}: var({role});\n" for fill, role in chosen.items()) + "}\n"


# --- resolve --------------------------------------------------------------------------------------

def _base_css(module):
    path = HERE / "base" / f"{module}.css"
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _load_package(root):
    manifest_path = root / "kit-manifest.json"
    if not manifest_path.is_file():
        raise DesignError(f"{root} has no kit-manifest.json; it is not a delivery-comms design system")
    manifest = _read_json(manifest_path, "manifest")
    _refuse_newer_minor(manifest.get("contractVersion"))
    schema = _read_json(_contract_file("kit-manifest.schema.json"), "schema")
    errors = manifest_check.check(manifest, schema)
    if errors:
        raise DesignError("kit-manifest.json is invalid:\n  " + "\n  ".join(errors))
    major = _contract()["contractVersion"].split(".")[0]
    if manifest["contractVersion"].split(".")[0] != major:
        raise DesignError(f"kit-manifest.json targets contract {manifest['contractVersion']}; this kit reads {major}.x")
    package = _read_json(root / "package.json", "package.json") if (root / "package.json").is_file() else {}
    return manifest, package


def _refuse_newer_minor(version):
    """Refuse a manifest of this major at a newer minor before the schema check, whose error would name a module
    or key this kit does not know instead of the kit version to install."""
    match = re.match(r"(\d+)\.(\d+)\.\d+", version) if isinstance(version, str) else None
    major, minor = (int(part) for part in _contract()["contractVersion"].split(".")[:2])
    if match and int(match.group(1)) == major and int(match.group(2)) > minor:
        raise DesignError(f"this design targets contract {version}; update delivery-comms to "
                          f"{match.group(1)}.{match.group(2)}.0 or later")


_RULE = re.compile(r"([^{}]*)\{([^{}]*)\}")
_COMMENT = re.compile(r"/\*.*?\*/", re.S)


def _refuse_scoped_roles(css, module, roles):
    """Refuse a contract role declared under any selector but :root: role_values reads every declaration as the
    design's own value, so a scoped one would replace the role for the whole render."""
    for selector, body in _RULE.findall(_COMMENT.sub("", css)):
        selector = selector.strip()
        if selector == ":root":
            continue
        scoped = [role for role in re.findall(r"(--[\w-]+)\s*:", body) if role in roles]
        if scoped:
            raise DesignError(f"the {module} module declares {', '.join(scoped)} under `{selector}`; module CSS "
                              "declares roles on :root only (a dark slide's roles come from the dark module)")


def resolve(start_dir, explicit=None):
    contract = _contract()
    modules = list(contract["modules"])
    warnings, identity, root = [], {"source": "base"}, None

    if explicit is not None:
        root = Path(explicit).resolve()
        identity = {"source": "path", "path": display_path(root)}
    else:
        pin_file, legacy = _find_source(Path(start_dir))
        if pin_file is None and legacy is not None:
            raise DesignError(_legacy_message(legacy))
        if pin_file is not None:
            if legacy is not None:
                warnings.append(f"{display_path(legacy)} is ignored because docs/ux/package.json pins a design "
                                "system; delete it")
            name, folder, version = _pin_target(pin_file)
            if folder is not None:
                root, identity = folder, {"source": "path", "path": display_path(folder)}
            else:
                root, identity = _fetch_package(name, version), {"source": "registry"}
            identity["name"] = name
            if version:
                identity["version"] = version

    manifest, package, exports = {}, {}, {}
    if root is not None:
        manifest, package = _load_package(root)
        exports = package.get("exports", {})
        identity.setdefault("name", package.get("name", ""))
        identity.setdefault("version", package.get("version", ""))

    css, fonts, sources, guidance = {}, [], {}, {"informational": True, "export": None}
    roles = {role for spec in contract["modules"].values() for role in spec["roles"]}
    raw_brand = role_values(_base_css("brand"))
    for module in modules:
        provided = manifest.get("provides", {}).get(module)
        sources[module] = "design-system" if provided else "base"
        if module == "guidance":
            guidance["export"] = provided
            if provided:
                _export_path(root, exports, provided)
            css[module] = ""
            continue
        text = _base_css(module)
        if provided:
            module_file = _export_path(root, exports, provided)
            own, faces = _split_faces(module_file.read_text(encoding="utf-8"), module_file, root)
            _refuse_scoped_roles(own, module, roles)
            if module == "dark":
                missing = [r for r in contract["modules"]["dark"]["requiredRoles"] if r not in role_values(own)]
                if missing:
                    raise DesignError(f"the dark module lacks the required role(s) {', '.join(missing)}")
            if module == "brand":
                raw_brand = role_values(text + own)
                own = _inline_brand(own, root, exports)
            fonts += faces
            text += "\n" + own
        css[module] = text

    assembled = "".join(css.values())
    bad = failing_pairs(assembled, contract["pairs"] + contract["modules"]["dark"]["pairs"])
    if bad:
        lines = ["  " + describe_failure(*failure) for failure in bad]
        raise DesignError("the design's own text pairs fail WCAG AA:\n" + "\n".join(lines))
    # text on a fill: one --kit-on-<fill> per list pair, declared in the module that owns the fill role
    owner = {role: module for module, spec in contract["modules"].items() for role in spec["roles"]}
    chosen = fill_text(assembled, contract["pairs"])
    for module in css:
        block = fill_text_css({fill: role for fill, role in chosen.items() if owner[fill] == module})
        if block:
            css[module] += ("" if css[module].endswith("\n") else "\n") + block

    brand_roles = contract["modules"]["brand"]["roles"]
    brand = {role: _inline_brand_value(raw_brand[role], root, exports) for role in brand_roles if role in raw_brand}
    provenance = {"designSystem": identity, "modules": sources, "guidance": guidance,
                  "exceptions": [], "warnings": warnings}
    return Design(css=css, fonts=fonts, brand=brand, exceptions=dict(manifest.get("exceptions", {})),
                  provenance=provenance, root=root)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=("css", "fonts", "provenance"))
    ap.add_argument("--module", help="comma-separated modules for `css` (default: all, in contract order)")
    ap.add_argument("--design-system", help="a design-system folder, bypassing the pin")
    ap.add_argument("--from", dest="start", default=".", help="folder to start the pin search from")
    args = ap.parse_args(argv)
    try:
        design = resolve(Path(args.start), explicit=args.design_system)
        if args.command == "css":
            chosen = args.module.split(",") if args.module else list(design.css)
            unknown = [m for m in chosen if m not in design.css]
            if unknown:
                raise DesignError(f"unknown module(s): {', '.join(unknown)}")
            sys.stdout.write("".join(design.css[m] for m in chosen))
        elif args.command == "fonts":
            sys.stdout.write("".join(face + "\n" for face in design.fonts))
        else:
            print(json.dumps(design.provenance, indent=2))
    except DesignError as exc:
        print(f"design_source: {exc}", file=sys.stderr)
        return exc.code
    return 0


if __name__ == "__main__":
    sys.exit(main())
