# Sound-change pipeline is parse → compile → validate

Index Diachronica processing has **three** stages: **parse** (HTML → applier-neutral index), **compile** (index → a concrete applier), **validate** (applier checker + inventory). There is no fourth “applier-neutral index validation” stage — the inventory already compiles to ASCA and calls `validate_asca`, so that name implied a gate the YAML cannot have.

This does not change [ADR-0003](0003-validate-after-applier-compile.md): the automated gate remains **after** compile. Operator CSV/summary artifacts live under **validate**, not beside it.

## Considered Options

- **Four stages including “applier-neutral index validation” (previous docs)** — useful as an operator-loop description; misnames ASCA inventory as applier-neutral.
- **Three stages (chosen)** — matches the real seam: parse writes YAML, compile emits applier text, validate runs the applier and records inventory.

## Consequences

- `docs/SYSTEM.md` and stage docs list three rows. Inventory, failure-class CSVs, and the correction-loop commands (`uv run create_index` then `uv run validate_rules`) are documented under validate.
- `docs/applier-neutral-index-validation.md` is not a pipeline stage; fold or redirect it into the validate doc.
- Hold-out policy is [ADR-0010](0010-historical-fidelity-class-first-status.md) as amended: `status: skipped` only from `skip_sections` / `skip_rules`.
