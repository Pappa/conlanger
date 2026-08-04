# Conlanger

Automatic and assisted conlang tooling: phoneme inventories, morphology/grammar parameters, and diachronic sound-change pipelines.

## Documentation

- [Project overview](docs/CONLANGER.md)
- [System map](docs/SYSTEM.md)
- [Architectural decisions](docs/adr/)

## Language

### Appliers

**Sound-change applier**:
An engine that applies ordered phonological [sound-change rules](https://en.wikipedia.org/wiki/Phonological_rule) (or laws).
_Avoid_: SCA (unless naming a specific tool)

**ASCA**:
The default sound-change applier for this project (`asca-rust` / ASCA rule syntax). Execution code and tests may assume ASCA first.
_Avoid_: treating ASCA as the only conceivable applier forever

**Brassica**:
An alternate sound-change applier the package should remain able to target in principle, behind the same conceptual pipeline.
_Avoid_: hard-wiring Brassica-only assumptions into the shared corpus format without an explicit decision

**Sound-change sequence**:
An ordered list of corpus rules (or compiled applier rules) applied across an evolutionary step.
_Avoid_: “sound change rules” when the ordering/batch of application is what matters

### Corpus and source of truth

**Source of truth (SoT)**:
The artifact treated as authoritative for a given stage of work. Index Diachronica HTML is SoT for attested rules today; the cleaned rule corpus is the planned successor SoT.
_Avoid_: “canonical” without naming which artifact; treating provisional YAML dumps or compiled ASCA strings as SoT

**Applier-neutral**:
Describes a representation (especially the rule corpus) owned by this project, not by ASCA or Brassica syntax. Appliers compile from it; they do not define its on-disk shape.
_Avoid_: “format-agnostic YAML” as a substitute term; storing ASCA rule strings in the corpus

**Rule corpus**:
The project’s stored sound-change rules as applier-neutral structured YAML. Appliers (ASCA, Brassica) receive compiled views of this corpus, not ad-hoc one-off formats.
_Avoid_: “the YAML”, “output.xml”, treating ASCA rule strings as the source of truth

**Cleaned rule corpus**:
The planned authoritative applier-neutral YAML successor to relying on the raw HTML.
_Avoid_: calling today’s provisional YAML dumps “cleaned” or “canonical” until that effort lands

**Index Diachronica**:
The curated HTML corpus of attested sound-change rules being ingested into this project (`index_diachronica_original.html` and derived artifacts).
_Avoid_: “the HTML file”, “diachronica dump” as glossary terms

**Index Diachronica HTML**:
The current ultimate source artifact for attested rules (`notebooks/data/index_diachronica_original.html`).
_Avoid_: treating hand-cleaned XML/YAML samples as overriding the HTML

### Sound-change structure

**Sound-change section**:
One Index Diachronica `<h2>` section — a named language-change block (index, title, citation, comments) containing zero or more rule lines. One sound-change section maps to one runtime compile unit (e.g. a `PhonologicalRuleSet`), not to a single corpus rule.
_Avoid_: `SoundChangeRule` as the glossary term for this level; conflating “section” with “rule line”

**Corpus rule**:
One structured entry in the rule corpus, normally corresponding to a single Index Diachronica rule line (including internal sets/alternations when needed). It always carries input, output, raw, and source; environment and exception are optional (absent environment = any; absent exception = none). Optional rule status may hold a rule out or flag it for extra validation; edge cases not yet representable use empty input/output with `status: skipped` instead of splitting.
_Avoid_: treating every surface alternation as a separate authored rule by default; using “rule” when the whole HTML section is meant

**Environment**:
The phonological context in which a sound change applies — the `/ … _` portion of a rule (where the change is conditioned). Stored as optional field `env` on a corpus rule; absent means any environment.
_Avoid_: “context” when `exception` is meant; prose paragraphs from Index comments

**Exception**:
A phonological context that blocks an otherwise applicable change — the `! …` or `| …` portion of a rule. Stored as optional field `exception` on a corpus rule; absent means no exceptions.
_Avoid_: the English word “except” in citation prose; conflating with environment

**Raw**:
The original Index Diachronica rule-line string preserved on a corpus rule for audit and fidelity checks.
_Avoid_: treating the cleaned `input`/`output`/`env`/`exception` fields as the only recoverable form of the HTML line

**Source**:
Provenance of a corpus rule as `file:line` pointing at the Index Diachronica HTML location of its raw string (e.g. `index_diachronica_original.html:1288`).
_Avoid_: section index alone as sufficient provenance; opaque “from HTML” notes without a locatable line

### Index Diachronica notation

**Abbreviation**:
Index Diachronica notational shorthand whose expansion is defined for compile — including class letters, symbols, and series-indexed tokens.
_Avoid_: “alias”, “mapping”, “grouping” as the glossary term for these symbols

**Class letter**:
A capital-letter class abbreviation from the Index key (`C`, `V`, `S`, `A`, …) denoting a phonological class. Expanded at compile from `group_mappings.csv` where Index meaning diverges from ASCA inbuilt groupings; unmapped letters stay in the rule string.
_Avoid_: treating every capital letter in a rule as a class letter; single-character blind substitution at ingest

**Symbol**:
Index boundary, null, stress, or syllable marks (`#`, `$`, `%`, `∅`, stress notation, etc.) — distinct from class letters. Normalised to ASCA-canonical form in corpus fields at HTML→YAML ingest; `raw` preserves the Index form.
_Avoid_: lumping symbols with class letters under “abbreviation” when the distinction matters

**Series index**:
A subscript marker on a segment in Index Diachronica (e.g. `x₂`) identifying which member of a correspondence series is meant.
_Avoid_: “subscript decoration”, treating `x₂` as identical to `x`

**Correspondence series**:
An ordered set of related segments referenced by series indices in a section (e.g. Athabaskan `T`, `TŠ`, `K`, `Q` series). Resolution requires section-specific mapping; unmapped indices surface via validation clusters.
_Avoid_: treating a series index as a free-standing segment; silent stripping to the base letter

**Feature matrix**:
A distinctive-feature bundle written in brackets on a segment or alone in a rule string (e.g. `[+voice]`, `C:[+strident]`). At HTML→YAML ingest, Index feature names with safe 1:1 ASCA equivalents are normalised to ASCA canonical names via `feature_mappings.csv`; unmapped names are left as-is. `raw` preserves the original HTML form.
_Avoid_: listing individual ASCA feature names or shorthands in this glossary; “features” when meaning phoneme-inventory dimensions

**Meta-notation**:
Index notational conventions that are neither class letters nor normalisable symbols — e.g. `X0`, `Xn`, `Xx`, retroflex `X̣`, `(…X)` repetition. Handled via validation clusters; no global compile expansion yet.
_Avoid_: treating meta-notation as class letters; inventing ASCA expansions without a cluster-driven decision

### Compile and validation

**Applier compiler**:
A translation step from the rule corpus into a concrete sound-change applier’s syntax or API (e.g. ASCA or Brassica).
_Avoid_: parser (reserved for Index Diachronica HTML → rule corpus)

**PhonologicalRuleSet**:
A runtime container for one sound-change section: its corpus rules, abbreviation mappings (passed in from package CSV), and compiled applier output. Applies mappings to rule strings; unmapped tokens remain unchanged.
_Avoid_: `SoundChangeRule` as the name for this container; assuming mappings are baked into the corpus YAML

**Abbreviation table**:
Runtime mapping from Index shorthand to applier strings, loaded from package CSV (e.g. `src/conlanger/data/asca/group_mappings.csv`) and passed into a `PhonologicalRuleSet`. Apply known rows; unmapped tokens stay in the rule string. Section-specific overrides are deferred — handle high-volume failures via validation clusters and hand-authored rows.
_Avoid_: “mapping”, “series map”, “alias table”; global one-size alphabet substitution without section scope; assuming structured per-section abbreviation tables exist in the HTML

**Compile validation**:
Checking that a compiled rule is acceptable to a concrete sound-change applier (syntax/runtime). This is the automated gate before execution tests — not raw YAML ingest.
_Avoid_: “XML well-formedness” as a stand-in for applier correctness

**Probe wordlist**:
A minimal lexicon file (`.wsca`) used by `asca run` to exercise compiled rules during validation — catching runtime failures, not just parse errors.
_Avoid_: treating validation as parse-only; a production lexicon of the conlang

**Failure class**:
A grouped category of compile-validation errors (e.g. `unknown_feature`, `nested_brackets`) used to prioritise correction work across the corpus.
_Avoid_: ad-hoc one-off regex fixes without clustering; “error message” when the class label is meant

**Validation report**:
A temporary CSV of per-rule validation state (status, reason, description, and related detail) produced for analysis (e.g. with pandas); not the long-term source of truth.
_Avoid_: treating the report as the cleaned rule corpus; requiring the CSV to interpret an omitted (ok) status

**Rule status**:
Optional lifecycle marker on a corpus rule: `needs-validation` or `skipped` (omit means ok). Full reason and description live in a temporary validation report, not on the YAML rule.
_Avoid_: `skipped` as a reason-string field on the rule; embedding validator diagnostics in the cleaned corpus SoT

**Skipped**:
A rule-status value meaning the rule is held out of normal compile (empty input/output) pending investigation or an owner-approved permanent deferral.
_Avoid_: deleting the HTML line from the corpus; silent drop without provenance; using “skipped” for rules that still compile

### Cleaning policy

**Class-first**:
The preferred correction strategy: define reusable transform classes (formatting, token replacement, safe normalisation) and apply them mechanically across the corpus before case-by-case fixes.
_Avoid_: hand-editing individual rules when a class rewrite exists; “batch fix” without recording the transform class

**Historical fidelity**:
Prefer faithfulness to the attested phonological claim in Index Diachronica HTML over rewriting a rule into a valid-but-inaccurate form. `raw` and `source` preserve the surface line for audit.
_Avoid_: maximising “compiles” by changing phonological meaning; byte-identical spelling as a substitute for the claim

### Generative pipeline

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
