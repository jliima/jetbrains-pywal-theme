# JetBrains Pywal Theme — Copilot Instructions

## Project overview
This project provides a dynamic pywal-integrated theme for all JetBrains IDEs. It colors both the editor (syntax highlighting) and the IDE UI chrome. Colors are driven by a pywal colorscheme and applied without restarting the IDE via a bundled reload plugin.

Two separate plugins are deployed to each IDE:
1. **`pywal-theme.jar`** — the UI theme plugin (Look and Feel)
2. **`pywal-reload-plugin-1.0.0.jar`** — the live reload plugin (HTTP server)

See `architecture.md` for the full system design and `theme-variables.md` for the variable reference.

## Key files

| File | Purpose |
|---|---|
| `pywal_color_scheme.icls` | Editor color scheme template — `{varName}` placeholders |
| `theme/ui-mapping.json` | Maps IntelliJ UI keys to palette variable names; also contains theme metadata |
| `scripts/build-icls.py` | Substitutes `{varName}` in ICLS template with bare hex from `colors.json` |
| `scripts/build-theme-json.py` | Combines `colors.json` + `ui-mapping.json` → full IntelliJ theme JSON |
| `scripts/generate-template.py` | One-time dev tool to (re)generate the ICLS template |
| `assets/META-INF/plugin.xml` | Static plugin metadata for the theme JAR |
| `reload-plugin/` | Kotlin/Gradle project for the live reload plugin |

## Color source
- Pywal colorscheme: `~/dotfiles/.config/wal/colorschemes/dark/parecolors.json`
- At apply-time, pywal writes `~/.cache/wal/colors.json` — this is what the build scripts read
- The application script is: `~/dotfiles/scripts/pywal/applications/intellij.sh`

## Template syntax (ICLS)
- `{varName}` — replaced with a bare 6-digit hex value (no `#`) from `colors.json`
- Variable names come from `special.*` keys in `colors.json` (e.g. `{syntaxKeyword}`, `{blue5}`)
- ICLS format requires hex WITHOUT `#` — `build-icls.py` strips it via `.lstrip("#")`

## UI mapping syntax (ui-mapping.json)
- Values are variable names (strings) from `colors.json` — **not** hex values
- The `build-theme-json.py` script expands them into a `colors` section in the final JSON
- IntelliJ theme JSON references named colors; the build script handles translation
- Nested objects represent IntelliJ's nested UI key namespacing (e.g. `"Borders": { "color": "border" }`)
- Non-color values (integers, booleans) are passed through as-is

## Live reload
The reload plugin starts an HTTP server on `localhost:9988` when any JetBrains IDE starts.

```
POST http://localhost:9988/reload
```

`intellij.sh` calls this after deploying files. The plugin reads `~/.cache/wal/colors.json`
and the project files directly (hardcoded to `~/JetBrainsProjects/jetbrains-pywal-theme/`)
to rebuild and apply both the UI theme and editor scheme in-process without restart.

## Adding new variables
- **New syntax variable**: add to `parecolors.json` under `special`, choose a color from the existing
  `colorN` / `redN` / `blueN` etc. palette, update `pywal_color_scheme.icls` template.
- **New UI variable**: add it to `theme/ui-mapping.json`. The variable must exist in `colors.json`
  (either `special.*` or `colors.color0-15`).
- Only add universally applicable variables — not language-specific ones.

## Code style
- 2-space indentation in JSON and Python.
- camelCase for variable and function names.
- Max line length 120 characters.