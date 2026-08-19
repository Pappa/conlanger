Type: task
Status: ready-for-agent
Blocked by: 87

# Wire conlanger to forked asca `validate`

## Question

How should this repo invoke the **private** asca fork’s `validate` / `validate_part` CLI without changing whole-rule inventory `ok` (still `asca run` + probe words)?

## Depends on

[Implement `validate` + `validate_part` on the private asca fork](87-implement-asca-fork-validate.md) in `/home/pappa/Projects/Pappa/asca-rust` (fork **0.10.3** when that ticket is done).

Grill 2026-08-19: **Q3 A** — do not redefine `ok`.

## What to build

1. **Binary resolution:** honor `ASCA_BIN` if set; else `shutil.which("asca")`. Use the same helper for `validate_asca` and `run_asca` (today `run_asca` hardcodes `~/.cargo/bin/asca`).
2. **Install note** (short, in the applier/validation doc or module docstring): `cargo install --path /home/pappa/Projects/Pappa/asca-rust` so `PATH` `asca` is the fork; `asca --version` should report **0.10.3** (not crates.io 0.10.2).
3. **Helpers** for later field isolation — e.g. `validate_asca_syntax(rule)` → `asca validate --rules …` and `validate_asca_part(part, fragment)` → `asca validate --field …`. Do **not** switch inventory `ok` onto these.
4. **`validate_asca`** remains `asca run` + probe words (Tier 1–4 sample). Optional: call `validate` first as a fast syntax fail (same fail set for Tiers 1–2; must not turn current runtime-only fails into `ok`).
5. Tests: `ASCA_BIN` override; skip or xfail cleanly if the binary lacks `validate` (old 0.10.2).

## Out of scope

- Sidecar CSV / `blame` ([Field-isolation inventory sidecar](36-field-isolation-inventory-sidecar.md) — may be rewritten, deleted, or closed after this)
- Probe synthesis (ticket 10 wontfix)
- Changing success-metric definitions

## Acceptance criteria

- [ ] `ASCA_BIN` + PATH resolution shared by run and validate helpers
- [ ] Inventory / `validate_asca` still uses `asca run` + probes for `ok`
- [ ] Callable `validate_part` wrapper for the four fields
- [ ] Docs: install the fork; expected `--version` **0.10.3**
