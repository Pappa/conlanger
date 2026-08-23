# Applier-neutral rule index in YAML

Stored sound-change rules live as an **applier-neutral intermediate representation in YAML**. ASCA and Brassica are compile targets of that index, not owners of the canonical on-disk format.

This supersedes the vibe-coding path where generated XML/YAML fragments were treated as ASCA-native source of truth. The Index Diachronica HTML parser should emit (or migrate toward) the neutral YAML index; separate **applier compilers** produce ASCA- or Brassica-ready artifacts for execution and tests.

## Considered Options

- **ASCA-shaped index + adapters** — faster for current ASCA work; makes Brassica a permanent second-class retrofit.
- **Applier-neutral YAML IR (chosen)** — one source of truth; ASCA and Brassica both compile from it.
- **Keep raw Index Diachronica strings only** — maximum fidelity to the HTML; every applier re-parses linguistic notation.

## Consequences

- Do not encode ASCA-only syntax (or Brassica-only syntax) as the only representable form in the YAML schema.
- Near-term ASCA execution/tests go through an ASCA compiler over the index.
- Existing ASCA-flavoured YAML from the transcript era is a migration input, not the long-term schema.
