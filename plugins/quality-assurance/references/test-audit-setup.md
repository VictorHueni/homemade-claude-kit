# Setting up a test-audit

The `test-auditor` agent of this plugin judges the findings of a test-decay scan: whether a flagged test can really fail on a regression, duplicates another, is obsolete, or only restates its own fixture, and what to do about it. It names no language, test framework or project. A project that wants it provides the scanners, the files below and two commands; this page says what each must hold.

The split is deliberate: the agent (the judgement) is shared and lives here, the scanners are language-specific and live in each project. One project's scan never has to look like another's, only its files.

## What the project provides

| Piece | Calls a model | Purpose |
| --- | --- | --- |
| `make test-audit-scan` | no | Runs the project's scanners, one per stack, and writes one merged findings file. Costs nothing but time. |
| `make test-audit` | yes, Opus | Runs the scan, computes the diff file against the reviewed baseline, then runs the agent on it. Paid: it runs on a person's request or on a schedule the project decided. |
| Taxonomy file | — | The project's categories per stack, what its scan can and cannot tell, and what the auditor needs to know about the project; committed. |
| Diff engine | no | Compares the findings file with the reviewed baseline and selects `top_new`; kept in the project. |

`make test-audit` calls the installed agent by its name, so the project keeps no copy of the prompt:

```make
TEST_AUDITOR_AGENT ?= test-auditor

test-audit: test-audit-scan
	@DIFF_FILE=$(TEST_AUDIT_DIR)/$$(date +%F).json && \
	<diff engine> > "$$DIFF_FILE" && \
	claude -p --agent $(TEST_AUDITOR_AGENT) \
	  "Run in review mode. Diff file: $$DIFF_FILE. Taxonomy file: <path>." \
	  --allowedTools "Read,Grep,Glob" < /dev/null > $(TEST_AUDIT_DIR)/$$(date +%F).md
```

The name is `test-auditor` when the kit is installed through `install.sh` (the symlink channel, or a project install), and `quality-assurance:test-auditor` on the marketplace channel, where plugin agents carry their plugin's name. The request comes before `--allowedTools`, which takes every argument after it as a tool name. Without `< /dev/null`, `claude -p` waits three seconds for standard input before it starts.

For full-suite mode, give the findings file instead of the diff file and name the categories, or the duties, to judge in the request.

**In CI**, a runner has no kit installed. Fetch the agent at a pinned kit commit and send its body with the request, so that a change to the kit reaches CI only through a reviewed change of the pin:

```bash
curl -fsSL "https://raw.githubusercontent.com/VictorHueni/homemade-claude-kit/<commit>/plugins/quality-assurance/agents/test-auditor.md" \
  -o "$RUNNER_TEMP/test-auditor.md"
```

## The findings file

One JSON report per scan, every stack's findings merged. Every finding is a candidate a tool established mechanically, never a conclusion.

```json
{
  "schema_version": "2.0",
  "generated_at": "2026-11-17T10:00:00+00:00",
  "category_counts": { "no_assertions": 3, "disabled_test": 1 },
  "findings": [
    {
      "fingerprint": "<sha256 hex>",
      "severity": "high",
      "category": "no_assertions",
      "file": "src/test/java/org/example/OrdersTest.java",
      "line": 42,
      "summary": "totalIsComputed: no assertion",
      "stack": "backend"
    }
  ]
}
```

- `severity` is `critical`, `high`, `medium` or `low`, or an info tier the taxonomy names, which never enters `top_new`; `file` is relative to the repository root.
- `stack` names the scanner that produced the finding (`backend`, `frontend`, `contract`, or the project's own names). The report keeps one section per stack.
- **The fingerprint is the finding's identity across scans.** Compute it from the stack, the category, the file, the owning test and the finding's detail, never from the line: `sha256("{stack}|{category}|{file}|{test}|{detail}")`, with every digit of the detail replaced by `#`, so that "identical to 3 other tests" keeps its identity when the 3 becomes 2. A test that moves to another file is a new finding, which is intended.

## The categories

The taxonomy file is the ground truth for category names; a project lists only the categories its scan produces. The agent has a judgment duty for these, by these names:

| Category | What the scan establishes |
| --- | --- |
| `no_assertions`, `no_assert_block` | The test makes no assertion. |
| `vacuous_assertion` | Its sole assertion is a bare truthiness or not-null check. |
| `tautological_assertion` | An assertion compares a value with what the same test planted into it earlier. |
| `loop_only_assertion` | An assertion sits only inside a loop, with no check that the loop runs. |
| `conditional_expect` | An assertion sits where it may not run: a catch that swallows, an `if` with no `else`, a loop over a collection not known to be non-empty. |
| `no_production_call` | The test reaches nothing of the production tree. |
| `disabled_test` | The test is skipped. |
| `redundant_duplicate` | Its body is structurally identical to another test's in the same file. |
| `tombstone_candidate` | Every assertion is an absence. |
| `mutation_survivor` | A mutant of production code survived the suite. |

Any other category is judged on the taxonomy's description; one the taxonomy marks as pass-through is reported as the scan states it.

## The taxonomy file

Markdown, committed, handed to the agent on every run. It holds:

- per stack: the scanner and the folders it reads; per category: its severity, what the scan established and what it cannot tell;
- what the scan leaves out on purpose, the idioms it drops, and which stacks or categories are pass-through;
- a section **"What the auditor needs to know about this project"**: the test tiers and their folders, the gates that already enforce a rule (a type checker over the tests, layout or architecture tests), the names the scanners allowlist, where plans, decisions and the release record live, how long a tombstone lives, the table of test subjects if there is one, the capabilities the scan does not have yet, and the project's own checklist items, tied to its golden fixtures.

The more of the project's false-positive shapes it names, the fewer findings the agent has to argue from scratch.

## The baseline and the diff file

The baseline is the set of fingerprints already reviewed. The diff engine compares the findings file with it, never silently drops a finding, and adds this run's `top_new` to the baseline, so that a finding beyond the cap stays new until it gets a review slot.

```json
{
  "current": { "...": "the findings file, whole" },
  "diff": { "new": [ ], "carried": [ ], "resolved": 3, "collisions": 0, "baseline_reseeded": false },
  "top_new": [ ]
}
```

- `diff.new` and `diff.carried` are the findings on each side of the baseline; `diff.resolved` is a count of reviewed fingerprints that no longer appear, never a list.
- When the baseline is absent or of another schema version, the engine reseeds it: every current finding becomes reviewed, `new` is empty and `baseline_reseeded` is `true`.
- `top_new` holds at most eight new findings, most severe first, info tier excluded; `mutation_survivor` and `tombstone_candidate` take at most two places each.

## Checking a new setup

Run `make test-audit-scan` twice on an unchanged tree: the fingerprints must be identical. Then run `make test-audit` once and walk the manual checklist at the end of the agent's prompt (`agents/test-auditor.md`), with the project's own items from its taxonomy file.
