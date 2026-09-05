Type: task
Status: resolved
Blocked by: 12

# Correction pass: prose env `else`

Target cluster: `expected_underscore` — Index catch-all **`/ else`** — **93** index rules with `env` matching `^\s*else\b` (inventory: **90** of those in `expected_underscore`; baseline in older notes said 85).

Spawned from [correction pass template](13-correction-pass-template.md). **Grill 2026-08-09** retargeted this ticket (parse-time complementary rewrite; no `#_` stub).

## Problem

Index writes a default branch as prose `else` in the environment slot, e.g.:

```
kʼ → {χʷ,qʷ} / #_
kʼ → q / else
```

ASCA rejects `else` (`Expected '_'`). The second rule is the complementary default: apply **except** where the previous rule’s environment holds.

## Decision (grill 2026-08-09)

**Parse-time** rewrite within each sound-change section (YAML SoT gets real `env`/`exception`; `raw` unchanged):

1. Strip trailing glosses / uncertainty on the else line first (`(rarely)` → `comment`, `sometimes` → `sporadic`, etc.) so `env` is bare `else` / `else?`.
2. If the **immediately preceding** rule in the same section has **`env` and no `exception`**, rewrite the else rule to:
   - **omit** `env` (any environment)
   - set **`exception`** = previous rule’s `env`
3. ASCA emit is then `… // <prev env>` (existing exception join).

**In scope:** the **85** pairs matching step 2 (including cascades: v1 uses **immediate prev only**, not union of all prior envs).

**Deferred (leave `env: else` / `else?` — do not invent `#_` stubs):**
- **4** pairs where prev has both `env` and `exception`
- **3** where prev has neither
- **1** else-after-else
- Prev env is still prose that cannot be an ASCA exception (will keep failing until a later prose-env pass)
- Non-catch-all `else` fragments (e.g. `_# else`, English “elsewhere”)

## What to build

1. Section-local post-pass (or equivalent) after per-line extract: resolve `/ else` as above.
2. Tests: classic complementary pair; gloss-then-resolve (`/ else (rarely)`); deferred shapes unchanged; cascade uses immediate prev only.
3. Full inventory re-run; record before/after for catch-all `else` cluster.

**Expected impact:** large cut of the 90 `expected_underscore` else rows where prev env is already ASCA-shaped (e.g. `#_`).

## Policy

- Historical fidelity: complementary default = exception ← prev env; `raw` keeps Index `/ else`.
- No fake `#_` stub for unresolvable else.
- Class-first: do not rewrite the 4 env+exception predecessors until a later design.

## Acceptance criteria

- [x] Parse resolves in-scope else → omitted `env` + `exception` = prev `env`
- [x] Deferred leftovers still have `env: else` / `else?` (or gloss variants only after strip failure)
- [x] Tests cover complementary, gloss, cascade-immediate-prev, and one deferred env+exception pair
- [x] Full inventory re-baseline; else cluster size in **Answer**
- [x] Fixtures updated where outcomes change
- [x] `CONTEXT.md` Environment / Exception wording kept aligned

## Answer

Baseline (before): **7308 / 9201** ok (79.4%); **93** rules with catch-all `env: else` / `else?`.

Full inventory re-run:

- **7372 / 9201** ok (**+64** rules, **80.1%**)
- Catch-all `else` / `else?` in `env`: **93 → 9** (84 rewritten to `exception` = immediate prev `env`; 8 structural deferred + 1 gloss-only else-after-else chain)
- `expected_underscore` failure class: **409 → 334** (−75)
- Implementation: `resolve_catch_all_else_rules` section post-pass in `IndexDiachronicaParser.parse`

## References

- Grill 2026-08-09 (`/ else` complementary distribution)
- [Correction pass template](13-correction-pass-template.md)
- [Correction pass: stress conditions](22-correction-pass-stress-conditions.md)
- Examples: Proto-Agaw to Xamtanga `kʼ → … / #_` then `/ else` (`index_diachronica_original.html:1222–1223`)
