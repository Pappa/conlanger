# `position.in` and embedded `in <target>` → ASCA compile projection

Research for spike [173](../issues/173-spike-position-in-asca-compile-projection.md). Implements compile-only policy for [174](../issues/174-task-position-in-asca-compile-projection.md). Builds on [156](../issues/156-task-indexcontext-position-in-relation.md) (`in {v}` materialize), [98 / index-syllable-position-u-hash.md](./index-syllable-position-u-hash.md) (`#U` / `U#`), and [162](../issues/162-grill-syllable-structure-env-resolution.md) / [163](../issues/163-task-prose-position-env-string-fixes.md) (stress focus).

Primary sources:

- ASCA **0.10.2** semantics (cited URLs match upstream; local probes use fork **0.10.3** per [DEV.md](../../../docs/DEV.md)): [Syllable structure matching](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#syllable-structure-matching), [Underline structures](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#underline-structures), [Environment sets](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#environment-sets), [Special characters](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#special-characters) (`#`, `$`, `%`)
- Compile today: [`project_index_context.py`](../../../src/conlanger/compile/project_index_context.py), [`resolve_index_rule.py`](../../../src/conlanger/compile/resolve_index_rule.py), [`syllable_position.py`](../../../src/conlanger/compile/tools/asca/syllable_position.py), [`pipeline.py`](../../../src/conlanger/compile/tools/asca/pipeline.py) (`apply_syllable_position_compiled_overrides` at end of field compile)

Inventory: [`position-in-asca-compile-projection.csv`](./position-in-asca-compile-projection.csv) (regenerate: `uv run python .scratch/rule-index/research/_build_position_in_inventory.py`). Probes: [`probes-173/`](./probes-173/) (`words.wsca`); field validation via `lib/bin/asca validate -s '<env>' -f context`.

---

## 1. Executive summary

| Decision | Recommendation |
| --- | --- |
| **Is literal Index `in …` valid ASCA?** | **No.** `in U[-stress]`, `in #U`, `U[+lo]` all fail `asca validate -f context` (unknown grouping `U`, missing `_`, etc.). Editorial `in` is always stripped or rewritten at compile. |
| **Integration point** | **Option B2** — one **post-materialize, pre-emission** compile transform on **env/exception strings**, centralized in (or beside) `syllable_position.py`, invoked from the existing ASCA field pipeline. Keep applier-neutral `in {v}` from materialize ([156](../issues/156-task-indexcontext-position-in-relation.md)); do **not** put ASCA grammar in `project_index_context.py`. |
| **`position_templates.in`** | **Keep** `in: "in {v}"` as the applier-neutral intermediate for unclassified targets and inventory diffing; classified syllable classes rewrite in the B2 pass. |
| **Mechanical uplift (estimate)** | **~23** stress-class rows + **~11** syllable-edge rows + **~4** stress-height matrix rows with validated ASCA targets ≈ **38** rules with a concrete compile outcome; **~30** embedded-string rows overlap structured classes; **~11** prose/manual deferrals remain. |

**Why B2 over B1:** ~**30** env/exception values never pass through structured `IndexContext` (embedded `C_CV in U[-stress]`). B1-only projection in `materialize_index_rule_env_exception` cannot see those without duplicating logic. B2 runs on the same string shape whether the source was a dict (after materialize) or a legacy string.

**Why not only the late `apply_syllable_position_compiled_overrides` hook:** That pass today handles **whole-field** mechanical `#U`/`U#` and **some** stress tails, but not **comma-joined** `context, in U[…]`, not **embedded** `prefix in U[…]`, and leaves `U:[+stress][+lo]` as invalid `in U:[…]`. B2 should **subsume and extend** that module rather than add a third pass.

---

## 2. ASCA semantics (cited)

From [Special characters](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#special-characters):

- `%` — syllable token (class `U` maps here at compile via `group_mappings`)
- `$` — syllable boundary (stress features attach here in segment-focused envs)
- `#` — word boundary (env only)

From [Underline structures](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#underline-structures): `#<.._>` / `<.._>#` express segment focus inside word-initial / word-final syllable constituents (ticket 98 table).

From [Syllable structure matching](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#syllable-structure-matching): syllable-tier envs use `%` with allowed features (e.g. `[+stress]`, `[+hi]`); segment-tier envs need a segment focus `_` when the rule targets segments.

**Probe (fork 0.10.3, `validate -f context`):**

| Fragment | Result |
| --- | --- |
| `_ $[-stress]`, `_ $[+stress]` | pass |
| `#<.._>`, `<.._>#` | pass |
| `:{#_#, #<.._>}:` (exception set member) | pass |
| `_ %[+stress][+lo]`, `_ %[+hi]` | pass |
| `in U[-stress]`, `U[+lo]`, `C_CV, in U[-stress]` | **fail** (unknown `U` / no focus) |
| `_ %[+open]` | **fail** (no `open` feature on `%`) — Index `U[+lo]` / `U[+hi]` is **not** a straight `%[±open]` swap |

---

## 3. Target-class mapping

### 3.1 Mechanical syllable edges (`#U`, `U#`, `#U, U#`)

Reuse ticket 98 encodings ([index-syllable-position-u-hash.md](./index-syllable-position-u-hash.md) §5). Apply when the **`in` tail** is exactly the mechanical marker (after optional editorial `in` strip), including:

- structured `position.in: '#U'` / `U#`
- whole-field `env: '#U'` / `in #U`
- **embedded** tails `O_ in #U`, `%u in #U`, `if N in U#` → rewrite **only the tail**; preserve prefix (`O_`, `%u`, …) per Index semantics.

| Index tail | Field | ASCA emission |
| --- | --- | --- |
| `#U` | env | `#<.._>` (or `prefix #<.._>` when embedded) |
| `U#` | env | `<.._>#` |
| `#U, U#` | exception | `// :{#_#, #<.._>, <.._>#}:` |
| `#U` / `U#` | exception | `// :{#_#, #<.._>}:` / `// :{#_#, <.._>#}:` |

**Defer:** prose after the marker (`in #U before a U with /iː/`, `in #U with the following U…`) — keep `manual_mappings` / `skipped` until a cluster ticket splits env.

### 3.2 Syllable stress (`U[+stress]`, `U[-stress]`, `U:[+stress]`)

Per [162](../issues/162-grill-syllable-structure-env-resolution.md) / [163](../issues/163-task-prose-position-env-string-fixes.md):

| Index surface | Whole-field env | Embedded / `context` + `in` |
| --- | --- | --- |
| `U[+stress]` / `in U[+stress]` | `_ $[+stress]` | `{context} in $[+stress]` (replace `, in U[+stress]` → ` in $[+stress]` per 163) |
| `U[-stress]` / `in U[-stress]` | `_ $[-stress]` | `{context} in $[-stress]` |
| `U:[+stress]` (colon matrix) | `_ %[+stress]` | `{prefix} in %[+stress]` or `_ %[+stress]` when whole-field |

**Already partially implemented** in `project_syllable_stress_compiled_env`; gap: materialized `in U:[+lo]` still emitted for matrix rows ([inventory CSV](./position-in-asca-compile-projection.csv) `current_compiled_tail`).

### 3.3 Stress + height matrices (`U:[+stress][+lo]`, …)

| Index | Proposed ASCA | Probe |
| --- | --- | --- |
| `in U:[+stress][+lo]` | `_ %[+stress][+lo]` | pass |
| `in U:[+stress][+hi]` | `_ %[+stress][+hi]` | pass (hi on `%` valid) |

Colon-bracket normalization to ASCA comma-inside (`U:[+stress, +lo]`) may stay in existing symbol projection; B2 must run **after** that normalization or share the same helper.

### 3.4 Open/closed syllable features (`U[+lo]`, `U[+hi]`, matrices with `+lo` / `+hi`)

Index “open/closed syllable” does **not** map to ASCA `%[±open]` (feature unknown). Provisional compile targets (inventory probes on representative strings):

| Index | Proposed ASCA (segment-focused) | Notes |
| --- | --- | --- |
| `in U[+hi]` | `_ %[-hi]` or `_ %[+closed]` | Validate policy with linguist; `_ %[+hi]` passes syntax but may not match Index “closed” intent |
| `in U[+lo]` | defer / manual | No stable ASCA feature for “open syllable” in 0.10.x |

CSV marks **28** `syllable_feature_matrix` rows — implement only after feature mapping is locked (or route to `manual_mappings`).

### 3.5 `context` + `position.in` (comma join)

[`resolve_index_context_to_string`](../../../src/conlanger/compile/project_index_context.py) emits `"{context}, in {target}"` when both are set ([144](../issues/144-implement-indexcontext-compile-resolution.md)).

**Compile policy (174):**

1. Detect `, in U…` / `, in #U` / `, in U:` tails on env strings.
2. Rewrite tail to ASCA per §3.1–3.3; join with **` in `** (not comma-before-`in`) for stress tails per 163, e.g. `C_CV, in U[-stress]` → `C_CV in $[-stress]` (validated pattern: segmental prefix + syllable stress scope).
3. Do **not** parse-split embedded `in` into structured `position` (out of scope for 173/174).

### 3.6 Prose / morpho / non-phonological `in`

Inventory **`defer_or_manual`**: Athabaskan `in prefixes`, `in the`, Bantu `in C₁ position`, `in even syllables`, Biblical Hebrew “adjacent syllable”, etc. — **no compile rewrite**; keep SoT strings; validation remains fail or `skipped` until manual_mappings or parse extraction tickets.

---

## 4. Corpus inventory (2026-10-18)

From [`position-in-asca-compile-projection.csv`](./position-in-asca-compile-projection.csv):

| Slice | Rows | Notes |
| ---: | ---: | --- |
| Structured `position.in` | **38** | Matches ticket baseline |
| Embedded `in <U…>` / `#U` / `U#` in env/exception strings | **30** | Regex `\bin\s+(#U|U#|U\[|U:|…)` |
| **Total in-scope rows** | **68** | One row per rule field hit |

| `target_class` (approx.) | Count | 174 action |
| --- | ---: | --- |
| `syllable_stress` | 12 | Implement `_ $[±stress]` + embedded tail rewrite |
| `syllable_stress_height_matrix` / `syllable_stress_colon` | 12 | Implement `_ %[+stress]…` matrix projection |
| `syllable_edge` | 11 | Extend mechanical `#U`/`U#` to **embedded** tails |
| `syllable_feature_matrix` | 28 | Defer or manual until hi/lo ASCA policy |
| `syllable_edge_feature` (`#U:[+stress]`) | 1 | Defer (edge + feature) |
| `other` / prose | 4+ | Defer |

---

## 5. B1 vs B2 (compile placement)

| Criterion | B1 (`project_index_context` / materialize emits ASCA) | B2 (post-materialize string transform) |
| --- | --- | --- |
| Embedded string envs | Needs second path | **Same path** |
| Applier-neutral SoT | **Blurs** YAML/compile boundary | **Preserves** `in {v}` after materialize |
| Ticket 98 raw-aware overrides | Awkward (materialize has no ASCA pipeline context) | **Fits** existing `env_raw` + `compiled_env` pattern in `pipeline.py` |
| Testability | Split across materialize + pipeline | **One** function table + pipeline hook |

**Recommendation: B2** — add `project_position_in_compiled_fields(env_raw, exception_raw, env_compiled, exception_compiled) -> …` (name TBD) called once from `compile_asca_rule_fields` **after** subscript/matrix normalization and **replacing** the ad hoc tail of `apply_syllable_position_compiled_overrides` (merge implementations).

Materialize ([`materialize_index_rule_env_exception`](../../../src/conlanger/compile/resolve_index_rule.py)) **unchanged** except docs/tests: still `in {v}` + comma `context`.

---

## 6. Relation to [156](../issues/156-task-indexcontext-position-in-relation.md)

- **Keep** default template `in: "in {v}"` in [`compiler_config.yml`](../../../config/compile/asca/compiler_config.yml).
- Classified targets (§3.1–3.3) **must not** rely on the template as final ASCA; B2 rewrites to validated fragments.
- Unclassified / prose targets keep `in {v}` until manual intervention — same as today, but documented.

---

## 7. Handoff checklist for [174](../issues/174-task-position-in-asca-compile-projection.md)

- [ ] Implement B2 projector (extend `syllable_position.py` or sibling module) with table §3.1–3.3.
- [ ] Handle **embedded** tails (`C_CV in U[-stress]`, `O_ in #U`) without requiring parse extraction.
- [ ] Normalize `, in U…` → ` in $…` / ` in %[…]` per 163; add regression tests mirroring inventory rule_ids (Egyptian-Arabic-V, Blackfoot-e_2, Vowel-Shifts_3-*, Lydian-e,o, …).
- [ ] Wire single call site in [`pipeline.py`](../../../src/conlanger/compile/tools/asca/pipeline.py); remove duplicate logic paths if any.
- [ ] Document compile table in `docs/system/sound-change-applier.md`.
- [ ] Run `uv run compile_rules && uv run validate_rules`; append inventory changelog; expect ok-flips on stress/edge rows, not on deferred hi/lo prose.
- [ ] Leave `syllable_feature_matrix` + prose `in` rows as explicit defer/manual in CSV.

---

## 8. Acceptance (spike 173)

- [x] Findings file under `research/`
- [x] Inventory CSV with structured + embedded rows
- [x] ASCA citations + `asca validate` probes for stress, edge, matrix classes
- [x] B1 vs B2 recommendation and 156 template policy
- [x] Checklist for 174
