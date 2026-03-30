---
name: design
description: Use when implementing a new feature, complex refactor, or migration touching multiple files. Triggers on "plan this", "how should we build", "design this", or tasks with structural risk.
---

# Design

## Overview

Creates a detailed, executable coding plan before any code is written. Surfaces assumptions, identifies files, and aligns on approach — so implementation is focused, not exploratory.

## When to Use

- New feature implementation touching multiple files or systems
- Complex refactors with cross-cutting changes
- Feature migrations from reference projects
- User says "plan this", "how should we build", "design this"

**Do NOT use when:**
- Simple bug fixes (1-2 files, clear cause)
- Typo/config changes
- User has already given a detailed plan

---

## Process

### Phase 1: Understand (Reverse-Prompting)

Do NOT start planning immediately. First, ask the user targeted questions to fill gaps. Topics to cover:

- **Scope:** What should this do? What should it NOT do?
- **Files:** Which existing files or systems are involved?
- **Reference:** Existing implementation to follow?
- **Constraints:** Performance, platform, or architectural constraints?
- **Dependencies:** Depends on or blocks other work?
- **Edge cases:** Failure/empty/boundary scenarios?

Keep asking until you have enough to plan confidently. There is no question limit.

**Questioning style:**

- **Short questions.** 1-2 sentences. No preamble, no restating what the user said.
- **Short options.** Label + brief phrase when offering choices.
- **Skip the question** if you can infer the answer from context — state your assumption and move on.
- **Batch related gaps** into one question when they're tightly coupled (e.g. "Scope: X and Y, or just X?").

### Phase 2: Discover (Targeted Only)

Once scope is clear, read **only** the files needed to plan. Follow the scoping rules from CLAUDE.md Task Intake:
- State which files you plan to read and why.
- If more than 5 files, list them and get confirmation.
- Use Grep/Glob to locate, then read only relevant sections.

Do NOT scan broadly. If you're unsure which files matter, ask.

### Phase 3: Plan

Produce a structured plan with:

1. **Summary** — One paragraph: what we're building and why.
2. **Files to create/modify** — Exact paths, what changes in each.
3. **Class/method design** — Key classes, method signatures, data flow.
4. **Implementation order** — Which files to touch first, dependencies between steps.
5. **Risk areas** — Anything that might break, need testing, or has unknowns.

### Phase 4: Confirm

Present the plan and wait for approval. Do NOT write code until the user says go.

If the user wants changes, revise the plan. If they approve partially, implement only the approved parts.

---

## Light Mode

When routing classifies the task as **light**, collapse the 4-phase process:

1. **Phase 1 (Understand):** 0-1 targeted questions. If intent is clear, skip.
2. **Phase 2 (Discover):** Read only the target file(s). No broad exploration.
3. **Phase 3 (Plan):** Short bullet list — files, key changes, order. Not a full structured document.
4. **Phase 4 (Confirm):** Single approval gate.

Same rules apply (no coding during planning, prefer additive changes). Light mode compresses the *ceremony*, not the *discipline*.

## Rules

- Never start coding during the planning phase.
- Never read files without stating which and why.
- Prefer additive plans — build on existing patterns in the codebase rather than introducing new ones.
- If the plan changes during implementation, update it before continuing.
- Design skill hands off to `plan` — context doc updates happen during execution, not design.

## Chaining

**Writes handoff to:** `.claude/handoffs/design-to-plan.md`
**Chains to:** `plan`

After user approves the plan in Phase 4, write a handoff file:

```markdown
---
from: design
to: plan
spec: <path to spec doc if written, or "inline">
---

- **Decisions:** [summary, files to create/modify, class/method design, implementation order]
- **Files touched:** [files read during Phase 2 discovery]
- **User preferences:** [constraints, approved scope, any partial approvals]
- **Skip:** plan Phase 1 (Understand scope), plan Phase 2 (File discovery)
```

Then suggest-and-confirm:
> "Design complete. Ready to move to plan. Proceed?"
