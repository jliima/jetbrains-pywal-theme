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
| `scripts/diff-color-changes.py` | Compares resolved template against an edited ICLS to find color changes |
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

## Updating the template from a hand-edited ICLS

When the user tweaks colors manually in the JetBrains IDE (or exports a modified `.icls`),
use `scripts/diff-color-changes.py` to find what changed and update `pywal_color_scheme.icls`.

### Workflow

1. **Run the diff script** against the edited file:
   ```bash
   python3 scripts/diff-color-changes.py <path-to-edited.icls>
   ```

2. **Read the output** — it has three sections:

   - **VALUE CHANGES** — options where the hex value differs. The output shows:
     - `template:` the current `{varName}` placeholder and its resolved hex
     - `edited:` the target hex from the edited file
     - `candidates:` palette variables matching the target hex, sorted by semantic relevance (best first)
   - **REMOVE FROM TEMPLATE** — option blocks present in the template but missing from the edited file.
     Delete the entire `<option>...</option>` block for each listed entry.
   - **ADD TO TEMPLATE** — option blocks in the edited file but not in the template.
     Add them in alphabetical order within the correct section (`<colors>` or `<attributes>`),
     using `{varName}` placeholders. Candidate variables are listed for each hex value.

3. **Choose the best variable** for each change. The first candidate is usually best, but use judgment:
   - Prefer semantic names (`syntaxFunction`, `accent`, `foreground`) over raw color names (`blue5`, `color4`)
   - Pick variables that describe the *purpose* of the color in context
     (e.g. `{accent}` for markdown headers, `{syntaxString}` for link URLs)
   - If no candidate fits semantically, consider adding a new variable to `parecolors.json`

4. **Apply changes** to `pywal_color_scheme.icls` using `{varName}` placeholder syntax (not raw hex).

5. **Verify** by re-running the diff script — it should report "No differences found."

### Example commands

```bash
# Diff against a hand-edited file in the project
python3 scripts/diff-color-changes.py pywal_color_scheme_käsin_paranneltu.icls

# Diff against the currently installed scheme in IntelliJ (should show no changes
# right after a pywal update, since the installed file is built from the template)
python3 scripts/diff-color-changes.py \
    ~/.config/JetBrains/IntelliJIdea2026.1/colors/pywal-color-scheme.icls
```