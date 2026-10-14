# Skill naming convention

Folder name and `name:` field follow `<category>-<artifact-singular>[-<verb>]`. For a doc-producing skill the category names the output folder under `docs/`; for a utility it names the function.

## Categories (exactly one)

| Category | Output folder | Examples |
|---|---|---|
| `business-` | `docs/business/` | `business-persona`, `business-capability-map`, `business-value-stream`, `business-process`, `business-model-canvas`, `business-quantitative-model` |
| `discovery-` | `docs/discovery/` (pre-formal evidence: ideation, interviews, workshops; feeds every downstream artefact) | `discovery-idea` (→ `ideation/`), `discovery-research` (→ `interviews/`), `discovery-workshop` (→ `workshops/`) |
| `spec-` | `docs/product-specs/` | `spec-prd`, `spec-functional-breakdown-structure`, `spec-quality-attributes`, `spec-use-case` |
| `plan-` | `docs/plans/` (intended build sequence) | `plan-delivery-roadmap` (epics `E-NN`), `plan-implementation` (`Plan-NNNN`) |
| `arch-` | `docs/architecture/` (subfolder per artefact type) | `arch-adr` (→ `decisions/`), `arch-c4`, `arch-uml` |
| `domain-` | `docs/domain/` (DDD: the shared language between business and tech) | `domain-bounded-context`, `domain-glossary`, `domain-model` |
| `ops-` | `docs/ops/`, or no doc folder for infra automation | `ops-runbook` (→ `runbooks/`), `ops-bug-rca` (→ `rcas/`), `ops-terraform-exoscale` (scaffolds into `infra/`) |
| `qa-` | `docs/qa/` | Tests that verify the quality requirements `spec-quality-attributes` defines (`QA-XXNN`): `qa-test-strategy` (`TS-NN`, pyramid allocation, policy only), `qa-test-scenario` (`UC-NN.SC-NN`, `TC-NN`). Reserved, no skill yet: `qa-test-plan`, `qa-acceptance-test` (execution, results, bug filing) |
| `dev-` | none (developer workflow) | `dev-git-init`, `dev-release-init`, `dev-git-commit`, `dev-pr`, `dev-git-worktree`, `dev-stack-guide`, `dev-getting-started` |
| `agent-` | none (agent-centric development: Guide → Verify → Solve) | `agent-config` (Guide), `agent-grill-me`, `agent-peer-review` (Verify), `agent-ralph-loop`, `agent-issue-loop` (Solve), `agent-handoff` |
| `ux-` | `docs/ux/` (design source; the resolved design themes `com-`) | `ux-design-system` (→ `package.json` pin, or `DESIGN.md` + generated `design-system/`) |
| `com-` | `docs/communication/` | `com-slide-deck` (→ `slides/{slug}/`), `com-artefact-viz`, `com-release-note` (→ `release-notes/`) |
| `util-` | none (housekeeping) | `util-docs-audit`, `util-docs-lint`, `util-open-items`, `util-toolkit-doctor` |

## Artefact name

The noun the skill produces, kebab-case, singular, the natural English noun for the deliverable: `business-persona`, not `business-personas` or `business-building-personas`. If it already starts with the category word, strip the repeat: `business-process`, not `business-business-process`; `arch-adr`, not `arch-architecture-decision`.

## Verb suffix

Only when two skills share one artefact with different intents (a creating skill `spec-prd` and a reviewing one `spec-prd-review`). With one skill per artefact the build intent is implicit: `plan-implementation`, not `plan-implementation-builder`; `agent-peer-review`, not `agent-peer-reviewer`.

| Verb | Use for |
|---|---|
| `-builder` | Creates new instances (never `-creator` or `-generator`) |
| `-manager` | Full lifecycle |
| `-mapper` | Links artefacts |
| `-review` | Critical review |
| `-audit` | Read-only assessment |
| `-runner` | Executes a process |

## Anti-patterns

| Anti-pattern | Fix |
|---|---|
| No category prefix (`docs-auditor`) | `util-docs-audit` |
| `-skill` suffix (`slide-builder-skill`) | `com-slide-deck` |
| Verb-led or plural (`using-git-worktrees`) | `dev-git-worktree` |
| Synonym verbs mixed (`-creator`, `-generator`) | `-builder` |
| Folder name ≠ `name:` | Align both |

## Registered exceptions (a new one needs an ADR)

| Skill | Exception | ADR |
|---|---|---|
| `metamodel` | No category prefix: it defines the categories, so a prefix would be circular | ADR-0007 |
| `business-vision` | Writes `docs/VISION.md`, not `docs/business/` (north-star singleton at the docs root for `CLAUDE.md` wiring) | none; recorded in the metamodel prefix mapping |

`spec-quality-attributes` ships in the `quality-assurance` set while keeping the `spec-` prefix, because its output is a product spec.

## Verify

```bash
for skill in plugins/*/skills/*/; do
  skill_name="$(basename "${skill%/}")"
  name=$(grep -m1 "^name:" "$skill/SKILL.md" | sed -E 's/name: *//; s/^"//; s/"$//')
  [ "$skill_name" != "$name" ] && echo "MISMATCH: folder=$skill_name name=$name"
done
```

No output means every folder matches its `name:`.
