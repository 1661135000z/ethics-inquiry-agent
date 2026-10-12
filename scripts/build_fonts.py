#!/usr/bin/env python3
"""Rebuild local InquireSans assets; development only: pip install fonttools[woff].

Run from the repository: python scripts/build_fonts.py
Use --source /path/NotoSansSC.ttf --license /path/OFL.txt for an offline rebuild.
The official source lives in a temporary directory, never in the repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import urllib.request
from pathlib import Path

import fontTools
from fontTools import subset
from fontTools.ttLib import TTFont

FONT_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf"
LICENSE_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/notosanssc/OFL.txt"
ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ranges(codepoints: set[int]) -> str:
    result = []
    ordered = sorted(codepoints)
    start = previous = ordered[0]
    for point in ordered[1:] + [None]:
        if point is not None and point == previous + 1:
            previous = point
            continue
        result.append(f"U+{start:X}" if start == previous else f"U+{start:X}-{previous:X}")
        start = previous = point
    return ",".join(result)


def build(source: Path, license_path: Path, output: Path, ui_file: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    font = TTFont(source)
    coverage = set(font.getBestCmap())
    axes = {axis.axisTag: [axis.minValue, axis.maxValue] for axis in font["fvar"].axes}
    ui_text = ui_file.read_text(encoding="utf-8") if ui_file.exists() else ""
    # A small Latin part and the application characters load before uncommon CJK.
    latin = {point for point in coverage if point < 0x300}
    ui = ({ord(character) for character in ui_text} | set(range(0x2000, 0x2070)) | set(range(0x3000, 0x3040))) & coverage - latin
    remaining = sorted(coverage - latin - ui)
    groups = [("latin", latin), ("ui", ui)]
    groups.extend((f"cjk-{index // 1000:02d}", set(remaining[index:index + 1000])) for index in range(0, len(remaining), 1000))
    artifacts = []
    css = ["/* Noto Sans SC derived subsets. SIL OFL 1.1; see OFL.txt. */"]
    union: set[int] = set()
    for name, codepoints in groups:
        if not codepoints:
            continue
        current = TTFont(source)
        options = subset.Options()
        options.flavor = "woff2"
        options.name_IDs = ["*"]
        options.name_languages = ["*"]
        options.name_legacy = True
        worker = subset.Subsetter(options=options)
        worker.populate(unicodes=codepoints)
        worker.subset(current)
        current.flavor = "woff2"
        target = output / f"inquire-sans-{name}.woff2"
        current.save(target)
        actual = set(TTFont(target).getBestCmap())
        assert actual == codepoints, f"Coverage mismatch in {name}"
        assert not union & actual, f"Overlapping unicode ranges in {name}"
        union |= actual
        unicode_range = ranges(actual)
        css.append("@font-face {\n  font-family: 'InquireSans';\n  font-style: normal;\n  font-weight: 100 900;\n  font-display: swap;\n  src: url('" + target.name + "') format('woff2');\n  unicode-range: " + unicode_range + ";\n}")
        artifacts.append({"file": target.name, "bytes": target.stat().st_size, "sha256": digest(target), "codepoints": len(actual), "unicode_range": unicode_range})
        print(f"{target.name}: {target.stat().st_size:,} bytes, {len(actual)} codepoints", flush=True)
    assert union == coverage, "Subsets must retain the entire source cmap"
    (output / "font.css").write_text("\n\n".join(css) + "\n", encoding="utf-8")
    (output / "OFL.txt").write_bytes(license_path.read_bytes())
    manifest = {
        "family": "InquireSans", "source_family": "Noto Sans SC", "font_url": FONT_URL,
        "license_url": LICENSE_URL, "license": "SIL Open Font License 1.1",
        "source_sha256": digest(source), "license_sha256": digest(license_path),
        "fonttools_version": fontTools.__version__, "source_axes": axes,
        "source_codepoints": len(coverage), "subset_codepoints": len(union),
        "coverage_verified": True, "ranges_disjoint": True,
        "ui_seed_file": str(ui_file.relative_to(ROOT)) if ui_file.is_relative_to(ROOT) else ui_file.name,
        "ui_seed_sha256": digest(ui_file) if ui_file.exists() else None,
        "total_woff2_bytes": sum(item["bytes"] for item in artifacts), "artifacts": artifacts,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Complete: {len(artifacts)} parts, {manifest['total_woff2_bytes']:,} bytes; full source cmap retained.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--license", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "static/fonts")
    parser.add_argument("--ui-file", type=Path, default=ROOT / "app.py")
    args = parser.parse_args()
    if bool(args.source) != bool(args.license):
        parser.error("--source and --license must be supplied together")
    if args.source:
        build(args.source, args.license, args.output, args.ui_file)
    else:
        with tempfile.TemporaryDirectory(prefix="inquire-fonts-") as folder:
            font_path, license_path = Path(folder) / "source.ttf", Path(folder) / "OFL.txt"
            urllib.request.urlretrieve(FONT_URL, font_path)
            urllib.request.urlretrieve(LICENSE_URL, license_path)
            build(font_path, license_path, args.output, args.ui_file)
