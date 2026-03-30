# Skill System — Decisions & Improvements

A living record of why the system works the way it does, what changed, and why.

---

### 2026-03-27 — Skill Chaining Protocol

**Problem:** Skills were cold-starting every time. brainstorm would gather context, then plan would re-ask the same questions. Debug would find the root cause, then error-fix would re-investigate.

**Fix:** Standalone handoff files in `.claude/handoffs/`. Each skill writes what it learned, the next skill reads it and skips covered phases. Suggest-and-confirm pattern ensures the user controls transitions.

**Benefit:** No redundant questions, no re-reading files, no lost context between skill transitions.

---

### 2026-03-27 — Lightweight Mode

**Problem:** Every task got the full ceremony — 9-step brainstorm checklist for renaming a variable, 4-phase design process for a config tweak. Skills didn't scale down for simple work.

**Fix:** Routing classifies task complexity (light vs full) by weighing 5 signals: change scope, intent clarity, language cues, cause clarity, spec expectation. No single signal decides — it's the combination. Skills have a `## Light Mode` section that collapses phases and gates for simple tasks.

**Benefit:** Simple tasks feel fast. Complex tasks still get full rigor. The user can override in either direction.

---

### 2026-03-27 — Concise Questioning Style

**Problem:** Skills asked verbose questions with paragraph-long options. "Option A would be an event-driven approach where we create a system that listens for..." when "A) Event-driven B) Polling C) Hybrid — I'd lean A" would do.

**Fix:** Added questioning style rules to brainstorm, design, plan, execute, debug: 1-2 sentence questions, short option labels, lead with recommendation, skip if inferable from context.

**Benefit:** Faster conversations. Less reading. User still gets all the information they need.

---

### 2026-03-27 — Platform Pattern Extraction

**Problem:** Skills had Unity/C# content hardcoded into their core logic — MonoBehaviour lifecycle checks in debug, CS#### error codes in error-fix, GetComponent caching in refactor. This made the system unusable for non-Unity projects and impossible to share.

**Fix:** Extracted all platform-specific content into pluggable `patterns/unity-csharp.md` files (one per skill). Skills are now generic. They check for `.claude/project-profile.md` — if it exists and matches a platform, the skill loads the corresponding patterns file. Without a profile, skills work generically.

**Affected skills:** debug, error-fix, inspect, refactor, integrate (5 pattern files created).

**Benefit:** System is shareable across any tech stack. Unity users get the same depth as before. Adding support for a new platform (e.g. React/TypeScript) means creating `patterns/react-typescript.md` files — no SKILL.md changes needed.

---

### 2026-03-27 — Structural Cleanup

**Specs/plans consolidation:** Removed separate `specs/` folder. Both specs and plans live in `plans/` (project-local or global). One folder, less confusion.

**Project profile scoping:** Project profile is project-local only (`.claude/project-profile.md`). Removed from global CLAUDE.md — the global system should not assume a platform.

**Path standardization:** All file references in global docs use `~/.claude/skills/<name>/` full paths. No bare filenames that could be ambiguous.

**Deprecated info cleanup:** Updated CHANGELOG and README to reflect current structure. No stale references left in active docs.
