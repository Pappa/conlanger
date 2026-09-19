Type: task
Blocked by: [124](124-correction-pass-merge-adjacent-matrices.md)

# Correction pass: env chained colon feature matrices (`missing_slash_output_env` / `:`)

Target cluster: `missing_slash_output_env` with `error_token` **`:`** — **11** failing rules (**6** sections; **3** mono-class sections would complete if cleared). Spawned from `/grill-with-docs` on [map.md](../map.md) (2026-09-19).

Related: [124 merge adjacent `][` matrices](124-correction-pass-merge-adjacent-matrices.md) (I/O only today); [131 env/exception feature matrices](131-correction-pass-env-exception-feature-matrices.md) (bare-matrix → input; neighbour bracket→colon); [22 stress conditions](22-correction-pass-stress-conditions.md) (parse-time stress phrases that feed env templates).

## Problem

ASCA 0.10.3 reports *Did you forget a '/' between the output and environment?* when a **second colon-bound feature matrix** appears on the same segment host in the **environment** (parser receives `:` where it expects end-of-rule after output).

Inventory compiled shapes (representative):

```
kʷ > s / _V:[+front]:[+stress]
j > ∅ / V_V:[+front]:[+stress]
e > ə / #(C,0)_($,0):[+stress] in %[+lo]
t > tʃ / _V:[+front]:[+stress]
```

These are **not** the `][` adjacent-matrix split fixed in ticket 124 (`C:[+labial][+spread]`). They are **`host:[featuresA]:[featuresB]`** chains — often after Index class-letter expansion (`E` → `V:[+front]`) combined with a separate stress matrix (`:[+stress]`) on the same vowel host in the env template.

`normalize_asca_adjacent_feature_matrices` runs on **compiled input/output only** (`pipeline.py`); **env/exception** get `normalize_asca_host_bracket_matrices` but no merge pass for colon-chained matrices.

`config/compile/asca/group_mappings.yml` mappings that contain colons (e.g. `E: V:[+front]`) are **correct** single-matrix expansions; the bug is the **second** matrix glued with an extra colon on the same host in env, not the mapping file syntax itself.

## What to build

1. **Compile pass** (extend `merge_adjacent_feature_matrices` in `tone_matrices.py` or sibling) to merge **colon-chained** matrices on one host:
   - `V:[+front]:[+stress]` → `V:[+front,+stress]` (comma-join interiors; preserve host token).
   - Apply to **compiled env** and **compiled exception** after `normalize_asca_host_bracket_matrices` (and after ticket 131 cross-field steps if order matters — document in compile table).
   - Optionally run the same helper on I/O if probes show residual `host:[a]:[b]` there (superscript + group expansion comment in `superscript_modifiers.py`).

2. **Do not** merge across distinct hosts (`V:[+long] C:[+stress]` unchanged).

3. **Unit tests** from inventory rows: Gheg/Tosk `kʷ`, French/Provençal `j`, Proto-Čiwere-Winnebago `t`, Romanian `dj`; French `e` / `a_2` env templates with `($,0):[+stress]` if the merge regex covers matrix-after-template tails.

4. Full inventory re-run (`uv run create_index && uv run validate_rules`); record ok/fail delta and `missing_slash_output_env` cluster size (especially `error_token` `:`) in **Answer**.

## Out of scope (file separate passes if still failing)

- **15** `missing_slash_output_env` rows with `error_token` **`)`** — editorial parenthetical gloss tails (`dialectally?)`, `analogy interfered)`); overlap [115 editorial slash](../issues/115-correction-pass-editorial-slash-prose-residue.md) / parse comment strip.
- Output-side **matrix + segment** without `/` (e.g. `C:[+cor,+dist]j > Cʲ:[+long]` — Tocharian-A-Cʲj).
- Kleene `*`, ellipsis `…`, metathesis `&`, optional output `(l:[+long]?)` — distinct shapes in the same failure class.

## Policy

- Index YAML unchanged; compiled-string shape only ([ADR-0010](../../../docs/adr/0010-historical-fidelity-class-first-status.md)).
- Prefer reusing ticket 124’s `merge_adjacent_feature_matrices` loop with an additional pattern for `:[…]:[…]` on the same host rather than env-only regex in group mapping expansion.

## Acceptance criteria

- [x] Target cluster sized at claim time from current inventory (`missing_slash_output_env` / `:`)
- [x] Class-first compile transform; `raw` unchanged
- [x] Full inventory re-run; before/after metrics in **Answer**
- [x] Unit tests for Albanian/Romance/Siouan env stress chains

## Answer

**Shipped 2026-09-19.** Extended `merge_adjacent_feature_matrices` with `:[featuresA]:[featuresB]` colon-chain merge (ticket 124 helper); `normalize_asca_adjacent_feature_matrices` now runs on compiled **env** and **exception** after `normalize_asca_host_bracket_matrices` (order 10¾ in `docs/system/sound-change-applier.md`).

- **Cluster `missing_slash_output_env` / `error_token` `:`:** **11 → 3 (−8)**. Remaining three are French `($,0):[+stress]` template tails (out of scope here; not colon-chained host matrices).
- **Inventory:** OK **8900 → 8925 (+25)**; fail **410 → 385 (−25)** (`validate_rules`, 2026-09-19). Recovered Albanian `kʷ`, Romance `j` / Provençal / Romanian `dj`, Proto-Čiwere-Winnebago `t`, etc.
- **Tests:** `test_adjacent_feature_matrices.py` — colon-chain unit cases + compile probes with `load_compiler_config()`.

## References

- [missing_slash_output_env_errors.csv](../inventory/error_clusters/missing_slash_output_env_errors.csv)
- `src/conlanger/tools/compile/asca/tone_matrices.py`
- `src/conlanger/tools/compile/asca/pipeline.py`
- [Correction pass template](13-correction-pass-template.md)
