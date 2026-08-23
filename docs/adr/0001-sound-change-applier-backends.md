# ASCA first, multi-applier capable

Conlanger will treat ASCA [asca-rust](https://github.com/Girv98/asca-rust) as the default sound-change applier. Howerver, this package should abstract its interface to the sound-change applier foso thatr [Brassica](https://github.com/bradrn/brassica) or another tool can be used optionally in future without needing to rewrite a significant amount of code.

## Considered Options

- **ASCA-only forever** — faster short term; locks the whole stack to one syntax and CLI.
- **Applier-neutral from day one with no ASCA bias** — may be unnecessarily complex to support multiple appliers long term
- **ASCA-first with an explicit multi-applier boundary** — chosen: ship ASCA hard, keep the door open for Brassica.

## Consequences

- Prefer interfaces and index shapes that can compile or adapt to more than one applier.
- Do not scatter raw ASCA CLI calls through unrelated modules without a single applier boundary.
- Brassica support may stay “in principle” until a later ADR adopts it for real.
