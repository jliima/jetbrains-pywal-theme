# Theme Variables Reference

## Syntax variables (editor color scheme)
These live in `parecolors.json` under the `special` key and are used in the ICLS template.

| Variable | Hex | Usage |
|---|---|---|
| `{syntaxKeyword}` | `#0bde96` | Keywords (`if`, `for`, `class`, `fun`, etc.) |
| `{syntaxString}` | `#c91b8e` | String literals |
| `{syntaxComment}` | `#556072` | Line and block comments |
| `{syntaxNumber}` | `#cd222f` | Numeric literals |
| `{syntaxFunction}` | `#61afef` | Function/method declarations and calls |
| `{syntaxClass}` | `#61afef` | Class names (same as function in this palette) |
| `{syntaxType}` | `#0ba3a4` | Types, interfaces, type parameters |
| `{syntaxConstant}` | `#cd222f` | Constants (same as number in this palette) |
| `{syntaxVariable}` | `#cfdceb` | Variables, identifiers (foreground) |
| `{syntaxOperator}` | `#cfdceb` | Operators (foreground) |
| `{syntaxAnnotation}` | `#61afef` | Annotations / metadata |
| `{syntaxDocTag}` | `#ee8109` | Doc comment tags (`@param`, `@return`, etc.) |
| `{syntaxStringEscape}` | `#0ba3a4` | String escape sequences |
| `{syntaxPunctuation}` | `#d3dde8` | Punctuation (braces, brackets, semicolons) |

## UI variables (theme JSON)
These are used in the UI theme template (`pywal_ui_theme.json`) and come from the
`special` section of `parecolors.json`.

### Backgrounds / surfaces
| Variable | Hex | Usage |
|---|---|---|
| `{background}` | `#10171e` | Main editor background |
| `{backgroundAlt}` | `#0d1419` | Alternative background (gutter, status bar) |
| `{surface}` | `#142431` | Elevated surface (tool windows, panels) |
| `{surfaceHover}` | `#193545` | Hovered surface |
| `{overlay}` | `#1c252d` | Overlay / modal background |

### Accent / interactive
| Variable | Hex | Usage |
|---|---|---|
| `{accent}` | `#61afef` | Primary accent (selected tab underline, links) |
| `{accentHover}` | `#4d8cc4` | Accent on hover |
| `{accentSubtle}` | `#274762` | Subtle accent background |

### Text
| Variable | Hex | Usage |
|---|---|---|
| `{foreground}` | `#cfdceb` | Primary text |
| `{textSecondary}` | `#a1adba` | Secondary text (file explorer, tool windows) |
| `{textMuted}` | `#8b98a6` | Muted text (line numbers, metadata) |
| `{textDisabled}` | `#556072` | Disabled text |
| `{textInverse}` | `#10171e` | Text on colored backgrounds |
| `{textLink}` | `#61afef` | Hyperlinks |

### Borders
| Variable | Hex | Usage |
|---|---|---|
| `{border}` | `#27313b` | Standard border |
| `{borderSubtle}` | `#1c252d` | Subtle border (indent guides) |
| `{borderFocus}` | `#61afef` | Focus border |

### Selection / highlight
| Variable | Hex | Usage |
|---|---|---|
| `{selection}` | `#274762` | Text selection background |
| `{highlight}` | `#193545` | Hover highlight background |
| `{highlightActive}` | `#333e49` | Active line / breadcrumb background |

### Status (use only for semantically correct elements)
| Variable | Hex | Usage |
|---|---|---|
| `{success}` | `#0bde96` | VCS added, test pass |
| `{warning}` | `#ee8109` | VCS modified, lint warnings |
| `{error}` | `#cd222f` | VCS deleted, errors |
| `{info}` | `#61afef` | Informational |

### Palette colors (for diff backgrounds, coverage, etc.)
| Variable | Hex | Notes |
|---|---|---|
| `{color9}` | `#f3170d` | Bright red (error underlines) |
| `{red1}` | `#2d0a0c` | Darkest red diff background |
| `{red2}` | `#5b1418` | Dark red diff background |
| `{green2}` | `#065b3d` | Dark green diff inserted background |
| `{cyan2}` | `#044243` | Dark cyan diff modified background |
| `{green3}` | `#08875b` | Debugger execution point background |

## Monokai-to-pywal color mapping
The original color scheme contained many Monokai Pro colors. These have been replaced
with the nearest semantically-appropriate pywal variable:

| Monokai hex | Monokai role | Mapped to |
|---|---|---|
| `#7bd88f` | Function (green) | `{syntaxFunction}` |
| `#fc618d` | Keyword (pink) | `{syntaxKeyword}` |
| `#5ad4e6` | Type reference (cyan) | `{syntaxType}` |
| `#fd9353` / `#f59762` | Parameter (orange) | `{syntaxDocTag}` |
| `#948ae3` | Special/purple | `{syntaxAnnotation}` |
| `#fce566` | Label/module (yellow) | `{syntaxDocTag}` |
| `#f7f1ff` | Near-white | `{syntaxVariable}` |
| `#8b888f` / `#69676c` | Medium grey | `{syntaxComment}` |
| `#363537` | Code block bg | `{highlightActive}` |
