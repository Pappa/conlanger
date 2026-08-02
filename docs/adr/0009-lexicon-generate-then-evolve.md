# Generate lexicon from inventory, then evolve with sound changes

Lexicons are produced by a **generator** that takes a phoneme inventory (and phonotactics) and emits word forms. Naturalism is pursued primarily by applying **sound-change sequences** afterward (toward proto-roots and later historical stages), not by requiring the initial generator to be highly realistic.

The current “very naive” lexicon tool is an acceptable starting implementation and may be replaced without changing this arc.

## Considered Options

- **Generate then evolve (chosen)** — matches the README plan; aligns with ADRs 0001–0007.
- **Hand/external lexicons only** — skips a core generative stage.
- **Demand a high-fidelity generator before sound change** — delays the pipeline; fights the documented approach.

## Consequences

- APIs should accept inventory (+ phonotactics) → lexicon, then optionally apply sound-change sequences.
- Poor initial word shape is expected; evaluation should emphasize post-change results where that is the goal.
- Phonotactics defaults (e.g. early `(C)V`) remain a separate small decision if locked later.
