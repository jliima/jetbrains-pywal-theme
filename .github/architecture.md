# Architecture

## System overview

```
parecolors.json          pywal templates           ~/.cache/wal/                JetBrains IDEs
(colorscheme)  ──wal──►  colors-intellij.icls  ──► colors-intellij.icls  ──┐
                          colors-intellij-       ──► colors-intellij-        │  intellij.sh
                          theme.json                 theme.json           ──┘  (app script)
                                                                                     │
                                                                     ┌───────────────┴──────────────────┐
                                                                     ▼                                  ▼
                                                   ~/.config/JetBrains/*/colors/    ~/.local/share/JetBrains/*/
                                                   pare-colors.icls                pare-colors.jar
                                                   (editor color scheme)           (UI theme plugin)
```

## Components

### 1. Pywal colorscheme (`~/dotfiles/.config/wal/colorschemes/dark/parecolors.json`)
The source of all colors. Contains:
- `colors.color0`–`color15` — 16-color terminal palette
- `special.background`, `foreground`, `cursor` — basic terminal colors
- `special.syntaxKeyword`, `syntaxString`, etc. — semantic syntax colors
- `special.backgroundAlt`, `surface`, `overlay`, etc. — UI surface colors
- `special.accent`, `accentHover`, `selection`, etc. — interactive colors
- `special.success`, `warning`, `error`, `info` — status colors

### 2. ICLS pywal template (`pywal_color_scheme.icls`)
The editor color scheme template. Contains `{varName}` placeholders for every color value.
Pywal replaces these with `#RRGGBB` values; the application script then strips the `#` since
IntelliJ's ICLS format uses bare 6-digit hex.

Inherits from `Darcula` (parent scheme). Language-specific entries in the template override defaults.

### 3. UI theme template (`pywal_ui_theme.json`)
A JSON template for the IntelliJ LaF (Look and Feel) theme. Uses `{varName}` placeholders
that pywal replaces with `#RRGGBB` values. No `#` stripping needed for JSON theme files.

The JSON is bundled into a JAR plugin (`pare-colors.jar`) alongside `plugin.xml` and
`pluginIcon.svg`. This JAR is what IntelliJ loads as the UI theme plugin.

### 4. Application script (`~/dotfiles/scripts/pywal/applications/intellij.sh`)
Runs after `wal --theme parecolors`. It:
1. Takes `~/.cache/wal/colors-intellij.icls` and strips `#` from hex values
2. Copies the processed ICLS to every `~/.config/JetBrains/*/colors/pare-colors.icls`
3. Packages `~/.cache/wal/colors-intellij-theme.json` + static assets into `pare-colors.jar`
4. Copies the JAR to every `~/.local/share/JetBrains/*/pare-colors.jar`

### 5. JAR plugin structure
```
pare-colors.jar
├── META-INF/
│   ├── MANIFEST.MF
│   ├── plugin.xml        (references /theme/parecolors.theme.json)
│   └── pluginIcon.svg
└── theme/
    ├── parecolors.theme.json   (UI theme, references editorScheme "pare-colors")
    └── pare-colors.icls        (bundled fallback; live copy is in colors/ dir)
```

## IntelliJ theme loading
- **Color scheme** (ICLS): IntelliJ reads directly from `~/.config/JetBrains/<IDE>/colors/`
  at startup. Updating this file and restarting the IDE applies the new scheme immediately.
- **UI theme** (JAR): IntelliJ loads theme plugins from `~/.local/share/JetBrains/<IDE>/`
  at startup. The JAR must be re-packaged and the IDE restarted for UI changes to apply.

## Applying the theme
```bash
python3 ~/dotfiles/scripts/pywal/run-pywal.py --theme parecolors --app intellij
```
Or for all apps:
```bash
python3 ~/dotfiles/scripts/pywal/run-pywal.py --theme parecolors
```

## Live reload status
- **Editor scheme**: Requires IDE restart (or File > Invalidate Caches)
- **UI theme**: Requires IDE restart
- Dynamic plugin loading for UI themes is complex; a restart approach is used for reliability

## IDE version support
The plugin's `plugin.xml` targets `since-build="242"` (IntelliJ 2024.2+).
The application script targets all IDE installations found in `~/.local/share/JetBrains/`.
