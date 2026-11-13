# What goes in each tab

A sheet has four tabs, from the outside in. A reader who stops after the first tabs has seen what the slice looks like from outside; one who reads on sees how it is built. Write for a product owner first: say what a thing does before naming it.

## Rules for every tab

- **Only this slice.** Show what the slice adds or changes. Name what it reuses in one line; do not describe it again.
- **Only what the specification supports.** Each statement comes from the specification, from a document it cites, or from a decision recorded in the tab's closing block. Do not design ahead of the slice.
- **Content only.** A partial holds headings, paragraphs, tables and the two slots. No `<style>`, no `<script>`, no literal colour: the page's validator refuses them. The classes a partial may use are listed in the `com-artefact-viz` skill's `references/parsing-contract.md`, section "slice-design"; use those and no other.
- **The summary line.** The first line, `<!-- summary: ... -->`, is shown on the tab: a count of what the tab holds (`2 operations · 1 event`).
- **Sections.** Each heading and what follows it sits in a `<div class="block">`. A table sits in a `<div class="scroll">`; it becomes cards on a phone, so give every column a header.
- **Figures.** `{{FIGURE:name|alt|caption}}`: `name` is the stem of a diagram of the folder (`class-01-rebooking`), `alt` says in plain text what the diagram shows, `caption` is optional. Draw the diagram with `arch-uml` before placing the slot; a slot whose diagram is not rendered stops the build.
- **An empty tab is a statement.** When the slice does not touch a layer, keep only the summary line. The page then says that the slice has nothing on that layer and what the tab would hold otherwise. Do not write filler to avoid an empty tab.

## Screens (`screens.html`)

**Belongs here**

- One mock-up per screen the slice adds or changes, with the states that matter: empty, loading, error, filled.
- The components the slice adds or changes, and those it reuses.
- For each screen, the operations of the next tab that it calls.

**Does not belong here**

- The visual language itself (colours, type, spacing): that is the design system's.
- Screens the slice leaves untouched.
- Final wording of labels and messages, unless the specification fixes it.

A mock-up is a figure: an SVG in `views/` with its dark twin in `views/dark/`, placed with a `{{FIGURE:...}}` slot. A slice with no screen (a batch, an API, a migration) leaves this tab empty.

## API and contracts (`api.html`)

**Belongs here**

- A table of the operations and contracts the slice adds or changes: name, what it does, direction, carrier.
- The HTTP operations, shown by the `{{OPENAPI}}` slot from `openapi.json` or `openapi.yaml` in the folder. The document holds the slice's operations only. The viewer shows JSON bodies, local `$ref` schemas, examples and responses; it says on the operation what it does not show (parameters, composed schemas).
- The contracts each side reads: files, messages, events, with the fields that matter.
- The shapes of the results, and the decision tables behind them when a result depends on rules.

**Does not belong here**

- The classes and modules that serve an operation: next tab.
- Tables and columns: last tab.
- The whole interface of the product. The lasting contract is `arch-service-contract`'s; the sheet shows the slice's part and cites it.

## Code organisation (`code.html`)

**Belongs here**

- A table of what each module gains, and how that gain is tested. Name a module the slice reuses unchanged in one line.
- A class diagram of the types the slice adds, and the shapes of those other modules will read.
- A sequence diagram of one run, from the entry point to the stored result.
- How the slice is tested: the seams, and what stands in for what is outside them.

**Does not belong here**

- Method bodies, file listings, framework configuration.
- The order of the work and its increments: that is the plan's.
- Types the slice does not touch.

## Database (`database.html`)

**Belongs here**

- An entity-relationship diagram of the tables the slice touches.
- A table of the tables it adds or changes: what changes, and how many rows to expect.
- The column conventions the slice follows (keys, timestamps, naming), when it sets or relies on one.

**Does not belong here**

- Migration scripts.
- Indexes and tuning, unless the specification decides them; otherwise they are left to the implementation and said so.
- Tables the slice only reads, beyond one line.

## The decisions block that closes a tab

Every tab with content ends with a block titled "Decisions on this layer", in two parts:

```html
<div class="block">
  <h2>Decisions on this layer</h2>
  <div class="decisions">
    <section>
      <span class="chip solid">Settled</span>
      <ul>
        <li>What was decided, in one sentence.<span class="refs"><span class="chip ref">its source</span></span></li>
      </ul>
    </section>
    <section class="open">
      <span class="chip open">Left to the implementation</span>
      <ul>
        <li>What the implementer decides.</li>
      </ul>
    </section>
  </div>
</div>
```

- **Settled** lists what is decided for this layer and will not be reopened while the slice is built. Each item names its source in a reference chip: a story, an ADR, a section of the specification. An item with no source is a decision the sheet is making on its own: take it to the owner, and record it in the specification or in an ADR before it is listed.
- **Left to the implementation** lists what the sheet deliberately does not decide, so that the implementer knows the choice is theirs and a reviewer does not look for it in the sheet. Name the choice; do not hint at an answer.
- A choice that is neither settled nor safe to leave open is an open question on the specification. Raise it; do not park it in either list.
- If a part has nothing to list, say so in one item rather than dropping the part.
