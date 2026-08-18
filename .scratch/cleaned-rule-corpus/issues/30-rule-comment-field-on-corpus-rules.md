Type: grilling
Status: resolved
Blocked by: None

# Rule comment field on corpus rules

## Question

Should the cleaned rule corpus schema carry an optional **`comment`** on each **corpus rule** — and how should parse-time extraction populate it from Index Diachronica rule lines?

## Notes

- Amends [YAML schema for the cleaned rule corpus](03-yaml-schema-cleaned-rule-corpus.md) (2026-08).
- Distinct from section-level **`comments`** (non-`schg` `<p>` blocks between rules).
- Distinct from **`sporadic`** (boolean uncertainty flag), **`status`** / validation report, and compile-time ASCA comments ([Historical fidelity vs valid-but-inaccurate fallback](04-historical-fidelity-vs-validity.md) edit-ladder step 3).
- Current parser **discards** much inline prose via correction passes 19–22, 21 (`strip_semicolon_prose`, trailing parens/quotes) — ~87 rules still carry `;` in `raw`; qualifiers like `short only` / `when unstressed` often remain in `env` or were stripped without retention.
- Owner observations: semicolon (`; `) reliably starts editorial tail; leftover string after rule extraction may be comment; qualifier phrases are useful for later syntax inference.

## Answer

### Schema (amends ticket 03)

Add optional **`comment`** on each **corpus rule**:

| Field | Required | Notes |
|-------|----------|--------|
| `comment` | no | Inline editorial prose pertaining to **this rule line** — English qualifiers, semicolon tails, parenthetical notes. Omitted when absent. Multi-line via `\|` when needed. **Not** ASCA syntax. |

**`raw`** still holds the full Index line unchanged. **`comment`** holds prose **removed from** `input`/`output`/`env`/`exception` during parse so compile fields stay ASCA-clean while auditability improves.

Section-level **`comments`** unchanged (prose paragraphs, not inline rule tails).

### What belongs in `comment`

Capture inline prose that is **about the rule** but not valid phonological notation:

1. **Semicolon tails** — text from the first `; ` onward in a field (owner: consistently editorial). Example: `{a,i} → ə / short only; the change of short a blocked…`
2. **Trailing parenthetical / quoted glosses** currently stripped by ticket 21 — retain in `comment` instead of discarding.
3. **Env qualifiers** removed for ASCA (`short only`, `when unstressed` when stripped from `env`, etc.) — append to `comment`.
4. **Sporadic / sometimes** gloss text stripped when setting `sporadic: true` — optional duplicate in `comment` for audit (prefer one canonical place: flag on rule, prose in `comment` if stripped).

Do **not** duplicate text that remains in cleaned `env`/`exception` unless it was also removed from another field.

### Extraction policy (parse-time)

- **Capture, don't discard:** parse transforms that today strip prose must **append** removed text to `comment` (joined with `; ` or newline when multiple captures).
- **Order:** run after primary `→` / `/` / `!` split; accumulate comment tails as later normalizations (gloss strip, stress env cleanup, sporadic strip) run.
- **Leftover line text:** when a future stricter rule parser leaves a verified non-syntax remainder on the line, treat it as `comment` — defer full “leftover” heuristic to implementation ticket; semicolon + known strip paths are MVP.
- **Ambiguous env prose:** when unsure whether text is env or comment, **keep in `env`** and copy to `comment` only when stripped for ASCA — do not pre-emptively skip rules.

### Analysis loop

Extracted **`comment`** values are an explicit corpus artifact for iterative review: cluster common qualifiers (`short only`, `unstressed`, dialect labels) to drive later env-syntax transforms or prose-env mapping — not thrown away after strip.

### Compile / validation

- **`comment`** is not emitted into ASCA rule strings in the first slice (avoids `malformed_comment` failures).
- Future: applier compiler *may* emit `comment` as an ASCA comment line when safe (ticket 04 step 3 follow-on).
- Validation report **`trailing-comment`** reason remains for compile failures; **`comment`** on YAML is the ingest-side preservation.

### Follow-on

- [Capture rule comments at parse time](31-capture-rule-comments-at-parse-time.md) — implement capture-not-discard; refactor passes 19–22 / 21.

## Amendment (grill 76, 2026-08-18)

Extraction **order** only: the first `;` on the working line is peeled **before** `extract_rule_parts` / chain split ([76](76-grill-double-semicolon-rule-comment-delimiter.md), implement [77](77-implement-first-semicolon-comment-cut.md)). Schema, capture-not-discard, and “do not emit `comment` into ASCA” are unchanged. Detectors still do not scan **rule comment**; uncertainty keywords belong before `;`.

## Comments

- 2026-08-18: Grill 76 amended pass order (see **Amendment** above).
