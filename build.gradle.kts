plugins {
    kotlin("jvm") version "2.2.0"
    id("io.quarkus") version "3.24.0"
}

kotlin {
    jvmToolchain(21)
    compilerOptions {
        progressiveMode = true
        freeCompilerArgs = listOf("-Xjsr305=strict", "-Xjdk-release=21")
        allWarningsAsErrors = true
    }
}

group = "com.ia_ecommerce_assistant.catalog"
version = "1.0.0-SNAPSHOT"

repositories {
    mavenCentral()
    mavenLocal()
}

dependencies {
    implementation(enforcedPlatform("io.quarkus.platform:quarkus-bom:3.24.1"))
    implementation(kotlin("stdlib-jdk8"))
    implementation("io.quarkus:quarkus-rest-kotlin-serialization")
    implementation("io.quarkus:quarkus-kotlin")
    implementation("io.quarkus:quarkus-arc")
    testImplementation("io.quarkus:quarkus-junit5")
    testImplementation("io.rest-assured:rest-assured")
}

tasks.withType<JavaCompile>().configureEach {
    sourceCompatibility = "21"
    targetCompatibility = "21"
}

java {
    sourceCompatibility = JavaVersion.VERSION_21
    targetCompatibility = JavaVersion.VERSION_21
}


quarkus {
    // Adicione configurações específicas do Quarkus aqui, se necessário
}


