# How ASCA represents ejectives (e.g. `tʃʼ`)

Primary sources: [ASCA 0.10.2 `doc/doc.md`](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md), local `asca run` smoke tests.

## Summary

Index Diachronica writes ejectives as **`ʼ`** (U+02BC modifier letter apostrophe) **after** the segment — e.g. `tʃʼ`, `tsʼ`, or `ts:[+long]ʼ`.

ASCA accepts the same character, but with important constraints:

| Index notation | ASCA equivalent | Notes |
|----------------|-----------------|-------|
| `pʼ`, `tsʼ`, `tʃʼ` | same, or `p:[+cg]`, `ts:[+cg]`, `tʃ:[+cg]` | Diacritic **or** `[+cg]` (constricted glottis) feature |
| `dʼ`, `dzʼ`, `bʼ` | `d:[+cg]`, `dz:[+cg]`, `b:[+cg]` | Voiced segments **cannot** take the `ʼ` diacritic; use `[+cg]` |
| `ts:[+long]ʼ` | `ts:[+long,+cg]` or `tsʼ:[+long]` | **Invalid**: diacritic after a feature matrix |
| `{t,ts}ʼ` | `{t:[+cg],ts:[+cg]}` or `{tʼ,tsʼ}` | **Invalid**: diacritic after a set |
| `pʼ` with stress | use `ʼ` not `'` | ASCII `'` is **primary stress**, not ejective |

## ASCA model

1. **Diacritic** — `ʼ` attaches to a base IPA segment (PHOIBLE-style modifier letter). Alias: `"'` → `ʼ` ([Inbuilt Aliases](https://github.com/Girv98/asca-rust/blob/0.10.2/doc/doc.md#inbuilt-aliases)).

2. **Feature** — Ejectives are `[+cons]` segments with **`[+cg]`** (constricted glottis / `[+const]` glottis node). Works on voiced and voiceless segments.

3. **Affricates** — Doc says `dʒ` is two segments (`d` + `ʒ`); tied form is `d^ʒ`. In practice ASCA 0.10.2 also accepts bare `tʃ`/`ts` multigraphs in rules; `t^ʃʼ` and `tʃʼ` both validate.

4. **Prerequisite** — The `ʼ` diacritic requires **`[-voice]`** on the base segment. Voiced “ejectives” in Index (e.g. `dʼ > tʼ`) must use `[+cg]` features instead.

## Verified examples (ASCA 0.10.2)

```
tʃʼ > tʃ          ✓  (diacritic form)
tʃ:[+cg] > tʃ     ✓  (feature form)
ts:[+long,+cg] > ts:[+long]   ✓  (long ejective via features)
ts:[+long]ʼ > …   ✗  Expected '>' but received 'ʼ'
dʼ > tʼ           ✗  Must be [-voice]
d:[+cg] > t:[+cg] ✓
{t,ts}ʼ > s       ✗  Expected '>' but received 'ʼ'
{t:[+cg],ts:[+cg]} > s  ✓
```

## Compile-time correction (issue 20)

`normalize_asca_ejective_marks()` in `rules.py` maps Index placement to ASCA:

1. `segment:[features]ʼ` → `segment:[features,+cg]`
2. `{a,b,…}ʼ` → `{a:[+cg],b:[+cg],…}` (per-member expansion)
3. bare `segmentʼ` → `segment:[+cg]` (covers voiced ejectives and normalizes voiceless)

Corpus YAML fields and `raw` stay unchanged; transform runs at ASCA compile only (same seam as length marks).

## Out of scope

- `(ʼ)` optional ejective after length — no valid ASCA I/O optional; needs manual set expansion or skip.
- Index `(kʼ)` parenthesis notation in environments — separate syntax cluster.
