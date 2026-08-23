# Index Diachronica HTML is current source of truth; cleaned YAML is the planned successor

For ingestion today, **`index_diachronica_original.html` is the ultimate source of truth**. Hand-edited XML/YAML samples guide structure and regressions only; when they disagree with the HTML (or with post-compile applier checks), the HTML and the compilers win.

A **new cleaned YAML rule index** is the intended long-term source of truth (aligned with ADR-0002). Planning that migration — including schema and cleanup spikes — is deferred to a `/wayfinder` effort, not decided in detail here.

## Considered Options

- **HTML as current SoT + cleaned YAML as planned successor (chosen)** — honest about today’s artifact; points at the real destination.
- **Manual XML/YAML overrides HTML** — recreates the slow hand-edit bottleneck the transcript was escaping.
- **Declare cleaned YAML SoT immediately** — desirable end state, but the cleaned index does not exist yet as an authoritative artifact.

## Consequences

- Do not treat `index_diachronica.xml` / early AI YAML dumps as canonical when they conflict with the HTML.
- Wayfinder owns the route to the cleaned YAML SoT (including unresolved items such as prose-environment mapping).
- Until that index exists and is adopted, regenerations should be traceable back to the HTML.
