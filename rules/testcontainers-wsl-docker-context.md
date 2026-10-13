---
type: rule
---

# Docker on WSL: Docker Desktop's context breaks docker-py and Testcontainers

When Testcontainers fails with `npipe:// protocol is only supported on Windows` (in under a second: it never reached Docker, so don't debug the tests), or integration tests skip in an automated run and pass by hand, run `grep currentContext ~/.docker/config.json`: Docker Desktop's `desktop-linux` context is a Windows pipe, while the `docker` CLI keeps working. Fix it with `docker context use default` (again after a Docker Desktop restart) and `tc.host=unix:///var/run/docker.sock` in `~/.testcontainers.properties`; Testcontainers never reads `DOCKER_CONTEXT`. Not in `~/.bashrc`: it never reaches non-interactive runs, and an `unset DOCKER_HOST` there removes a fallback. Probe a clean environment with `env -i HOME="$HOME" …`, not from your own shell.
