Type: task
Status: ready-for-agent
Blocked by:

# Correction pass: env/exception feature matrices

Spawned from [Grill: distinctive features in env and exception](119-grill-distinctive-features-env-exception.md) (policy resolved 2026-09-07 + 2026-09-13). Ticket [121](121-correction-pass-io-matrix-bracket-to-colon.md) colon-normalizes host+bracket matrices on **input/output only**; this ticket implements the grilled env/exception policy.

## Problem

Parsed index rules store env/exception feature constraints in applier-neutral Index bracket form. ASCA 0.10.2 either rejects the compiled strings or accepts them with **wrong semantics** (postfix brackets as separate tokens, bare matrices without `_`, invalid `// [-stress]` exceptions).

| Failure mode | Example compiled today | Root cause |
|--------------|-------------------------|------------|
| `expected_underscore` | `V > ə / [-stress]` | bare env matrix — no `_` in env |
| `expected_underscore` / invalid exception | `… // [-stress]` | bare exception matrix |
| Silent wrong match | `s > z / C[+voice]_` | postfix on neighbour host — should be `C:[+voice]_` for fidelity |

**Corpus scale (parsed index):** ~39 bare stress envs (`[-stress]` / `[+stress]`), ~22 `C[…]` envs, ~25 `V[…]` envs, ~34 exception lines containing `[`.

## Policy (from ticket 119 — do not re-litigate)

| Shape in YAML | Meaning | Compile target |
|---------------|---------|----------------|
| Bare `env: '[±F]'` (no `_`, no neighbour host) | **Segment-at-focus** — changed segment at `_` must carry feature | Move matrix to **input** with colon; env structural only (e.g. `V:[-stress] > ə / _`) |
| Bare `exception: '[±F]'` (no neighbour host, not identity `=`) | Blocks when focus segment carries feature | **Inverse polarity on input**; drop bare exception matrix (e.g. `V:[+stress] > ∅ / …`) |
| Postfix on host in env/exception (`C[+voice]_`, `V[-long]_#`) | **Neighbour qualification** on that host | Bracket→colon on host **in the same field** (`C:[+voice]_`); do **not** move to input |
| Neighbour templates (`_ [+rtr], [+rtr]_`) | Per-token neighbour predicates | Bracket→colon per host where needed; pass through when ASCA already accepts (Egyptian-Arabic-aː) |

**SoT unchanged:** YAML `env` / `exception` / **stages** / **raw** stay Index-shaped ([ADR-0010](../../../docs/adr/0010-historical-fidelity-class-first-status.md)). No parse-time rewrite into ASCA colon form.

## What to build

1. **Cross-field compile transform** (name TBD) in `src/conlanger/tools/compile/asca/` — detect bare env/exception matrices and segment-at-focus vs neighbour-host shapes on the **raw** field strings (or early compiled strings before env post-subscript finishes).

2. **Three rewrite families:**
   - **A — bare env matrix → input colon:** when entire `env` (trimmed) is a standalone `[…]` matrix, merge feature onto input host with colon; set compiled env to `_` or empty structural env as appropriate.
   - **B — bare exception matrix → inverse input:** when entire `exception` (trimmed) is standalone `[…]`, flip polarity features onto input; set `compiled_exception = None`.
   - **C — neighbour host postfix → env/exception colon:** apply `normalize_asca_host_bracket_matrices` (or shared `host_bracket_matrix_to_colon`) to **env** and **exception** compile fields — same helper as ticket 121, extended scope.

3. **Pipeline order** in [`pipeline.py`](../../../src/conlanger/tools/compile/asca/pipeline.py):
   - Family **A/B**: cross-field step — after identity exceptions ([128](128-correction-pass-index-identity-exceptions.md)), **before** or coordinated with I/O `normalize_asca_host_bracket_matrices` (Family B may need input already colon-normalized for host narrowing consistency).
   - Family **C**: on env/exception after per-field post-subscript (alongside set wrapping / syllable-position overrides) — mirror ticket 121 placement but on env/exception strings.
   - Document final order in [sound-change-applier.md](../../../docs/system/sound-change-applier.md) compile table.

4. **Unit tests** from ticket 119 worked examples:

   | Rule id | Parsed | Target compiled (representative) |
   |---------|--------|----------------------------------|
   | Palauan-V | `env: '[-stress]'`, `V > ə` | `V:[-stress] > ə / _` |
   | Old-Irish-s | `env: 'C[+voice]_'` | `s > z / C:[+voice]_` |
   | Old-Irish-V_3 | `exception: '[-stress]'` | `V:[+stress] > ∅ / …` (inverse; env template unchanged except unrelated fixes) |
   | Egypto-Berber-h,ħ,q | `env: 'C[+voice]_V'` | `{h,ħ,q} > ʕ / C:[+voice]_V` |
   | Egyptian-Arabic-aː | `env: '_[+rtr], [+rtr]_'` | unchanged or minor host colons only |

5. **`validate_asca` integration** where `asca` on PATH for representative rules.

6. **Full inventory re-run** (`uv run create_index && uv run validate_rules`); before/after ok/fail counts, `expected_underscore` cluster delta, and per-rule notes in **Answer**.

## Out of scope

- **I/O** host+bracket matrices — [121](121-correction-pass-io-matrix-bracket-to-colon.md) (done)
- **Identity exceptions** `! Host = seg` — [128](128-correction-pass-index-identity-exceptions.md) (done)
- **Alpha / co-reference** env matrices (`_C[α PLACE]`) — separate cluster
- **Parse-time** manual-mapping cleanup retiring `_:[+feature]` targets — follow-on ticket (config/parser only; policy locked in 119)
- **Invalid SoT rejection** at parse for `_:[+feature]` — optional schema guard; not required for compile pass acceptance
- `legacy/` imports

## Acceptance criteria

- [ ] Cross-field + per-field compile steps wired at documented pipeline order
- [ ] Families A, B, C with ticket 119 worked examples passing `validate_asca`
- [ ] Index YAML / **raw** unchanged (compile-only projection)
- [ ] Reuse or extend `host_bracket_matrices.py` for Family C (no duplicated regex drift)
- [ ] Inventory re-run with before/after metrics in **Answer**; list residual env/exception matrix failures
- [ ] Docs: compile table row in [sound-change-applier.md](../../../docs/system/sound-change-applier.md)
- [ ] No imports from `legacy/`

## References

- [119 — grill policy](119-grill-distinctive-features-env-exception.md)
- [CONTEXT.md](../../../CONTEXT.md) — **Environment**, **Exception**, **Feature matrix**
- [asca-rule-validity.md](../research/asca-rule-validity.md)
- `src/conlanger/tools/compile/asca/host_bracket_matrices.py`
- `src/conlanger/tools/compile/asca/pipeline.py`
- `.scratch/rule-index/inventory/error_clusters/expected_underscore_errors.csv`

## Comments

- 2026-09-13: Ticket filed from `/grill-with-docs` session on ticket 119 (round 2 closed; compile pass is follow-on implementation).
