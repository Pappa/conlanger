# Inter-segment whitespace and phoneme boundaries

Spike: [44-spike-inter-segment-whitespace.md](../issues/44-spike-inter-segment-whitespace.md). Deferred fog from [ticket 07](../issues/07-normalise-segment-features.md) (“Whitespace tokenisation for ASCA”).

**Verdict:** Do **not** insert Brassica-style inter-segment spaces into the applier-neutral YAML SoT at parse time. ASCA **0.10.2** does **not** require (or prefer) space-separated phonemes; Brassica does. Spacing belongs in the **Brassica applier compiler**. For ASCA, the related problem is **digraph ties** / length normalisation at compile — not spaces. Index spaces in I/O mostly mark **parallel condensed parts**, which must not be conflated with segment boundaries.

Supporting table: [inter-segment-whitespace-examples.csv](./inter-segment-whitespace-examples.csv).

Context7: ASCA / Brassica are **not indexed**; sources below are first-party GitHub docs + local `asca 0.10.2` crate / CLI.

---

## 1. Primary sources — how each applier tokenises

### 1.1 ASCA 0.10.2 — spaces optional; IPA trie segments

| Claim | Source |
|-------|--------|
| Digraphs need ligature tie (`͡`/`͜`) or `^`; **untied** `dʒ` is **two** segments `d`+`ʒ` | [IPA Characters](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#ipa-characters) |
| Cardinal inventory is trie-backed (`cardinals.json`, 363 entries); `t͡ʃ`/`t͡s` present, bare `tʃ`/`ts` **absent** | crate `src/cardinals.json`, `CARDINALS_TRIE` in `src/lib.rs`; lexer `get_ipa` in `src/rule/lexer.rs` |
| Lexer **trims whitespace** before every token (`trim_whitespace` in `get_next_token`) — spaces separate tokens when present but are **not required** | `~/.cargo/registry/.../asca-0.10.2/src/rule/lexer.rs` |
| Inside feature matrices, **whitespace is not important** (`[+del.rel.]` ≡ `[ + d e l . r e l . ]`) | [Using Distinctive Features](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#using-distinctive-features) |
| Length in **words**: `ː` or `:` (and gemination `aa`); in **rules**, bare `ː` is `Unknown character`; use `a:[+long]` (existing compile pass) | [Suprasegmentals](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#suprasegmentals); CLI probes below; ticket 15 |
| Condensed parallel rules use **commas**, not spaces (`a, u > e, y`) | [Condensed Rules](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#condensed-rules) |

**CLI probes (`asca 0.10.2`):**

| Rule | Word | Result | Interpretation |
|------|------|--------|----------------|
| `ab > x` | `ab` | `x` | Glued I/O OK |
| `a b > x` | `ab` | `x` | Spaced I/O equivalent |
| `CV > x` / `C V > x` | `ka` | `x` | Group letters: space optional |
| `ts > s` | `tsa` | `sa` | Untied = two cardinals |
| `t͡s > s` | `t͡sa` | `sa` | Tied = one cardinal |
| `dʒ > ʒ` | `dʒa` | `ʒa` | Untied sequence, not affricate |
| `aː > a` | — | Syntax Error `ː` | Rule lexer ≠ word lexer for length |
| `{a,b}` / `{a, b}` | same | same | Set-internal spaces ignored |

**Implication:** “Space-separated phonemes like ASCA” is a **mischaracterisation**. ASCA is inventory/trie-driven and space-agnostic between tokens. Inserting spaces does not make rules more ASCA-valid.

### 1.2 Brassica — spaces required between graphemes

| Claim | Source |
|-------|--------|
| Target/replacement are sequences of **lexemes separated by a space** | [Writing Sound Changes — Unconditional](https://github.com/bradrn/brassica/blob/master/docs/Writing-Sound-Changes.md#unconditional-sound-changes) |
| Multi-grapheme sides **must have spaces between them** (calls out multigraphs) | same § (“they must have spaces between them”) |
| Default word tokenisation: one Unicode char per grapheme; **multigraphs** from category/`extra` lists use **longest match** | [Multigraphs](https://github.com/bradrn/brassica/blob/master/docs/Writing-Sound-Changes.md#multigraphs); [Reference — Phases of processing](https://github.com/bradrn/brassica/blob/master/docs/Reference.md#phases-of-processing) |
| Accidental glue (`ā / ay`) creates an unintended multigraph; write `ā / a y` | Multigraphs § |
| Grammar: consecutive lexemes/graphemes separated by whitespace **except when unambiguous**; grapheme = non-whitespace run | [Reference — Sound change syntax](https://github.com/bradrn/brassica/blob/master/docs/Reference.md#sound-change-syntax) |
| Inline categories are **space-separated** (`[a e i o u]`) | [Categories of sounds](https://github.com/bradrn/brassica/blob/master/docs/Writing-Sound-Changes.md#categories-of-sounds) |

**Implication:** Brassica’s space convention is real and **Brassica-shaped**. Baking it into YAML SoT fights [ADR-0002](../../../docs/adr/0002-applier-neutral-yaml-rule-corpus.md) (“Do not encode … Brassica-only syntax as the only representable form”).

### 1.3 Two different “whitespace” problems

| Kind | Where | ASCA | Brassica | SoT ownership |
|------|-------|------|----------|---------------|
| **A. Inter-segment / inter-grapheme spaces** | Between phonemes in I/O/env | Optional / ignored | Required (modulo unambiguous) | **Not SoT** — Brassica compile |
| **B. Bracket-internal feature-name spaces** | `[+high tone]`, `S[+ voice]` | Ignored inside matrices | Different feature model (`$Feature`, categories) | Separate (ticket 07 fog / feature ingest); **not** this spike’s deliverable |

---

## 2. Corpus survey (cleaned YAML)

Corpus: `data/diachronica/index_diachronica_parsed.yml` (**9201** rules), surveyed 2026-08-08.

### 2.1 What Index spaces usually mean

| Pattern | Approx. scale | Notes |
|---------|---------------|-------|
| I/O with ASCII space, **no** comma | ~1937 rules | Mostly **parallel** parts: `dz ʃ tʃ` → `ʒ f1 f2` (HTML:956) — Index analogue of ASCA condensed commas |
| Multi-token I/O (space-split outside `[]`/`{}`) | ~2488 rules | Same phenomenon |
| I/O with commas (ASCA-like condensed) | ~915 space-free + ~688 with spaces | Mixed migration state |
| Inter-segment space **inside** a single form | Rare / not the dominant use | Do not treat every Index space as a phoneme boundary |

### 2.2 Glued multi-base / digraph candidates (I/O rule counts)

See CSV. Highlights (substring hits in `input`/`output`):

| Pattern | Rules | Role |
|---------|------:|------|
| `tʃ` / `ts` / `dʒ` / `dz` | 450 / 446 / 235 / 160 | Untied affricates — Index digraphs; ASCA needs ties for single-segment semantics |
| Tied `t͜s` etc. | ≤4 | Almost never present in corpus |
| `kʷ` / `ɡʷ` | 350 / 240 | Base + labialisation diacritic (not inter-segment space) |
| `Vː` / `aː`… | hundreds | Length glued to segment; ASCA compile → `:[+long]` |
| `C₁C₂`, `V₀V₀`, `mV₀` | tens | Subscript compounds — compile/token split (tickets 40–41), not spaces |
| `VNC`, `Cw`, `CV` | low tens | Class-letter clusters — atomic letters, not IPA digraphs |
| Bracket-internal spaces in I/O | ~158 | Kind B (`[+ voice]`, `[- high - long]`) |

### 2.3 Incidental tokenisers (not SoT policy)

- [`series_mappings._tokenize_rule_side`](../../../src/conlanger/tools/series_mappings.py) — regex split for correspondence-series inference; merges subscript chars; **not** a phoneme boundary SoT.
- Legacy [`add_affricate_ties`](../../../legacy/scripts/parse_index_diachronica.py) — documents ASCA tie requirement; **do not copy** as SoT policy (map: no `legacy/` for cleaned-corpus implementation). Useful as a **compile-time** candidate list only.

---

## 3. Boundary algorithm sketch (for compilers / tooling)

Goal: turn an Index-shaped field string into an ordered list of **atomic units** so a Brassica compiler can join with spaces, or an ASCA compiler can apply per-segment transforms (ties, length, refs).

```
scan left→right with a nest stack ([], {}, (), ⟨⟩/<>, optional :[):
  1. Skip / preserve comments & prose (env qualifiers already stripped where possible).
  2. Inside [...] : do not insert inter-segment spaces; optionally normalise Kind-B
     feature tokens (separate pass).
  3. Inside {...} : split members on commas; recurse per member; ASCA keeps comma
     lists; Brassica may rewrite to [a b] later.
  4. Longest-match segment:
     a. ASCA cardinals trie (tied affricates, prenasals, …)
     b. Index digraph table (untied tʃ, ts, dʒ, …) — treat as ONE unit for Brassica
        multigraph / ASCA tie emission
     c. else one base letter/IPA char + following diacritics (ʷ ʲ ʼ ˤ ː …)
  5. Attach Unicode subscripts ₀-₉ₓ to the preceding unit (then classify
     correspondence / positional / identity / collective).
  6. Class letters C,S,O,P,F,L,N,G,V (+ labialized Kʷ) are atomic units.
  7. Length: keep glued for SoT; ASCA compile maps ː/ˑ → :[+long]; Brassica may
     keep ː as part of multigraph or separate lexeme per inventory policy.
  8. Emit Brassica: join units with single spaces (never inside Kind-B brackets).
     Emit ASCA: join without spaces (or spaces — equivalent); apply digraph ties.
```

### Failure modes

| Failure | Why |
|---------|-----|
| Treating Index parallel spaces as segment spaces | Breaks `dz ʃ tʃ` → would become six segments or wrong Brassica lexemes |
| Longest-match without Index digraph table | `tʃ` → `t`+`ʃ` in ASCA (doc-correct but historically wrong for affricates) |
| Digraph table too greedy | `st`, `nd`, vowel sequences mis-merged |
| Spacing inside `[+high tone]` as Kind A | Corrupts feature tokens; Kind B is separate |
| Spacing before attaching `ː` / `ʷ` / `ʼ` | Splits diacritics from bases |
| Spacing inside `C₁C₂` / `mV₀` without subscript policy | Wrong co-reference units |
| Putting Brassica spaces into SoT | ADR-0002 tension; ASCA gains nothing; Index parallel-space ambiguity worsens |
| Assuming ASCA `ː` in rules | Unknown character until length compile pass |

---

## 4. Placement recommendation

### Recommendation: **compile-only** (Brassica spacing); **SoT stays Index-shaped**

| Option | Assessment |
|--------|------------|
| **Parse-time SoT spacing** (maintainer preference to evaluate) | **Reject for now.** Contradicted for ASCA (spaces not part of the model). Encodes Brassica convention into “neutral” YAML (ADR-0002). Collides with Index’s use of spaces for parallel parts. Digraph/boundary errors would permanently mutate the corpus. |
| **Compile-only Brassica spacing** | **Adopt.** Brassica compiler owns grapheme inventory + multigraph list + space insertion. |
| **Compile-only ASCA digraph ties / length** | **Keep / extend** existing seam (tickets 15, 20, 25; legacy tie list as seed only). Spaces unnecessary. |
| **Structured segment arrays in YAML** | Possible future IR (list of atoms per field) — larger schema change; not required to unblock ASCA path. |

### Evidence vs maintainer preference

Preference stated in the spike: spaced segments in applier-neutral SoT “like ASCA and Brassica.”

- **Brassica half:** true for rule lexemes.
- **ASCA half:** false — ASCA is space-optional / trie-segmented.
- **Neutral SoT:** Index-shaped glued strings (plus already-decided parse expansions) remain the least applier-specific surface; compilers project.

---

## 5. Grill / follow-on questions

1. Confirm rejection of parse-time SoT spacing (or accept Brassica-shaped SoT explicitly and amend ADR-0002)?
2. Should Index **parallel** spaces be normalised to ASCA **commas** at parse or compile (separate from phoneme spacing)?
3. Affricate policy: always insert ties at ASCA compile for the legacy digraph list, or only when inventory/`unknown_character` clusters demand it?
4. Brassica multigraph inventory source: ASCA `cardinals.json` ties + Index digraph table + section abbreviations — who authors it?
5. Kind B (`[+high tone]`) — keep deferred under feature-matrix ingest, or schedule a tiny normalisation pass before `feature_mappings.csv` lookup?
6. Any desire for a structured `segments: […]` IR later, vs string fields forever?

**Implementation ticket shape (only if grill affirms compile-only):**  
“Brassica compile: segmentise Index-shaped fields and emit space-separated graphemes” — blocked on Brassica compiler (ADR-0001); algorithm §3 + CSV as fixtures. Optional sibling: “ASCA compile: affricate digraph ties” if not absorbed into an existing unknown_character / meta pass.

---

## 6. Source index

| Source | Use |
|--------|-----|
| https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md | IPA Characters; Distinctive Features whitespace; Condensed Rules; Suprasegmentals |
| Local crate `asca-0.10.2` `src/rule/lexer.rs`, `src/cardinals.json`, `src/lib.rs` | Trie tokenisation; `trim_whitespace` |
| `asca` CLI 0.10.2 probes | Spaced ≡ glued; untied vs tied; `ː` in rules |
| https://github.com/bradrn/brassica/blob/master/docs/Writing-Sound-Changes.md | Spaces required; Multigraphs; Categories |
| https://github.com/bradrn/brassica/blob/master/docs/Reference.md | Lexeme whitespace; word tokenisation longest-match |
| `data/diachronica/index_diachronica_parsed.yml` | Corpus counts |
| `src/conlanger/tools/series_mappings.py` | Incidental tokenizer |
| `legacy/scripts/parse_index_diachronica.py` `add_affricate_ties` | Legacy digraph list (reference only) |
| ADR-0002 | Applier-neutral SoT constraint |
