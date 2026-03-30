---
name: plan
description: Use when you have a spec or requirements for a multi-step task, before touching code
---

# Writing Plans

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for the codebase. Document everything they need: which files to touch, what code to write, how to verify. Give them the whole plan as bite-sized tasks. DRY. YAGNI.

Assume they are a skilled developer, but know almost nothing about the toolset or problem domain.

**Announce at start:** "I'm using the plan skill to create the implementation plan."

**Save plans to:** `.claude/plans/YYYY-MM-DD-<feature-name>.md`
- Project-specific work → `<project>/.claude/plans/`
- Global/cross-project work → `~/.claude/plans/`
- User preferences for plan location override these defaults

## Step 0: Check for Handoff

Before starting the full process, check for a handoff file:

1. Look for `.claude/handoffs/*-to-plan.md` (e.g., `brainstorm-to-plan.md`, `design-to-plan.md`)
2. If found → read it, honor the `Skip` list, pre-load `Decisions` and `Files touched`
3. If not found → run full process as normal

| Handoff field | What it skips |
|---|---|
| Decisions | Phase 1 scope questions — scope is already defined |
| Files touched | File discovery — files are already identified |
| User preferences | Constraint gathering — already captured |

**Staleness check:** If files listed in handoff have changed since it was written, fall back to full process for that phase.

After consuming the handoff, delete the handoff file.

---

## Questioning Style

When asking clarification questions during planning:

- **Short questions.** 1-2 sentences. No preamble.
- **Skip the question** if you can infer the answer from the spec or handoff — state your assumption and move on.
- **Batch related gaps** into one question when tightly coupled.

## Scope Check

If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during brainstorming. If it wasn't, suggest breaking this into separate plans — one per subsystem. Each plan should produce working software on its own.

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns.

This structure informs the task decomposition. Each task should produce self-contained changes that make sense independently.

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the implementation" — step
- "Verify it compiles/works" — step
- "Update references" — step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** Use the `execute` skill to implement this plan task-by-task.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

---
```

## Task Structure

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file`
- Modify: `exact/path/to/existing`

- [ ] **Step 1: [Action]**

```
// Exact code to write (use project's language)
```

- [ ] **Step 2: Verify**

Expected: [What success looks like]

- [ ] **Step 3: [Next action]**

[Continue with exact code and verification]
````

## No Placeholders

Every step must contain the actual content an engineer needs. These are **plan failures** — never write them:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Similar to Task N" (repeat the content — tasks may be read out of order)
- Steps that describe what to do without showing how (code blocks required for code steps)
- References to types, functions, or methods not defined in any task

## Remember
- Exact file paths always
- Complete code in every step — if a step changes code, show the code
- Exact verification steps with expected output
- DRY, YAGNI

## Light Mode

When routing classifies the task as **light**, compress the plan:

1. **Skip** scope check — task is already well-defined
2. **Skip** file structure discussion — go straight to tasks
3. **Compact task format** — simple checklists without elaborate code blocks for obvious changes. Still include file paths and verification steps.
4. **Skip self-review** for plans with fewer than 5 tasks
5. **Plan header** still required (Goal, Architecture, Tech Stack) but can be 1 line each

Light mode plans are shorter but still executable by someone with zero codebase context. No placeholders, no vagueness — just less ceremony around structure.

## Self-Review

After writing the complete plan, review with fresh eyes:

**1. Spec coverage:** Skim each section/requirement in the spec. Can you point to a task that implements it? List any gaps.

**2. Placeholder scan:** Search your plan for red flags — any of the patterns from the "No Placeholders" section. Fix them.

**3. Type consistency:** Do the types, method signatures, and property names you used in later tasks match what you defined in earlier tasks? A function called `ClearLayers()` in Task 3 but `ClearFullLayers()` in Task 7 is a bug.

If you find issues, fix them inline. If you find a spec requirement with no task, add the task.

**For complex plans:** Consider dispatching a plan-reviewer subagent (see `plan-reviewer-prompt.md`) for thorough independent review.

## Chaining

**Reads handoff from:** `.claude/handoffs/*-to-plan.md`
**Writes handoff to:** `.claude/handoffs/plan-to-execute.md`
**Chains to:** `execute`

After saving the plan, write a handoff file:

```markdown
---
from: plan
to: execute
plan: <path to plan doc>
---

- **Decisions:** [mode recommendation (direct/delegate/dispatch), task count, coupling assessment]
- **Files touched:** [all files listed in the plan — create and modify]
- **User preferences:** [any execution preferences expressed during planning]
- **Skip:** execute plan review (already written by plan skill)
```

Then suggest-and-confirm with execution choice:

> "Plan saved to `<path>`. Two execution options:
> 1. **Delegate mode** — subagent per task with review cycles
> 2. **Direct mode** — sequential execution with checkpoints
>
> Proceed with one of these?"

Use the `execute` skill with the chosen mode.
