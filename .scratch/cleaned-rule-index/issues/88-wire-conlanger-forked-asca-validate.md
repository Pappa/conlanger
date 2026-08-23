Type: task
Status: resolved
Blocked by: 87

# Wire conlanger to forked asca `validate`

## Question

How should this repo invoke the **private** asca fork’s `validate` / `validate_part` CLI without changing whole-rule inventory `ok` (still `asca run` + probe words)?

## Depends on

[Implement `validate` + `validate_part` on the private asca fork](87-implement-asca-fork-validate.md) on branch `feature/validate` in `github.com/Pappa/asca-rust`.

Grill 2026-08-19: **Q3 A** — do not redefine `ok`.

**Install and run the fork locally:** [docs/DEV.md](../../../docs/DEV.md) (ASCA sound change rule validation).

## What to build

1. **Binary resolution:** honor `ASCA_BIN` if set; else `shutil.which("asca")`. Use the same helper for `validate_asca` and `run_asca` (today `run_asca` hardcodes `~/.cargo/bin/asca`).
2. **Helpers** for later field isolation — e.g. `validate_asca_syntax(rule)` → `asca validate -s …` (whole rule) and `validate_asca_part(part, fragment)` → `asca validate -s … -f …`. Do **not** switch inventory `ok` onto these.
3. **`validate_asca`**:
   1. call `validate` first (using whole compiled rule string) as a fast syntax fail (same fail set for Tiers 1–2;
   2. if `validate` is successful, call  `asca run` + probe words (Tier 1–4 sample).
   3. must not turn current runtime-only fails into `ok`).
4. Tests: `ASCA_BIN` override; skip or xfail cleanly if the binary lacks `validate` (old 0.10.2).

## Out of scope

- Per-field blame CSV / `blame` ([Per-field ASCA blame in inventory](36-per-field-asca-blame-in-inventory.md) — may be rewritten, deleted, or closed after this)
- Probe synthesis (ticket 10 wontfix)
- Changing success-metric definitions

## Acceptance criteria

- [x] `ASCA_BIN` + PATH resolution shared by run and validate helpers
- [x] Inventory / `validate_asca` still uses `asca run` + probes for `ok`
- [x] Callable `validate_part` wrapper for the four fields
- [x] Install/run documented in [docs/DEV.md](../../../docs/DEV.md); implementation docs point there instead of duplicating cargo commands

## Answer

**Gist:** `resolve_asca_bin()` (`ASCA_BIN` then PATH) shared by `validate_asca`, `run_asca`, `validate_asca_syntax`, `validate_asca_part`. `validate_asca` runs `asca validate -r` then `asca run` + probes when validate exists. Part wrapper maps index `env` → ASCA `context`. Tests in `tests/conlanger/appliers/test_asca.py`; docs in [DEV.md](../../../docs/DEV.md) and [sound-change-applier.md](../../../docs/sound-change-applier.md). Unblocks native [Per-field ASCA blame in inventory](36-per-field-asca-blame-in-inventory.md).
