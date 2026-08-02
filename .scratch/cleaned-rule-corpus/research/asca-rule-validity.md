# What counts as a valid ASCA rule string?

Primary sources (verified against local install **asca 0.10.2**):

- Docs: [asca-rust `doc/doc.md`](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md), [`doc/doc-cli.md`](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc-cli.md)
- Crate source: cargo registry `asca-0.10.2` (`~/.cargo/registry/src/…/asca-0.10.2/`) — especially `src/lib.rs`, `src/rule/{lexer,parser,mod,rule_repr}.rs`, `src/error/{syntax,runtime}.rs`, `CHANGELOG.md`
- CLI: `asca --version` → `0.10.2`

Context7: **not indexed** for asca / asca-rust.

Earlier inventory work used **0.9.3**; see §7 for breaking changes that affect validity/matching.

---

## 1. Whole-rule syntax

A rule has up to four parts:

| Part | Role |
|------|------|
| **input** | content to transform |
| **output** | result of the transformation |
| **context** (environment) | where the change applies |
| **exception** | where the change must *not* apply |

Form (parser grammar in `Parser::rule`, `src/rule/parser.rs`):

```text
input ARROW output [/ context] [PIPE exception]
```

- **ARROW**: `>`, `->`, `=>` (LTR). RTL: `~` or `~>` ([True Right-to-left Propagation](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#true-right-to-left-propagation)).
- **PIPE** (exception): `|` or `//` — both lex to `TokenKind::Pipe` ([The Basics](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#the-basics); `lexer.rs`).
- Context after `/` may be omitted; empty `/` / trailing separator with no env is **invalid** (`EmptyEnv`).
- Exception may be omitted. `| _` is *not* the same as omitted (except everywhere).

**Comments:** `;;` to end of line (`MalformedComment` if a lone `;`).

**Condensed rules:** comma-join parallel parts: `a, u > e, y / #_, _#`. Lengths must match or one side singleton (`UnbalancedRuleIO` / `UnbalancedRuleEnv` at split-into-subrules time).

**CLI file wrapper (`.rsca`):** `@ Title`, indented rule lines, `#` description lines ([Rule file](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc-cli.md#rule-file-rsca)). File splitting is `parse_rsca` (`src/cli/parse.rs`) — it does **not** validate rule strings; that happens later in the rule lexer/parser.

---

## 2. Validity checklist by field

### Input

- [ ] Non-empty. Empty input → insertion; use `*` or `∅` **alone** (`EmptyInput` / `InsertErr`).
- [ ] No bare word boundary `#` in I/O (`WordBoundLoc`).
- [ ] IPA / groups / matrices / sets / structures / refs / ellipses as documented — not prose.
- [ ] Word-only romanisation aliases must not be used as IPA inside rules; letters like `S` are **groupings** ([Inbuilt Aliases](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#inbuilt-aliases)).
- [ ] Negation (`-` / `¬`) allowed on segment/matrix/group/ref in **input and env** (0.10.1+); not in output (`BadNegation` / `BadNegationOutput`).

### Output

- [ ] Non-empty. Empty output → deletion; use `*` or `∅` **alone** (`EmptyOutput` / `DeleteErr`).
- [ ] Metathesis: output is **only** `&` (reverse) or `@` (ordered metathesis, 0.10+) (`MetathErr`).
- [ ] Cannot be both insert+delete (`* > *` / `∅ > ∅`) or insert+metathesis (`InsertDelete` / `InsertMetath`) — checked in `Rule::split_into_subrules`.
- [ ] Output-only set without matching input set is invalid (runtime `LonelySet` / similar).
- [ ] Paired sets: same cardinality; sets non-empty; **no nested `{}` of same type** (`NestedBrackets` at lex time).
- [ ] Optionals `(…)` are **env/structure only** — not in input/output (`OptLocError`).

### Environment (context)

- [ ] Exactly one focus: one `_` or joined `___` — not spaced `_ _` (`TooManyUnderlines`). Underline may sit **inside** a structure (`<(..)_>`, 0.10+; `TooManyUnderlinesStruct` if multiple).
- [ ] If `/` is present, environment must not be empty (`EmptyEnv`).
- [ ] `#` only at periphery of env; at most one `#` per side (`StuffBeforeWordBound` / `StuffAfterWordBound` / `TooManyWordBoundaries`). Boundaries also allowed at structure periphery (0.10.1+).
- [ ] Env shorthand `_,#` ≡ `#_, _#`.
- [ ] Multi-env: env set `:{ … }:` ([Environment Sets](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#environment-sets)). Env-set insertion still constrained at runtime.

### Exception

- [ ] Same env grammar as context.
- [ ] Introduced by `|` or `//`.
- [ ] Omitting exception ≠ `| _`.

---

## 3. Important operators / features

| Construct | Syntax | Notes | Source |
|-----------|--------|-------|--------|
| Deletion / insertion | `*` or `∅` alone in I or O | Not omit blank sides | docs + `EmptySet` token |
| Metathesis | O = `&` or `@` | `@` keeps grouped ellipsis order (0.10) | CHANGELOG 0.10.0 |
| Ellipsis | `..` / `...` / `…`; optional `(..)` | Groups for metathesis in 0.10 | docs + lexer |
| Word / syll / phrase bound | `#` `$` `%` `##` | `#` mostly env; `%` syllable | docs |
| Feature matrix | `[+cons, -son]` | Commas preferred; parser is lenient on commas | `get_param_args` |
| Segment+matrix | `a:[-stress]` | Colon joins | docs |
| Any segment | `[]` | Wildcard | docs |
| Groupings | `C O S P F L N G V` (+ aliases) | **`C` = `[+cons,-syll]` since 0.10** (was `[-syll]`); glides ∉ `C` | CHANGELOG |
| Sets | `{p,t,k}`, multi-item choices, `{i,u}:[+long]` | No nest same brackets; commas required | 0.10 set rework |
| Optionals | `(C)`, `(C,3:5)`, `(C,0)` | Env/struct only | `OptLocError` |
| References | `V=1` … `1` | Not on IPA literals | `IPACannotBeRefd` |
| Negation | `-` / `¬` | Input/env (0.10.1+) | CHANGELOG |
| Structures | `<…>` / `⟨…⟩` | May contain `_` | docs |
| Alpha / combined supras | `α…` / `A…Z`; `[A length]`, `[A anystress]` | 0.10 combined length/stress | CHANGELOG |

---

## 4. How to validate a single rule (CLI / library)

**No dedicated `validate` subcommand** — CLI has `run`, `seq`, `conv`, and (0.10.2) `trace`.

### Parse-only (preferred for syntax)

Public library path (exact parity with internal tests):

```rust
use asca::rule::{RuleGroup, ParsedRules};

let groups = vec![RuleGroup {
    name: "check".into(),
    rule: vec!["YOUR_RULE_HERE".into()],
    description: String::new(),
}];
let _parsed = ParsedRules::try_from(groups.as_slice())?; // Err(RuleSyntaxError)
```

Per-line (same as `src/rule/tests`):

```rust
Lexer::new(&line.chars().collect::<Vec<_>>(), group_idx, line_idx).get_line()?;
Parser::new(tokens, group_idx, line_idx).parse()?; // Ok(None) = blank/comment-only
```

`parse_rsca` only splits `@` / `#` / rule lines — **not** a syntax check.

### Practical CLI check (`run` / `trace`)

```bash
asca run words.wsca --rules rule.rsca
# or
asca trace <WORD> -r rule.rsca
```

- Syntax/runtime failures → non-zero; `Syntax Error:` / `Runtime Error:` on stderr.
- Success prints output (even if unchanged).
- Project: `conlanger.utils.run_asca` wraps `~/.cargo/bin/asca run …`.

**Caveat:** `run` also parses words and applies rules, so failures can be word/alias/runtime — not only rule syntax. Prefer `ParsedRules::try_from` (or a thin wrapper) for syntax-only validation.

### Structural checks that need apply boundary

`Rule::split_into_subrules` (`src/rule/mod.rs`, `pub(crate)`) runs at **first apply**, not inside `Parser::parse()`. It rejects unbalanced condensed I/O/env and `InsertDelete` / `InsertMetath`. A Python validator that only mirrors lexer+parser will miss these unless it ports that function or applies via ASCA.

---

## 5. Internal parse / validation pipeline (basis for Python)

This section is the implementation map for a Python ASCA validator. Source: **asca 0.10.2** crate.

### 5.1 Pipeline

```text
.rsca / RuleGroup { name, rule: Vec<String>, description }
        │
        ▼  (per group, per line — parallel_parse_rule_groups in lib.rs)
   Lexer::get_line()  →  Vec<Token>                 src/rule/lexer.rs
        │
        ▼
   Parser::parse()    →  Option<Rule>               src/rule/parser.rs
        │                  (None = blank / comment-only)
        ▼
   ParsedRules { names, rules: Vec<Vec<Rule>>, descs }
        │
        ▼  (first apply only)
   Rule::split_into_subrules() → Vec<SubRule>       src/rule/mod.rs
        │                  + RuleType inference
        ▼
   SubRule::apply() → Phrase                        src/rule/subrule/*
                       + RuleRuntimeError
```

Orchestration:

| Step | API | File |
|------|-----|------|
| File → groups | `parse_rsca` | `src/cli/parse.rs` |
| Groups → rules | `ParsedRules::try_from` → `parallel_parse_rule_groups` | `rule_repr.rs`, `lib.rs` |
| Apply | `ParsedRules::apply` / `Rule::apply` | `rule_repr.rs`, `rule/mod.rs` |

### 5.2 Stages a Python validator should mirror

**Tier 1 — Lexer (`src/rule/lexer.rs`)**  
Tokenise with bracket-nesting state (`inside_matrix`, `inside_option`, `inside_set`, `inside_env_set`, …). Reject e.g. `NestedBrackets`, `UnknownCharacter`, `MalformedComment`, `UnknownFeature` (+ Levenshtein hint), `ExpectedAlphabetic`, tone/binary feature misuse. IPA via `cardinals.json` trie; diacritics via `diacritics.json`. Accept `//`→pipe, arrow spellings, ellipsis forms, Americanist aliases.

**Tier 2 — Parser (`src/rule/parser.rs`)**  
Recursive descent: `rule` ← `get_input` + arrow + `get_output` + optional `get_context_block` + optional `get_except_block`. Build `ParseItem` / `ParseElement` trees. Reject field-level errors from §2 (`EmptyInput`, `WordBoundLoc`, `EmptyEnv`, `TooManyUnderlines`, `MetathErr`, `OptLocError`, `UnknownIPA`, set/matrix/structure errors, …). ~50+ `RuleSyntaxError` variants in `src/error/syntax.rs`.

**Tier 3 — Split-into-subrules (`src/rule/mod.rs`)**  
Without words: `UnbalancedRuleIO`, `UnbalancedRuleEnv`, `InsertDelete`, `InsertMetath`.

**Tier 4 — Runtime (`src/error/runtime.rs` + `subrule/*`)**  
Needs apply (or a large static walk): lonely/uneven sets, insertion-must-have-env, alpha/ref unknowns, deletion edge cases, infinite-loop detection, structure nesting, etc. **Not** all catchable by parse-only APIs.

### 5.3 Recommended strategy for this repo

| Approach | Use when |
|----------|----------|
| Drive **`ParsedRules::try_from`** (PyO3 / small Rust helper / wasm) | Want exact syntax parity with 0.10.2 |
| Port Tier 1–2 (+ optionally Tier 3) in pure Python | Offline / no native dep; must ship cardinal/diacritic tables and track ASCA upgrades |
| Shell `asca run` / `asca trace` on dummy words | Catch some Tier 4; slower; conflates word errors |
| **Hybrid (preferred default)** | Tier 1–3 via parse API or faithful port; optional ASCA apply for Tier 4 |

Do **not** re-implement the full grammar from docs alone — follow the crate pipeline and error enum names so messages stay mappable to `RuleSyntaxError` / `RuleRuntimeError`.

Public Rust modules to wrap or mirror:

```text
asca::rule::{RuleGroup, ParsedRules, Rule, Lexer, Parser, …}
asca::error::{RuleSyntaxError, RuleRuntimeError, ASCAError}
```

---

## 6. Common invalid patterns (Index Diachronica → ASCA)

Drawn from docs + observed failures (`notebooks/data/asca_errors.csv`; classify against §2). Re-verify under **0.10.2** when inventoring — set/metathesis/`C` semantics changed in 0.10.0.

| Pattern | Why invalid / fix direction |
|---------|-----------------------------|
| Nested sets `{{a,b}, c}` | `NestedBrackets` — flatten / rewrite |
| Prose in `/ …` | Env must be phonological with `_` |
| Blank I/O (`> x`, `x >`) | Use `*`/`∅` |
| `0` / `_` as zero (SCA²/ID habits) | Use `*` or `∅` |
| Category defs `// C = {…}` | Not ASCA rule syntax |
| Unknown features (`dental`, `palatal`, …) | ASCA feature names/shorthands |
| Matrix without host (`S > :[+voice]`) | `S:[+voice]` |
| Env-set punctuation mangled | `:{ a_, b_ }:` with `_` each |
| `#` then material after word end | `StuffAfterWordBound` |
| Trailing junk / missing arrow | `ExpectedArrow` / `ExpectedEndLine` |
| Word-alias capitals as IPA | Expand IPA or use features/groups |
| Unequal set sizes / output-only sets | Align or drop (often runtime) |
| Expecting old `C` = all non-syllabics | Since 0.10 use `{C,G}` or `[-syll]` to include glides |

---

## 7. Notable changes since 0.9.3 (validity-relevant)

From `CHANGELOG.md` in the 0.10.2 crate (0.9.3 source not kept in local registry):

| Version | Change |
|---------|--------|
| **0.10.0** | `C` → `[+cons,-syll]`; glottalics `[+cons]`; IPA subst preserves length; set rework; `@` metathesis; underline-in-structure; combined length/stress alphas |
| **0.10.1** | Negation in input/env; boundaries at structure periphery |
| **0.10.2** | New CLI `trace`; runtime fix for RHS boundary in underline structures (no new syntax) |

Pin validator behaviour and fixtures to **0.10.2** (current install). Re-check if the project upgrades ASCA again.

---

## 8. Source index

| Claim area | Path / URL |
|------------|------------|
| User-facing rule docs | https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md |
| CLI / `.rsca` / `run` / `trace` | https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc-cli.md |
| Version / changelog | crate `Cargo.toml`, `CHANGELOG.md` |
| Parse orchestration | `src/lib.rs` (`parse_rule_groups`, `parallel_parse_rule_groups`, `run_unparsed`) |
| Parse-only entry | `src/rule/rule_repr.rs` (`ParsedRules::try_from`) |
| Lexer / tokens | `src/rule/lexer.rs` |
| Parser / AST | `src/rule/parser.rs` |
| Split / RuleType | `src/rule/mod.rs` (`split_into_subrules`) |
| Syntax errors | `src/error/syntax.rs` (`RuleSyntaxError`) |
| Runtime errors | `src/error/runtime.rs` (`RuleRuntimeError`) |
| `.rsca` split only | `src/cli/parse.rs` |
| IPA / diacritics tables | `src/cardinals.json`, `src/diacritics.json` |
