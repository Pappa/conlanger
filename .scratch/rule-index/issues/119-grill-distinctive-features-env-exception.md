Type: grilling
Blocked by: None

# Grill: distinctive features in env and exception blocks

Spawned from wayfinder session on [Cleaned rule index SoT](map.md) (2026-09-05). Owner is revising `config/parser/manual_mappings.yml` and `config/parser/index_diachronica_corrections.yml` before this grill runs.

## Question

How should **distinctive-feature matrices** in Index **`env`** and **`exception`** fields be represented in the **applier-neutral** rule index, and how should compile rewrite them to valid ASCA?

Decide policy for bare matrices (`/[+stress]`, `// [+stress]`), segment-at-focus stress/length (`/ unstressed`, `/ stressed`), interim `_:[+feature]` placeholders, and related shapes — **before** a compile correction pass or wholesale manual-mapping rollout.

## Owner interim policy (2026-09-05; do not treat as settled)

- **Applier-neutral SoT** may keep feature matrices directly in `env` / `exception` when they read clearly, e.g. `a > b / [+stress]`, `a > ∅ / _ // [+stress]`.
- A few **`_:[+feature]`** rows remain in manual mappings while a better solution is sought (`_:[-long]#`, `_:[+stress, -long]%`).
- Manual mappings now map `/ unstressed` → `/ [-stress]` and `/ stressed` → `/ [+stress]` (not `_[-stress]` / `_[+stress]`).

## Facts (from ASCA 0.10.2 + local validation; do not re-litigate without new evidence)

- ASCA `=` in env/exception is **reference assignment** (`V=1`), not Index identity (`V = a`) — see prior map session on Spanish-V_5.
- Colon in **env** attaches to **segment tokens** adjacent to `_` (e.g. `V:[+long]_#` in compensatory lengthening), **not** to `_` itself. `_:[-stress]` is a **parse error**.
- Without colon, a matrix adjacent to `_` is a **separate segment** in that slot: `_[-stress]` = focus then an unstressed segment **after** `_`; `[-stress]_` = matrix **before** `_` (different from “feature on the matched input segment”).
- Feature on the **changing segment at `_`** is idiomatically expressed on **input** with colon: `a:[-stress, -long] > ə`, `V:[-stress] > ∅ / _`.
- **Syllable-level** unstressed is distinct from segment-level: [Correction pass: prose env positions](107-correction-pass-prose-env-positions.md) maps `unstressed syllables` → `_ %[-stress]`.
- [Correction pass: when stressed / when unstressed env conditions](22-correction-pass-stress-conditions.md) handles `when stressed` / `when unstressed` prose tails on structural envs — orthogonal to bare `/ [+stress]` env-only rows.
- [What counts as a valid ASCA rule string?](01-valid-asca-rule-string.md) / [asca-rule-validity.md](../research/asca-rule-validity.md) — segment+matrix checklist.

## Edge cases to grill (non-exhaustive)

1. **Env-only matrix** — `X > Y / [+stress]` with no `_`: applier-neutral encoding vs compile target (`X:[+stress] > Y / _`? `X > Y / [-stress]_`? env-set?).
2. **Exception-only matrix** — `X > Y / _ // [+stress]`: exception semantics vs input-side constraint vs neighbor env.
3. **`/ unstressed` / `/ stressed`** — segment-level (owner: `[-stress]` / `[+stress]` in env) vs syllable-level (`_ %[-stress]`); interaction with [manual_mappings.yml](../../../config/parser/manual_mappings.yml).
4. **Interim `_:[+feature]`** — migrate to what at compile? Retire from SoT? Document as compile-only sugar?
5. **Matrices on class letters** — `C[+voice]_`, `V[-long]`, env `VC_:[-stress, -long]CV` (corrections overlay): neighbor vs focus vs template notation.
6. **Identity / grouping exceptions** — `! V = a`, `C = r`, `V:[+back] = ɒ` (`expected_number` cluster): input narrowing vs env vs manual row.
7. **Alpha / bundled features** — `_ %[-str]%#`, `_[+ emphatic]` from manual mappings: same policy as binary matrices?
8. **Historical fidelity** — keep applier-neutral `env`/`exception` as authored; compile-only rewrite ([ADR-0010](../../../docs/adr/0010-historical-fidelity-class-first-status.md)).
9. **Validation split** — which shapes are valid in SoT but fail ASCA until compile vs invalid SoT schema.

## Related tickets / artifacts

- [Correction pass: when stressed / when unstressed env conditions](22-correction-pass-stress-conditions.md)
- [Correction pass: prose env positions](107-correction-pass-prose-env-positions.md)
- [Spike: Index feature matrices → ASCA targets](29-spike-index-feature-matrices-to-asca-targets.md) + [research](../research/index-feature-matrices-to-asca-targets.md)
- [Normalise segment feature matrices for appliers](07-normalise-segment-features.md)
- `config/parser/manual_mappings.yml` — `/ unstressed`, `/ stressed`, `_:[-long]#`, `_:[+stress, -long]%`, `_[+ emphatic]`, …
- `config/parser/index_diachronica_corrections.yml` — section-local env shapes (e.g. `VC_:[-stress, -long]CV`)

## Notes

- Skills: `/grill`, `/domain-modeling` (wayfinder default for grilling tickets).
- **HITL** — owner deferred grill session; ticket is queued only.
- Follow-on (after resolve): compile correction pass ticket(s) + manual-mapping / corrections cleanup; do not implement compile rewrites until this grill closes.

## Comments

- 2026-09-05: Ticket filed from map session (ASCA env colon semantics, Spanish-V_5, owner manual-mapping edits). Grill not yet run.
