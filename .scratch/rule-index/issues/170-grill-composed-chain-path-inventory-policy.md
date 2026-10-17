Type: grilling
Status: needs-grilling
Blocked by:

# Grill: composed chain paths vs per-stage inventory (`no composed chain paths from stages`)

Spawned from [169](169-task-validate-compiled-yaml-without-series-roundtrip.md) follow-on (2026-10-17). After **asca_rules.yml v3** and **composed chain paths** in `resolve_inventory_targets` (`_enumerate_composed_chain_paths`), inventory only emits targets that form a **valid multi-stage spine**: each step’s `input.compiled` must equal the previous step’s `output.compiled`. When no path survives, compile/inventory records `format_error: no composed chain paths from stages`.

**Current corpus (2026-10-17):** 3 index rules hit this (2 in `rule-inventory-error.csv`, same rows in `asca_rules.yml` as `compile_error`):

| `rule_id` | Failure shape (summary) |
| --- | --- |
| `Polish-ьr` | Step 2 branch outputs `{ɛr,…}` / `{ɛʐ,…}`; step 3 input is merged set `{ɛr,…,ɛʐ,…}` — no exact match. |
| `Catalan-ɛj-ɔj` | Step 1 output `jɛj uei`; step 2 input `jɛj:[+stress] uei:[+stress]` — materialization mismatch. |
| `Upper-Tanana-ə` | Step 1 outputs `a` / `ɨ`; step 2 input `{a,ɨ}` — split vs unsplit set. |

Code: `src/conlanger/tools/inventory_targets.py` (`_enumerate_composed_chain_paths`, `resolve_inventory_targets`). Related: `compiled_rule_shape.py` (branch YAML), `parallel.py` (Balinese-style `h > ∅` supplement).

## Question

Which policy should we adopt for **multi-stage chains** when compile does not expose a consistent segment-by-segment spine for strict input/output linking—and what follow-on **task** (if any) implements the chosen option?

## Options (decide one primary direction)

### Option A — Inventory: looser composition matching

Keep composed paths as the default, but **relax linking** when exact string equality fails, e.g.:

- Treat prior output `a` / `ɨ` as compatible with next input `{a,ɨ}`.
- Normalize stress/features between stages before compare (Catalan case).
- Other heuristics documented in GLOSSARY / ADR.

| Pros | Cons |
| --- | --- |
| Small, localized change in `inventory_targets` (or a matcher module). | Heuristic; risk of validating **impossible** stage pairings again. |
| Restores green inventory for the 3 rules quickly. | Hard to explain in `asca_rules.yml` branch semantics; matcher drift from compile truth. |
| Does not require re-opening parallel/chain compile tests. | Each new edge case adds matcher complexity. |

### Option B — Compile: align stages so spine is exact (preferred long-term in agent analysis)

Extend **chain expansion** / **parallel branching** so each `SoundChangeRule` part’s alternatives are exactly what the next stage can consume: split sets, uneven columns (ticket 109), optional outputs (66), null sets (81) **per chain segment**—not one blob `{…} > {…}` between stages unless that blob is the only legal successor.

| Pros | Cons |
| --- | --- |
| Single source of truth; `asca_rules.yml` branches stay honest (cf. Balinese-r). | Larger scope: `expand_chained_index_rule`, `parallel.py`, `SoundChangeRule._build_alternatives`, tests. |
| Inventory stays strict; no fuzzy matching. | Polish-style rules may need new expansion rules or ADR. |
| Matches Index “stages spine” mental model. | Catalan may need **between-stage normalization** (features), not only parallel zip. |
| | Upper-Tanana may be **parse/index garbage** (`ø in the Northway dialect)`) — compile cannot fix without ingest fix or skip. |
| | Inventory/YAML size and test churn when blobs split into many branches. |

### Option C — Inventory fallback: per-stage flatten when composition is empty

If `_enumerate_composed_chain_paths` returns `[]`, **fall back** to pre-169 behaviour: emit every compile alternative per `step_idx` / `alt_idx` independently (no cross-stage filter). Optionally log or tag rows as `composition_fallback` in inventory metadata.

| Pros | Cons |
| --- | --- |
| Minimal code; immediate recovery of prior validate coverage. | Reintroduces **cross-stage pairing bugs** (why composed paths were added). |
| Clear escape hatch for pathological rules. | `asca_rules.yml` v3 branch shape may not represent fallback rows without a second schema story. |
| Compile/index can be fixed later without blocking ship. | Hides compile gaps; 3 failures become “OK” without fixing semantics. |

## Grill rounds (suggested)

1. **Product:** Is a strict spine required for all chained rules, or is per-stage validation acceptable for &lt;0.1% hold-outs?
2. **Option pick:** Primary = A, B, or C; hybrid allowed? (e.g. B for parallel chains + C fallback with explicit skip list.)
3. **Corpus:** For each of the 3 rules, what is the **intended** ASCA path set (owner linguistics)?
4. **YAML:** If B, how do `alternatives` / `steps` represent Polish-scale Cartesian products without unreadable files?
5. **Parse vs compile:** Which failures are **ingest** (Upper-Tanana) vs **compile** (Polish) vs **normalize** (Catalan)?
6. **Follow-on:** One task vs split (compile spine vs matcher vs fallback flag).

## Non-goals (unless grill expands)

- Reverting v3 `asca_rules.yml` shape or Balinese-r branch logic.
- Changing applier-neutral index YAML SoT.
- Full rearchitecture of field isolation (may still read compile models at compile time).

## Related

- [169](169-task-validate-compiled-yaml-without-series-roundtrip.md) · [ADR-0018](../../../docs/adr/0018-compiled-asca-rules-yaml.md) · [compile-rules.md](../../../docs/system/compile-rules.md)
- Chain expansion: [ADR-0005](../../../docs/adr/0005-chain-expansion.md) (if present), `chains.py`, `test_chains.py`
- Parallel null sets: tickets 60 / 81 / 109, `test_parallel.py`

## Comments

- Opened 2026-10-17 after user report of `no composed chain paths from stages` in inventory; agent traced 3 rules and documented options A/B/C for grill.
