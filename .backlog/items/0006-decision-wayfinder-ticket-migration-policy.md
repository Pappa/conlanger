Type: epic-duck:decision
Status: ready
Plan: [0001-plan-migrate-project-to-duck-skills.md](0001-plan-migrate-project-to-duck-skills.md)
Overview: Rules for which wayfinder tickets move to `.backlog/`, how to merge and summarize them, and how much to compress the rule-index map.
Blocked by:

## Question

What **migration policy** applies when copying wayfinder work from `.scratch/` into the duck-skills **`.backlog/`** (planning and implementation items), so agents do not replay obsolete or redundant tickets?

Resolve all of the following in one documented answer (usable as checklist for plan **0003** and the other product plans):

1. **Merged implementation tasks** — When may several related wayfinder **task** tickets become **one** backlog item with heavily summarized content (problem, outcome, and acceptance criteria), instead of a 1:1 file copy? What makes tickets “related” enough to merge (same failure class, same pipeline stage, same correction-pass theme, etc.)?
2. **Terminal exclusions** — Confirm that wayfinder tickets closed as **out of scope** or **wontfix** (and epic-duck **`out-of-scope`** / **`wontfix`**) are **never** migrated as active backlog work. Where, if anywhere, should a one-line summary live (plan **Out of scope**, **Decisions so far** gist only, or archive pointer)?
3. **Superseded work** — How to identify and **exclude** tickets whose decisions or implementations were **overruled or overwritten** by later tickets (e.g. map strike-through chains, “supersedes” / “wontfix (superseded by …)” in [.scratch/rule-index/map.md](../../.scratch/rule-index/map.md)). What is the rule for keeping historical gists in **Decisions so far** vs omitting them entirely from `.backlog/`?
4. **Spikes** — Under what conditions is a wayfinder **spike** (repo alias for upstream **research**) copied to `.backlog/`? Owner leaning: **only if still valuable** — define “still valuable” (feeds open work, documents unresolved constraints, findings not captured elsewhere) and whether findings stay in `.backlog/spike/` vs `.scratch/.../research/`.
5. **Rule-index map compression** — Target scale when migrating [.scratch/rule-index/map.md](../../.scratch/rule-index/map.md): owner leaning **~174 wayfinder issues → ~20–25** backlog children (merged/summarized). Decide exact band, what rolls up into **Decisions so far** on plan **0003** vs standalone **`Type: task`** / **`Type: spike`** items, and what remains only as links into `.scratch/` for archaeology.

**Resolution criteria:** A short policy section (bullets or table) that implementers can apply ticket-by-ticket, plus any updates needed to plan **0001** **Out of scope** / **Not yet specified** and plan **0003** **Notes**.

## Comments

- 2026-10-29: Owner input when filing — prefer **fewer** backlog tickets via **merge + heavy summarization**; **exclude** out-of-scope, wontfix, and superseded/overwritten work; **spikes** only when still valuable; rule-index map migration target **~20–25** items from **~174** wayfinder issues.
