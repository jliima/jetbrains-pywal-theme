plugins {
    id("org.jetbrains.kotlin.jvm") version "2.1.20"
    id("org.jetbrains.intellij.platform") version "2.13.1"
}

group = providers.gradleProperty("pluginGroup").get()
version = providers.gradleProperty("pluginVersion").get()

repositories {
    mavenCentral()
    intellijPlatform {
        defaultRepositories()
    }
}

dependencies {
    intellijPlatform {
        // Target the oldest supported version installed on this machine
        intellijIdeaUltimate("2024.2")
    }
}

intellijPlatform {
    pluginConfiguration {
        id = "com.github.jliima.pywal.reload"
        name = "Pywal Theme Reloader"
        version = providers.gradleProperty("pluginVersion").get()
        ideaVersion {
            sinceBuild = "242"
        }
    }
    buildSearchableOptions = false
}

kotlin {
    jvmToolchain(17)
}
