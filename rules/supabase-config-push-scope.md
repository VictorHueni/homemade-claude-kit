---
type: rule
paths:
  - "**/supabase/**"
---

# Supabase: `config push` pushes the whole local config

**`supabase config push` diffs the entire `config.toml` against the hosted project.** The base file is the local-dev config (localhost `site_url` and redirects, short OTPs, MFA off). For a ref with no matching `[remotes.<env>]` block (`project_id = "<ref>"`, deep-merged over the base), that dev config is what gets pushed. Never push a hosted ref without its block. With the blocks in place, config push (ideally from CI) is the right tool: secrets come in through `env()`, and `project_id` must name an existing project or branch, so creating and configuring a branch takes two commits.

**Its prompts are not a safety gate.** Without a TTY every `[Y/n]` auto-confirms, and there is no `--dry-run`. `yes n | supabase config push` works as a read-only diff viewer. A push that errors partway may already have applied earlier sections: diff before assuming nothing changed.

**For one hosted setting, PATCH the Management API instead:** `GET` then `PATCH https://api.supabase.com/v1/projects/<ref>/config/auth` with only the intended fields (token in `~/.supabase/access-token`, not an old `~/.supabase_token`), then `GET` again and check fields you did not send. Names differ from `config.toml`: `enable_confirmations` is the inverse of `mailer_autoconfirm`, `otp_length` is `mailer_otp_length`, `[auth.email] max_frequency` is `smtp_max_frequency` (seconds), `secure_password_change` is `security_update_password_require_reauthentication`, `additional_redirect_urls` is the comma-joined `uri_allow_list`.

**SMTP is the dangerous group.** A local `[auth.email.smtp]` section that is absent leaves the hosted block alone; one present with `enabled = false` wipes it. A PATCH carrying some SMTP fields replaces the whole block: send the complete set and re-assert the email rate limit in the same call.

**If a push already went wrong,** save its diff output first: the `remote` side is the pre-push state. Restore only the damaged fields by PATCH, then verify with a GET of every expected value (the SMTP block included) and with `yes n | supabase config push`.
