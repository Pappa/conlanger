# Spike: ASCA alias file vs `group_mappings.csv` at compile

Spike for replacing compile-time `group_mappings.csv` expansion with an ASCA `.alias` file passed via CLI `-l` / `--alias`.

**Question:** Can Index class-letter semantics (`S` = plosive, `P` = labial, `K` = velar, …) move from Python compile substitution to an ASCA alias file at validation/apply time?

**Answer:** **No.** ASCA alias files are **word-input (de)romanisation only**. They do not rewrite tokens inside `.rsca` rule strings. Class letters must still be expanded before ASCA parses rules — today's `apply_asca_group_mappings` (or equivalent) stays required.

**ASCA version probed:** 0.10.2 (`~/.cargo/bin/asca`)

---

## Executive summary

| Claim | Result |
|-------|--------|
| `-l index_class_aliases.alias` redefines Index class letters inside rules | **False** — rules parsed without alias expansion |
| `@into` accepts union sets like `{L,G}` | **False** — `Unknown character {` at parse |
| `@into` accepts bare grouping targets like `S > P` | **Parse may succeed** but applies to **words**, not rules |
| `@into` accepts feature-matrix targets like `K > [+cons, -fr, +bk, +hi, -lo]` | **Fails on trace/deromanise** — `Cannot create a segment from a limited list of features` |
| `@into` accepts IPA segment lists like `h₁, h₂, h₃ > h, x, ɣʷ` | **True** — for word input only |
| Existing `data/asca/asca_aliases.alias` loads on `asca run` | **True** — but does not affect rule grouping letters |
| Compile pipeline bracket / labial / positional behaviour | **Still needed** — alias file provides none of this |

**Recommendation:** Keep compile-time class-letter expansion. Optionally migrate **word-only** alias concerns (PIE `h₁`/`h₂`/`h₃` in probe lexica) to `-l`; do **not** remove `group_mappings.csv` / `apply_asca_group_mappings`.

---

## Primary sources

| Source | What it establishes |
|--------|---------------------|
| [ASCA 0.10.2 `doc/doc.md` § Inbuilt Aliases](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#inbuilt-aliases) | Capital letters that clash with rule groupings “**cannot be used inside a rule** … but can be used when defining a word” |
| [ASCA 0.10.2 `doc/doc-cli.md` § Romanisation file](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc-cli.md#romanisation-file-alias) | `.alias` has `@into` (deromanise words) and `@from` (romanise output) |
| [`asca-0.10.2/src/lib.rs` `par_run_unparsed`](https://github.com/Girv98/asca-rust/blob/0.10.2/src/lib.rs) | Rules: `parallel_parse_rule_groups(unparsed_rules)` — **no alias pass**. Words: `Word::with(w, &alias_into)` |
| [`asca-0.10.2/src/alias/parser.rs`](https://github.com/Girv98/asca-rust/blob/0.10.2/src/alias/parser.rs) | Alias `@into` output grammar: IPA segments, group+matrix (`C:[…]`), bare `[…]` matrices — **not** rule-level set unions `{…}` |
| [`research/asca-class-letter-mappings.md`](./asca-class-letter-mappings.md) | Seventeen validated Index→ASCA expansions; several use `{L,G}`, `{C:[…],[+click]}` |
| [`data/asca/group_mappings.csv`](../../../data/asca/group_mappings.csv) | Current compile-time mapping source |
| [`src/conlanger/tools/asca_compile/group_mappings.py`](../../../src/conlanger/tools/asca_compile/group_mappings.py) | Bracket-safe expansion, labialized class letters (`Kʷ`), optional `(ʷ)`, positional-slot protection (`C₁`) |

---

## Empirical probes (local, 2026-08-10)

Probe artifacts: `.scratch/cleaned-rule-index/research/_alias-spike/` (gitignored scratch).

### 1. Alias file does not change rule grouping semantics

`minimal.alias`:

```
@into
    S > P
    P > C:[+labial]
@from
```

Rule `S > F` on word `sami`:

| Run | Result |
|-----|--------|
| `asca run … -l minimal.alias` | `sami => saᵐb̝i` — **S matched ASCA Sonorant** (nasal `m` devoiced/fricated) |
| Same rule, no alias file | Identical output |
| Compile-expanded `P > F` (Index `S→P`) | `sami => sami` — no sonorant match |

**Conclusion:** `@into S > P` is not applied when parsing the rule string. ASCA **S** in the rule remains the built-in Sonorant grouping.

### 2. Class letters in rules still fail without compile expansion

With a full Index mapping alias file, single-rule probes **without** compile expansion:

| Rule | Error (with alias `-l`) |
|------|-------------------------|
| `R > N` | `Unknown grouping 'R'` |
| `K > T` | `Unknown grouping 'K'` |
| `Q > F` | `Unknown grouping 'Q'` |
| `J > N` | `Unknown grouping 'J'` |

Alias file did not register custom groupings for the rule parser.

### 3. Alias `@into` grammar limits vs `group_mappings.csv` rows

| Mapping row | Alias `@into` feasible? | Notes |
|-------------|-------------------------|-------|
| `S > P` | Word-only; not rule grouping | Group→group alias syntax not applied to rules |
| `J > {L,G}` | **No** | `Unknown character {` |
| `Q > {C:[-front,+back,-hi,-lo],[+click]}` | **No** | Set unions not in alias grammar |
| `K > C:[-front,+back,+hi,-lo]` | **No** (as `@into` target for `K`) | Use `C:[…]` form in rules directly (compile path) |
| `K > [+cons, -fr, +bk, +hi, -lo]` | **No** | `Cannot create a segment from a limited list of features` on deromanise |
| `h₁, h₂, h₃ > h, x, ɣʷ` | **Yes** | Works for **word** deromanisation |
| `U > %` | Untested as alias; `%` is rule special character | Syllable class in rules — compile expansion still required |

### 4. Rule tokens vs word tokens (PIE laryngeals)

Using `data/asca/asca_aliases.alias`:

| Setup | Result |
|-------|--------|
| Word `h₁at`, rule `h > x`, with `-l` | `h₁at => Kat` — alias deromanised **word** `h₁→h`, then rule applied |
| Word `h₁at`, rule `h₁ > x`, with `-l` | **Syntax Error: Unknown character '₁'** — subscripts invalid in rule tokens; alias does not rewrite rules |

Matches current Python `apply_asca_aliases` at **compile** time for rules containing `h₁`/`h₂`/`h₃`.

### 5. Existing `data/asca/asca_aliases.alias`

File loads on `asca run … -l data/asca/asca_aliases.alias` (exit 0). The `@into K > [+cons, …]` line is intended for **romanised word input**, not for making `K` a legal grouping letter in rules. The `@from` block romanises output segments back to `K` / PIE symbols.

This file is complementary to compile expansion, not a substitute.

### 6. Compile pipeline behaviour alias files cannot replace

From `apply_asca_group_mappings_to_string` (representative):

```
'S > F'   -> 'P > F'
'P > F'   -> 'C:[+labial] > F'
'C₁ > C₂' -> 'C₁ > C₂'          # positional slot protected
'Kʷ > T'  -> 'C:[-front,+back,+hi,-lo,+round] > P:[-voice]'
'[Z] > T' -> '[Z] > P:[-voice]'  # bracket literal preserved; output T still expanded
```

No ASCA `-l` mechanism provides bracket-aware class-letter rewriting or labialized-class-letter expansion on rule strings.

---

## Implications for the cleaned-rule index pipeline

1. **`group_mappings.csv` + `apply_asca_group_mappings` stay** for Index class letters in compiled ASCA rule strings (ticket 14 / spike 09 findings unchanged).

2. **`validate_asca` should not rely on `-l` for class letters** — validation must continue to exercise the same compile output the pipeline emits today (expanded ASCA tokens).

3. **Optional convergence (separate, smaller scope):** Move PIE laryngeal **word-list** aliases and similar romanisation into `data/asca/asca_aliases.alias`, pass `-l` from `validate_asca` / `run_asca` for **probe `.wsca` files** only; keep compile-time `apply_asca_aliases` for rule strings until ASCA exposes rule-level aliasing (none in 0.10.2).

4. **Glossary (`CONTEXT.md` Class letter):** Still “expanded at compile from `group_mappings.csv`” — no change warranted by this spike.

5. **ADR:** Not warranted — spike refutes the proposal; no hard-to-reverse architectural choice to record.

---

## Alternative misread (format swap only)

If the intent were only to **store** mappings in `.alias` syntax but still expand at compile time in Python, that could be a maintainability refactor — but it would **not** remove compile code, and the `.alias` grammar is ** poorer** than CSV for several rows (no `{…}` unions). Not recommended unless ASCA adds rule-level alias application.

---

## Reproduction

```bash
# Rule grouping unchanged by alias file
cd .scratch/cleaned-rule-index/research/_alias-spike
printf '@ T\n    S > F\n' > s.rsca
printf 'sami\n' > w.wsca
printf '@into\n    S > P\n@from\n' > m.alias
asca run w.wsca --rules s.rsca -l m.alias    # sami => saᵐb̝i (Sonorant S)

# Compile expansion (project)
uv run python -c "
from conlanger.tools.asca_compile.group_mappings import apply_asca_group_mappings_to_string, asca_group_mappings_dict
print(apply_asca_group_mappings_to_string('S > F', asca_group_mappings_dict()))
"   # P > F
```
