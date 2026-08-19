# Effort to add native ASCA rule (and per-field) validation

Spike for [ticket 86](../issues/86-spike-asca-native-per-field-validation.md).  
**ASCA version:** 0.10.2 (local crate `~/.cargo/registry/src/…/asca-0.10.2/`, `asca --version`).  
**Context7:** asca / asca-rust not indexed — claims cite crate source, CLI docs, GitHub.

Recovers and extends the 2026-08-04 wayfinder discussion: validation is staged; `asca run` is word-dependent at Tier 4; `ParsedRules::try_from` exists but there is no `validate` CLI.

Related: [asca-rule-validity.md](asca-rule-validity.md), [field-isolation-compile-validation.md](field-isolation-compile-validation.md), [Field-isolation inventory sidecar](../issues/36-field-isolation-inventory-sidecar.md).

---

## 1. Executive summary

**Native per-field validation is a small-to-medium asca change, not a parser rewrite.** The four field grammars already exist as private methods on `Parser`. What is missing is a public “check without applying” surface — library + CLI — that can call those methods on a fragment and stop at EOL.

| Slice | Private fork (working) | Upstream-ready PR |
|-------|------------------------:|------------------:|
| Whole-rule `asca validate` wrapping existing `ParsedRules::try_from` | **½–1 day** | **1–2 days** |
| Word-independent structural check (`split_into_subrules` without leaking AST) | **+2–4 h** | **+½ day** |
| Per-field library API (`input` / `output` / `env` / `exception`) | **1–2 days** | **2–4 days** |
| CLI `--field` / stdin | **+2–4 h** | **+½ day** |
| Optional wasm `validate` for asca-web | **+½–1 day** | **+1–2 days** |
| **Total for “validate rules, and each section independently”** | **~2–5 focused days** | **~1–2 weeks** (docs, tests, changelog) |

This is cheaper than ticket 36’s stub sidecar **in semantic quality**, and similar or slightly more in calendar time if you include Python inventory wiring. It does **not** replace whole-rule `ok`: cross-field / match-dependent errors (`UnevenSet`, `LonelySet`, `InsertionNoEnv`, `UnbalancedRuleIO`) stay whole-rule. Native field checks **avoid** the stub false-fails that made spike 35 “go-with-limits”.

**Upstream interest:** plausible. No open “validate” issue today; the maintainer recently added `trace` as a similar CLI increment; asca-web would benefit from parse-without-apply. Per-field is a linter/editor feature — useful to them, not only to this corpus.

---

## 2. What already exists (0.10.2)

### 2.1 Pipeline (unchanged from [asca-rule-validity.md](asca-rule-validity.md) §5)

```text
RuleGroup.rule: Vec<String>
        │
        ▼  Lexer::get_line()          pub(crate)   src/rule/lexer.rs
        ▼  Parser::parse() → Rule     pub(crate)   src/rule/parser.rs
        ▼  ParsedRules::try_from      **public**   src/rule/rule_repr.rs
        ▼  Rule::split_into_subrules  pub(crate)   first apply, no words
        ▼  SubRule::apply             runtime, **match-dependent**
```

CLI 0.10.2: `run`, `seq`, `conv`, `trace`. **No `validate`.** Confirmed in `src/cli/args.rs` and `src/main.rs`. GitHub issue search for “validate” returns nothing relevant ([issue #8](https://github.com/Girv98/asca-rust/issues/8) is rule-*file* syntax, not rule-string checking).

### 2.2 The public parse-only door

`ParsedRules::try_from(&[RuleGroup])` already runs lexer+parser (Tiers 1–2) with **no words**. That is the “internal check” recalled in the Aug 4 session. It is library-only; the CLI never exposes it. Ticket [Create an ASCA validator for DiachronicSeries](../issues/08-asca-validator.md) tried a thin Rust helper, hit crates.io network, and shipped `asca run` + probe words instead.

`Lexer` / `Parser` / `Rule::split_into_subrules` are `pub(crate)`. External crates cannot call field getters without a fork or a new public API.

### 2.3 Field parsers already exist

`Parser::rule` is literally four steps (`src/rule/parser.rs`):

```text
Rule ← Input Arrow Output ContBlock? ExptBlock? Terminal
```

| Method | Visibility | Field | Stop tokens today |
|--------|------------|-------|-------------------|
| `get_input` | private | input | comma-separated terms; leftover is arrow / reverse |
| `get_output` | private | output | comma-separated; leftover slash / pipe / EOL / comment |
| `get_context_block` | private | env | eats `/` then `get_env_expr` |
| `get_except_block` | private | exception | eats `\|` then **the same** `get_env_expr` |
| `get_env_expr` | private | env grammar | env-set `:{…}:` or comma-joined envs with `_` |

Env and exception share one grammar. Independent exception validation is independent env validation with a different introducer.

Field-specific errors are already distinct (examples from `src/error/syntax.rs`): `EmptyInput`, `EmptyOutput`, `EmptyEnv`, `WordBoundLoc`, `OptLocError`, `BadNegationOutput`, `ExpectedUnderline`, `InsertErr` / `DeleteErr` / `MetathErr`. Lexer-time errors (`UnknownCharacter`, `UnknownFeature`, `NestedBrackets`) are field-agnostic and still useful in isolation.

The parser **defers** set cardinality to apply:

```1452:1455:src/rule/parser.rs (asca 0.10.2)
    fn get_output_el(...) {
        // NOTE: a set in the output only makes sense when matched to a set in the input
        // w/ the same # of elements. This will be validated when applying
```

So a native `validate_output("{b,d,g}")` would **pass syntax** — which is the correct isolated answer. Stub isolation **false-fails** that case (spike 35 §5).

### 2.4 Word dependence (lost Aug 4 finding, restated)

| Tier | When | Words needed? |
|------|------|----------------|
| 1–2 lexer/parser | `ParsedRules::try_from` | **No** |
| 3 `split_into_subrules` | first `Rule::apply` | **No** (but currently only reached via apply) |
| 4 runtime (`UnevenSet`, `LonelySet`, `InsertionNoEnv`, `DeletionOnlySeg`, …) | **on match** | **Yes** |

`asca run` therefore cannot prove a rule valid; it can only fail. That is why [Rule-derived probe synthesis](../issues/10-rule-derived-probe-synthesis.md) was considered and later **wontfix**, and why spike 35 stayed inside the baseline wordlist.

Native validation of Tiers 1–3 **closes the “no CLI validate” gap** without reviving probe synthesis. It does **not** close Tier 4.

---

## 3. What to add (recommended design)

Keep Lexer/Parser crate-private. Add a small public façade so neither asca-web nor this repo has to reconstruct fake whole rules.

### 3.1 Library (core)

```rust
pub enum RulePart { Input, Output, Environment, Exception }

pub fn parse_rules(groups: &[RuleGroup]) -> Result<ParsedRules, RuleSyntaxError>;
// already: ParsedRules::try_from

impl ParsedRules {
    /// Tier 3 without words. Do not return SubRule; just Result<(), RuleSyntaxError>.
    pub fn check_structure(&self) -> Result<(), RuleSyntaxError>;
}

pub fn validate_part(part: RulePart, fragment: &str) -> Result<(), RuleSyntaxError>;
```

`validate_part` implementation sketch (all inside the crate):

1. `Lexer::new(fragment.chars(), 0, 0).get_line()?`
2. `Parser::new(tokens, 0, 0)`
3. Dispatch:
   - Input → `get_input()` then expect EOL/comment (do **not** require an arrow)
   - Output → `get_output()` then expect EOL
   - Environment / Exception → `get_env_expr()` **without** requiring `/` or `|` (those are whole-rule introducers; corpus fields are stored without them)
4. Reject leftover tokens with `ExpectedEndLine`

Tiny glue; the grammar stays where it is. Need a few terminator tweaks so `get_input` treats EOL as a successful end (it already breaks on non-comma leftover when the term is non-empty). Empty fragment → existing `EmptyInput` / `EmptyOutput` / `EmptyEnv`.

### 3.2 CLI (pattern: `trace`)

`trace` is the template: new `AscaCommand` variant, ~70-line `src/cli/trace.rs`, three-line `main.rs` match, clap help, `doc/doc-cli.md` section. `validate` would be the same size or smaller (no words, no alias).

Suggested UX:

```text
asca validate -r rules.rsca          # whole file, exit 0/1, Syntax Error: … on stderr
asca validate --rule 'p > e / #_'    # one line, no .rsca wrapper (avoids # description hazard)
asca validate --field env '#_'
```

Exit codes matching `run` keep Python `validate_asca` as a thin subprocess wrapper.

### 3.3 What **not** to do

- **Do not** reimplement the grammar.
- **Do not** make every `RuleSyntaxError` variant carry a `Field` enum unless upstream wants it — independent `validate_part` already attributes the field by which API was called. Whole-rule errors still have token `Position` (line/column) for caret display.
- **Do not** claim per-field runtime completeness. Sets, condensed balance, insertion+env coupling remain whole-rule (same honest limit as spike 35, without the false-fail tax).

---

## 4. Comparison with ticket 36 (stub sidecar)

| | Stub sidecar (ticket 36 as written) | Native asca per-field |
|--|-------------------------------------|------------------------|
| Mechanism | Real field + canned stubs → `asca run` + probe words | Fragment → existing field parser |
| Tiers | 1–4 sampled (word-dependent) | 1–2 reliably; 3 on whole-rule `check_structure`; 4 still whole-rule |
| False fail | Lonely set, deletion vs lexicon, `#` `.rsca` comment, insert env | **None of those** (no stubs, no words, no `.rsca` `#` wrap) |
| False pass | Cross-field (uneven sets, unbalanced I/O, insert+env) | Same class — still need whole-rule |
| Cost in this repo | Python stub table + 4× `asca run` per fail | Switch `validate_asca` / sidecar to `asca validate`; drop stub table |
| Cost in asca | Zero | 2–5 days fork / 1–2 weeks PR |
| Ongoing | Stub heuristics bit-rot as ASCA grammar grows | Stays in lockstep with asca parser |

If native per-field lands, ticket 36 **rewrites** to “call asca per field, write sidecar CSV + `blame`” — the inventory artifact stays; the stub engine goes away.

If only whole-rule `asca validate` lands, ticket 36 stubs **remain** the only field-blame tool, but whole-rule inventory can drop probe-word dependence for Tiers 1–3.

---

## 5. Fork vs upstream

**License:** GPL-3.0-only. A private fork is legally fine; cargo `[patch]` / path dep / `cargo install --path` are the integration options. Rebase cost on each asca minor is real (0.10.0 already broke `C`, sets, metathesis).

**Maintainer fit:** James Girv (`Girv98`) asks for user-facing CLI/lib features (issue #8 “always looking for feedback”; 0.10.2 added `trace` in ~100 lines). A `validate` command is the obvious sibling of `run`/`trace`. Per-field is slightly more “tooling/LSP/web editor” — still in character for asca-web (`run_wasm` already exists in `lib.rs`; a `validate_wasm` would be a thin extra).

**Suggested sequence if both matter:**

1. Fork off 0.10.2, implement library + CLI, point this repo at it.
2. Open an upstream issue (problem: no parse-only check; CLI users must supply words; editors cannot lint a field) with a sketch PR.
3. Keep the fork until it merges; then unpin.

Do not wait on merge to decide ticket 36 — calendar of a volunteer maintainer is the slow variable, not the code.

---

## 6. Worked file list (asca)

Whole-rule CLI + `check_structure`:

- `src/rule/rule_repr.rs` — `ParsedRules::check_structure`
- `src/rule/mod.rs` — call `split_into_subrules` from that method (keep `SubRule` private)
- `src/cli/args.rs`, `src/cli/validate.rs` (new), `src/cli/mod.rs`, `src/main.rs`
- `doc/doc-cli.md`, `CHANGELOG.md`
- tests: wrap existing `src/rule/tests` invalid cases + a few `UnbalancedRuleIO` lines

Per-field additionally:

- `src/rule/parser.rs` — `pub(crate)` wrappers around `get_input` / `get_output` / `get_env_expr` that expect EOL
- `src/lib.rs` or `src/rule/mod.rs` — `validate_part`
- tests per field: unknown char/feature, `OptLocError` on I/O, `WordBoundLoc` on I/O, missing `_` on env, `BadNegationOutput`, empty sides
- CLI `--field`

No change required in `subrule/*` unless you also want a static walk for lonely/uneven sets without matching — that is a **different**, larger ticket (and overlaps ticket 10’s wontfix).

---

## 7. Recommendation

**Build the asca façade (library `validate_part` + whole-rule `validate` / `check_structure` + CLI).** It is the right layer for field blame, it is sized to one focused week even as an upstream PR, and it is the kind of feature asca already ships (`trace`).

For **this map:** treat ticket 36’s stub engine as the fallback if asca work is declined; if asca work is accepted, retarget 36 at the sidecar CSV only.

Do **not** use native validation as an excuse to revive probe synthesis.

---

## 8. Sources

| Claim | Source |
|-------|--------|
| No validate CLI; commands `run`/`seq`/`conv`/`trace` | asca 0.10.2 `src/cli/args.rs`, `src/main.rs`, `doc/doc-cli.md` |
| `ParsedRules::try_from` is public parse-only | `src/rule/rule_repr.rs` |
| Lexer/Parser/`split_into_subrules` are `pub(crate)` | `src/rule/{lexer,parser,mod}.rs` |
| `Parser::rule` = input → arrow → output → context? → except? | `src/rule/parser.rs` ~1586–1616 |
| Env and exception share `get_env_expr` | `parser.rs` ~710–717 |
| Set cardinality deferred to apply | `parser.rs` `get_output_el` comment |
| `split_into_subrules` is word-independent | `src/rule/mod.rs` ~111–188, called from `apply` ~210 |
| Runtime errors on match | `src/error/runtime.rs`; `subrule/mod.rs` (Aug 4 trace) |
| `trace` CLI size as precedent | commit [58407be](https://github.com/Girv98/asca-rust/commit/58407be7ee46cf43b0d3031c75907dfdbb621d0b) |
| No existing validate issue | GitHub search 2026-08-19 |
| License / crate layout | `Cargo.toml` GPL-3.0-only, lib+bin+cdylib |
| Stub limits | [field-isolation-compile-validation.md](field-isolation-compile-validation.md) §5 |
| Current Python path | `src/conlanger/appliers/asca.py` (`asca run` + probe `.wsca`) |
