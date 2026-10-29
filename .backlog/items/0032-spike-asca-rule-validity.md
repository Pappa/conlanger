Type: spike
Status: resolved
Plan: [0003-plan-cleaned-rule-index.md](0003-plan-cleaned-rule-index.md)
Overview: ASCA rule string validity checklist and parse pipeline (0.10.2).
Result: [0032-asca-rule-validity.md](../spike/0032-asca-rule-validity.md)
Blocked by:

## Question

From asca-rust primary docs, what makes a rule string valid for input/output/environment/exception (and whole-rule forms the CLI/library accepts)? Capture a concise validity checklist and citation pointers so later tickets can classify and fix Index Diachronica–derived rules.

## Answer

**Gist:** An ASCA rule is `input ARROW output [/ env] [PIPE exception]` with non-empty I/O (use `*`/`∅` alone for insert/delete, `&`/`@` metathesis); env needs one `_` focus (joined `___` OK, spaced `_ _` not; underline-in-structure OK in 0.10+); `#` is env-peripheral only. Prefer parse-only validation via `ParsedRules::try_from` (or lexer+parser); `asca run` / `asca trace` also work but mix in word/runtime errors. Context7 has no asca index — findings are from asca-rust docs + crate source.

**Findings:** [0032-asca-rule-validity.md](../spike/0032-asca-rule-validity.md).

**Context pointer:** Use that file’s per-field checklists, §5 pipeline tiers, and §6 ID failure patterns when inventoring/fixing Index Diachronica–derived rules.

## Source list

- `legacy wayfinder rule-index issue 01-valid-asca-rule-string.md`
