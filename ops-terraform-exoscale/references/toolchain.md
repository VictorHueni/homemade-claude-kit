# Toolchain

Deterministic, well-known tools only. Pinned versions (bump here on refresh, then re-test):

| Tool | Pinned | Role |
| :--- | :--- | :--- |
| Terraform | `>= 1.6` | `fmt`, `validate`, `init`, `plan` |
| Exoscale provider | `~> 0.69` (0.69.2) | provider plugin |
| tflint | `v0.62.1` | HCL linter (correctness, deprecations, naming) |
| Trivy | `v0.70.0` | Built-in IaC misconfig + secret scan (`trivy fs --scanners misconfig,secret`) |

Trivy is **auto-detected**: the scan runs when `trivy` is on `PATH` and is skipped (with a warning, not a failure) when it is absent. Checkov remains out of scope.

## The pipeline (what `scripts/tf-check.sh` runs)

1. `terraform fmt -check -recursive -diff` — formatting. Deterministic; no network. Fix with `terraform fmt`.
2. `terraform init -backend=false` + `terraform validate` — config correctness without touching remote state.
3. `tflint --init` (installs the `terraform` ruleset plugin) + `tflint` — lint rules: naming conventions, unused declarations, deprecated syntax, unpinned module sources.
4. `exoscale-policy.sh` — native, dependency-free Exoscale security checks (always runs). Starter check `EXO-001` fails when an `exoscale_security_group_rule` opens SSH (22) INGRESS to `0.0.0.0/0`.
5. `trivy fs --scanners misconfig,secret --severity HIGH,CRITICAL --exit-code 1` — built-in IaC misconfig (generic) + secret detection. Skipped with a warning if trivy is absent.
6. `terraform plan` — read-only diff against the real API (needs `EXOSCALE_API_KEY`/`SECRET`, and a real `init` if a backend is configured). **The pipeline stops here — never `apply`.**

The script exits non-zero on the first failing stage and prints which tool is missing if a binary isn't on `PATH`.

## Installing the tools

**Terraform** — via [tfenv](https://github.com/tfutils/tfenv) or the [official install](https://developer.hashicorp.com/terraform/install):

```bash
tfenv install 1.9.8 && tfenv use 1.9.8   # any >= 1.6
```

**tflint** — pinned install:

```bash
curl -sSL https://raw.githubusercontent.com/terraform-linters/tflint/v0.62.1/install_linux.sh | bash
tflint --version   # expect 0.62.1
```

(macOS: `brew install tflint`; verify the version matches the pin.)

**Trivy** — pinned install:

```bash
curl -sSL https://raw.githubusercontent.com/aquasecurity/trivy/v0.70.0/contrib/install.sh | sh -s -- -b /usr/local/bin v0.70.0
trivy --version   # expect 0.70.0
```

(macOS: `brew install trivy`; verify the version matches the pin.)

## Scanning notes

- **Coverage caveat.** Trivy's built-in misconfiguration checks (the Aqua Vulnerability Database) target AWS / Azure / GCP / Kubernetes / Docker — there are **no Exoscale-specific built-in checks**. On pure-Exoscale HCL the built-in pass mostly finds generic Terraform issues; its real value here is **secret detection** (catches hardcoded credentials, reinforcing the no-secrets safety rule).
- **Why Exoscale gating is native, not Trivy custom Rego.** Trivy's custom-Rego mechanism for Terraform (`--config-check` + `--check-namespaces`) does **not reliably fire** — verified on Trivy 0.70, an *unconditional* `deny` against a definitely-present resource never renders, matching open Trivy issues ([#2856](https://github.com/aquasecurity/trivy/issues/2856), [discussion #6453](https://github.com/aquasecurity/trivy/discussions/6453)). Shipping a Rego check that silently never fires would be false security. So Exoscale-specific gating lives in **`scripts/exoscale-policy.sh`** — a deterministic, dependency-free HCL check. Add new checks there following the `EXO-001` pattern.
- **Suppressions** for Trivy findings go in the scaffolded `.trivyignore` (one ID per line, with a justifying comment). Trivy auto-loads it from the scan dir. (The native `exoscale-policy.sh` has no suppression file — it is one focused check; fix the finding or remove the check.)
- **Determinism footnote.** `trivy fs` downloads its built-in checks bundle from a registry on first run and caches it (~24h TTL). For fully offline/reproducible CI, warm the cache once then pass `--skip-check-update`, or pin the bundle via `--checks-bundle-repository`. The native `exoscale-policy.sh` has no network dependency and is always deterministic.

## `.tflint.hcl` rationale

The scaffolded config enables the bundled `terraform` ruleset with `preset = "recommended"` — naming conventions, `terraform_required_version`, `terraform_required_providers`, unused declarations, deprecated-interpolation, and comment-syntax checks. There is no Exoscale-specific tflint ruleset plugin, so provider-specific correctness is handled by `terraform validate` + the recipes/gotchas in `exoscale-provider.md`.
