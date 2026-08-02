Type: research
Status: resolved

# What counts as a valid ASCA rule string?

## Question

From asca-rust primary docs, what makes a rule string valid for input/output/environment/exception (and whole-rule forms the CLI/library accepts)? Capture a concise validity checklist and citation pointers so later tickets can classify and fix Index Diachronica–derived rules.

## Notes

- Skills: `/research`; use Context7 if asca-rust is indexed, otherwise primary sources (asca-rust repo docs).
- Known doc URL from prior work: `https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md`
- Output: one Markdown findings file; link it from this ticket when done.
- Unblocks: inventory of valid/invalid rules; correction workflow; informs schema constraints that must compile to ASCA.

## Answer

**Gist:** An ASCA rule is `input ARROW output [/ env] [PIPE exception]` with non-empty I/O (use `*`/`∅` alone for insert/delete, `&`/`@` metathesis); env needs one `_` focus (joined `___` OK, spaced `_ _` not; underline-in-structure OK in 0.10+); `#` is env-peripheral only. Prefer parse-only validation via `ParsedRules::try_from` (or lexer+parser); `asca run` / `asca trace` also work but mix in word/runtime errors. Context7 has no asca index — findings are from asca-rust docs + crate source.

**Findings:** [../research/asca-rule-validity.md](../research/asca-rule-validity.md) (refreshed for **asca 0.10.2**, including §5 internal parse/validation pipeline for Python).

**Context pointer (for parent wayfinder / later tickets):** Use that file’s per-field checklists, §5 pipeline tiers, and §6 ID failure patterns when inventoring/fixing Index Diachronica–derived rules and when implementing [Create an ASCA validator for SoundChangeRule](08-asca-validator.md).

## Comments

- Research file updated from local install **asca 0.10.2** (was documented against 0.9.3). Includes internal lexer→parser→split_into_subrules→runtime map and 0.9.3→0.10.x changelog notes relevant to validity.
