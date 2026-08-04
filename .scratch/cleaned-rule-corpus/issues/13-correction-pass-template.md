Type: task
Status: needs-triage
Blocked by: 12

# Correction pass (cluster-driven)

## What to build

Implement one **class-first** correction pass targeting a specific **failure class** (or small related group) identified from the ticket 12 inventory. After the pass, re-run the full inventory and record before/after metrics.

**Do not claim this ticket until ticket 12 is resolved and the target cluster is named in the ticket body** (edit the `Target cluster:` line below before setting `Status: ready-for-agent`).

Target cluster: _TBD from inventory clustering_

Typical pass shape:

1. Implement parser and/or compile-layer fix for the named cluster (per edit ladder, ADR-0010)
2. Re-run ticket 12 pipeline on full HTML
3. Record ok/fail delta and residual cluster size in ticket **Answer**
4. Update fixtures for rules whose validation outcome changed (note failure class or edit-ladder step)

Passes may add ingest normalizations (feature mappings, class-letter compile, env-focus fixes), parsing fixes, or hold-outs (`status: skipped`) — whichever the cluster warrants. Multiple passes become tickets 13, 14, 15, … as needed.

## Blocked by

- [Full-corpus validation inventory](12-full-corpus-validation-inventory.md)

## Acceptance criteria

- [ ] Target cluster named and sized in ticket body before work begins
- [ ] Class-first transform implemented; no silent meaning-changing rewrites
- [ ] Full inventory re-run; before/after metrics recorded in ticket **Answer**
- [ ] Fixtures updated for intentionally changed validation outcomes
