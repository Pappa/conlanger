Type: task
Blocked by:

# Correction pass: syllable position `#U` / `U#` (compile-time)

Target cluster: mechanical `#U` / `U#` in `exception` and simple positive `env` on segment-level rules — **~29** rules estimated uplift.

Spawned from [Spike: Index syllable position `#U` / `U#` → ASCA](58-spike-index-syllable-position-u-hash.md) (2026-08-29). Findings: [index-syllable-position-u-hash.md](../research/index-syllable-position-u-hash.md). Probes: [probes-58/](../research/probes-58/).

## Context

Index `#U` / `U#` mark syllable-tier membership (segment anywhere in word-initial / word-final syllable). Naive `// #_%` or `U→%` on boundary tokens is **wrong**. Faithful ASCA uses [underline structures](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#underline-structures) + [environment-set exceptions](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#environment-sets). Env-set **member order matters** (`{#_#}` before structure members).

| Index surface (after `in` strip) | Field | ASCA emission |
|----------------------------------|-------|---------------|
| `#U` | `exception` | `// :{#_#, #<.._>}:` |
| `U#` | `exception` | `// :{#_#, <.._>#}:` |
| `#U, U#` | `exception` | `// :{#_#, #<.._>, <.._>#}:` |
| `#U` | `env` (positive) | `/ #<.._>` |
| `U#` | `env` (positive) | `/ <.._>#` |

**Do not:** rewrite `#U` → `#_%`; expand `U→%` inside `#U` / `U#` tokens.

## What to build

1. Compile-time transform in `SoundChangeRule` (after `group_mappings`, before validate) — match mechanical `exception` / `env` values only (exact `#U`, `U#`, `#U, U#` after optional `in` strip).
2. Parse-only (same PR or follow-up): strip editorial `in` before `#U` / `U#` in `exception` / `env`.
3. Amend `group_mappings.csv` comment — `U→%` is standalone class letter, not `#U`/`U#` position markers.
4. Unit tests from research §5 probe words (`ska:.ta:`, `a:`, `ta:.ska:`, trisyllabic Proto-Norse).
5. Full inventory re-run; before/after in **Answer**.

## Out of scope

- Prose env/exception tails (`#U before a U with /iː/`, `between #U and U[+stress]`, …) — defer / `status: skipped` (separate cluster tickets)
- `split_env_exception` trailing-`/` fix (ticket 58 note on `a → u / %u / ! in #U`)
- Rules where `#U`/`U#` live in `comment` only

## Acceptance criteria

- [x] Compile transform wired per research §5; index `raw` unchanged (ADR-0010)
- [x] `in` strip for mechanical `#U`/`U#` tails (parse or compile pre-match)
- [x] `group_mappings.csv` comment amended
- [x] Unit + ASCA integration tests on Old Norse, Proto-Norse, Iroquoian examples
- [x] Inventory re-run; ~29-rule uplift documented in **Answer**
- [x] No imports from `legacy/`

## Answer

**Shipped 2026-08-31.**

- **Compile:** `apply_syllable_position_compiled_overrides` in `syllable_position.py`, wired after group mappings in `compile_asca_rule_field_strings`. Mechanical `exception` / `env` tails map per research §5 (`#U` → `: {#_#, #<.._>}:` / `#<.._>`, etc.).
- **Parse:** `apply_syllable_position_editorial_strip` strips editorial `in` before mechanical `#U` / `U#` on env/exception (`raw` unchanged).
- **Config:** `group_mappings.yml` `U` row comment clarifies `#U`/`U#` position markers compile via structure rewrite, not `U`→`%`.
- **Inventory:** OK **8093 → 8121 (+28)**; sections all-OK **372 → 377 / 714**. Changelog flips match mechanical exception/env cluster (Old Norse `Vː`, Proto-Norse `Vː`/`i`, Iroquoian `Vː`, Papuan positive `#U` env, Yupik `in #U` exceptions, Kwamera `U#` env, …).
- **Tests:** `tests/conlanger/tools/compile/asca/test_syllable_position.py` — unit mapping + `validate_asca` on probe words from research §5.2–5.4.

## Comments
