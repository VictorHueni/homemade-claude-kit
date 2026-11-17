# Setting up a loc-audit

The `loc-auditor` agent of this plugin judges the findings of a source-code size and complexity scan: whether flagged code is really dead, duplicated, needless or too complex, and what to do about it. It names no language, tool or project. A project that wants it provides the scan, the files below and two commands; this page says what each must hold.

The split is deliberate: the agent (the judgement) is shared and lives here, the scanners are language-specific and live in each project. One project's scan never has to look like another's, only its files.

## What the project provides

| Piece | Calls a model | Purpose |
| --- | --- | --- |
| `make loc-audit-scan` | no | Runs the project's own analysis tools, writes the findings file and the diff file into a dated scan folder, and the context file when the project has one. Costs nothing but time. |
| `make loc-audit` | yes, Opus | Runs the scan, then the agent on the diff file. Paid: it runs on a person's request, never on a schedule the project did not decide. |
| Taxonomy file | — | The project's categories and what its scan can and cannot tell; committed. |
| Reviewed file | — | The findings a reader ruled on; committed. |

`make loc-audit` calls the installed agent by its name, so the project keeps no copy of the prompt:

```make
loc-audit: loc-audit-scan
	@OUT=$(LOC_AUDIT_DIR)/scan-$$(date +%F) && \
	claude -p --agent loc-auditor --allowedTools "Read,Grep,Glob" \
	  "Run in review mode. Diff file: $$OUT/diff.json. Taxonomy file: <path>. Reviewed file: <path>. Context file: $$OUT/context.json." \
	  < /dev/null > $(LOC_AUDIT_DIR)/$$(date +%F)-auditor.md
```

The name is `loc-auditor` when the kit is installed through `install.sh` (the symlink channel, or a project install). On the marketplace channel a plugin agent can carry its plugin's prefix: `/agents` in a session shows the name to use. Without `< /dev/null`, `claude -p` waits three seconds for standard input before it starts.

For full-tree mode, give the findings file instead of the diff file and name the categories to judge in the request.

## The findings file

One JSON report per scan. Every finding is a candidate a tool established mechanically, never a conclusion.

```json
{
  "schema_version": "2.0",
  "generated_at": "2026-11-17T10:00:00+00:00",
  "stack": "src",
  "category_counts": { "unreferenced": 3, "complex_function": 5 },
  "findings": [
    {
      "fingerprint": "<sha256 hex>",
      "severity": "high",
      "category": "unreferenced",
      "file": "src/main/java/org/example/Orders.java",
      "line": 40,
      "symbol": "legacyTotal",
      "summary": "legacyTotal: no reference beyond its definition",
      "stack": "src"
    }
  ]
}
```

- `severity` is `high`, `medium` or `low`; `file` is relative to the repository root.
- `symbol` names what the finding is about: a function, a class, `<file>` for a finding about a whole file, a hash of the duplicated text for a clone group.
- **The fingerprint is the finding's identity across scans.** Compute it from the stack, the category, the file and the symbol, never from the line or a score, so that a finding keeps it when the file shifts or a number moves: `sha256("{stack}|{category}|{file}|{symbol}")`, with every digit of the symbol replaced by `#` so that a numbered name keeps its identity when the number changes. A symbol that moves to another file is a new finding, which is intended: a reader rules on it again.

## The categories

The taxonomy file is the ground truth for category names; a project lists only the categories its scan produces. The agent knows how to judge these, by these names:

| Category | What the scan establishes |
| --- | --- |
| `unreferenced` | The symbol appears only at its definition, in code, scripts, build files and tests. |
| `test_only` | The same, except that at least one test names it. |
| `pass_through_wrapper` | A function whose whole body forwards one call with its own parameters. |
| `clone_cluster` | A group of duplicated code above the project's threshold (copies and length). |
| `complex_function` | Cyclomatic or cognitive complexity above the project's threshold. |
| `long_file` | A file above the project's line threshold. |
| `flag_argument` | A boolean parameter that may select between two behaviours. |
| `single_consumer_core_module` | A module of the shared layer that exactly one user imports. |

A finding a tool cannot reach (a name built from a string, a framework that discovers handlers) is still listed; the taxonomy says so and the agent reads the code.

## The taxonomy file

Markdown, committed, handed to the agent on every run. It holds:

- per category: its severity, the tool it comes from, what the scan established and what it cannot tell;
- what the scan leaves out on purpose, and how it counts references (code tokens, or a text search over named folders);
- the project's language and layout, the code its frameworks call without naming it, the registries its tests read by design, what repeats by design, where a shared helper belongs, and where its decisions (ADRs, plans) live;
- the external analyser and the tracker the context file reads, and what their measures mean.

The more of the project's false-positive shapes it names, the fewer findings the agent has to argue from scratch.

## The reviewed file and the diff file

The reviewed file lists the findings a reader ruled on and kept. A fixed finding needs no entry: it stops appearing.

```json
{
  "entries": [
    {
      "fingerprint": "<sha256 hex>",
      "category": "test_only",
      "file": "src/main/java/org/example/Registry.java",
      "symbol": "KNOWN_CODES",
      "verdict": "keep",
      "reviewed": "2026-11-17",
      "reason": "Registry a guard test compares with the schema."
    }
  ]
}
```

The agent's verdict block gives each `keep` a `reason` written to be pasted here.

The diff file is what review mode reads. It hides nothing by deletion:

```json
{
  "current": { "...": "the findings file, whole" },
  "diff": { "new": [ ], "carried": [ ], "resolved": 4 },
  "top_new": [ ]
}
```

- `diff.new` and `diff.carried` are the findings on each side of the reviewed file; `diff.resolved` is a count of reviewed fingerprints that no longer appear, never a list.
- `top_new` holds at most eight new findings, most severe first. Within a severity the order is `unreferenced`, `test_only`, `clone_cluster`, `pass_through_wrapper`, `complex_function`, `long_file`, `single_consumer_core_module`, `flag_argument`, and no category takes more than two places while another still has a new finding.

## The context file (optional)

What other sources already know about the flagged files. The scan fetches it; the agent never calls them. A source the scan could not read is marked `not read`, and the scan still succeeds.

```json
{
  "sources": { "sonar": "read", "tracker": "not read" },
  "files": {
    "src/main/java/org/example/Orders.java": {
      "sonar": { "measures": { "cognitive_complexity": 41 }, "issues": [] },
      "tracker": [{ "number": 12, "title": "…", "url": "…", "match": "path" }]
    }
  },
  "tracked_resolved": [{ "number": 9, "title": "…", "url": "…", "match": "fingerprint", "fingerprints": ["<sha256 hex>"] }]
}
```

A tracker item matches a finding by `fingerprint` when its body carries the line `loc-audit-fingerprint: <fingerprint>`, and a file by `path` when its title or body names the file. `tracked_resolved` lists the items whose every fingerprint has left the findings.

## Checking a new setup

Run `make loc-audit-scan` twice on an unchanged tree: the fingerprints must be identical. Then run `make loc-audit` once and walk the manual checklist at the end of the agent's prompt (`agents/loc-auditor.md`).
