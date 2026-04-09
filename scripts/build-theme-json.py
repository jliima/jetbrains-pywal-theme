#!/usr/bin/env python3
"""Combine pywal colors.json + ui-mapping.json into a full IntelliJ theme JSON.

Usage:
    python3 scripts/build-theme-json.py [colors.json] [ui-mapping.json] [output.json]

Defaults:
    colors.json   = ~/.cache/wal/colors.json
    ui-mapping    = <project>/theme/ui-mapping.json
    output        = stdout
"""
import json
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
DEFAULT_COLORS = Path.home() / ".cache/wal/colors.json"
DEFAULT_MAPPING = PROJECT_DIR / "theme/ui-mapping.json"


def load_color_palette(colors_path: Path) -> dict[str, str]:
    """Flatten colors.json into a single name→hex dict."""
    data = json.loads(colors_path.read_text())
    palette: dict[str, str] = {}
    # special.* (backgroundAlt, surface, accent, border, syntax*, etc.)
    for k, v in data.get("special", {}).items():
        palette[k] = v
    # colors.color0-15 → color0-15
    for k, v in data.get("colors", {}).items():
        palette[k] = v
    return palette


def build_theme(colors_path: Path, mapping_path: Path) -> dict:
    palette = load_color_palette(colors_path)
    mapping = json.loads(mapping_path.read_text())

    # Build the colors section from the full palette
    colors_section = {k: v for k, v in palette.items()}

    return {
        "name":         mapping["name"],
        "author":       mapping.get("author", ""),
        "dark":         mapping["dark"],
        "editorScheme": mapping["editorScheme"],
        "colors":       colors_section,
        "ui":           mapping["ui"],
        "icons":        mapping.get("icons", {}),
    }


def main():
    colors_path  = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_COLORS
    mapping_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_MAPPING
    output_path  = Path(sys.argv[3]) if len(sys.argv) > 3 else None

    if not colors_path.exists():
        print(f"Error: {colors_path} not found", file=sys.stderr)
        sys.exit(1)
    if not mapping_path.exists():
        print(f"Error: {mapping_path} not found", file=sys.stderr)
        sys.exit(1)

    theme = build_theme(colors_path, mapping_path)
    output = json.dumps(theme, indent=2)

    if output_path:
        output_path.write_text(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
