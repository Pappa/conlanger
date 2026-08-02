# Keep Index Diachronica series indices; map per section

Subscript digits and letters on segments in Index Diachronica (e.g. `x₂`) are **series / correspondence indices**, not decorative typography. The rule corpus must retain them. Resolution to concrete segments uses **per-section mapping tables** (as with `series_mapping.yaml` in the current tooling), not silent stripping to the base letter.

## Considered Options

- **Retain indices + per-section maps (chosen)** — preserves author intent; unmapped rows are explicit data debt.
- **Strip subscripts at ingest** — simpler strings; wrong when the letter stands for a series member.
- **Expand only inside the ASCA compiler** — acceptable mechanically, but still requires the same maps; choosing A keeps the corpus honest about what the HTML meant.

## Consequences

- Ingest must not “fix” indices by deleting them.
- Unmapped series should be reportable (e.g. `unmapped_series.csv` style), not silently guessed.
- Applier compilers consume mapped/concrete forms (or fail clearly when a map entry is missing).
