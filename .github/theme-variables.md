# Theme Variables Reference

All variables come from `~/.cache/wal/colors.json`, which pywal generates from
`~/dotfiles/.config/wal/colorschemes/dark/parecolors.json`.

## Semantic syntax variables (`special.*`)
Used in `pywal_color_scheme.icls` for editor syntax highlighting.

| Variable | Hex (parecolors) | Usage |
|---|---|---|
| `{syntaxKeyword}` | `#0bde96` | Keywords (`if`, `for`, `class`, `fun`, etc.) |
| `{syntaxString}` | `#c91b8e` | String literals |
| `{syntaxComment}` | `#556072` | Line and block comments |
| `{syntaxNumber}` | `#cd222f` | Numeric literals |
| `{syntaxFunction}` | `#61afef` | Function/method declarations and calls |
| `{syntaxClass}` | `#61afef` | Class names |
| `{syntaxType}` | `#0ba3a4` | Types, interfaces, type parameters |
| `{syntaxConstant}` | `#cd222f` | Constants |
| `{syntaxVariable}` | `#cfdceb` | Variables, identifiers |
| `{syntaxOperator}` | `#cfdceb` | Operators |
| `{syntaxAnnotation}` | `#61afef` | Annotations / metadata |
| `{syntaxDocTag}` | `#ee8109` | Doc comment tags (`@param`, `@return`, etc.) |
| `{syntaxStringEscape}` | `#0ba3a4` | String escape sequences |
| `{syntaxPunctuation}` | `#d3dde8` | Punctuation (braces, brackets, semicolons) |

## Semantic UI variables (`special.*`)
Used in `theme/ui-mapping.json` for IDE chrome coloring.

### Backgrounds / surfaces
| Variable | Hex | Usage |
|---|---|---|
| `{background}` | `#10171e` | Main editor / window background |
| `{backgroundAlt}` | `#0d1419` | Alternate background (gutter, status bar) |
| `{surface}` | `#142431` | Elevated surface (tool windows, panels) |
| `{surfaceHover}` | `#193545` | Hovered surface |
| `{overlay}` | `#1c252d` | Overlay / popup background |

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
| `{textSecondary}` | `#a1adba` | Secondary text (tool windows, file explorer) |
| `{textMuted}` | `#8b98a6` | Muted text (line numbers, metadata) |
| `{textDisabled}` | `#556072` | Disabled text |
| `{textInverse}` | `#10171e` | Text on colored backgrounds |
| `{textLink}` | `#61afef` | Hyperlinks |

### Borders
| Variable | Hex | Usage |
|---|---|---|
| `{border}` | `#27313b` | Standard border |
| `{borderSubtle}` | `#1c252d` | Subtle border (indent guides) |
| `{borderFocus}` | `#61afef` | Focus ring border |

### Selection / highlight
| Variable | Hex | Usage |
|---|---|---|
| `{selection}` | `#274762` | Text selection background |
| `{highlight}` | `#193545` | Hover highlight background |
| `{highlightActive}` | `#333e49` | Active line / current breadcrumb background |

### Status (use only for semantically correct elements)
| Variable | Hex | Usage |
|---|---|---|
| `{success}` | `#0bde96` | Test pass indicators |
| `{warning}` | `#ee8109` | Lint warnings |
| `{error}` | `#cd222f` | Errors |
| `{info}` | `#61afef` | Informational |

## Palette ramps (`special.*`)
Use these for VCS colors, diff gutter, file colors, project avatars, etc.
Avoid using status variables (`success`, `error`, `warning`) for these — use explicit ramp levels instead.

### Color ramps (5 = brightest, 1 = darkest)
| Ramp | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| **red** | `#2d0a0c` | `#5b1418` | `#881d24` | `#b6212b` | `#cd222f` |
| **green** | `#032e1f` | `#065b3d` | `#08875b` | `#0ab479` | `#0bde96` |
| **blue** | `#142431` | `#274762` | `#3a6a93` | `#4d8cc4` | `#61afef` |
| **yellow** | `#311b02` | `#613604` | `#905106` | `#c06b08` | `#ee8109` |
| **grey** | `#1c252d` | `#27313b` | `#333e49` | `#414d59` | `#556072` |

### VCS file status coloring guidelines
- **Added**: `green5` — brightest green
- **Modified**: `blue5` — brightest blue  
- **Deleted**: `red5` — brightest red
- **Hijacked / conflict**: `yellow5` — brightest yellow
- **Ignored**: `textDisabled` — grey
- **Gutter diff bars**: use `5` for main, `3` for ignored/subtle variants

### File color (background tint) guidelines
Use dark (`1`/`2`) ramp levels so they are subtle background tints, not bright alerts:
- Gray: `grey2`, Rose: `red2`, Green: `green2`, Yellow: `yellow2`
- Blue: `blue2`, Violet: `blue3`, Orange: `yellow3`

### Project avatar / RecentProject color guidelines
Use `5` variants for avatar start color (bright), `4` for end, `1`/`2` for toolbar gradient start (dark).

## Terminal palette (`colors.color0`–`color15`)
Available as `{color0}` through `{color15}` but generally avoid these in favor of named semantic
or ramp variables for maintainability.
