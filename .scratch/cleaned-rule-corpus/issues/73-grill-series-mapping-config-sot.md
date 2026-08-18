Type: grilling
Status: ready-for-human
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
