Type: grilling
Status: resolved
Blocked by:

# Grill: correspondence-series expansion config (deferred from 72)

Spawned from [grill 72](72-grill-series-mapping-manual-sot.md) when ingest-pipeline decisions overtook the series ontology. Skills: `/grilling`, `/domain-modeling`.

## Question

After parse-time `series_mappings.csv` is removed, what replaces it?

Owner direction from grill 72 (not yet fully grilled):

- **Correspondence-series expansion** is not an **Index Diachronica correction** and not a **Manual mapping**.
- `PIE_LARYNGEAL_ALIASES` (`h₁→h`, `h₂→x`, `h₃→ɣʷ`) move to a **config file** where other **optional** series expansions can be defined.
- I/O inference (`infer_parallel_rule_mappings` / `infer_singleton_rule_mappings`) and opaque placeholders (`s₁→f1`) are not a SoT.

Decide:

1. **What counts as a defined expansion** (citation/prose, inventory tables, conventional reconstructions, owner judgment, never rule I/O).
2. **Config shape and layer** — compile vs parse; section-scoped vs global; package default vs user overlay; relationship to `section_abbreviations.yml` and `apply_asca_aliases`.
3. **Indeterminate / unknown tokens** at compile (leave literal and fail validation vs skip vs require config). This would amend ADR-0004 if skip or compile-only expansion wins.
4. **Collective subscripts** (`Xₓ`) — they currently live in `series_mappings.csv` too.

## Facts (do not re-litigate without new evidence)

- Parse expansion today: `apply_series_mappings` on all stages + env/exception; unmapped tokens stay literal.
- `apply_asca_aliases` is **compile**, global substring replace, PIE only. ADR-0004 rejected compile as the long-term home for series expansion; interim policy is leave-literal + validation fail, no pre-emptive skip.
- Ticket 65’s 100% in-scope coverage counted I/O-inferred rows and placeholders. That metric is not a constraint.
- ASCA `.alias` / `-l` is word (de)romanisation, not rule-token expansion ([research](../research/asca-alias-file-vs-group-mappings.md)).

## Outcomes

A recorded decision on config SoT, unknown-token policy, and whether ADR-0004 needs an amendment. Implementation tickets after this grill closes.

## Comments

- 2026-08-16: Filed during grill 72. Q2/Q3 parked here. **Confirmed:** parse-time `series_mappings.csv` is removed in 72’s implementation ([74](74-implement-ingest-corrections-drop-series-csv.md)); `PIE_LARYNGEAL_ALIASES` stays in Python until this grill; inventory `ok` drop from deleting I/O maps is accepted. **Next frontier** after grill 72 close (2026-08-18).
- 2026-08-18: Grill closed. Split **series expansions** (parse, `parser_config.yml`) vs **series mappings** (compile, `compiler_config.yml`). Implementation: [74](74-implement-ingest-corrections-drop-series-csv.md) + [75](75-implement-compiler-config-series-mappings.md).

## Answer

### Two mechanisms (do not conflate)

| Mechanism | Config file | When | Input → output |
| --- | --- | --- | --- |
| **Series expansion** | `data/parser_config.yml` | **Parse** | Collective `Xₓ` → member **indices** (global only) |
| **Series mapping** | `data/compiler_config.yml` | **Compile** | Correspondence-series index `Xₙ` → ASCA-parseable segment (hierarchical section + `global`) |

Not **Manual mapping**, not **Index Diachronica correction**. Never rule I/O inference or opaque placeholders (`s₁→f1`).

### `parser_config.yml` — `series_expansions` (parse)

```yaml
series_expansions:
  Hₓ: [h₁, h₂, h₃]
  hₓ: [h₁, h₂, h₃]
  sₓ: [s₁, s₂, s₃]
```

- Global only; separate rows for `Hₓ` and `hₓ` (same members; not case-aliased).
- Apply on corpus `stages` / env / exception after Manual mapping; **`raw` keeps Index surface** (e.g. `{Hₓ,m̩,n̩}`).
- Standalone: `sₓ → ʃ` → `{s₁,s₂,s₃} → ʃ`.
- Inside set: `{Hₓ,m̩,n̩} → a` → `{h₁,h₂,h₃,m̩,n̩} → a` — flatten members, no nested set.
- Correspondence-series indices in corpus stay literal until compile mapping.

### `compiler_config.yml` — `series_mappings` (compile)

```yaml
series_mappings:
  global:
    h₁: h
    h₂: x
    h₃: ɣʷ
  sections:
    - section: "17.10"
      h₁: h
      h₂: x
      h₃: ɣʷ
```

- **`global`** — default for all sections; section list overrides per token on longest-prefix match.
- Replaces `PIE_LARYNGEAL_ALIASES` Python dict and retired `series_mappings.csv` **mapping** rows.
- Compile step before positional/identity subscript expansion.
- Unmapped indices: leave literal; validation fails; no pre-emptive `status: skipped` ([ADR-0010](../../../docs/adr/0010-historical-fidelity-class-first-status.md)).

### Config layering

- **Do not** rename `parser_config.yml` into a combined config; parse vs compile settings stay in separate files.
- User overlay merge: deferred; loaders accept optional override path later; package defaults only for now.

### Authoring sources

Citation/inventory prose, conventional reconstructions (PIE laryngeals in `global`), owner judgment with audit — never rule I/O inference.

### ADRs

- [ADR-0004](../../../docs/adr/0004-series-indices-per-section-maps.md) amended again (expansion vs mapping split).

### Implementation

- Parse expansions + ingest overlay: [74](74-implement-ingest-corrections-drop-series-csv.md)
- Compile mappings: [75](75-implement-compiler-config-series-mappings.md)
