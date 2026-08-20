Type: task
Status: done
Blocked by: 86

# Implement `validate` + `validate_part` on the private asca fork

## Question

Add parse-only whole-rule validation and independent field validation to the **private** asca-rust fork so this corpus can blame `input` / `output` / `env` / `exception` without stub rules.

## Repo

Work in **`/home/pappa/Projects/Pappa/asca-rust`** (`github.com/Pappa/asca-rust`), not this conlanger tree. Base: vanilla **0.10.2** (`36c3c62`). **Do not** open an upstream PR (grill 2026-08-19 Q2 C).

Design: [research/asca-native-per-field-validation.md](../research/asca-native-per-field-validation.md) §3. Spike: [Native ASCA per-field validation effort](86-spike-asca-native-per-field-validation.md).

## Version string (asca-rust convention)

Upstream does **not** use git-describe (`0.10.2-dev-36c3c62`) or a dropped leading `0`. Releases are **identical** `x.y.z` in `Cargo.toml`, git tag, GitHub release title, and CHANGELOG heading (e.g. `0.10.2`). Release tags must match `[0-9]+.[0-9]+.[0-9]+` (`.github/workflows/release.yml`).

For this fork:

- While the feature is in progress: Cargo pre-release **`0.10.3-dev`** so `asca --version` is distinguishable from crates.io `0.10.2`. (`-dev` is Cargo/semver, not something upstream publishes.)
- When this ticket is done: bump **`Cargo.toml` + CHANGELOG to `0.10.3`** (next patch slot) with a changelog entry for `validate`. Do not invent `0.10.2-pappa` or hash suffixes.

## What to build

Keep `Lexer` / `Parser` / `SubRule` crate-private. Façade only.

### Library

- `ParsedRules::check_structure(&self) -> Result<(), RuleSyntaxError>` — call existing `split_into_subrules` per rule; do not leak AST.
- `pub enum RulePart { Input, Output, Environment, Exception }`
- `pub fn validate_part(part: RulePart, fragment: &str) -> Result<(), RuleSyntaxError>`
  - Lex the fragment; dispatch to existing `get_input` / `get_output` / `get_env_expr`.
  - Env and exception share grammar; **do not** require a leading `/` or `|` (corpus fields are stored without introducers).
  - Expect EOL/comment after the field; leftover → `ExpectedEndLine`.
- Whole-rule parse stays `ParsedRules::try_from` (already public).

### CLI (mirror `trace`)

```text
asca validate -r rules.rsca
asca validate --rule 'p > e / #_'
asca validate --field env '#_'
```

Exit 0 on success; non-zero + existing `Syntax Error:` formatting on failure. No words, no alias, no apply.

### Tests + docs

- Invalid-field cases from [asca-rule-validity.md](../research/asca-rule-validity.md) §2 (unknown char/feature, `OptLocError` on I/O, `WordBoundLoc` on I/O, missing `_` on env, `BadNegationOutput`, empty sides).
- Whole-rule: `UnbalancedRuleIO` / `InsertDelete` via `check_structure`.
- `doc/doc-cli.md` + CHANGELOG.

## Out of scope

- Upstream PR / asca-web wasm
- Probe-word / runtime (Tier 4) completeness
- Changing conlanger (that is [Wire conlanger to forked asca validate](88-wire-conlanger-forked-asca-validate.md))

## Acceptance criteria

- [x] `asca validate` checks a `.rsca` / one `--rule` without words
- [x] `validate_part` (and `--field`) for input, output, env, exception
- [x] `check_structure` covers Tier 3 without applying
- [x] Version `0.10.3-dev` during work; `0.10.3` + CHANGELOG when done
- [x] Tests for the cases above; CLI help matches `trace` quality
