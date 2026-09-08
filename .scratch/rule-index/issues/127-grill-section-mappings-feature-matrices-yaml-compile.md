Type: grilling
Status: needs-grilling
Blocked by: None

# Grill: section_mappings feature matrices, YAML wrapping, and braced-set compile

Spawned from `/grill-with-docs` session on [Cleaned rule index SoT](../map.md) (2026-09-08). Owner will resolve later.

## Question

After expanding Athabaskan §29.1.1.1 `section_mappings` (`TŠ`, `TS`, `K`, … → distinctive feature matrices), parse output YAML shows long `stages` across multiple lines and compile validation fails. Initial hypothesis: YAML folding embeds `\n` in stage strings and ASCA rejects them; fix = strip newlines at compile time and/or raise `yaml.dump()` `width`.

**Grill must decide:** root cause, correct fix layer (parse / YAML I/O / compile), and whether `section_mappings` → feature matrices is the right applier-neutral SoT policy for section-local class labels.

## Facts established (2026-09-08; do not re-litigate without new evidence)

### YAML presentation ≠ embedded newlines

- `dump_cleaned_index()` (`src/conlanger/tools/index_io.py`) calls `yaml.safe_dump()` with default `width=80` and no custom representer for `stages` (only `raw` gets `_LiteralStr` `|` blocks).
- Long braced stage strings (>~200 chars) are **folded across lines in the file** but `read_cleaned_index` / `yaml.safe_load` round-trip **without** `\n` in the loaded string.
- Verified on regen `data/diachronica/index_diachronica_parsed.yml` (2026-09-08): **68** stages >80 chars, **0** stages with embedded `\n` after load.
- Setting `width=4096` on `dump_cleaned_index` produces single-line stage scalars on disk (cosmetic only; no semantic change on load).
- Increasing `width` on a generic `yaml.dump()` call does not change loaded strings — it only affects on-disk layout. Owner report that `width` “does nothing” likely conflated file appearance with in-memory values.

### Example inventory failure is not a newline bug

**Row:** `Deg-Hit’an-K` (`29.1.1.1.7`, `index_diachronica_original.html:10034`, `alt_idx=0`):

```text
Syntax Error: Expected `]`, but received End of Line | [+cons, -son, -cont, -cor, +fr, -bk, +hi, -lo] > [+cons | ^ @ Rule 1, Line 1
```

**Original Index line:** `K → {K,TŠ}`

**After `section_mappings` (§29.1.1.1):**

| Stage | Value |
| --- | --- |
| input | `[+cons, -son, -cont, -cor, +fr, -bk, +hi, -lo]` |
| output | `{[+cons, -son, -cont, -cor, +fr, -bk, +hi, -lo],[+cons, +dist, +fr, -bk, +hi, -lo]}` |

Loaded stages: single-line, `newlines=0`.

**Root cause:** compile-time field-token parsing, not YAML.

`parse_field_tokens` → `split_braced_set_members` (`src/conlanger/tools/compile/asca/sets.py`) splits `{…}` members on commas tracking only `{}` depth — **not** `[]` or `()`. Output set `{[matrix1],[matrix2]}` is split into 14 comma fragments instead of 2 matrices:

```text
tokens: (('[+cons', '-son', …, '-lo]', '[+cons', '+dist', …, '-lo]'),)
```

Optional-output expansion (ticket 66) then emits **14** bogus alternatives. `alt_idx=0` compiles to `> [+cons` (truncated first “member”). ASCA “End of Line” means **unexpected end of rule string** mid-matrix — not a YAML `\n` character.

**Contrast:** `split_set_members` in the same file already respects `[]` and `()` depth but is not used by `parse_field_tokens` for whole-field sets.

**Inventory:** 14 error rows for one rule (`alt_idx` 0–13) — all symptoms of the same split bug.

### §29.1.1.1 seed mappings (`config/parser/parser_config.yml`)

```yaml
section_mappings:
  "29.1.1.1":
    "TŁ": "[+lateral]"
    "TŠ": "[+cons, +dist, +fr, -bk, +hi, -lo]"
    "TŠʷ": "[+cons, +dist, +fr, -bk, +hi, -lo, +labial]"
    "TS": "{[+cons, -son, -cont, +cor, +anterior, +dist, +delrel], [+cons, -son, +cont, +cor, +anterior, +dist, -delrel]}"
    "K": "[+cons, -son, -cont, -cor, +fr, -bk, +hi, -lo]"
    "T": "[+cons, -son, -cont, +cor, +anterior, +dist]"
```

## Owner position (Q5 — section_mappings vs group_mappings)

Owner rejects routing these through compile `group_mappings`:

- Athabaskan `TŠ`, `TS`, `K`, `Q` are **not** Index key class letters (`C`, `V`, `S`) — there are no sensible applier-neutral “group letters” to substitute.
- Targets are **distinctive feature matrices** — standard handbook notation, not ASCA-specific. Storing them in `stages` is linguistically honest and applier-neutral per `CONTEXT.md` **Feature matrix** glossary entry.
- `section_mappings` is the right mechanism (ticket 97): section-scoped `from → to` maps; §10 `*D`→`D` and §29 `TŠ`→`[…]` are the same facility with different target types.

**Agent concurrence:** the failure mode is a **compile set-splitting bug**, not evidence that parse-time matrix expansion is wrong. `group_mappings` remains for global Index class letters where ASCA expansion differs from inbuilt groupings.

## Glossary gap

Current **Class letter** entry covers Index key capitals (`C`, `V`, `S`). Athabaskan key labels (`TŠ`, `TS`, `K`) are **section-local class labels** — section-scoped phonological classes, not global Index classes. Grill should decide canonical term and whether `CONTEXT.md` needs an entry (distinct from **Class letter** and **Feature matrix**).

## Grill must decide

1. **SoT policy:** confirm `section_mappings` → distinctive feature matrices at parse for section-local labels (owner position above) vs any alternative (defer expansion, structured YAML, compile-only).
2. **YAML I/O:** add `width=4096` (or similar) to `dump_cleaned_index` for readability? Required or cosmetic?
3. **Compile fix:** make braced-set member splitting bracket-aware — e.g. `split_braced_set_members` delegates to `split_set_members`, or `parse_field_tokens` uses bracket-aware splitter. Acceptance: `Deg-Hit’an-K` → 2 optional-output alternatives (two full matrices), not 14; similar rules with `{[matrix],…}` shapes.
4. **Defensive normalize:** `strip_whitespace` on stages in `read_cleaned_index` — needed given current evidence, or YAGNI?
5. **Explicit non-fix:** compile-time newline strip on stages — reject unless new evidence shows literal `\n` in loaded SoT.
6. **Glossary:** add **section-local class label** (or chosen term) to `CONTEXT.md`?
7. **Follow-on ticket type:** correction pass vs straight compile bugfix vs both?

## Rejected / deprioritised (pending grill)

| Proposal | Verdict (session 2026-09-08) |
| --- | --- |
| Strip `\n` at compile time | Wrong layer; no-op on current path; masks SoT corruption if literal `\n` ever appears |
| Move §29 matrices to `group_mappings` | Wrong tool; no stable group-letter substitute; not Index key class letters |
| Treat matrices as “ASCA-shaped” SoT leak | Incorrect — distinctive features are applier-neutral per glossary |

## Probes and acceptance (suggested)

| Probe | Expected after fix |
| --- | --- |
| `Deg-Hit’an-K` compile | 2 alternatives: input matrix `>` each output matrix member |
| `yaml.safe_load` after regen | still 0 stages with `\n` |
| `width=4096` dump | long §29 stages on one YAML line (if grill adopts) |
| §29.1.1.1 inventory | `Deg-Hit’an-K` alt rows collapse from 14 errors to 0–2 (depending on ASCA validity of matrix outputs) |
| Regression | existing optional-output rules with simple `{a,b}` sets unchanged |

## Related artifacts

- Parse mechanism: [97 implement section_mappings](97-implement-parser-config-section-mappings.md)
- Optional outputs: [61 grill optional outputs](61-grill-optional-outputs.md), [66 implement](66-implement-optional-outputs-alt-idx.md)
- Field tokens / sets: `src/conlanger/tools/compile/field_tokens.py`, `src/conlanger/tools/compile/asca/sets.py`
- YAML I/O: `src/conlanger/tools/index_io.py`, `tests/conlanger/tools/test_index_io.py`
- Example parsed YAML: `data/diachronica/index_diachronica_parsed.yml` §29.1.1.1.7 `Deg-Hit’an-K`
- Error inventory rows: `.scratch/rule-index/inventory/rule-inventory-error.csv` (`Deg-Hit’an-K`, alt_idx 0–13)

## Follow-on (after grill resolves)

- Implement compile fix (bracket-aware braced-set splitting) — likely a **task** ticket, not a correction pass.
- Optional: `dump_cleaned_index` width tweak.
- Optional: `CONTEXT.md` glossary entry for section-local class labels.
- Re-run `create_index && validate_rules`; measure §29.1.1.1 ok delta.

## Comments

- Session used `/grill-with-docs` on [map.md](../map.md); domain-modeling notes folded into Owner position and Glossary gap above.
