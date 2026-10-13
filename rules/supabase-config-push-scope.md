---
type: rule
paths:
  - "**/supabase/**"
---

# `supabase config push` pushes the whole config — and the base `config.toml` IS the local-dev config

## The trap: one intended setting in, the entire local dev config out

`supabase config push` diffs the project's **entire local `config.toml`** against the linked hosted project and pushes every difference — not the one setting you meant to change. This is the documented contract, not a bug: the command is officially Supabase's config-as-code mechanism ("manage project configuration as code by defining settings locally and then pushing them", CLI v2, Nov 2024). The trap is structural: **the base `config.toml` is the local-dev config** (localhost `site_url`, localhost redirect allow-lists, fast-iteration rate limits like `max_frequency = "1s"`, short OTPs, MFA off) and there is no `[local]` override section (supabase/cli#4732, closed not-planned) — local is the unprotected base, and every hosted environment must be an explicit exception via a `[remotes.<env>]` block. Push a hosted ref that has **no matching `[remotes]` entry** and the raw dev config goes out verbatim. Measured incident: an intended two-field password-policy push to a hosted staging project also rewrote `site_url` to `http://localhost:3010`, narrowed the redirect allow-list to localhost (breaking every magic-link/recovery email the project would send), disabled MFA TOTP and email confirmations, and dropped the email OTP from 8 to 6 chars.

**Worse: without a TTY, the CLI auto-confirms its own `[Y/n]` prompts — by design.** Source-verified (`apps/cli-go/internal/utils/console.go`): with no TTY, `ReadLine` waits 100 ms for stdin then returns empty, and `PromptYesNo` returns its default on empty input — which config push sets to **true**. A global `--yes` flag ("answer yes to all prompts") exists on every command. The prompts are deliberately non-blocking so CI can run push unattended; they are **not a safety gate**. The push in the measured case "failed" with a 402 on a later storage prompt — which made it look aborted — while the auth section had already been applied. There is **no `--dry-run`**; a re-run with `yes n |` (each per-section prompt reads one "n") is the only way to use the command as a **read-only diff viewer**, and that remains reliably useful.

## The structural fix: `[remotes.<env>]` blocks make config push safe by construction

CLI v2 (Nov 2024) added per-environment override blocks in `config.toml` — the sanctioned multi-environment pattern:

```toml
[remotes.staging]
project_id = "<staging-ref>"
[remotes.staging.auth]
site_url = "https://staging.example.com"
# All standard config sections are available under [remotes.<env>] — db, api, auth, functions…
```

When `config push --project-ref <ref>` finds a remote whose `project_id` matches the pushed ref, it **deep-merges that block over the base config** and pushes the result; with no matching block it falls back to the bare base config — which is exactly the incident path. Secrets go in via `env()` from CI secret storage. So the ecosystem-correct posture is: **never push a hosted ref that lacks a `[remotes.<its-ref>]` block**; with the blocks in place, config push (ideally from CI) is the right tool for config-as-code, and the auto-yes design intent belongs there. Note the docs' constraint: `project_id` must refer to an existing project/branch, so you cannot provision and configure a persistent branch in one commit.

## How to change one hosted setting NOW: surgical Management API PATCH

For one-off scoped changes and emergency restores — complementary to remotes-based config-as-code, not an alternative. `PATCH /v1/projects/{ref}/config/auth` is a fully documented public endpoint (all body params optional — partial update is the contract), and it is literally what the CLI itself calls under config push.

```bash
TOKEN=$(cat ~/.supabase/access-token)   # the CLI's real token store — not any stale ~/.supabase_token file
# 1. Read current state FIRST (also your restore record):
curl -sS "https://api.supabase.com/v1/projects/<ref>/config/auth" -H "Authorization: Bearer $TOKEN"
# 2. PATCH only the intended fields:
curl -sS -X PATCH "https://api.supabase.com/v1/projects/<ref>/config/auth" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"password_min_length": 12}'
# 3. GET readback to verify — including fields you did NOT send.
```

Field names differ from `config.toml`: `enable_confirmations` → inverted `mailer_autoconfirm`, `otp_length` → `mailer_otp_length`, `[auth.email] max_frequency` → `smtp_max_frequency` (seconds), `secure_password_change` → `security_update_password_require_reauthentication`, `additional_redirect_urls` → comma-joined `uri_allow_list`.

## The SMTP block is the highest-stakes field group

Hosted GoTrue configs often carry a custom-SMTP block (host/port/user/**password**/sender). Three behaviors, all verified (two empirically, one in CLI source `pkg/config/auth.go`):

- A PATCH (or config push) whose local `[auth.email.smtp]` section is **absent/commented out** leaves the hosted block intact — "when local config is not set, we assume platform defaults should not change".
- A local `[auth.email.smtp]` section **present with `enabled = false`** actively **wipes the hosted SMTP block**: the CLI sends `smtp_host = ""` and the API resets all SMTP values — strictly worse than omission, and silent.
- A PATCH that **includes some** SMTP field replaces the whole block — sending `smtp_pass` alone wipes `smtp_host` etc., and the project silently falls back to the platform's built-in mailer, breaking DMARC alignment on a `p=reject` domain. If you must touch anything SMTP-adjacent, send the complete SMTP field set and re-assert the email rate limit in the same PATCH. (The API-side replace-whole-block behavior is undocumented officially; this empirical record is the only one.)

## Recovery, when the trap has already fired

The failed push's own diff output is a **perfect record of the pre-push remote state** (`--- remote[auth]` side) — save it before doing anything else; it is the restore target. Cross-check against the project's ops runbook/bootstrap doc for the documented hosted values, restore via a surgical PATCH of only the damaged fields, then verify twice: an independent GET readback of every expected value (including untouched ones like the SMTP block), and `yes n | supabase config push` showing the remote back on the documented side of the diff.

**Anti-pattern in self:** reaching for `config push` because the setting lives in `config.toml` locally. Without a `[remotes.<env>]` block for the target ref, the file describes the *local* environment only, and the push exports dev posture to production infrastructure. Either adopt remotes blocks so the push is safe by construction, or go through the Management API with explicit fields — always with a GET-before and a GET-after.
