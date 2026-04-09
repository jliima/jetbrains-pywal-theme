# JetBrains Pywal Theme — Copilot Instructions

## Project overview
This project provides a dynamic pywal-integrated theme for all JetBrains IDEs. It consists of two components:
1. **Editor color scheme** (`pywal_color_scheme.icls`) — pywal template for syntax highlighting
2. **UI theme** (`pywal_ui_theme.json`) — pywal template for the IDE chrome/UI

See `architecture.md` for detailed system design and `theme-variables.md` for the variable reference.

## Pywal integration
- This project follows the pywal workflow described in `~/dotfiles/.copilot/instructions.pywal.md`
- Pywal colorscheme: `~/dotfiles/.config/wal/colorschemes/dark/parecolors.json`
- Pywal templates in this project are copied to `~/dotfiles/.config/wal/templates/`
- The IntelliJ application script lives at `~/dotfiles/scripts/pywal/applications/intellij.sh`

## Template syntax
- `{varName}` — pywal variable, produces the hex color WITH `#` prefix (e.g. `{syntaxKeyword}` → `#0bde96`)
- Since IntelliJ ICLS files use hex WITHOUT `#`, the application script strips the `#` via sed
- Pywal escapes: use `{{` for literal `{` if ever needed
- For the UI theme JSON, `#RRGGBB` with `#` is expected, so no stripping needed

## Key files
- `pywal_color_scheme.icls` — pywal template for the editor color scheme (has `{varName}` placeholders)
- `pywal_color_scheme.icls.backup` — original hand-crafted color scheme before templating
- `pywal_ui_theme.json` — pywal template for the UI theme JSON
- `scripts/generate-template.py` — dev tool to (re)generate the ICLS template from the backup
- `scripts/build-jar.sh` — packages the theme into a plugin JAR

## Deployment
The application script (`intellij.sh`) handles:
1. ICLS: strips `#`, copies to `~/.config/JetBrains/*/colors/pare-colors.icls` for every installed IDE
2. UI theme: copies JSON into JAR, deploys JAR to `~/.local/share/JetBrains/*/pare-colors.jar`
3. No plugin rebuild needed for the ICLS — IDEs read it directly from their colors/ dir

## Adding new syntax variables
If a new `syntax*` variable is needed, add it to `parecolors.json` under the `special` section,
choose a value from the existing palette colors, then update the template accordingly.
Only add variables that are universal across languages (not language-specific accents).

## Code style
- Use 2 spaces for indentation.
- Use camelCase for variable and function names.
- Use maximum line length of 120 characters.