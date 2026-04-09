#!/usr/bin/env python3
"""Generate pywal ICLS template from original IntelliJ color scheme.

Reads pywal_color_scheme.icls.backup and replaces all hex color values
with pywal template variable references ({varName}), then writes the
result to pywal_color_scheme.icls.

Run from the project root or from the scripts/ directory.
"""

import re
import sys
from pathlib import Path

# ── Hex → pywal variable mappings ─────────────────────────────────────────────
# Keys are lowercase hex WITHOUT # prefix (as they appear in ICLS).
# Some entries have 5 chars due to a missing leading 0 in the original file.
HEX_TO_VAR: dict[str, str] = {
  # Direct syntax variable matches
  "0bde96": "syntaxKeyword",
  "bde96":  "syntaxKeyword",   # truncated (missing leading 0)
  "0bde86": "syntaxKeyword",   # near-identical green (very minor variant)
  "bde86":  "syntaxKeyword",   # truncated variant
  "c91b8e": "syntaxString",
  "556072": "syntaxComment",
  "cd222f": "syntaxNumber",    # also error/constant
  "61afef": "syntaxFunction",  # also class, annotation, accent
  "0ba3a4": "syntaxType",
  "ba3a4":  "syntaxType",      # truncated (missing leading 0)
  "ee8109": "syntaxDocTag",    # also warning/orange
  "d3dde8": "syntaxPunctuation",
  "cfdceb": "syntaxVariable",  # also foreground

  # Background / surface colors
  "10171e": "background",
  "0d1419": "backgroundAlt",
  "0a0f14": "backgroundAlt",   # slightly darker variant
  "142431": "surface",
  "193545": "surfaceHover",    # also highlight
  "1c252d": "overlay",         # also borderSubtle
  "1e2a30": "overlay",         # close variant
  "1b262b": "overlay",         # close variant

  # Accent / interactive
  "4d8cc4": "accentHover",
  "274762": "selection",       # also accentSubtle
  "27313b": "border",
  "333e49": "highlightActive",
  "333a48": "highlightActive", # near-identical (minor variant in original)

  # Text
  "a1adba": "textSecondary",
  "8b98a6": "textMuted",

  # Status / special
  "f3170d": "color9",          # bright red (error underlines)

  # ── Monokai-originated colors → nearest semantic pywal variable ───────────
  "5ad4e6": "syntaxType",       # Monokai cyan type → syntaxType
  "7bd88f": "syntaxFunction",   # Monokai green function → syntaxFunction
  "fc618d": "syntaxKeyword",    # Monokai pink keyword → syntaxKeyword
  "fd9353": "syntaxDocTag",     # Monokai orange param → syntaxDocTag
  "f59762": "syntaxDocTag",     # Monokai orange variant → syntaxDocTag
  "948ae3": "syntaxAnnotation", # Monokai purple → syntaxAnnotation
  "fce566": "syntaxDocTag",     # Monokai yellow → syntaxDocTag
  "f7f1ff": "syntaxVariable",   # Monokai near-white → syntaxVariable
  "8b888f": "syntaxComment",    # Medium grey → syntaxComment
  "69676c": "syntaxComment",    # Dark grey → syntaxComment
  "c1c0c0": "syntaxVariable",   # Off-white → syntaxVariable
  "363537": "highlightActive",  # Dark bg (code blocks, Markdown tables)
  "525053": "syntaxComment",    # Dark inactive grey → syntaxComment
  "646877": "syntaxComment",    # Grey → syntaxComment
  "9373a5": "syntaxAnnotation", # Purple-ish → syntaxAnnotation
  "549dbc": "syntaxFunction",   # Close to accent blue
  "219598": "syntaxType",       # Close to cyan/syntaxType

  # Diff / coverage backgrounds
  "4b1515": "red2",            # Diff conflict background
  "5d1616": "red2",            # Diff deleted background
  "621118": "red2",            # Breakpoint background
  "62111":  "red2",            # Truncated variant
  "114835": "green2",          # Diff inserted background
  "12404b": "cyan2",           # Diff modified background
  "264b33": "green2",          # Coverage full background

  # Debugger
  "6815e":  "green3",          # Execution point (truncated 06815e)
  "06815e": "green3",          # Execution point background

  # Selection / inline hints
  "262b36": "selection",       # Close to selection color

  # ── Remaining unmapped colors ─────────────────────────────────────────────
  "222222": "backgroundAlt",   # Scrollbar track, inactive dark backgrounds
  "404040": "surface",         # Medium-dark background
  "8000ff": "accentSubtle",    # Current breadcrumb bg (purple → accent subtle)
  "939393": "textMuted",       # Effect/border grey
  "a2a2a2": "textSecondary",   # Light grey effects
  "f65f87": "syntaxString",    # Pink/rose links (Markdown)
  "f78c6c": "syntaxDocTag",    # Peach/orange effects
  "dbdbdb": "textSecondary",   # Light grey error stripe
  "536c46": "syntaxComment",   # Olive (conditionally inactive code)
  "5789dd": "syntaxFunction",  # Medium blue (Markdown bold-italic)
  "6e2424": "red2",            # Dark red backgrounds
  "727272": "textMuted",       # Medium grey
  "7867e7": "syntaxAnnotation",# Purple-blue (Markdown strikethrough formatting)
  "87cefa": "syntaxFunction",  # Light blue (rainbow brackets)
  "c4b3a3": "textSecondary",   # Warm grey
  "c7c8f5": "textSecondary",   # Light lavender
  "da70d6": "syntaxString",    # Orchid (rainbow brackets)
  "ffd700": "syntaxDocTag",    # Gold/yellow (rainbow brackets, labels)
  "ffffff": "foreground",      # Pure white → foreground
}

# ── Context-aware overrides for the <colors> section ─────────────────────────
# Keyed by option name; values are variable names (without braces).
# None = keep the value as-is (e.g. empty values).
COLORS_SECTION_MAP: dict[str, str] = {
  "ADDED_LINES_COLOR":                                  "success",
  "ANNOTATIONS_COLOR":                                  "foreground",
  "CARET_COLOR":                                        "foreground",
  "CARET_ROW_COLOR":                                    "highlightActive",
  "DELETED_LINES_COLOR":                                "error",
  "DIFF_SEPARATORS_BACKGROUND":                         "overlay",
  "DIFF_SEPARATORS_TOP_BORDER":                         "overlay",
  "DOCUMENTATION_COLOR":                                "background",
  "FILESTATUS_ADDED":                                   "success",
  "FILESTATUS_COPIED":                                  "accent",
  "FILESTATUS_DELETED":                                 "error",
  "FILESTATUS_HIJACKED":                                "warning",
  "FILESTATUS_IDEA_FILESTATUS_DELETED_FROM_FILE_SYSTEM": "textDisabled",
  "FILESTATUS_IDEA_FILESTATUS_IGNORED":                 "textDisabled",
  "FILESTATUS_IDEA_SVN_FILESTATUS_EXTERNAL":            "success",
  "FILESTATUS_IDEA_SVN_FILESTATUS_OBSTRUCTED":          "warning",
  "FILESTATUS_IDEA_SVN_REPLACED":                       "success",
  "FILESTATUS_IGNORE.PROJECT_VIEW.IGNORED":             "textMuted",
  "FILESTATUS_MERGED":                                  "syntaxAnnotation",
  "FILESTATUS_MODIFIED":                                "accent",
  "FILESTATUS_NOT_CHANGED_IMMEDIATE":                   "syntaxType",
  "FILESTATUS_NOT_CHANGED_RECURSIVE":                   "syntaxType",
  "FILESTATUS_OBSOLETE":                                "warning",
  "FILESTATUS_SUPPRESSED":                              "textDisabled",
  "FILESTATUS_SWITCHED":                                "syntaxString",
  "FILESTATUS_UNKNOWN":                                 "syntaxString",
  "FILESTATUS_addedOutside":                            "warning",
  "FILESTATUS_modifiedOutside":                         "error",
  "FOLDED_TEXT_BORDER_COLOR":                           "accent",
  "GUTTER_BACKGROUND":                                  "backgroundAlt",
  "IGNORED_ADDED_LINES_BORDER_COLOR":                   "success",
  "IGNORED_DELETED_LINES_BORDER_COLOR":                 "error",
  "IGNORED_MODIFIED_LINES_BORDER_COLOR":                "warning",
  "INDENT_GUIDE":                                       "border",
  "INFORMATION_HINT":                                   "overlay",
  "INLINE_REFACTORING_SETTINGS_DEFAULT":                "syntaxKeyword",
  "INLINE_REFACTORING_SETTINGS_FOCUSED":                "syntaxKeyword",
  "INLINE_REFACTORING_SETTINGS_HOVERED":                "syntaxKeyword",
  "LINE_NUMBERS_COLOR":                                 "textDisabled",
  "LINE_NUMBER_ON_CARET_ROW_COLOR":                     "foreground",
  "LOOKUP_COLOR":                                       "background",
  "METHOD_SEPARATORS_COLOR":                            "border",
  "MODIFIED_LINES_COLOR":                               "warning",
  "MT_FILESTATUS_ADDED":                                "success",
  "MT_FILESTATUS_DELETED":                              "error",
  "MT_FILESTATUS_IDEA_FILESTATUS_IGNORED":              "textDisabled",
  "MT_FILESTATUS_MODIFIED":                             "accent",
  "MT_FILESTATUS_modifiedOutside":                      "error",
  "MT_IGNORE.PROJECT_VIEW.IGNORED":                     "textMuted",
  "MT_SUPPRESSED":                                      "foreground",
  "NOTIFICATION_BACKGROUND":                            "highlightActive",
  "NOT_CHANGED":                                        "textMuted",
  "QUESTION_HINT":                                      "overlay",
  "RECENT_LOCATIONS_SELECTION":                         "highlightActive",
  "RIGHT_MARGIN_COLOR":                                 "highlightActive",
  "SELECTED_INDENT_GUIDE":                              "borderFocus",
  "SELECTED_TEARLINE_COLOR":                            "accent",
  "SELECTION_BACKGROUND":                               "selection",
  "SELECTION_FOREGROUND":                               "foreground",
  "SEPARATOR_ABOVE_COLOR":                              "warning",
  "SEPARATOR_BELOW_COLOR":                              "backgroundAlt",
  "SOFT_WRAP_SIGN_COLOR":                               "overlay",
  "TAB_UNDERLINE":                                      "accent",
  "TAB_UNDERLINE_INACTIVE":                             "borderSubtle",
  "TEARLINE_COLOR":                                     "highlightActive",
  "TOOLTIP":                                            "overlay",
  "VCS_ANNOTATIONS_COLOR_1":                            "textDisabled",
  "VCS_ANNOTATIONS_COLOR_2":                            "textDisabled",
  "VCS_ANNOTATIONS_COLOR_3":                            "error",
  "VCS_ANNOTATIONS_COLOR_4":                            "syntaxType",
  "VCS_ANNOTATIONS_COLOR_5":                            "warning",
  "VISUAL_INDENT_GUIDE":                                "highlightActive",
  "WHITESPACES":                                        "textDisabled",
  "WHITESPACES_MODIFIED_LINES_COLOR":                   "textDisabled",
}

# Attribute sub-option names that contain color values (others are numbers)
COLOR_ATTR_NAMES = {"FOREGROUND", "BACKGROUND", "EFFECT_COLOR", "ERROR_STRIPE_COLOR"}

# Regex patterns
OPTION_LINE_RE = re.compile(r'(\s*<option name="([^"]+)" value=")([^"]*)"(.*)')
HEX_RE = re.compile(r'^[0-9a-fA-F]{5,7}$')


def lookup_var(hex_val: str) -> str | None:
  """Return pywal variable name for a hex value, or None if unknown."""
  return HEX_TO_VAR.get(hex_val.lower())


def replace_color_value(line: str, name: str, val: str, m: re.Match) -> str:
  """Replace a color value in a matched line with a {varName} placeholder."""
  prefix = m.group(1)
  suffix = m.group(4)
  return f'{prefix}{{{name}}}"' + suffix


def process_colors_section(line: str) -> str:
  """Process a line from the <colors> section using context-aware + hex matching."""
  m = OPTION_LINE_RE.match(line)
  if not m:
    return line

  option_name, val = m.group(2), m.group(3)

  # Empty value → keep as-is
  if not val or not HEX_RE.match(val):
    return line

  # Context-aware override first
  var_name = COLORS_SECTION_MAP.get(option_name)
  if not var_name:
    # Fall back to hex mapping
    var_name = lookup_var(val)

  if var_name:
    return replace_color_value(line, var_name, val, m)

  # Unknown color — leave as-is (will be hardcoded in the template)
  return line


def process_attributes_section(line: str) -> str:
  """Process a line from the <attributes> section using hex matching."""
  m = OPTION_LINE_RE.match(line)
  if not m:
    return line

  attr_name, val = m.group(2), m.group(3)

  # Only replace recognized color sub-options (skip FONT_TYPE, EFFECT_TYPE, etc.)
  if attr_name not in COLOR_ATTR_NAMES:
    return line

  if not val or not HEX_RE.match(val):
    return line

  var_name = lookup_var(val)
  if var_name:
    return replace_color_value(line, var_name, val, m)

  return line


def process_icls(input_path: Path, output_path: Path) -> None:
  """Transform ICLS file: replace hex colors with {varName} placeholders."""
  content = input_path.read_text(encoding="utf-8")
  lines = content.splitlines(keepends=True)

  in_colors = False
  in_attributes = False
  result: list[str] = []
  unmapped: set[str] = set()

  for line in lines:
    stripped = line.strip()

    # Section tracking
    if stripped == "<colors>":
      in_colors, in_attributes = True, False
      result.append(line)
      continue
    elif stripped == "</colors>":
      in_colors = False
      result.append(line)
      continue
    elif stripped == "<attributes>":
      in_attributes, in_colors = True, False
      result.append(line)
      continue
    elif stripped == "</attributes>":
      in_attributes = False
      result.append(line)
      continue

    if in_colors:
      new_line = process_colors_section(line)
      # Track unmapped hex values for debug output
      m = OPTION_LINE_RE.match(line)
      if m and HEX_RE.match(m.group(3)) and new_line == line:
        unmapped.add(f"  colors/{m.group(2)}: {m.group(3)}")
      result.append(new_line)

    elif in_attributes:
      new_line = process_attributes_section(line)
      # Track unmapped hex values
      m = OPTION_LINE_RE.match(line)
      if m and m.group(2) in COLOR_ATTR_NAMES and HEX_RE.match(m.group(3)) and new_line == line:
        unmapped.add(f"  attrs/{m.group(2)}: {m.group(3)}")
      result.append(new_line)

    else:
      result.append(line)

  output_path.write_text("".join(result), encoding="utf-8")

  if unmapped:
    print(f"⚠  {len(unmapped)} unmapped colors (kept as-is):")
    for entry in sorted(unmapped):
      print(entry)
  else:
    print("✓ All color values replaced with pywal variables")


def main() -> int:
  script_dir = Path(__file__).parent
  project_dir = script_dir.parent

  input_file = project_dir / "pywal_color_scheme.icls.backup"
  output_file = project_dir / "pywal_color_scheme.icls"

  if not input_file.exists():
    print(f"Error: backup file not found: {input_file}", file=sys.stderr)
    return 1

  print(f"Processing: {input_file}")
  process_icls(input_file, output_file)
  print(f"Template written: {output_file}")
  return 0


if __name__ == "__main__":
  sys.exit(main())
