package com.github.jliima.pywal.reload

import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.application.PathManager
import com.intellij.openapi.diagnostic.thisLogger
import com.intellij.openapi.editor.colors.EditorColorsManager
import com.intellij.openapi.editor.colors.impl.EditorColorsSchemeImpl
import com.intellij.openapi.util.JDOMUtil
import com.intellij.ide.actions.QuickChangeLookAndFeel
import com.intellij.ide.ui.LafManager
import com.intellij.ide.ui.UITheme
import com.intellij.ide.ui.laf.UIThemeLookAndFeelInfo
import com.intellij.ide.ui.laf.UIThemeLookAndFeelInfoImpl
import java.io.File

object ThemeReloader {
    private val log = thisLogger()

    fun reload(): Result<String> = runCatching {
        val messages = mutableListOf<String>()
        ApplicationManager.getApplication().invokeAndWait {
            reloadUiTheme()?.let { messages += it }
            reloadEditorScheme()?.let { messages += it }
        }
        messages.joinToString("; ").ifEmpty { "ok" }
    }

    private fun reloadUiTheme(): String? {
        val jsonFile = File(System.getProperty("user.home"), ".cache/wal/colors-intellij-theme.json")
        if (!jsonFile.exists()) {
            log.warn("Theme JSON not found: $jsonFile")
            return "theme JSON missing"
        }

        val theme = jsonFile.inputStream().use { stream ->
            @Suppress("UnstableApiUsage")
            UITheme.Companion.loadTempThemeFromJson(stream, "pywal-theme")
        }

        // Explicit cast to UIThemeLookAndFeelInfo to resolve overload ambiguity
        val lafInfo: UIThemeLookAndFeelInfo = UIThemeLookAndFeelInfoImpl(theme)
        QuickChangeLookAndFeel.switchLafAndUpdateUI(LafManager.getInstance(), lafInfo, false)
        log.info("Pywal UI theme reloaded from $jsonFile")
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
}
