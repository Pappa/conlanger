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
The curated HTML corpus of attested sound-change rules being ingested into this project (`index_diachronica.html` and derived artifacts).
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

**Series map**:
A per-section table from series indices to concrete segments used when compiling or completing rules.
_Avoid_: global one-size alphabet substitution without section scope

**Corpus rule**:
One structured entry in the rule corpus, normally corresponding to a single Index Diachronica rule line (including internal sets/alternations when needed).
_Avoid_: treating every surface alternation as a separate authored rule by default

**Index Diachronica HTML**:
The current ultimate source artifact for attested rules (`notebooks/data/index_diachronica.html`).
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
