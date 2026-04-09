# Architecture

## System overview

```
parecolors.json           pywal                ~/.cache/wal/
(colorscheme)   ──wal──►  (run-pywal.py)  ──►  colors.json
                                │
                                ▼
                         intellij.sh  (application script)
                                │
              ┌─────────────────┼──────────────────────┐
              │                 │                       │
              ▼                 ▼                       ▼
     build-icls.py      build-theme-json.py      (jar packaging)
     + pywal_color_      + ui-mapping.json
       scheme.icls
              │                 │                       │
              ▼                 ▼                       ▼
  pywal-color-scheme.icls   pywal.theme.json    pywal-theme.jar
  (processed, no #)         (full theme JSON)   (UI theme plugin)
              │                                         │
              ▼                                         ▼
  ~/.config/JetBrains/          ~/.local/share/JetBrains/
  <IDE>/colors/                 <IDE>/pywal/lib/
  pywal-color-scheme.icls       pywal-theme.jar

                         + POST localhost:9988/reload
                           (live reload via reload plugin)
```

## Components

### 1. Pywal colorscheme (`~/dotfiles/.config/wal/colorschemes/dark/parecolors.json`)
The source of all colors. After running `wal --theme parecolors`, pywal writes:
- `~/.cache/wal/colors.json` — all palette colors in a structured JSON

`colors.json` structure:
- `special.background`, `foreground`, `cursor` — basic terminal colors
- `special.syntaxKeyword`, `syntaxString`, etc. — semantic syntax variables
- `special.backgroundAlt`, `surface`, `overlay`, etc. — UI surface colors
- `special.accent`, `accentHover`, `selection`, etc. — interactive colors
- `special.red1`–`red5`, `green1`–`green5`, `blue1`–`blue5`, `yellow1`–`yellow5`, `grey1`–`grey5` — palette ramps
- `colors.color0`–`color15` — 16-color terminal palette

### 2. Editor color scheme template (`pywal_color_scheme.icls`)
The editor color scheme with `{varName}` placeholders for every color value. Processed by
`scripts/build-icls.py` at apply-time, which substitutes each `{varName}` with a bare 6-digit
hex value (no `#`) from `colors.json`.

Inherits from `Darcula`. Language-specific entries override defaults. Colors cover:
- Syntax highlighting (keywords, strings, comments, types, etc.)
- VCS/git status colors (`FILESTATUS_*`, gutter diff bars)
- Editor chrome (gutter, caret, selection, indent guides, etc.)

### 3. UI theme mapping (`theme/ui-mapping.json`)
Static JSON that maps IntelliJ UI key paths to palette variable names. Also contains
theme metadata (`name`, `dark`, `editorScheme`, `author`).

`build-theme-json.py` combines this with `colors.json` to produce the full theme JSON:
- A `colors` section is built from the entire `colors.json` palette (name → `#hex`)
- The `ui` section is taken directly from `ui-mapping.json` (values reference the color names)
- IntelliJ resolves the references at theme load time

Editing `ui-mapping.json` is enough to change which UI element uses which color — no
pywal re-run is required, and live reload will pick up the change immediately.

### 4. Application script (`~/dotfiles/scripts/pywal/applications/intellij.sh`)
Orchestrates the full deployment after `wal --theme parecolors` runs:

1. **Build ICLS**: runs `build-icls.py` → processes `pywal_color_scheme.icls` template
2. **Deploy ICLS**: copies to `~/.config/JetBrains/*/colors/pywal-color-scheme.icls`
3. **Build theme JSON**: runs `build-theme-json.py` → full IntelliJ theme JSON
4. **Build JAR**: packages `plugin.xml` + theme JSON + ICLS into `pywal-theme.jar`
5. **Deploy JAR**: copies to `~/.local/share/JetBrains/*/pywal/lib/pywal-theme.jar`
6. **Deploy reload plugin**: copies built JAR to `~/.local/share/JetBrains/*/pywal-reload-plugin/lib/`
7. **Trigger live reload**: `POST localhost:9988/reload`

### 5. Theme JAR plugin structure
```
pywal-theme.jar
├── META-INF/
│   ├── MANIFEST.MF
│   ├── plugin.xml          (references /theme/pywal.theme.json)
│   └── pluginIcon.svg
└── theme/
    ├── pywal.theme.json    (full UI theme, built at apply-time)
    └── pywal-color-scheme.icls  (processed ICLS, bundled as fallback)
```

Installed at: `~/.local/share/JetBrains/<IDE>/pywal/lib/pywal-theme.jar`

### 6. Live reload plugin (`reload-plugin/`)
A Kotlin/Gradle IntelliJ plugin that enables theme changes without IDE restart.

- On IDE start: `PywalReloadStartupActivity` launches `PywalReloadServer`
- `PywalReloadServer` listens on `localhost:9988` (Java `HttpServer`)
- On `POST /reload`: `ThemeReloader` reads `~/.cache/wal/colors.json` and the project
  templates directly, builds the theme in-memory, and applies it via IntelliJ platform APIs:
  - `UITheme.loadTempThemeFromJson()` + `QuickChangeLookAndFeel.switchLafAndUpdateUI()` — UI
  - `EditorColorsSchemeImpl.readExternal()` + `EditorColorsManager.setGlobalScheme()` — editor

Plugin ID: `com.github.jliima.pywal.reload`  
Built with: IntelliJ Platform Gradle Plugin 2.13.1, Kotlin 2.3.0, target 2026.1 (`sinceBuild=261`)  
Installed at: `~/.local/share/JetBrains/<IDE>/pywal-reload-plugin/lib/pywal-reload-plugin-1.0.0.jar`

## Applying the theme
```shell
# Run pywal + deploy theme to all IDEs
python3 ~/dotfiles/scripts/pywal/run-pywal.py --theme parecolors --app intellij

# Trigger live reload in a running IDE (without pywal re-run)
curl -X POST http://localhost:9988/reload
```

## IDE compatibility
- Theme plugin: `since-build="261"` (IntelliJ 2026.1+)
- The application script targets all IDE installations found under `~/.local/share/JetBrains/`
- Tested IDEs: IntelliJIdea, PyCharm, WebStorm, Rider, DataGrip, GoLand
