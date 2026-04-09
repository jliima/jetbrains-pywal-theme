package com.github.jliima.pywal.reload

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ObjectNode
import com.fasterxml.jackson.databind.node.TextNode
import com.intellij.ide.actions.QuickChangeLookAndFeel
import com.intellij.ide.ui.LafManager
import com.intellij.ide.ui.UITheme
import com.intellij.ide.ui.laf.UIThemeLookAndFeelInfo
import com.intellij.ide.ui.laf.UIThemeLookAndFeelInfoImpl
import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.application.PathManager
import com.intellij.openapi.diagnostic.thisLogger
import com.intellij.openapi.editor.colors.EditorColorsManager
import com.intellij.openapi.editor.colors.impl.EditorColorsSchemeImpl
import com.intellij.openapi.util.JDOMUtil
import java.io.File

object ThemeReloader {
    private val log = thisLogger()
    private val mapper = ObjectMapper()

    // Path to the ui-mapping.json in the project
    private val mappingFile = File(
        System.getProperty("user.home"),
        "JetBrainsProjects/jetbrains-pywal-theme/theme/ui-mapping.json"
    )

    fun reload(): Result<String> = runCatching {
        val messages = mutableListOf<String>()
        ApplicationManager.getApplication().invokeAndWait {
            reloadUiTheme()?.let { messages += it }
            reloadEditorScheme()?.let { messages += it }
        }
        messages.joinToString("; ").ifEmpty { "ok" }
    }

    private fun reloadUiTheme(): String? {
        val colorsFile = File(System.getProperty("user.home"), ".cache/wal/colors.json")
        if (!colorsFile.exists()) {
            log.warn("colors.json not found: $colorsFile")
            return "colors.json missing"
        }
        if (!mappingFile.exists()) {
            log.warn("ui-mapping.json not found: $mappingFile")
            return "ui-mapping.json missing"
        }

        val themeJson = buildThemeJson(colorsFile, mappingFile)
        val theme = themeJson.byteInputStream().use { stream ->
            @Suppress("UnstableApiUsage")
            UITheme.Companion.loadTempThemeFromJson(stream, "pywal-theme")
        }

        val lafInfo: UIThemeLookAndFeelInfo = UIThemeLookAndFeelInfoImpl(theme)
        QuickChangeLookAndFeel.switchLafAndUpdateUI(LafManager.getInstance(), lafInfo, false)
        log.info("Pywal UI theme reloaded from $colorsFile + $mappingFile")
        return "UI theme reloaded"
    }

    private fun reloadEditorScheme(): String? {
        val configPath = PathManager.getConfigPath()
        val iclsFile = File(configPath, "colors/pywal-color-scheme.icls")
        if (!iclsFile.exists()) {
            log.warn("ICLS not found: $iclsFile")
            return "ICLS missing"
        }

        val colorsManager = EditorColorsManager.getInstance()
        val parentScheme = colorsManager.getScheme("Darcula")
            ?: colorsManager.allSchemes.firstOrNull()
            ?: return "no parent scheme available"
        val scheme = EditorColorsSchemeImpl(parentScheme)

        val element = JDOMUtil.load(iclsFile)
        scheme.readExternal(element)

        colorsManager.addColorScheme(scheme)
        colorsManager.setGlobalScheme(scheme)
        log.info("Pywal editor scheme reloaded from $iclsFile")
        return "editor scheme reloaded"
    }

    /**
     * Combines colors.json palette with ui-mapping.json to produce a full IntelliJ theme JSON.
     * The mapping's ui/icons sections reference color variable names (e.g. "border", "accent")
     * which are resolved from the palette into a `colors` section.
     */
    private fun buildThemeJson(colorsFile: File, mappingFile: File): String {
        // Build flat palette: name → #hex from special.* and colors.*
        val colorsRoot = mapper.readTree(colorsFile)
        val palette = mutableMapOf<String, String>()
        colorsRoot.get("special")?.fields()?.forEach { (k, v) -> palette[k] = v.asText() }
        colorsRoot.get("colors")?.fields()?.forEach { (k, v) -> palette[k] = v.asText() }

        // Load mapping (contains name, dark, editorScheme, ui, icons)
        val mapping = mapper.readTree(mappingFile) as ObjectNode

        // Build colors section from full palette
        val colorsNode = mapper.createObjectNode()
        palette.forEach { (k, v) -> colorsNode.put(k, v) }

        // Assemble final theme object: mapping fields + injected colors section
        val theme = mapper.createObjectNode().apply {
            put("name",         mapping.get("name").asText())
            put("dark",         mapping.get("dark").asBoolean())
            put("editorScheme", mapping.get("editorScheme").asText())
            set<ObjectNode>("colors", colorsNode)
            set<ObjectNode>("ui",     mapping.get("ui") as ObjectNode)
            mapping.get("icons")?.let { set<ObjectNode>("icons", it as ObjectNode) }
        }

        return mapper.writeValueAsString(theme)
    }
}
