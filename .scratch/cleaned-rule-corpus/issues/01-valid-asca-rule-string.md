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

**Gist:** An ASCA rule is `input ARROW output [/ env] [PIPE exception]` with non-empty I/O (use `*`/`∅` alone for insert/delete, `&` alone for metathesis); env needs one `_` focus (joined `___` OK, spaced `_ _` not); `#` is env-peripheral only. Validate by compiling a one-rule `.rsca` via `asca run words.wsca -r rule.rsca` (no dedicated validate command). Context7 has no asca index — findings are from asca-rust docs + crate source.

**Findings:** [../research/asca-rule-validity.md](../research/asca-rule-validity.md)

**Context pointer (for parent wayfinder / later tickets):** Use that file’s per-field checklists + §5 ID failure patterns when inventoring/fixing Index Diachronica–derived rules. Do not treat this ticket’s answer as a Decisions-so-far update — parent owns `map.md`.
