# jetbrains-pywal-theme

A dynamic dark theme for all JetBrains IDEs that automatically syncs colors from [pywal](https://github.com/dylanaraps/pywal) / [pywal16](https://github.com/eylles/pywal16).

Covers both the **IDE UI** (chrome, tool windows, menus) and the **editor** (syntax highlighting, VCS colors, diff gutter).

> This is a personal theme built around a specific pywal colorscheme. It is not published to the JetBrains Marketplace. If you want to use it, you will need to wire it into your own pywal setup.

---

## How it works

The theme is split into two parts:

1. **UI theme** — an IntelliJ Look and Feel plugin (`pywal-theme.jar`) built from a static mapping of UI keys to palette variables, combined with colors from pywal at apply-time.
2. **Editor color scheme** — an ICLS file (`pywal-color-scheme.icls`) generated from a template with `{varName}` placeholders, substituted with colors from pywal at apply-time.

A companion **live reload plugin** (`pywal-reload-plugin`) runs a local HTTP server inside the IDE, allowing the theme to update instantly without restarting.

```
parecolors.json  ──pywal──►  colors.json  ──intellij.sh──►  IDE (live reload via :9988/reload)
```

## Project structure

```
jetbrains-pywal-theme/
├── pywal_color_scheme.icls        # Editor scheme template ({varName} placeholders)
├── theme/
│   └── ui-mapping.json            # Maps IntelliJ UI keys → palette variable names
├── assets/
│   └── META-INF/
│       ├── plugin.xml             # Theme plugin metadata
│       └── pluginIcon.svg
├── scripts/
│   ├── build-icls.py              # Processes ICLS template with colors.json
│   ├── build-theme-json.py        # Combines ui-mapping.json + colors.json → theme JSON
│   └── generate-template.py      # Dev tool: regenerate ICLS template from a scheme
└── reload-plugin/                 # Kotlin/Gradle IntelliJ plugin for live reload
    └── src/main/kotlin/.../
        ├── PywalReloadStartupActivity.kt
        ├── PywalReloadServer.kt   # HTTP server on localhost:9988
        └── ThemeReloader.kt       # Applies theme/scheme in-process
```

## Requirements

- [pywal16](https://github.com/eylles/pywal16) (or pywal)
- Python 3.10+
- JDK (for `jar` command)
- A JetBrains IDE (tested: IntelliJ IDEA, PyCharm, WebStorm, Rider, DataGrip)
- The live reload plugin requires IntelliJ 2026.1+ (`since-build=261`)

## Setup

### 1. Wire the application script into pywal

Copy or symlink the application script to your pywal applications directory:

```bash
cp dotfiles/scripts/pywal/applications/intellij.sh \
   ~/.config/wal/applications/intellij.sh
```

Or integrate it into your own pywal runner. The script expects:
- `~/.cache/wal/colors.json` — written by pywal automatically
- `~/JetBrainsProjects/jetbrains-pywal-theme/` — this repo at that path (hardcoded in the reload plugin and script)

> If you clone this repo elsewhere, update the paths in `intellij.sh` and in `ThemeReloader.kt`.

### 2. Build the reload plugin

```bash
cd reload-plugin
./gradlew buildPlugin
```

This produces `reload-plugin/build/distributions/pywal-reload-plugin-1.0.0.zip`.
The application script will deploy it automatically on the next pywal run.

### 3. Run pywal

```bash
# Using the example parecolors colorscheme
wal --theme parecolors

# Or via a pywal runner script
python3 ~/dotfiles/scripts/pywal/run-pywal.py --theme parecolors --app intellij
```

The application script will:
1. Process the ICLS template → deploy to all IDE `colors/` directories
2. Build the theme JSON → package into `pywal-theme.jar` → deploy to all IDEs
3. Deploy the reload plugin JAR to all IDEs
4. Trigger live reload via `POST localhost:9988/reload`

## Customizing the theme

### Editor colors
Edit `pywal_color_scheme.icls`. Variables like `{syntaxKeyword}`, `{blue5}`, `{green3}` etc. are
substituted with actual hex values at apply-time. See [`.github/theme-variables.md`](.github/theme-variables.md)
for the full variable reference.

### UI colors
Edit `theme/ui-mapping.json`. This file maps IntelliJ UI key paths to palette variable names.
You do **not** need to re-run pywal — just trigger a reload:

```bash
curl -X POST http://localhost:9988/reload
```

Changes take effect immediately in any running IDE with the reload plugin installed.

## Color palette

Colors are driven by `parecolors.json`, which defines:

- Semantic variables: `background`, `foreground`, `accent`, `surface`, `selection`, …
- Syntax variables: `syntaxKeyword`, `syntaxString`, `syntaxType`, `syntaxComment`, …
- Palette ramps: `red1`–`red5`, `green1`–`green5`, `blue1`–`blue5`, `yellow1`–`yellow5`, `grey1`–`grey5`

The brightest (`5`) ramp levels are used for VCS status colors and project avatars.
The darkest (`1`/`2`) levels are used for background tints (file colors, diff backgrounds).

## Live reload

The reload plugin exposes:

```
POST http://localhost:9988/reload
```

It reads `~/.cache/wal/colors.json` and the project template files directly at runtime,
builds the theme in-memory, and applies it via IntelliJ's internal APIs — no restart needed.

If no IDE is running, the script skips the reload silently; the new theme will apply on next IDE start.

## License

MIT
