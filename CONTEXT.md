# Conlanger

Automatic and assisted conlang tooling: phoneme inventories, morphology/grammar parameters, and diachronic sound-change pipelines.

## Documentation

- [Project overview](docs/CONLANGER.md)
- [System map](docs/SYSTEM.md) — parse → compile → validate for the rule index
- [Index Diachronica parse](docs/system/index-diachronica-parser.md)
- [Applier compile](docs/system/sound-change-applier.md)
- [Validate](docs/system/validate.md) — inventory, correction loop, compile validation
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
_Avoid_: hard-wiring Brassica-only assumptions into the shared index format without an explicit decision

**Sound-change sequence**:
An ordered list of index rules (or compiled applier rules) applied across an evolutionary step.
_Avoid_: “sound change rules” when the ordering/batch of application is what matters

### Corpus and source of truth

**Source of truth (SoT)**:
The artifact treated as authoritative for a given stage of work. Index Diachronica HTML is SoT for an attested rule line unless an **Index Diachronica correction** replaces that line; the cleaned rule index is the planned successor SoT.
_Avoid_: “canonical” without naming which artifact; treating provisional parse dumps or compiled ASCA strings as SoT

**Applier-neutral**:
Describes a representation (especially the rule index) owned by this project, not by ASCA or Brassica syntax. Appliers compile from it; they do not define its on-disk shape.
_Avoid_: “format-agnostic YAML” as a substitute term; storing ASCA rule strings in the index

**Rule index**:
The project’s stored sound-change rules as applier-neutral structured YAML. Appliers (ASCA, Brassica) receive compiled views of this index, not ad-hoc one-off formats.
_Avoid_: “the YAML”, “output.xml”, treating ASCA rule strings as the source of truth

**Cleaned rule index**:
The planned authoritative applier-neutral YAML successor to relying on the raw HTML.
_Avoid_: calling today’s provisional YAML dumps “cleaned” or “canonical” until that effort lands

**Index Diachronica**:
The curated HTML index of attested sound-change rules being ingested into this project (`index_diachronica_original.html` and derived artifacts).
_Avoid_: “the HTML file”, “diachronica dump” as glossary terms

**Index Diachronica HTML**:
The published HTML artifact (`data/diachronica/index_diachronica_original.html`). It is SoT for a rule line unless an **Index Diachronica correction** overrides that line; the file itself is never edited to apply owner corrections.
_Avoid_: treating uncorrected parse dumps as overriding the HTML; using “the HTML” when a correction has already replaced the line

### Sound-change structure

**Sound-change section**:
One Index Diachronica `<h2>` section — a named language-change block (index, title, citation, comments) containing zero or more rule lines. One sound-change section maps to one runtime compile unit (`DiachronicSeries`), not to a single index rule. Optional **status** may hold the whole section out of compile (`status: skipped`).
_Avoid_: `DiachronicSeries` as the glossary term for this level; conflating “section” with “rule line”; boolean `skipped: true` on the section

**Corpus rule**:
One structured entry in the rule index, normally corresponding to a single Index Diachronica rule line (including internal sets/alternations when needed). It always carries **stages**, raw, **rule id**, and source; environment and exception are optional (absent environment = any; absent exception = none). **Status** is omitted unless the rule’s **rule id** is listed in `parser_config.yml` `skip_rules`. A line with no change arrow is still a index rule (not auto-skipped); its **stages** hold the pre-env text and compile validation is allowed to fail.
_Avoid_: treating every surface alternation as a separate authored rule by default; using “rule” when the whole HTML section is meant; required `input`/`output` fields as the index shape (replaced by **stages**); positional `rule_idx` as the stored identifier; `skip: true`; auto-skipping missing-arrow or prose lines at parse

**Stages**:
The ordered list of opaque Index-shaped strings on a index rule that encode the change spine — successive forms separated by arrows in the Index line. Length 2 is a single-step change (former `input` then `output`); length ≥ 3 is a chain (compile expands adjacent pairs; parse does not split the chain into extra index rows). Length 1 is a line with no `→`: the pre-env / pre-exception / pre-comment text; compile supplies a missing output. Each entry stays an opaque string (sets, matrices, class letters intact), not a structured segment object.
_Avoid_: `input`/`output` as the stored spine; encoding the chain only as `" > "` inside a single string field; list-typed `input` with scalar `output`; parse-time chain split into extra YAML rows; treating a length-1 spine as a skip

**Compile field**:
One of the four textual parts of a sound-change rule at ASCA compile time — input, output, environment, or exception — after chain expansion from **stages**. Distinct from **stages** on the corpus rule (YAML source of truth). During compile, each compile field may retain Index-raw text, a compile-time **intermediate representation**, and a compiled ASCA string; render and inventory read the compiled form.
_Avoid_: treating compile fields as the stored index shape; conflating with **raw** (full Index line) or with **stages** entries before expansion

**Compile-field intermediate representation**:
The structured, in-memory form of a **compile field** while ASCA compile runs — an ordered sequence of **field tokens**, optional-length nodes, and (in later versions) richer syntax nodes — so alternatives and transforms need not detect notation by regex on opaque strings. Not stored in YAML **stages**; not the emitted `.rsca` line. Distinct from the applier-neutral rule index YAML ([ADR-0002](docs/adr/0002-applier-neutral-yaml-rule-index.md)), which is the project’s authoritative stored format.
_Avoid_: “IR” as an abbreviation in glossary or user-facing docs; treating compiled ASCA strings as the only compile-time view; adding a structured alternatives field to the index YAML

**Field token**:
One top-level unit in a **compile field** after splitting on spaces outside `{…}`, `(…)`, and `[…]`. Each field token is either a **singleton** (one opaque string — IPA, matrix, class letter, …) or an **ordered set** (brace members as an ordered list, not a Python `set`). A whole-field `{a,b}` is one field token whose payload is an ordered set; `c ɲ` is two singleton field tokens. Parallel alignment zips field tokens by index between input and output at rule level.
_Avoid_: “column” for this unit (conflicts with inventory/spreadsheet sense); treating every space-separated substring as a field token when it is only part of a grouper-delimited atom; using Python `set` for brace members

**Parallel tokens**:
Index notation where one **compile field** lists several **field tokens** separated by spaces outside groupers, each aligned with the corresponding field token on the other side of the change (e.g. `c ɲ > ∅ n`; `{r,h} > {∅,h}` is one field token per side, each an ordered set). Project tickets sometimes call this “condensed”; that word is not a glossary term here.
_Avoid_: conflating parallel tokens with comma-separated set members inside `{…}`; calling brace sets “parallel” when only one field token is present; treating parallel Index spaces as inter-segment phoneme boundaries

**Inter-segment whitespace**:
Spaces between phoneme or grapheme units in applier syntax. Brassica requires them between lexemes; ASCA 0.10.2 treats them as optional. YAML **stages** stay Index-shaped — no parse-time insertion. Brassica inter-segment spacing is an **applier compiler** transform when Brassica is supported; Index ASCII spaces in I/O are **parallel tokens**, not phoneme boundaries. Design: [ticket 45](.scratch/rule-index/issues/45-grill-inter-segment-whitespace-placement.md).
_Avoid_: parse-time SoT mutation with Brassica-style spaced strings; conflating inter-segment spaces with parallel tokens; assuming ASCA requires space-separated phonemes

**Optional outputs**:
An Index output written as a set while the matching input is **not** a set (e.g. `d → {∅,ð}`), encoding speaker variation among alternative results (including null). Detection gate: whole-field output `{…}` and input not a whole-field set — not unequal paired-set arity. Uneven set↔set and nested sets are out of scope for this resolution path. The YAML SoT keeps the set opaque in **stages**. At compile, every member becomes an **alternative outcome** (full compiled peer rule, no further children); the parent picks one uniformly at random via an instance `Random` (unseeded if omitted) as its emitted outcome. Inventory validates **only** those alternatives (column **`alt_idx`**, empty when there are no alternatives)—never the parent’s sample. Design recorded in [ticket 61](.scratch/rule-index/issues/61-grill-optional-outputs.md). Distinct from **Sporadic** (whether to apply the rule at all).
_Avoid_: calling this `sporadic`; structuring optional outputs as a separate YAML field; treating paired input/output sets (`{a,b} → {c,d}`) as optional outputs; using unequal zip arity or nested sets as the optional-outputs trigger; inventory rows for the randomly chosen parent when alternatives exist; process-global `random.seed` as the shared randomness story

**Sporadic**:
Index uncertainty glosses (`sporadic`, `sometimes`, `occasionally`, …) stripped at parse and recorded as boolean `sporadic: true` on the rule — distinct from **optional outputs** (which vary the outcome when the rule applies). On the **render path**, a sporadic rule samples apply vs skip with probability **0.5** via the same instance `Random` used for optional-output picks; the sporadic gate runs **first**, then optional-output alternative selection when both apply. Skip renders as a `#\t`-prefixed commented line with compiled fields (same prefix pattern as `status: skipped`, but compiled rather than Index `raw`). Inventory and unit tests **always apply** sporadic rules (no skip branch, no `sporadic_idx` column). Design recorded in [ticket 68](.scratch/rule-index/issues/68-sporadic-sampling.md).
_Avoid_: folding sporadic into `alternatives`; per-rule apply-rate overrides in index YAML; inventory rows for the skip branch; process-global `random.seed` as the shared randomness story; conflating sporadic with optional outputs

**Environment**:
The phonological context in which a sound change applies — the `/ … _` portion of a rule (where the change is conditioned). Stored as optional field `env` on a index rule; absent means any environment. Index prose catch-all **`else`** is not itself an environment — after parse resolution it becomes an **exception** derived from the previous rule (see correction pass on `/ else`). Index prose **`medial`** / **`medially`** means word-internal (not word-initial, not word-final) — after parse resolution bare forms become `_` with a boundary **exception** (ASCA `// :{#_, _#}:`); tentative qualifiers in **`comment`** do not narrow the rewrite. Index **position** env prose (e.g. **`final syllables`**, **`syllable-final`**, **`next to {X}`**, **`unstressed syllables`**, trailing ``, in monosyllables`` on a structural env) normalizes at parse time to ASCA-shaped `env` values (`U#`, `_,{…}`, `_ %[-stress]`, …); removed prose is captured in **`comment`**; rules that already have a separate **`exception`** keep bare env rewrites deferred (qualifier stripping still applies).
_Avoid_: “context” when `exception` is meant; prose paragraphs from Index comments; treating bare `else` as a valid `env` value in the cleaned SoT; equating medial with intervocalic (`V_V`) or with boundary shorthand `#_, _#`

**Exception**:
A phonological context that blocks an otherwise applicable change — the `! …` or `| …` portion of a rule. Stored as optional field `exception` on a index rule; absent means no exceptions. For Index `/ else` rules whose previous sibling has an environment and no exception, parse writes that previous environment into `exception` and omits `env` (complementary default branch). For Index word-internal **`medial`** / **`medially`** env prose (when no separate exception is already present), parse sets `exception: :{#_, _#}:` to block word-initial and word-final positions.
_Avoid_: the English word “except” in citation prose; conflating with environment; leaving Index `else` in `env`

**Rule comment**:
Optional inline editorial prose on a **index rule** — English qualifiers, semicolon tails, parenthetical notes, and other text stripped from `stages`/`env`/`exception` at parse so compile fields stay ASCA-clean. Stored as optional field `comment`; omitted when absent. **`raw`** always preserves the full Index line. Distinct from section-level **`comments`** (non-rule `<p>` prose blocks between rules).
_Avoid_: “comment” without qualification when section comments are meant; embedding validator skip reasons in `comment`; treating `comment` as ASCA syntax

**Raw**:
The Index rule-line string stored on a index rule for audit. It is the HTML P text after subscript tags become Unicode characters, except that an **Index Diachronica correction** replaces that string entirely when one is keyed for the rule.
_Avoid_: treating raw as byte-identical to the on-disk HTML; treating `stages`/`env`/`exception` as the only recoverable form of the Index line

**Index Diachronica correction**:
A maintainer-authored replacement for one Index rule line, keyed by **rule id**, stored as a Unicode Index string (not HTML). When present, it is the rule’s **raw** — an updated Index claim without editing the HTML file.
_Avoid_: Manual mapping; correspondence-series expansion; “correction pass” (class-first transforms); keying by positional `rule_idx`; putting `<sub>` markup in the replacement

**Rule id**:
The HTML `id` on an Index sound-change rule element (`p.schg`). In the current Index file every rule element has one, and values are unique. It is the identifier on a index rule, inventory and changelog rows, debug CSVs, and **Index Diachronica correction** keys.
_Avoid_: `rule_idx` as a stored identifier; “series index” when the **sound-change section** index is meant

**Manual mapping**:
A maintainer-authored rewrite of part or all of an Index rule string, keyed by a `from` pattern. At parse, after **raw** is fixed, it replaces the first match of `from` with `to` on a working copy (literal substring, or a regular expression when flagged); **raw** is not rewritten by this step. Hits are logged to `manual_mappings_matched_rules.csv` at regen.
_Avoid_: IPA mapping, feature mapping, or correction-pass transforms; conflating with **Index Diachronica correction**

**Source**:
Provenance of a index rule as `file:line` pointing at the Index Diachronica HTML location of the original P (e.g. `index_diachronica_original.html:1288`). When an **Index Diachronica correction** replaced **raw**, source still locates that HTML P, not the overlay file.
_Avoid_: section index alone as sufficient provenance; opaque “from HTML” notes without a locatable line

### Index Diachronica notation

**Abbreviation**:
Index Diachronica notational shorthand whose expansion is defined for compile — including class letters, symbols, section-local tokens, and subscript-marked slots. See **Class letter**, **Symbol**, and the four subscript uses under **Subscript notation**.
_Avoid_: “alias”, “mapping”, “grouping” as the glossary term for these symbols

**Class letter**:
A capital-letter class abbreviation from the Index key (`C`, `V`, `S`, `A`, …) denoting a phonological class. Expanded at compile from `CompilerConfig.group_mappings` (loaded from `config/compile/asca/group_mappings.yml`) where Index meaning diverges from ASCA inbuilt groupings; unmapped letters stay in the rule string. **Glued class-letter sequences** (e.g. `SR`, `VOR`) are consecutive class letters without delimiters — each letter expands when compile boundary rules recognise it (see applier compile doc). A mapped uppercase class letter in a rule segment expands regardless of a lowercase IPA prefix (`rK` → velar class + `r`, same as `Kr`).
_Avoid_: treating every capital letter in a rule as a class letter; single-character blind substitution at ingest; preserving lowercase-glued uppercase class letters as literal digraphs when the uppercase letter is a mapped Index class

**Symbol**:
Index boundary, null, stress, or syllable marks (`#`, `$`, `%`, `∅`, stress notation, etc.) — distinct from class letters. Normalised to ASCA-canonical form in index fields at HTML→YAML ingest; `raw` preserves the Index form.
_Avoid_: lumping symbols with class letters under “abbreviation” when the distinction matters

**Subscript notation**:
Index Diachronica’s use of Unicode subscripts (from HTML `<sub>`) attached to rule tokens. Four distinct uses — **correspondence-series index**, **positional slot**, **identity subscript**, **collective subscript** — must not be conflated; each has different resolution requirements.
_Avoid_: “subscript decoration”; treating every subscript as a correspondence-series index; silent stripping of subscripts

**Correspondence-series index**:
An ordinal subscript on a **concrete segment** (IPA letter or spelled segment such as `s`, `x`, `eh`) selecting the *n*th member of a **correspondence series** for that sound-change section (Index key: `Xₙ` on segments; e.g. `s₁`, `x₂`, `eh₂`). Corpus fields keep the Index-shaped token at HTML→YAML parse. **Series mapping** at compile (`config/compile/asca/compiler_config.yml`, hierarchical section + `global`) expands mapped indices to ASCA-parseable segments; unmapped stay literal and surface via validation clusters.
_Avoid_: treating `s₁` as identical to `s`; parse-time index→IPA substitution; applying global segment→IPA substitution without section scope

**Correspondence series**:
An ordered set of related segments referenced by **correspondence-series indices** in a section (e.g. Afro-Asiatic `s₁`–`s₃`, `h₁`–`h₃` defined in section citation). Distinct from Athabaskan multi-letter series labels (`TŠ`, `TS`, `K`) — those are **section-local abbreviations**, not subscripts.
_Avoid_: treating a correspondence-series index as a free-standing segment; silent stripping to the base letter; calling Athabaskan `TŠ` a series index

**Positional slot**:
An ordinal subscript on a **class letter**, marking a numbered position in a rule template; tokens sharing the same base+subscript co-refer within the rule (Index key: `Xₙ` on class letters; e.g. `C₁C₂ → C₂`, `N₁N₂ → N₂ː`, `V₁…V₂`). Slot compounds such as `nV₀` or `sV₀` combine a segment literal with a vowel slot (often **identity subscript** on `V₀`). Corpus fields keep Index-shaped tokens; each **applier compiler** projects them (ASCA references, Brassica backreferences) — not correspondence-series expansion and not parse-time rewrite.
_Avoid_: expanding `C₁` via `group_mappings.csv`; treating `C₁` as a correspondence-series index on a concrete segment; storing ASCA `C=1` or Brassica `@#…` in the rule index

**Identity subscript**:
Subscript `₀` on any base, meaning “the same instance as other tokens bearing the same base+₀ in this rule” (Index key: `X₀`; e.g. `V₀V₀ → V₀`, `h → ʔ / V₀V₀`, `V₀ʔV₀ → V₀ː`). Co-reference notation, not selection from a correspondence series. Like **positional slots**, Index-shaped in the index and projected at compile per applier.
_Avoid_: treating `V₀` as “zeroth vowel of a series”; stripping `₀` to normalize; conflating with ASCA optional `(C,0)` zero-or-more syntax

**Collective subscript**:
Subscript `ₓ` (or `x`), meaning all members of a sequence or series (Index key: `Xₓ`; e.g. `{Hₓ,m̩,n̩} → a`). Quantifies over a class or series rather than picking one member. At parse, **series expansion** in `config/parser/parser_config.yml` fans out collectives to member **correspondence-series indices** in index fields (flatten inside sets; `raw` unchanged). **Series mapping** at compile resolves those indices to segments.
_Avoid_: treating `Hₓ` as a single segment; conflating with correspondence-series index `H₁`; nested sets after collective expansion; inventing a second on-disk set notation before Brassica is adopted

**Section-local abbreviation**:
Multi-letter or prose shorthand defined only for one sound-change section (or family of sections), not in the global Index key — e.g. Athabaskan `TŠ`, `TS`, `K`, `Q` series labels. Resolved via section `abbreviations` tables when mapped; otherwise cluster-driven. Not a subscript use.
_Avoid_: “series index” for `TŠ`; global `group_mappings.csv` rows for section-only labels

**Feature matrix**:
A distinctive-feature bundle in square brackets, attached to a segment or class letter (e.g. `V[+long]`, `C[+voice]`, `[+voice]` alone) — the standard handbook / Index Diachronica convention: the bracketed features apply to the immediately preceding segment or class. **Stages** and other index fields keep this postfix bracket form; it is applier-neutral. At HTML→YAML ingest, feature *names* inside `[...]` are normalised via `config/parser/feature_mappings.yml` (1:1 renames, bundles, polarity inverts); bracket syntax is unchanged. At ASCA **compile**, host+bracket matrices on input/output compile fields are rewritten to colon form (`V[+long]` → `V:[+long]`) because ASCA treats postfix brackets as separate tokens, not as a matrix on the host. Standalone matrices (`[-long]`, `[+voice]`) stay bracket-shaped unless an applier-specific pass requires otherwise. `raw` preserves the original HTML form.
_Avoid_: listing individual ASCA feature names or shorthands in this glossary; “features” when meaning phoneme-inventory dimensions; storing colon matrices in the rule index YAML; assuming postfix brackets and colon matrices are interchangeable in ASCA

**Meta-notation**:
Index notational conventions that are neither class letters, symbols, nor the four **subscript notation** uses — e.g. retroflex `X̣`, `(…X)` repetition, tone **superscripts** `Xⁿ` (distinct from subscript `Xₙ`). Handled via validation clusters; no global compile expansion yet.
_Avoid_: treating meta-notation as class letters or subscript slots; inventing ASCA expansions without a cluster-driven decision

### Compile and validation

**Applier compiler**:
A translation step from the rule index into a concrete sound-change applier’s syntax or API (e.g. ASCA or Brassica).
_Avoid_: parser (reserved for Index Diachronica HTML → rule index)

**DiachronicSeries**:
A runtime container for one sound-change section: its index rules, abbreviation mappings (passed in from package CSV), and compiled ASCA output. Applies mappings to rule strings; unmapped tokens remain unchanged.
_Avoid_: assuming mappings are baked into the index YAML

**Abbreviation table**:
Runtime mapping from Index shorthand to applier strings, held in `CompilerConfig.group_mappings` and passed into a `DiachronicSeries`. Apply known rows; unmapped tokens stay in the rule string. Section-specific overrides are deferred — handle high-volume failures via validation clusters and hand-authored rows.
_Avoid_: “mapping”, “series map”, “alias table”; global one-size alphabet substitution without section scope; assuming structured per-section abbreviation tables exist in the HTML

**Compile validation**:
Checking that a compiled rule is acceptable to a concrete sound-change applier (syntax/runtime). This is the automated gate before execution tests — not raw YAML ingest.
_Avoid_: “XML well-formedness” as a stand-in for applier correctness

**Probe wordlist**:
A minimal lexicon file (`.wsca`) used by `asca run` to exercise compiled rules during validation — catching runtime failures, not just parse errors.
_Avoid_: treating validation as parse-only; a production lexicon of the conlang

**Failure class**:
A grouped category of compile-validation errors (e.g. `unknown_feature`, `nested_brackets`) used to prioritise correction work across the index.
_Avoid_: ad-hoc one-off regex fixes without clustering; “error message” when the class label is meant

**Validation report**:
A temporary CSV of per-rule validation state (status, reason, description, and related detail) produced for analysis (e.g. with pandas); not the long-term source of truth.
_Avoid_: treating the report as the cleaned rule index; requiring the CSV to interpret an omitted (ok) status

**Status**:
Optional lifecycle marker: `skipped` (omit means active). On a **sound-change section**, set when the section `index` is in `parser_config.yml` `skip_sections`. On a **index rule**, set only when the **rule id** is in `skip_rules`. Parse does not invent `status` for missing arrows, gloss-only lines, or other unrepresentable spines.
_Avoid_: `skip: true`; boolean `skipped: true`; auto-skip at parse; embedding validator diagnostics in the cleaned index SoT

**Skipped**:
A **status** value meaning compile hold-out from owner config. A skipped **section** is parsed then bypassed at compile and inventory. A skipped **index rule** is parsed then emitted as an ASCA comment (`#\t…`), not as an active change. Unlisted failing rules still compile and are allowed to fail **compile validation**.
_Avoid_: auto-skipping rules that are merely invalid; omitting unlisted failures from validation; deleting the HTML line from the index

### Cleaning policy

**Class-first**:
The preferred correction strategy: define reusable transform classes (formatting, token replacement, safe normalisation) and apply them mechanically across the index before case-by-case fixes.
_Avoid_: hand-editing individual rules when a class rewrite exists; “batch fix” without recording the transform class

**Historical fidelity**:
Prefer faithfulness to the attested phonological claim — Index Diachronica HTML, or the **Index Diachronica correction** that replaces that line — over rewriting a rule into a valid-but-inaccurate form. `raw` and `source` preserve the Index surface and the HTML location for audit.
_Avoid_: maximising “compiles” by changing phonological meaning; byte-identical HTML spelling as a substitute for the claim

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
