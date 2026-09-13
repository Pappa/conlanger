Type: task
Status: resolved
Blocked by:

# Correction pass: env slash glued after delimiter + sporadic trailing `?`

Spawned from `/grill-with-docs` on [map.md](../map.md) (2026-09-13). Reporter examples: `Orkney-Norn-ð_2` (env slash boundary), `Orkney-Norn-l_3` (sporadic `?` residue).

## Problem

Two small gaps in **Phase C** (`split_output_rest`) and **Phase D1** (`apply_sporadic_qualifier` / `extract_uncertainty_qualifier_from_field`) leave Index editorial punctuation in parsed fields.

### 1 — Env delimiter with space before `/` but env glued after

| | |
|---|---|
| **HTML** | `ð → ∅ /{a,E}_` (`Orkney-Norn-ð_2`) |
| **Parsed today** | `stages: [ð, "∅ /{a,E}_"]` — no `env`; slash treated as output |
| **Inventory** | `syntax_other` — *Output cannot be empty* (`ð > /{a,V:[+front]}_`) |

[Ticket 82](82-correction-pass-output-env-slash-boundary.md) handled `∅/ _#` — slash glued to **output** with a **trailing space** after `/` (`GLUED_ENV_SEP = "/ "`). It did **not** handle the symmetric shape: spaced slash **before** env with **no** space after `/` (`∅ /{a,E}_`).

**Corpus size:** **1** rule (`Orkney-Norn-ð_2`). No additional HTML rows match ` /` + env-start without ` / ` after filtering editorial phonemic slashes.

### 2 — Trailing `?` detected as sporadic but not stripped

| | |
|---|---|
| **HTML** | `l → ∅ / _# ?` (`Orkney-Norn-l_3`) |
| **Parsed today** | `sporadic: true`, `env: "_# ?"` — `?` remains |
| **Inventory** | `stuff_after_word_bound` — *Cannot have segments after the end of a word* |

`field_has_uncertainty_qualifier()` already treats a trailing `?` as uncertainty (`text.endswith("?")`), so `apply_sporadic_qualifier` sets `sporadic: true`. **`extract_uncertainty_qualifier_from_field()` only strips uncertainty *words*** (`sporadic`, `sometimes`, `occasionally`, `(?)` in parens) — not a bare trailing `?` or ` ?`.

`double_slash_env.py` strips `?` from **exception** tails only when sporadic was set via *word* captures — duplicate, incomplete logic.

**Corpus size:** **22** sporadic rules with trailing `?` in `env` or `exception` (12 currently in error inventory). Simple strip fixes **~9** failing rules; **~3** prose env tails (`#_, possibly everywhere?`, `_Cko, ko lost?`, `…dialectally?`) remain failures after `?` removal and need separate prose-env work.

## Resolution

### Fix 1 — `split_output_rest` (`src/conlanger/utils/parsing.py`)

After existing `ENV_SEP` (` / `) and `GLUED_ENV_SEP` (`/ `) checks, add a third peel:

- Split on ` /` (space + slash) when the character immediately after `/` is **non-whitespace** and **env-start** (`#`, `_`, `{`, `!` — same guard family as ticket 82).
- Do **not** split editorial phonemic slashes in output glosses (the env-start gate prevents most false positives; `Orkney-Norn-ð_2` is the only corpus hit).

Update `tests/conlanger/tools/ingest/test_parser.py` `test_split_output_rest` and any `extract_rule_parts` fixtures. Amend `docs/system/index-diachronica-parser.md` Phase C3 note (symmetric to pass 82).

### Fix 2 — `extract_uncertainty_qualifier_from_field` (`src/conlanger/utils/gloss.py`)

After existing word/paren/quote stripping, when `field_has_uncertainty_qualifier(text)` is still true because of a **trailing** `?`:

- Strip trailing ` ?` or bare `?` from the field value.
- Append `?` (or `?` with surrounding space) to captures → `comment` via existing `apply_sporadic_qualifier` path.
- **Do not** strip `?` when it is not trailing (e.g. `_j(w){?,ia,a(ta)}`, `Cʲ_?w`) — the end-anchor handles this.
- **Do not** re-strip `(?)` — already handled by `_TRAILING_PAREN_WITH_UNCERTAINTY_RE`; leave `_# (?)` behaviour unchanged.

Remove the redundant `if flags.get("sporadic") and value.endswith("?")` block from `double_slash_env.py` once centralised (or leave a one-line comment pointing to gloss helper).

Extend `tests/conlanger/utils/test_gloss.py` and ingest integration (`Orkney-Norn-l_3`, Albanian `_B?`, `_E:[+stress]?`).

### Policy (grill-aligned)

- **`?` at end of env/exception** = Index uncertainty → `sporadic: true` + strip from SoT field (same lane as ticket 19). Completes the detection-without-removal gap.
- **Prose env + `?`** (e.g. `not universal?`) — prose transforms ([107](107-correction-pass-prose-env-positions.md), [55](55-correction-pass-prose-env-medial.md)) own the env rewrite; this pass only removes the terminal `?` so ASCA does not see a segment after `#` / `_`.
- **Omitted `/` entirely** — still overlay-only per ticket 82; out of scope.

## What to build

1. Implement fix 1 in `split_output_rest`.
2. Implement fix 2 in `extract_uncertainty_qualifier_from_field`; dedupe `double_slash_env` tail strip.
3. Unit tests for both helpers + at least one `parse_rule_element` integration per bug.
4. `uv run create_index && uv run validate_rules`; record before/after in **Answer**.
5. Update parser doc Phase C3 / D1 one-liners.

## Expected inventory impact (estimate)

| Fix | Rules touched | Expected ok-flips |
|-----|--------------:|------------------:|
| Slash glued after ` /` | 1 | **+1** (`Orkney-Norn-ð_2`) |
| Trailing `?` strip | 22 fields / ~18 rules | **+8 to +10** (9 failing rules with structural env after strip; prose tails stay fail) |

Watch for regressions on rules that currently pass with `_Vr ?` in env (`Orkney-Norn-s_2` — should become `_Vr`, still ok).

## Acceptance criteria

- [x] `Orkney-Norn-ð_2` parses to `stages: [ð, ∅]`, `env: "{a,E}_"` (or equivalent after feature mapping)
- [x] `Orkney-Norn-l_3` parses to `env: "_#"`, `sporadic: true`, no `?` in env
- [x] Trailing `?` / ` ?` stripped from all 22 sporadic env/exception fields; captured in `comment` where applicable
- [x] No change to mid-field `?` (alternation braces, `Cʲ_?w`, etc.) or lone `?` segment values (`j → ?`, `? → ∅`)
- [x] Full inventory re-run; before/after metrics in **Answer**
- [x] Parser doc updated

## Answer

**Shipped 2026-09-13.**

### Inventory

| | Before | After | Δ |
|---|---:|---:|---:|
| OK | 8865 (90.1%) | 8877 (90.2%) | **+12** |
| Fail | 459 (4.7%) | 451 (4.6%) | **−8** |

Notable ok-flips: `Orkney-Norn-ð_2`, `Orkney-Norn-l_3`, Albanian `_B?` rules (×4), `Old-Provençal-n_3`, `Coptic-r`. Lone `?` segment values (`j → ?`, `? → ∅`) preserved via `text != "?"` guard.

### Changes

- `split_output_rest`: third peel on ` /` when env is glued after slash (`∅ /{a,E}_`).
- `extract_uncertainty_qualifier_from_field`: strip trailing ` ?` / `?` (not lone `?`); deduped `double_slash_env` tail strip.

## Out of scope

- Prose env normalization for tails that remain invalid after `?` strip (`Sorowahá-ʔ`, `Muskogean-V`, `Guānhuà-yʔ`) — inventory-driven follow-on
- Fully glued `output/env` with no space before or after `/` when env does not start with `#_!{` (0 corpus hits today)
- Omitted `/` Index errata — `index_diachronica_corrections.yml` only

## References

- [Correction pass: output/env slash boundary (82)](82-correction-pass-output-env-slash-boundary.md)
- [Correction pass: uncertainty glosses / sporadic (19)](19-correction-pass-sporadic-qualifier.md)
- [Sporadic sampling (68)](68-sporadic-sampling.md)
- `src/conlanger/utils/parsing.py` — `split_output_rest`
- `src/conlanger/utils/gloss.py` — `extract_uncertainty_qualifier_from_field`
