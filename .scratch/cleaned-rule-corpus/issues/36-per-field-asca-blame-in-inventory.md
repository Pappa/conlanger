Type: task
Status: ready-for-agent
Blocked by:

# Per-field ASCA blame in inventory

## Question

How should regen attach **per-field** ASCA diagnostics for failing corpus rules so correction triage can blame `input` / `output` / `env` / `exception` — without changing whole-rule `ok` or reviving probe synthesis?

## Decision (2026-08-20)

**Rewrite:** drop the stub engine from [Spike: field-isolation compile validation](35-spike-field-isolation-compile-validation.md). Use fork **`validate_asca_part`** ([Wire conlanger to forked asca `validate`](88-wire-conlanger-forked-asca-validate.md)) on **compiled** field strings from the same `SoundChangeRule` path as whole-rule inventory.

Whole-rule inventory `ok` stays **`validate_asca`** (`asca validate -r` when available, then `asca run` + probes) — grill Q3 A.

## Prerequisites (done)

- [Implement `validate` + `validate_part` on the private asca fork](87-implement-asca-fork-validate.md)
- [Wire conlanger to forked asca `validate`](88-wire-conlanger-forked-asca-validate.md) — `validate_asca_part(part, fragment)` in `src/conlanger/appliers/asca.py`; corpus `env` → ASCA `-f context`
- ~~[Inventory success/error CSV splits and ok-change changelog](34-inventory-success-error-splits-and-ok-changelog.md)~~

## What to build

### 1. Field-blame CSVs

Write three artifacts under `inventory/` (name constants beside existing `INVENTORY_*_NAME` in `corpus_inventory.py`):

| File | Rows |
|------|------|
| `asca-field-isolation.csv` | **Default: fails-only** (`whole_ok == false`); optional `--field-isolation-all` writes all rows |
| `asca-field-isolation-success.csv` | `whole_ok == true` (no errors) |
| `asca-field-isolation-error.csv` | `whole_ok == false` (errors) |

Success and error splits use the **same columns** as the full field-blame CSV and are **rewritten every regen** (mirror [34](34-inventory-success-error-splits-and-ok-changelog.md)). When the main CSV is fails-only, its rows are a subset of `asca-field-isolation-error.csv`.

**Join keys** (match main inventory): `section_index`, `section_name`, `rule_id`, `alt_idx`, `source`.

**Columns** (extend [research/field-isolation-compile-validation.md](../research/field-isolation-compile-validation.md) §6):

| Column | Notes |
|--------|--------|
| `whole_ok` | copy from main inventory row |
| `input_ok`, `output_ok`, `env_ok`, `exception_ok` | `true` / `false`; empty when field absent |
| `input_class`, `output_class`, `env_class`, `exception_class` | reuse `classify_error` on ASCA message |
| `input_description`, … | truncated stderr (same cap as main inventory) |
| `blame` | derived — see below |

### 2. Field source

For each inventory row (same `DiachronicSeries` / optional-output expansion as `validate_corpus_rule`):

- Read **post-compile** strings from the active `SoundChangeRule`: `.input`, `.output`, `.env`, `.exception` (after compile transforms; not raw YAML / `stages`).
- Call `validate_asca_part("input", input)` etc.; catch `ASCAValidationError` → `ok=false`, message for class/description.
- **Absent** optional `env` / `exception` → leave `*_ok` / `*_class` / `*_description` empty (N/A), do not call validate.

### 3. `blame` derivation

Relative to main row `whole_ok`. Count **present** fields only (env/exception omitted when absent).

| `blame` | When |
|---------|------|
| `none` | `whole_ok` is true (row omitted by default; included only with `--field-isolation-all`) |
| `input` \| `input\|env` (etc.) | one or more present fields have `*_ok == false` — **pipe-separated** failing field names in stable order: `input`, `output`, `env`, `exception` |
| `multi` | every present field passes per-field validate but `whole_ok` is false (uneven sets, unbalanced I/O, Tier-4 runtime, cross-field coupling, etc.) |

Do **not** redefine main `ok` from isolation.

### 4. Regen integration

- Hook from `regenerate_corpus` after main inventory CSV is written (same pass; share compile context).
- Build the full field-blame dataframe, then:
  - write `asca-field-isolation-success.csv` / `asca-field-isolation-error.csv` (filter on `whole_ok`)
  - write `asca-field-isolation.csv` — **default: fails-only** (`whole_ok == false`); optional `--field-isolation-all` for all rows
- Optional flag e.g. `--field-isolation-all` documented in help (all rows in main CSV; for regression lens).
- Summary markdown: link all three CSV paths; optional one-line count of `blame` buckets on error rows.

### 5. Tests

- Unit: `blame` derivation table (mock field ok flags + `whole_ok`); success/error split on `whole_ok`.
- Integration (requires fork / `ASCA_BIN` per `tests/conftest.py`):
  - Unknown feature on input only → `blame=input`, `input_class=unknown_feature`
  - Missing `_` on env only → `blame=env`
  - Two fields fail → e.g. `blame=input|env`
  - At least one **`multi`** fixture (e.g. uneven set whole-rule fail with syntactically valid I/O fields)
- Document in module docstring: per-field validate is Tier 1–2 (+ field-local syntax); `blame=multi` = whole-rule structural/runtime when all fields pass in isolation; ticket 10 boundary unchanged.

## Out of scope

- Stub rules / shape-aware canned I/O (superseded)
- Per-rule probe-word synthesis (ticket 10 wontfix)
- Replacing whole-rule inventory metrics or `ok` definition
- Bare I/O “transform-exempt” tagging (map fog)

## Supersedes

Stub build plan in [research/field-isolation-compile-validation.md](../research/field-isolation-compile-validation.md) §4–§5 (false pass/fail from stubs no longer apply). CSV column shape §6 still applies.

## Comments

- 2026-08-19: Blocked pending native asca; stub engine deferred.
- 2026-08-20: [87](87-implement-asca-fork-validate.md) + [88](88-wire-conlanger-forked-asca-validate.md) done; ticket rewritten for `validate_asca_part`.
- 2026-08-20: Renamed from “Field-isolation inventory sidecar” → **Per-field ASCA blame in inventory**.
- 2026-08-20: Add `asca-field-isolation-success.csv` / `asca-field-isolation-error.csv` filtered views (`whole_ok` split).
- 2026-08-20: Field-level fail → pipe-separated names (`input`, `input|env`, …); former `cross_field` → `multi` (no separate single-field case).

## Acceptance criteria

- [ ] Field-blame CSVs produced by regen: full (fails-only by default), success, and error splits
- [ ] Per-field checks via `validate_asca_part` on compiled `SoundChangeRule` strings; no stubs
- [ ] `blame` column derived; main inventory `ok` unchanged
- [ ] Tests: pipe-joined failing fields (`input`, `input|env`), `blame=multi` (whole fail, fields ok); ticket-10 boundary noted in docs
- [ ] Summary links `asca-field-isolation.csv`, `-success.csv`, and `-error.csv`
