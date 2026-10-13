---
type: rule
paths:
  - "**/pom.xml"
  - "**/build.gradle*"
  - "**/mvnw"
  - "**/.mvn/**"
  - "**/*.java"
  - "**/mise.toml"
  - "**/.github/workflows/**"
---

# JVM toolchain

- **Maven over Gradle** for new JVM projects (Maven multi-module, wrapper committed, `only-script` distribution is fine); use Gradle only where a repo already standardises on it.
- **OpenJDK builds only, never the Oracle-licensed JDK:** pin Eclipse Temurin in `mise.toml` and CI (`actions/setup-java` with `distribution: temurin`); a distro OpenJDK is fine locally.
- **Target the current LTS** (`maven.compiler.release`), not the previous one, after checking that the framework and toolchain actually build on it.
- On WSL, a `mvn` on `PATH` can be a Windows Maven under `/mnt/c/`; use the project's `./mvnw` or a Linux Maven.
