Type: task
Status: ready-for-agent
Blocked by: 89

# Missing-arrow lines: `stages: ["text"]`; compile without output

Grill 2026-08-21 Q6: If the Index line has **no `→`**, parse still emits a index rule. **`stages`** is a one-element list: the text that can be parsed **before** env, exception, or **rule comment**. Compile treats that as input and **deals with the missing output** (empty output), so ASCA **compile validation** can fail in the open. These rules are **not** skipped unless they are also in `skip_rules` ([ticket 89](89-unify-status-skipped.md)). Glossary: `CONTEXT.md` (**Stages**).

## What to build

### Parse

- After comment peel and env/exception isolation, if there is no `→`: `stages: ["<pre-env text>"]` (stripped working remainder before `/` env, `!`/`except`/second-`/` exception, already-peeled comment).
- Do **not** use `status: skipped` for this case.
- Keep `raw` / `source` / `rule_id` / optional `env` / `exception` / `comment` as for any other rule.

### Compile

- `len(stages) == 1` → one `SoundChangeRule` with `input` = that string and `output` = `""` (or equivalent). Do not omit the rule; do not require a second stage.
- Emit a normal (non-comment) ASCA line so `validate_asca` / inventory see the failure.

### Tests

- HTML/`schg` line with no arrow, optional env/exception/comment → `stages` length 1, no `status`.
- `DiachronicSeries` / inventory: compiles; `validate_asca` fails (empty output / unbalanced I/O is expected).

## Out of scope

- Changing `skip_rules` / `skip_sections` policy ([ticket 89](89-unify-status-skipped.md))
- Pydantic rewrite ([ticket 93](93-pydantic-compile-refactor.md))

## Acceptance criteria

- [ ] No-arrow parse emits `stages: ["text"]` without `status: skipped`
- [ ] Compile produces a real rule with empty output; inventory records an ASCA failure, not omit/skip
- [ ] Full gate: `uv run pytest`; `uv run ruff check --fix`; `uv run ruff format && uv run ruff format --check src`
