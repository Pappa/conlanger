# What counts as a valid ASCA rule string?

Primary sources: [asca-rust `doc/doc.md`](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md), [`doc/doc-cli.md`](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc-cli.md), and asca crate source (installed CLI `asca 0.9.3`: `src/error/syntax.rs`, `src/rule/lexer.rs`, `src/lib.rs`).  
Context7: **not indexed** for asca / asca-rust (resolve-library-id returned unrelated hits).

---

## 1. Whole-rule syntax

A rule has up to four parts:

| Part | Role |
|------|------|
| **input** | content to transform |
| **output** | result of the transformation |
| **context** (environment) | where the change applies |
| **exception** | where the change must *not* apply |

Form:

```text
input ARROW output / context PIPE exception
```

- **ARROW**: `>`, `->`, `=>` (LTR). RTL: `~` or `~>` ([True Right-to-left Propagation](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#true-right-to-left-propagation)).
- **PIPE** (exception): `|` or `//` ([The Basics](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#the-basics)).
- Context after `/` may be omitted; empty `/` / trailing separator with no env is **invalid**.
- Exception may be omitted. An empty-looking exception like `| _` is *not* the same as omitted (means “except everywhere”) — see HEAD docs under The Basics.

**Comments:** `;;` to end of line ([Single Line Comments](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#single-line-comments)).

**Condensed rules:** comma-join parallel parts: `a, u > e, y / #_, _#`. Part lists must be same length **or** one singleton side ([Condensed Rules](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#condensed-rules)).

**CLI file wrapper (`.rsca`):** `@ Title`, indented rule lines, `#` description lines ([Rule file](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc-cli.md#rule-file-rsca)). The rule *string* itself is the indented line.

---

## 2. Validity checklist by field

### Input

- [ ] Non-empty. Empty input → insertion; use `*` or `∅` **alone** ([Insertion and Deletion](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#insertion-and-deletion-rules); `EmptyInput` / `InsertErr` in `syntax.rs`).
- [ ] No bare word boundary `#` in I/O (`WordBoundLoc`: “Wordboundaries are not allowed in the input or output”). `#` / `##` belong in environments (or `##` for cross-word ops — [Special Characters](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#special-characters), [Cross Word-Boundary](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#cross-word-boundary-operations)).
- [ ] IPA / groups / matrices / sets / structures / refs / ellipses as documented — not prose.
- [ ] Word-only romanisation aliases (`S→ʃ`, `Z→ʒ`, …) **must not** be used as IPA inside rules; in rules those letters are **groupings** (Sonorant, etc.) ([Inbuilt Aliases](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#inbuilt-aliases)).

### Output

- [ ] Non-empty. Empty output → deletion; use `*` or `∅` **alone** (`EmptyOutput` / `DeleteErr`).
- [ ] Metathesis: output is **only** `&` ([Metathesis Rules](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#metathesis-rules); `MetathErr`).
- [ ] Cannot be both insert+delete (`* > *` / `∅ > ∅`) or insert+metathesis (`InsertDelete` / `InsertMetath`).
- [ ] Output-only set without matching input set is invalid ([Sets](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#sets)).
- [ ] Paired sets: same cardinality; sets non-empty; **no nested `{}` of same type** (`NestedBrackets`).

### Environment (context)

- [ ] Exactly one focus marker: one `_` or a **joined** run `___` — not spaced `_ _` ([The Basics](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#the-basics); `TooManyUnderlines`).
- [ ] If `/` is present, environment must not be empty (`EmptyEnv` / `ExpectedUnderline`).
- [ ] `#` only at periphery of env; at most one `#` per side; no segments outside the word (`StuffBeforeWordBound` / `StuffAfterWordBound` / `TooManyWordBoundaries`).
- [ ] Env shorthand `_,#` ≡ `#_, _#`; cannot mix with other envs in the same condensed list ([Environment Shorthand](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#environment-shorthand)).
- [ ] Multi-env in one pass: env set `:{ … }:` (not plain `{…}`) ([Environment Sets](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#environment-sets)). Env sets **not** allowed in insertion rules yet (runtime error).

### Exception

- [ ] Same env grammar as context (must contain `_` focus when present).
- [ ] Introduced by `|` or `//`.
- [ ] Omitting exception ≠ `| _` (latter blocks everywhere).

---

## 3. Important operators / features

| Construct | Syntax | Notes | Source |
|-----------|--------|-------|--------|
| Deletion / insertion | `*` or `∅` alone in I or O | Not omit blank sides (≠ SCA²) | [Insertion/Deletion](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#insertion-and-deletion-rules) |
| Metathesis | O = `&` | Reverses matched input | [Metathesis](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#metathesis-rules) |
| Ellipsis | `..` / `...` / `…`; optional `(..)` | Long-range; bare `..` ≥1 segment | same + [Ellipses](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#ellipses) |
| Word / syll / phrase bound | `#` `$` `%` `##` | `#` env-only (mostly); `%` = syllable | [Special Characters](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#special-characters) |
| Feature matrix | `[+cons, -son]` | Comma-separated; shorthands OK; whitespace ignored | [Distinctive Features](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#using-distinctive-features) |
| Segment+matrix | `a:[-stress]` | Colon joins; `a[-stress]` = two segments | same |
| Any segment | `[]` | Wildcard | same |
| Groupings | `C O S P F L N G V` | Fixed classes; glides ≠ `C` | [Groupings](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#groupings) |
| Sets | `{p,t,k}` | Choice / parallel map; no nest | [Sets](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#sets) |
| Optionals | `(C)`, `(C,3:5)`, `(C,0)` | min:max; defaults 0…∞ | [Optionals](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#optionals) |
| References | `V=1` … `1` | Matrices/groups/syllables; not IPA literals | [References](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#references) |
| Negation | `-` / `¬` | On segment/matrix/group/ref | [Negation](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#negation) |
| Structures | `<…>` / `⟨…⟩` | Syllable shape; `_` inside for underline structures | [Syllable Structure Matching](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#syllable-structure-matching) |
| Alpha | `α`…`ω` or `A`…`Z` | Set in input/context before output | [Alpha Notation](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#alpha-notation) |
| Digraphs | `d͡ʒ` / `d^ʒ` | Tie/caret required | [IPA Characters](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#ipa-characters) |

---

## 4. How to validate a single rule (CLI / library)

**No dedicated `validate` subcommand** in CLI help (`run`, `seq`, `conv` only) — [`doc-cli.md` Usage](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc-cli.md#usage).

### Practical CLI check (documented `run`)

Minimal `.rsca` + dummy `.wsca`, then:

```bash
asca run words.wsca --rules rule.rsca
# or
asca run words.wsca -r rule.rsca
```

- Syntax/runtime failures exit non-zero with `Syntax Error:` / `Runtime Error:` on stderr.
- Success prints `OUTPUT` (even if the dummy word is unchanged).

Example `rule.rsca`:

```text
@ check
    YOUR_RULE_HERE
```

Example `words.wsca`:

```text
a
```

Project precedent: `conlanger.utils.run_asca` wraps `~/.cargo/bin/asca run … --rules …`.

Optional: `asca trace <WORD> -r rule.rsca` also loads/parses the rule file ([Trace](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc-cli.md#trace-command)).

### Library (asca crate)

- `asca::run_unparsed(&[RuleGroup], phrases, into, from)` parses then applies (`lib.rs`).
- `ParsedRules::try_from(Vec<RuleGroup>)` → parse-only path via `RuleSyntaxError` (`rule/rule_repr.rs`).
- Lexer tokens include `*` and `∅` as empty-set (`lexer.rs`).

---

## 5. Common invalid patterns (Index Diachronica → ASCA)

Drawn from docs + observed failures in repo `notebooks/data/asca_errors.csv` (empirical; classify against §2).

| Pattern | Why invalid / fix direction |
|---------|-----------------------------|
| Nested sets `{{a,b}, c}` | `NestedBrackets` — flatten / rewrite as condensed or multi-rule |
| Prose in `/ …` (“in certain contexts…”) | Env must be phonological with `_` |
| Blank I/O (`> x`, `x >`) | Use `*`/`∅` for insert/delete |
| `0` / `_` as zero (SCA²/ID habits) | Use `*` or `∅`, not digit `0` |
| Category defs `// C = {…}` | Not ASCA; use groupings/sets or expand |
| Unknown features (`dental`, `palatal`, typo `phargyn`) | Use ASCA feature names/shorthands ([Feature Shorthands](https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#feature-shorthands)) |
| Diacritic on illegal host (`tlʼ` as lateral+ejective host) | Affricate/tie or resegment |
| Matrix modifier without host (`S > :[+voice]`) | Need `S:[+voice]` (colon after segment/group) |
| Env set / set punctuation mangled | Use `:{ a_, b_ }:` correctly; each clause needs `_` |
| `#` then material after word end | `StuffAfterWordBound` |
| Env-set insertion `∅ > … / :{…}:` | Documented unsupported for insertion |
| Trailing comma in condensed envs | Unbalanced / expected `_` |
| Word-alias capitals as IPA in rules | `S`≠`ʃ` in rules — expand IPA or use features |
| Unequal set sizes / output-only sets | Align cardinalities or drop output set |

---

## 6. Source index

| Claim area | URL / path |
|------------|------------|
| Rule anatomy, env `_`, arrows, `|`/`//` | https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#the-basics |
| `*` / `∅` insert/delete | https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#insertion-and-deletion-rules |
| `&` metathesis, ellipsis | https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#metathesis-rules |
| `#` `$` `%` `##` | https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc.md#special-characters |
| Sets / env sets / optionals | `#sets`, `#environment-sets`, `#optionals` in same doc |
| Features / groupings / aliases | `#using-distinctive-features`, `#groupings`, `#inbuilt-aliases` |
| RTL `~` | `#true-right-to-left-propagation` |
| CLI `run` / `.rsca` | https://github.com/Girv98/asca-rust/blob/HEAD/doc/doc-cli.md |
| Error strings / empty I/O / nest / `#` location | `asca` crate `src/error/syntax.rs`, `src/error/runtime.rs` |
| Token `*` / `∅` / `&` | `asca` crate `src/rule/lexer.rs` |
| Parse entrypoints | `asca` crate `src/lib.rs`, `src/rule/rule_repr.rs` |

**Note:** Prefer HEAD docs for wording; local CLI verified at research time was `asca 0.9.3` (cargo registry copy of docs/source). Behavior should be re-checked if the project pins a different asca version.
