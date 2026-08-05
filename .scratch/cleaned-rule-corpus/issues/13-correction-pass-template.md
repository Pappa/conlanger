Type: task
Status: resolved
Blocked by: 12

# Correction pass (cluster-driven)

## What to build

Implement one **class-first** correction pass targeting a specific **failure class** (or small related group) identified from the ticket 12 inventory. After the pass, re-run the full inventory and record before/after metrics.

**Do not claim this ticket until ticket 12 is resolved and the target cluster is named in the ticket body** (edit the `Target cluster:` line below before setting `Status: ready-for-agent`).

Target cluster: _n/a — standing template; file numbered instances instead_

Typical pass shape:

1. Implement parser and/or compile-layer fix for the named cluster (per edit ladder, ADR-0010)
2. Re-run ticket 12 pipeline on full HTML
3. Record ok/fail delta and residual cluster size in ticket **Answer**
4. Update fixtures for rules whose validation outcome changed (note failure class or edit-ladder step)

Passes may add ingest normalizations (feature mappings, class-letter compile, env-focus fixes), parsing fixes, or hold-outs (`status: skipped`) — whichever the cluster warrants. Multiple passes become tickets 13, 14, 15, … as needed.

## Blocked by

- [Full-corpus validation inventory](12-full-corpus-validation-inventory.md)

## Acceptance criteria

- [x] Target cluster named and sized in ticket body before work begins (per numbered instance)
- [x] Class-first transform implemented; no silent meaning-changing rewrites
- [x] Full inventory re-run; before/after metrics recorded in ticket **Answer**
- [x] Fixtures updated for intentionally changed validation outcomes

## Answer

Standing recipe — not a single deliverable. Twelve instances filed and resolved as tickets [14](14-correction-pass-unknown-grouping.md) through [25](25-correction-pass-bare-length-marker.md). File new numbered tickets (26+) for further clusters from [inventory summary](../inventory/asca-rule-inventory-summary.md).
