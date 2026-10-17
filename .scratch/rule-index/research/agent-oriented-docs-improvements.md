# Agent-oriented documentation improvements

Spike for [ticket 154](../issues/154-spike-agent-oriented-docs-improvements.md).  
**Question:** What doc changes most improve **agent** comprehension of the rule-index pipeline and reduce wrong assumptions — without duplicating implementation detail?

**Primary sources:** `AGENTS.md`, `docs/agents/domain.md`, `CONTEXT.md`, `docs/SYSTEM.md`, `docs/system/*.md`, `docs/adr/0011`, `docs/adr/0013`, `docs/adr/0016`, `docs/adr/0017`, `.scratch/rule-index/map.md`, `.scratch/rule-index/spec.md`, [ticket 148](../issues/148-grill-asca-shaped-syntax-in-applier-neutral-sot.md) answer, domain-modeling skill (`GLOSSARY.md` vs glossary-in-`CONTEXT.md`).

---

## 1. Executive summary

Agents that land on **pipeline docs** (`docs/system/*`) without reading **`CONTEXT.md`** routinely inherit three wrong mental models:

1. **YAML shape** — parser/applier pages still describe corpus rules with `input`/`output` fields; the index has used **`stages`** since ADR-0011.
2. **Applier-neutral vs ASCA** — several surfaces say parse “normalizes toward ASCA” or that **Symbol** entries are “ASCA-canonical at ingest”; [148](../issues/148-grill-asca-shaped-syntax-in-applier-neutral-sot.md) locked the opposite for many tokens (`%`/`$`, stress postfix, no `→`/`>` in cleaned fields, dual feature configs).
3. **Navigation** — `docs/system/*.md` link ADRs as `./adr/…` (resolves to non-existent `docs/system/adr/`); agents following links hit 404s in the IDE.

**Highest leverage:** split **glossary** from **project overview** (`GLOSSARY.md` + slim `CONTEXT.md`), fix **broken ADR links** and **`stages` vocabulary** in pipeline docs, add a **rule-index agent entrypath** in `AGENTS.md`, and sync **Symbol / Environment / Feature matrix** glossary lines with 148 before the next regen-driven confusion.

Implementation owner: [ticket 155](../issues/155-task-glossary-migration-and-docs-improvements.md).

---

## 2. Agent-facing surface inventory

| Surface | Role today | Who points here | Agent risk |
| --- | --- | --- | --- |
| `AGENTS.md` | Skills + issue tracker + domain doc pointer | Cursor rules (implicit), skills | **Thin** — no rule-index path, no “read map vs CONTEXT” guidance |
| `docs/agents/domain.md` | Read `CONTEXT.md` + `SYSTEM.md` + ADRs | domain-modeling, grilling | Correct pattern; assumes `CONTEXT.md` is glossary-only (it is not) |
| `docs/agents/issue-tracker.md` | Wayfinder ops, `Status:` / `Type:` | wayfinder, AGENTS | Good for `.scratch/`; does not say map is index not spec |
| `CONTEXT.md` | **Glossary + doc map** (~250 lines) | spec, map Notes, hundreds of ticket links | **Overload** — domain terms mixed with notebook-era product arc; domain-modeling expects `GLOSSARY.md` |
| `docs/SYSTEM.md` | Pipeline table + legacy notebook map | CONTEXT link | Rule-index table is good; legacy table distracts agents on conlanger package work |
| `docs/system/index-diachronica-parser.md` | Parse transforms catalog | SYSTEM.md | Stale `input`/`output`; broken `./adr/` links; “toward ASCA-parseable” overstates parse intent |
| `docs/system/sound-change-applier.md` | Compile transform table | SYSTEM.md | Compile `input`/`output` on `SoundChangeRule` is correct **at compile** but needs explicit “derived from **stages**” callout |
| `docs/system/validate.md` | Inventory + correction loop | SYSTEM.md | Strong; broken `./adr/` links |
| `docs/system/applier-neutral-index-validation.md` | Redirect stub | ADR-0013, old tickets | Harmless if linked; should not appear in new entrypaths |
| `docs/DEV.md` | pytest, ruff, ASCA fork | quality gates | Good; not linked from AGENTS |
| `.scratch/rule-index/map.md` | Wayfinder decisions index | map Notes, many tickets | **Huge** — agents treat as spec; glossary lives in Notes + CONTEXT |
| `.scratch/rule-index/spec.md` | Product spec for cleaned index | ticket 154 scope | Correct “start here” for *effort*; not repo-global |
| `.scratch/rule-index/research/*.md` | Spike findings | map Decisions | Authoritative for *past* decisions; must not contradict living docs |
| `docs/adr/0001–0017` | Hard-to-reverse decisions | CONTEXT, system docs | Agents skip when links break |

**Skills/rules that should stay the compass:** `docs/agents/domain.md` order (CONTEXT → SYSTEM → ADRs). No `GLOSSARY.md` exists yet; domain-modeling skill defaults to creating one lazily.

---

## 3. Failure modes (recent agent work)

Observed confusion patterns from map Notes, grill 148, and doc/code drift:

| Failure mode | Symptom | Source of wrong assumption |
| --- | --- | --- |
| Parse vs compile | Agent adds class-letter expansion or length marks at parse | `index-diachronica-parser.md` scope blur; map Notes repeat “parse vs compile” but map is not first read |
| SoT tier confusion | Agent persists ASCA env strings (`U#`, `_ %[-stress]`, colon matrices) in YAML | Old correction-pass docs + glossary **Environment** describing parse rewrites that 148 retires → [149](../issues/149-grill-parse-time-asca-env-rewrites-vs-structured-indexcontext.md) |
| `stages` vs compile fields | Agent edits or validates `input`/`output` in YAML | Pipeline docs opening paragraphs still say `input`/`output` on **corpus** rules |
| Symbol `%` / `$` / stress | Agent runs `normalize_symbols` expecting SoT change | **Symbol** glossary: “Normalised to ASCA-canonical form … at ingest” — conflicts with 148 (Index `%`/`$` in SoT; stress postfix not colon) |
| Glossary vs implementation | Agent puts file paths and config names in glossary entries | `CONTEXT.md` **Feature matrix**, **Class letter**, **Collective subscript** embed `config/…` paths (useful for humans, violates domain-modeling “definitions only”) |
| Map as spec | Agent implements from Decisions-so-far one-liner without zooming ticket | map size + duplicate policy in Notes vs CONTEXT |
| Broken ADR links | Agent concludes “no ADR” | `./adr/` from `docs/system/` |
| Triage vs wayfinder | Agent sets `ready-for-agent` on wayfinder tickets | AGENTS explains spike alias; issue-tracker explains `claimed`/`resolved` — OK if read |
| `applier-neutral-index-validation` | Second validate doc | Mostly fixed (redirect); ticket 37 wanted merge — still a duplicate filename in search results |

---

## 4. Domain-modeling alignment

| Convention | Repo today | Recommendation |
| --- | --- | --- |
| `GLOSSARY.md` at root | Missing | **Must** — extract terms from `CONTEXT.md`; definitions only ([GLOSSARY-FORMAT](https://github.com/mattpocock/skills/blob/main/domain-modeling/GLOSSARY-FORMAT.md) via domain-modeling skill) |
| `CONTEXT.md` | Glossary + links | **Must** — slim to project blurb, doc map, “read GLOSSARY.md for terms”, link to `.scratch/rule-index/spec.md` for cleaned-index effort |
| ADRs | `docs/adr/` | Keep; add “read 0011, 0013, 0016, 0017 for rule index” in agent entrypath |
| Multi-context | Single context | No `GLOSSARY-MAP.md` |

**148 follow-on:** 148 explicitly deferred `GLOSSARY.md`; ticket 155 elevates it to **must**.

---

## 5. Prioritised recommendations

### Must (155 acceptance)

1. **Create `GLOSSARY.md`** — move all `###` glossary sections from `CONTEXT.md`; strip implementation paths from definitions (point to `docs/system/*` or ADRs in “see also” only if format allows — prefer keeping GLOSSARY implementation-free and linking from CONTEXT doc map).
2. **Slim `CONTEXT.md`** — retain: one-paragraph project summary, documentation bullet list, link to `GLOSSARY.md`, `docs/SYSTEM.md`, rule-index spec/map for index work.
3. **Fix ADR links in `docs/system/*.md`** — replace `./adr/` with `../adr/` (all occurrences in `index-diachronica-parser.md`, `sound-change-applier.md`, `validate.md`, `applier-neutral-index-validation.md`).
4. **Corpus YAML vocabulary in pipeline docs** — in parser doc intro and any corpus examples: **`stages`**, optional `env`/`exception`/`IndexContext`, `raw`, `rule id`; state clearly that **`input`/`output` are compile-time fields** on `SoundChangeRule`, not YAML keys.
5. **Sync glossary with 148 (Symbol, Feature matrix, Environment, Stages)** — before or as part of GLOSSARY extraction:
   - **Symbol:** Index `%` and `$` stay in SoT until compile ([153](../issues/153-task-atomic-syllable-symbol-compile-migration.md)); stress mark → postfix `[+stress]` at parse, not ASCA colon.
   - **Stages:** no `→` or `>` inside cleaned index strings (chain = array length ≥ 3).
   - **Environment / medial / syllable position:** point to structured `IndexContext.position` + 148 tier B/C; deprecate prose that recommends persisting ASCA env shorthands at parse.
6. **`AGENTS.md` rule-index entrypath** — short subsection: for cleaned-index work read order `GLOSSARY.md` → `docs/SYSTEM.md` (parse table) → `docs/adr/0013` → `.scratch/rule-index/spec.md`; wayfinder **map** = decision index only; **do not** treat map Notes as glossary.
7. **`docs/agents/domain.md`** — replace “`CONTEXT.md` (glossary and doc map)” with “`GLOSSARY.md` + `CONTEXT.md` (overview and doc map)”.

### Should

8. **`docs/SYSTEM.md`** — add one line under parse table: “Corpus rule YAML uses **`stages`** (ADR-0011), not `input`/`output`.”
9. **`sound-change-applier.md`** — opening paragraph: compile reads **materialized** env/exception + **stages**-derived compile fields; link ADR-0011.
10. **Dual feature configs** — new subsection in parser or compile doc (not glossary): `config/parser/feature_mappings.yml` (canonical cleaned-index names) vs `config/compile/asca/feature_mappings.yml` (ASCA projection); link 148, defer row lists to implementation tickets.
11. **`docs/DEV.md`** — link from `AGENTS.md` or `docs/agents/domain.md` for agents running validate/inventory.
12. **Retire search noise** — delete `applier-neutral-index-validation.md` or keep redirect but add `<!-- superseded by validate.md -->` in SYSTEM.md related docs only (optional; ADR-0013 already wants fold).

### Nice

13. **Map hygiene** — move standing operator preferences from map **Notes** into `spec.md` or `docs/system/validate.md` “Correction policy” once; leave map Notes as pointers (reduces duplicate policy).
14. **`docs/CONLANGER.md`** — banner at top: “Notebook narrative; for rule index see SYSTEM.md” (agents exploring repo root).
15. **Glossary term** — add **section-local class label** (ticket 129) when 155 touches glossary.
16. **Per-ADR “Agents” one-liner** — bottom of 0011, 0013, 0016, 0017: “If you only read one ADR for YAML shape, read this.”

---

## 6. File-level action checklist (for 155)

| File | Action |
| --- | --- |
| `GLOSSARY.md` | **Create** — migrated terms from CONTEXT |
| `CONTEXT.md` | **Slim** — overview + links; 148 sync on terms left in cross-refs only |
| `AGENTS.md` | **Add** rule-index read order + DEV link |
| `docs/agents/domain.md` | **Update** GLOSSARY + CONTEXT roles |
| `docs/SYSTEM.md` | **Add** stages note |
| `docs/system/index-diachronica-parser.md` | **Fix** links, stages vocabulary, applier-neutral framing |
| `docs/system/sound-change-applier.md` | **Clarify** stages → compile fields |
| `docs/system/validate.md` | **Fix** ADR links |
| `docs/system/applier-neutral-index-validation.md` | **Fix** link or delete after redirect note in SYSTEM |
| `.scratch/rule-index/spec.md` | **Optional** — link `GLOSSARY.md` at top alongside CONTEXT |

**Out of scope (154):** implementing 153, feature-config splits, regen, rewriting closed tickets, map Decisions-so-far.

---

## 7. Answer for ticket 154

**Prioritised doc work for agents:** glossary extraction + CONTEXT slimming, fix broken system-doc ADR links, align pipeline pages with **`stages`** and parse/compile/SoT tiers from 148, and a explicit **AGENTS.md** entrypath separating **GLOSSARY** / **SYSTEM** / **spec** from the **wayfinder map**. Full checklist above; implement on [155](../issues/155-task-glossary-migration-and-docs-improvements.md).

**Deliverable:** this file — [agent-oriented-docs-improvements.md](./agent-oriented-docs-improvements.md).
