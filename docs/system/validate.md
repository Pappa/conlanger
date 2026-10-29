# Validate

Stage 3 of the sound-change rule pipeline: **parse → compile → validate** ([ADR-0013](../adr/0013-parse-compile-validate.md)).

After [Index Diachronica parse](./index-diachronica-parser.md) and [compile_rules](./compile-rules.md) (on-disk `asca_rules.yml`), validate runs the applier checker and records inventory. This stage is the **correction loop** — **compile validation** per compiled target measures whether the **applier-neutral index** ([ADR-0002](../adr/0002-applier-neutral-yaml-rule-index.md)) produces valid ASCA, clusters failures for **class-first** correction, and iterates until adoption criteria are met. It is **not** ingest-time validation ([ADR-0003](../adr/0003-validate-after-applier-compile.md)): index fields may remain Index-shaped; the gate is post-compile `validate_asca`.

**Stale compile:** v1 `asca_rules.yml` has no index fingerprint. After changing `index_diachronica.yml`, run `uv run compile_rules` before `uv run validate_rules` ([ADR-0018](../adr/0018-compiled-asca-rules-yaml.md)).

**Glossary:** [GLOSSARY.md](../../GLOSSARY.md) — *Corpus rule*, *Failure class*, *Validation report*, *Status*, *Class-first*, *Historical fidelity*

---

## Steady-state workflow

The correction loop is driven by three commands:

```bash
uv run create_index && uv run compile_rules && uv run validate_rules
```

- **Parse-only** (YAML + parse diagnostics): `uv run create_index`
- **Compile-only** (regenerate `asca_rules.yml`): `uv run compile_rules`
- **Validate-only** (inventory from compiled YAML): `uv run validate_rules`

```mermaid
flowchart TD
  HTML[index_diachronica.html]
  Parse[IndexDiachronicaParser.parse]
  YAML[index_diachronica.yml]
  CommentSummary[rule-comment-phrases.md]
  Compile[compile_rules]
  ASCA_Y[asca_rules.yml]
  Inv[iter_compiled_inventory_bundles]
  Split[success / error CSVs]
  Changelog[ok-flip changelog]
  Summary[rule-inventory-summary.md]

  HTML --> Parse --> YAML
  Parse --> CommentSummary
  YAML --> Compile --> ASCA_Y --> Inv
  Inv --> Split
  Split --> Changelog
  Inv --> Summary
```

**Default paths:**

| Output | Path |
| --- | --- |
| Cleaned YAML | `data/diachronica/index_diachronica.yml` |
| Parse diagnostics | `diagnostics/parse/` |
| Inventory dir | `diagnostics/inventory/` |
| Compiled rules YAML | `diagnostics/compile/asca_rules.yml` (written by `compile_rules`; read by `validate_rules`) |
| Comment phrase survey | `diagnostics/parse/rule-comment-phrases.md` |
| Probe wordlist | `tests/fixtures/asca_probe_words.wsca` |

**`validate_rules` flags:** `--limit N` (smoke), `--compiled-in`, `--inventory-dir`, `--probe-words`, `--field-isolation`, `--use-asca-fork`, `--reset-changelog`.

**`create_index` flags:** `--html`, `--yaml-out`, `--parse-dir`.

**Steady-state loop** (ticket 05):

1. Parse HTML → write YAML (`uv run create_index`)
2. Compile index → write `asca_rules.yml` (`uv run compile_rules`)
3. Validate compiled targets → inventory (`uv run validate_rules`)
4. Regenerate YAML and/or validation report as needed
5. Git-diff YAML for churn control
6. Grow fixtures for changed **rule status**
7. Cluster **failure classes** (pandas on CSV)
8. File/implement correction pass
9. Repeat

---

## Inventory

**Goal:** Record, per **index rule**, whether ASCA compile validation passes — with section identity and failure taxonomy for clustering.

| Step | What happens | Code / artifact |
| --- | --- | --- |
| 1 | Parse HTML → applier-neutral YAML | `IndexDiachronicaParser` → `data/diachronica/index_diachronica.yml` |
| 2 | For each index rule in each section | `iter_inventory_with_field_isolation()` in `index_inventory.py` |
| 3 | Build mini-section (one rule) | `_mini_section()` |
| 4 | Compile | `DiachronicSeries(mini, compiler_config=…)` |
| 5 | Validate | `validate_asca(..., probe_words=tests/fixtures/asca_probe_words.wsca)` |
| 6 | Classify failure | `classify_error()`, `parse_unknown_token_error()` |
| 7 | Emit artifacts | See [Validation report](#validation-report) below |

**Scope:** One inventory row per **compile-expanded validation target** (not whole-section-only). A single index rule may emit multiple rows when compile fans out optional-output **alternatives** (`alt_idx`) or adjacent **stages** chain steps (`step_idx`). Each row runs `validate_asca` on a one-rule mini-series; the `rule` column is that target’s compiled ASCA line (not a stochastic parent pick). Compile uses a fixed inventory RNG seed (`INVENTORY_COMPILE_RNG_SEED` in `inventory_targets.py`) so optional-output and sporadic plumbing does not flip `ok` across regen. Config hold-outs (`status: skipped` from `skip_rules` / `skip_sections`, rendered as ASCA comments) inventory as `ok=SKIPPED` with description `held-out (commented rule)`. Missing-`→` and other unlisted parse failures inventory as `ok=FAILED` through compile validation.

**Per index rule `ok` semantics (correction rollups):** a rule id is **OK** only when every emitted row for that id is `ok=OK`; **FAILED** when any row fails; **SKIPPED** only when all rows are skipped. Changelog `ok` flips match prior inventory on `(source, alt_idx, step_idx)`.

**Baseline metrics** (re-run after each correction pass):

| Era | Rules | OK | Notes |
| --- | ---: | ---: | --- |
| Provisional AI YAML + asca 0.9.3 | 9721 | 57.1% | Ticket 02 |
| Cleaned schema + passes 14–25 | 9317 | 68.9% | Ticket 12 |
| Current on-disk summary | 9841 | **85.4%** (8400 ok) | [inventory summary](../diagnostics/inventory/rule-inventory-summary.md) |

**Section outcomes (current):** 417 / 714 sections all OK (58.4%); 268 some OK; 4 none OK; 25 sections skipped. See **Sections** in the summary markdown.

**Top failure classes (current):** `syntax_other`, `unknown_character`, `runtime_other`, `expected_underscore`.

**Limitations (accepted):** Tier 4 runtime failures may be under-detected when the fixed baseline wordlist does not match rule shape (~98% of failures are Tier 1–2 syntax). Rule-derived probe synthesis — ticket 10 — **wontfix**.

---

## Validation report

Temporary **analysis artifacts**, not long-term source of truth ([ADR-0010](../adr/0010-historical-fidelity-class-first-status.md)). Corpus YAML carries thin optional `status` only (`needs-validation` | `skipped`; omit = ok).

**Artifacts** (under `diagnostics/inventory/`):

| File | Role | Ticket |
| --- | --- | --- |
| `rule-inventory-success.csv` | Filtered `ok=OK` | 34 |
| `rule-inventory-error.csv` | Filtered `ok=FAILED` | 34 |
| `rule-inventory-changelog.csv` | Append-only **ok flips** matched by `(source, alt_idx, step_idx)` (HTML `file:line` + optional-output alternative + chain step). Prior `ok` is read from the success/error split CSVs. Pass `--reset-changelog` to overwrite after a column-schema change; with zero flips this writes a header-only CSV. | 34 |
| `rule-inventory-summary.md` | Rule/section counts, **Corrections** rollup for matched overlay rules, failure-class table, **Common Errors** (top `error_token` and description clusters per failure class), field-isolation blame | 12 |
| `field-isolation-success.csv` | filtered `whole_ok=OK` (and per-field clean) | 36 |
| `field-isolation-error.csv` | filtered `whole_ok=FAILED` or per-field fail | 36 |
| `unknown_grouping_errors.csv` | `unknown_grouping` cluster rows | error-cluster tooling |
| `unknown_character_errors.csv` | `unknown_character` cluster rows | error-cluster tooling |
| `expected_underscore_errors.csv` | `expected_underscore` cluster rows | error-cluster tooling |
| `nested_brackets_errors.csv` | `nested_brackets` cluster rows | error-cluster tooling |
| `unknown_features_errors.csv` | `unknown_feature` cluster rows | error-cluster tooling |
| `syntax_other_errors.csv` | `syntax_other` cluster rows | error-cluster tooling |
| `runtime_other_errors.csv` | `runtime_other` cluster rows | error-cluster tooling |
| `expected_number_errors.csv` | `expected_number` cluster rows | error-cluster tooling |
| `prose_or_expected_arrow_errors.csv` | `prose_or_expected_arrow` cluster rows | error-cluster tooling |

**CSV columns** (`VALIDATION_CSV_COLUMNS` in `index_inventory.py`):

`section_index`, `section_name`, `rule_id`, `alt_idx`, `step_idx`, `source`, `ok`, `failure_class`, `error_token`, `suggested`, `expected`, `description`

`alt_idx` is the 0-based optional-output alternative index (e.g. `d → {∅,ð}` emits one row per alternative and never the parent's random pick); it is empty when the target is not an alternative branch. `step_idx` is the 0-based chain step from `expand_chained_index_rule` (empty for single-step rules). See ticket 158.

**`ok` / `whole_ok` values** (`InventoryOk` in `index_inventory.py`): `FAILED`, `OK`, `SKIPPED`. New inventory CSVs write these strings only. Changelog flip detection and `load_inventory_csv` coerce legacy numeric cells (`0` / `1` / `2`) and boolean-ish strings when reading older files.

**Summary markdown (`rule-inventory-summary.md`):**

- **Rules** — ok / fail / skipped counts (section-skipped rules excluded from ok/fail percentages).
- **Corrections** — per-rule rollup for matched Index Diachronica correction overlays (`index_corrections.yml`); orphan correction ids are excluded. Lists failed rules by validation `failure_class` and skipped rules by skip reason (`rule_skipped` / `section_skipped`). Omitted when no matched corrections exist.
- **Sections** — mutually exclusive buckets: all OK, some OK, none OK, sections skipped (correction-pass prioritisation metric).
- **Failure classes** — full-class counts from error rows.
- **Common Errors** — for each failure class with a cluster CSV, top `error_token` rows plus (when token-less messages dominate) top normalised `description` rows; headings use `{failure_class} (error_token)` and `{failure_class} (description)`.
- **Field isolation blame** — when `--field-isolation` is on, per-field blame counts on whole-rule failure rows.

Inventory row count can exceed index rule count when optional-output alternatives (`alt_idx`) or multi-stage chains (`step_idx`) emit multiple validated rows.

**Failure classes** (regex-matched from ASCA stderr): include `syntax_other`, `runtime_other`, `unknown_character`, `unknown_reference`, `expected_ipa`, `expected_range_dots`, `invalid_ipa`, and others — full ordered list in `ERROR_CLASS_PATTERNS` (`index_inventory.py`). Dedicated cluster CSVs exist for each class in `CLUSTER_CSV_BY_FAILURE_CLASS`.

**Changelog behaviour:** First run (no prior success/error split CSVs) emits no flip rows; subsequent runs append only when `ok` changes for the same `source`, with shared UTC `timestamp` per run. The prior inventory is reconstructed by concatenating the success and error split CSVs from the last regen. `--reset-changelog` overwrites the changelog; when there are zero flips it writes header-only CSV (`CHANGELOG_CSV_COLUMNS`) with no data rows.

---

## Compile validation

Compile validation is part of **validate** (not a separate pipeline stage). It runs **after** applier compile, not at HTML→YAML ingest ([ADR-0003](../adr/0003-validate-after-applier-compile.md)).

### `validate_asca`

Module: [`appliers/asca.py`](../src/conlanger/appliers/asca.py)

```python
validate_asca(
    rule: DiachronicSeries,
    *,
    probe_words: Path | None = None,
    timeout: float = 15.0,
) -> bool  # raises ASCAValidationError

validate_asca_syntax(rule: str, *, timeout: float = 15.0) -> bool
validate_asca_part(part: ASCARulePart, fragment: str, *, timeout: float = 15.0) -> bool
resolve_asca_bin() -> str | None  # ASCA_BIN env, then PATH
```

**Binary resolution:** `validate_rules` defaults to the repo fork at `lib/bin/asca` (`--use-asca-fork`). Otherwise `ASCA_BIN` if set, else `shutil.which("asca")`. Same helper for `validate_asca`, `run_asca`, and the field helpers. Inventory and field isolation require **ASCA 0.10.3** from the private fork (`validate` subcommand). Install per [DEV.md](./DEV.md#asca-sound-change-rule-validation).

**Flow:**

1. `_active_rule_changes(rule)` — collect `SoundChangeRule` parts whose rendered line does **not** start with `#` (skipped rules render as `#\t…`).
2. Error if no active rules.
3. Resolve asca binary (repo fork, `ASCA_BIN`, or `PATH`; **0.10.3** fork with `validate`).
4. Write `str(rule)` (+ trailing newline) to temp `check.rsca`.
5. Resolve probe wordlist (see below).
6. When the binary supports `validate`: `subprocess.run([asca, "validate", "-r", rsca_path], …)` — fast syntax/structure fail (Tiers 1–3).
7. `subprocess.run([asca, "run", words_path, "--rules", rsca_path], …)` — still required for inventory `ok` (Tier 4).
8. Non-zero exit → `ASCAValidationError` with cleaned stderr.
9. Also fail if stderr contains `Syntax Error` or `Runtime Error` even on exit 0.

**Field helpers** (ASCA 0.10.3 `validate` only; used for field-isolation sidecar rows; whole-rule `ok` still uses `validate_asca` → `validate` + `run`):

- `validate_asca_syntax("a > b / _")` → `asca validate -s …`
- `validate_asca_part("env", "#_")` → `asca validate -s … -f context` (`env` maps to ASCA `context`)

**Inventory integration** (`index_inventory.py`): `validate_rules` loads `asca_rules.yml` → `iter_compiled_inventory_bundles` deserialises each target’s `series` → `validate_asca` on each one-rule mini-series (`probe_words=tests/fixtures/asca_probe_words.wsca` by default). Compile-time target resolution (`resolve_inventory_targets`) runs only in `compile_rules`.

### Probe wordlist

| Source | Path / content |
| --- | --- |
| Default (validator internal) | `a`, `ba`, `kata`, `sami`, `ntu` (5 words) |
| Inventory / tests fixture | `tests/fixtures/asca_probe_words.wsca` (same 5 words) |
| Override | `probe_words=` argument |

**Purpose:** `asca run` exercises parse **and** apply (Tier 1–4 in validity research). Not parse-only.

**Limits** (ticket 10 wontfix):

- ~98% of inventory failures are Tier 1–2 syntax — baseline probes suffice for clustering.
- Tier 4 runtime errors (lonely sets, insertion+env, deletion-only-segment) may be **under-detected** when probes don't match rule shape — acceptable for correction-loop clustering.

### ASCA validation tiers

See [asca-rule-validity.md](../../.backlog/spike/0032-asca-rule-validity.md) §5 for ASCA constraint detail (research pinned to **0.10.2** prose; project validation runs **0.10.3** fork):

| Tier | Stage | Caught by `validate_asca`? |
| --- | --- | --- |
| 1 | Lexer | Yes (`validate` when available, else `run`) |
| 2 | Parser | Yes |
| 3 | `split_into_subrules` (first apply) | Yes (`validate` when available, else `run`) |
| 4 | Runtime apply | Yes via `run` — probe-dependent |

### Skipped rules

Corpus `status: skipped` → `#\t{raw}` in ASCA output. `_active_rule_changes` excludes them; inventory marks `ok=SKIPPED`, description `"held-out (commented rule)"`. Hold-out policy: `status: skipped` only from `skip_sections` / `skip_rules` in `parser_config.yml` — not boolean `skip: true` / `skipped: true`, and not parse-time auto-skip ([ADR-0010](../adr/0010-historical-fidelity-class-first-status.md), ticket 89).

---

## Correction pass

**Goal:** Reduce failure clusters via **class-first** transforms — parser (parse-time) or compiler (`SoundChangeRule`, compile-time) — without meaning-changing rewrites unless owner-approved.

**Standing recipe** — ticket 13:

1. Name target **failure class** / `error_token` cluster from inventory summary or CSV.
2. Implement transform per **edit ladder** (ticket 04, [ADR-0010](../adr/0010-historical-fidelity-class-first-status.md)).
3. Re-run `uv run create_index && uv run compile_rules && uv run validate_rules`.
4. Record before/after ok/fail and residual cluster size in ticket **Answer**.
5. Update fixtures when **rule status** or validation outcome changes intentionally.

**Where fixes live:**

| Layer | Module | Examples (tickets 14–25) |
| --- | --- | --- |
| Parse-time | `IndexDiachronicaParser` / `parsers.py` | em dash 16, arrow 17, sporadic 19, glosses 21, stress 22, smart quotes 24 |
| Compile-time | `SoundChangeRule` in `rules.py` | class letters 14, length marks 15, 25, ejectives 20, labialized letters 23, chain expansion [compile-time chains](../src/conlanger/compile/tools/asca/chains.py) |

**Policy highlights:**

- Prefer **historical fidelity** over valid-but-inaccurate rewrites → `status: skipped` on the index rule.
- Structural normalisation → `status: needs-validation`; agent clears on clean re-validate.
- During bulk correction, do **not** pre-emptively skip unmapped tokens (ticket 26).
- Permanent skip / rare same-intent swaps → **project owner only**.

**Resolved correction passes (14–25):** unknown_grouping, length marker ː, em dash, arrow →, compile-time chain expansion, sporadic glosses, ejective ʼ, trailing glosses, stress env, labialized class letters, smart quotes, bare length marker.

**Follow-on cluster work:** correspondence-series 26–28, unknown_feature 32, positional/identity subscripts (planned compile-time, spike 38). (`samePOA` and other deferred unknown_feature leftovers: inventory-driven; no dedicated ticket.)

---

## Key modules

| Path | Role |
| --- | --- |
| [`create_index.py`](../src/conlanger/scripts/create_index.py) | Parse HTML → YAML + parse diagnostics |
| [`compile_rules.py`](../src/conlanger/scripts/compile_rules.py) | Load index YAML → write `asca_rules.yml` |
| [`validate_rules.py`](../src/conlanger/scripts/validate_rules.py) | Load compiled YAML → inventory |
| [`validation_cli.py`](../src/conlanger/scripts/validation_cli.py) | Shared ASCA fork/PATH resolution and `--version` probe |
| [`index_inventory.py`](../src/conlanger/tools/index_inventory.py) | Per-rule validation, CSV/changelog/summary |
| [`index_io.py`](../src/conlanger/tools/index_io.py) | Read/write cleaned YAML |
| [`parsers.py`](../src/conlanger/tools/parsers.py) | `IndexDiachronicaParser` |
| [`rules.py`](../src/conlanger/compile/models/rules.py) | Section compile (`DiachronicSeries`) |
| [`asca_validator.py`](../src/conlanger/tools/asca_validator.py) | `validate_asca` |

**Primary integration seam (tests):** `tests/conlanger/tools/test_index_pipeline.py` — HTML → parse → `DiachronicSeries` → `validate_asca`.

---

## ADR cross-links

| ADR | Relevance |
| --- | --- |
| [0002](../adr/0002-applier-neutral-yaml-rule-index.md) | Corpus is applier-neutral; validation report stays out of YAML |
| [0003](../adr/0003-validate-after-applier-compile.md) | Inventory runs post-compile, not at ingest |
| [0006](../adr/0006-html-source-of-truth-yaml-successor.md) | HTML source of truth until adoption criteria met |
| [0010](../adr/0010-historical-fidelity-class-first-status.md) | Class-first ladder; skip vs needs-validation |
| [0013](../adr/0013-parse-compile-validate.md) | Three pipeline stages; inventory under validate |

---

## Pipeline placement

| Stage | Doc |
| --- | --- |
| Index Diachronica parse | [index-diachronica-parser.md](./index-diachronica-parser.md) |
| Applier compile | [sound-change-applier.md](./sound-change-applier.md) |
| **Validate** (this page) | — |

See also [SYSTEM.md](./SYSTEM.md#pipeline-stages-new).
