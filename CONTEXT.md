# Conlanger

Automatic and assisted conlang tooling: phoneme inventories, morphology/grammar parameters, and diachronic sound-change pipelines.

## Language

**Sound-change applier**:
An engine that applies ordered phonological [sound-change rules](https://en.wikipedia.org/wiki/Phonological_rule) (or laws).
_Avoid_: SCA (unless naming a specific tool)

**ASCA**:
The default sound-change applier for this project (`asca-rust` / ASCA rule syntax). Execution code and tests may assume ASCA first.
_Avoid_: treating ASCA as the only conceivable applier forever

**Brassica**:
An alternate sound-change applier the package should remain able to target in principle, behind the same conceptual pipeline.
_Avoid_: hard-wiring Brassica-only assumptions into the shared corpus format without an explicit decision

**Index Diachronica**:
The curated HTML corpus of attested sound-change rules being ingested into this project (`index_diachronica_original.html` and derived artifacts).
_Avoid_: “the HTML file”, “diachronica dump” as glossary terms

**Rule corpus**:
The project’s stored sound-change rules as applier-neutral structured YAML. Appliers (ASCA, Brassica) receive compiled views of this corpus, not ad-hoc one-off formats.
_Avoid_: “the YAML”, “output.xml”, treating ASCA rule strings as the source of truth

**Applier compiler**:
A translation step from the rule corpus into a concrete sound-change applier’s syntax or API (e.g. ASCA or Brassica).
_Avoid_: parser (reserved for Index Diachronica HTML → rule corpus)

**Compile validation**:
Checking that a compiled rule is acceptable to a concrete sound-change applier (syntax/runtime). This is the automated gate before execution tests — not raw YAML ingest.
_Avoid_: “XML well-formedness” as a stand-in for applier correctness

**Series index**:
A subscript marker on a segment in Index Diachronica (e.g. `x₂`) identifying which member of a correspondence series is meant.
_Avoid_: “subscript decoration”, treating `x₂` as identical to `x`

**Abbreviation**:
A notational shorthand in Index Diachronica — a class letter (`C`, `V`), boundary/null mark (`#`, `∅`), or series-indexed token (`s₁`) — whose expansion is defined for compile.
_Avoid_: “alias”, “mapping”, “grouping” as the glossary term for these Index symbols

**Abbreviation table**:
A hierarchical lookup (global defaults plus section overrides along section `index` ancestry; more specific wins) that expands abbreviations when compiling or completing rules. Series-index rows are one kind of entry in this table.
_Avoid_: “mapping”, “series map”, “alias table”; global one-size alphabet substitution without section scope

**Corpus rule**:
One structured entry in the rule corpus, normally corresponding to a single Index Diachronica rule line (including internal sets/alternations when needed). It always carries input, output, raw, and source; environment and exception are optional (absent environment = any; absent exception = none). Optional rule status may hold a rule out or flag it for extra validation; edge cases not yet representable use empty input/output with `status: skipped` instead of splitting.
_Avoid_: treating every surface alternation as a separate authored rule by default; inventing split marks before that policy is decided

**Rule status**:
Optional lifecycle marker on a corpus rule: `needs-validation` or `skipped` (omit means ok). Full reason and description live in a temporary validation report, not on the YAML rule.
_Avoid_: `skipped` as a reason-string field on the rule; embedding validator diagnostics in the cleaned corpus SoT

**Skipped**:
A rule-status value meaning the rule is held out of normal compile (empty input/output) pending investigation or an owner-approved permanent deferral.
_Avoid_: deleting the HTML line from the corpus; silent drop without provenance; using “skipped” for rules that still compile

**Validation report**:
A temporary CSV of per-rule validation state (status, reason, description, and related detail) produced for analysis (e.g. with pandas); not the long-term source of truth.
_Avoid_: treating the report as the cleaned rule corpus; requiring the CSV to interpret an omitted (ok) status

**Feature matrix**:
A distinctive-feature bundle written in brackets on a segment or alone in a rule string (e.g. `[+voice]`, `C:[+strident]`). Index Diachronica forms may need normalisation before an applier accepts them.
_Avoid_: listing individual ASCA feature names or shorthands in this glossary; “features” when meaning phoneme-inventory dimensions

**Raw**:
The original Index Diachronica rule-line string preserved on a corpus rule for audit and fidelity checks.
_Avoid_: treating the cleaned `input`/`output`/`env`/`exception` fields as the only recoverable form of the HTML line

**Source**:
Provenance of a corpus rule as `file:line` pointing at the Index Diachronica HTML location of its raw string (e.g. `index_diachronica_original.html:1288`).
_Avoid_: section index alone as sufficient provenance; opaque “from HTML” notes without a locatable line

**Index Diachronica HTML**:
The current ultimate source artifact for attested rules (`notebooks/data/index_diachronica_original.html`).
_Avoid_: treating hand-cleaned XML/YAML samples as overriding the HTML

**Cleaned rule corpus**:
The planned authoritative applier-neutral YAML successor to relying on the raw HTML (schema and migration to be planned via wayfinder).
_Avoid_: calling today’s provisional YAML dumps “cleaned” or “canonical” until that effort lands

**Phoneme inventory**:
The set of contrastive sounds posited for a language (attested via PHOIBLE-derived data, or generated).
_Avoid_: “phoneme list”, “sound inventory” as competing glossary terms

**Preset inventory**:
One of the bundled, pre-generated phoneme inventories shipped with the library for use without running the GAN.
_Avoid_: “sample language”, “demo inventory” as the glossary term

**Lexicon**:
The generated word stock for a conlang stage (roots and later evolved forms).
_Avoid_: “wordlist” when meaning the full generated lexicon (reserve wordlist for external lemma sources)

**Wordlist**:
An external lemma/concept list used to drive or constrain lexicon generation (e.g. Basic English / ULD-derived lists).
_Avoid_: using “wordlist” for the generated lexicon itself

**Sound-change sequence**:
An ordered list of corpus rules (or compiled applier rules) applied across an evolutionary step.
_Avoid_: “sound change rules” when the ordering/batch of application is what matters
