---
name: review
description: Use when requesting or receiving code review — covers dispatching the code-reviewer agent and handling feedback with technical rigor.
---

# Review

## Overview

Full code review cycle: requesting review by dispatching the `code-reviewer` agent, and handling incoming feedback with technical rigor — verify before implementing, push back when wrong.

**Core principle:** Review early, review often. Verify before implementing. Technical correctness over social comfort.

---

## Step 0: Check for Handoff

Before starting, check for a handoff file:

1. Look for `.claude/handoffs/execute-to-review.md`
2. If found → read it, pre-load what was implemented and files changed
3. If not found → run full process as normal

| Handoff field | What it skips |
|---|---|
| Decisions (what was implemented) | "What did you change?" gathering |
| Files touched | File discovery — already listed |
| User preferences | Context about deviations from plan |

After consuming the handoff, delete the handoff file.

---

## Requesting Review

### When to Request

**Mandatory:**
- After each task in delegated execution
- After completing a major feature
- Before finalizing significant work

**Optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing complex bug

### How to Request

**1. Gather context:**
- What was implemented (summary)
- What was the plan/spec (requirements)
- Which files were changed

**2. Dispatch code-reviewer agent:**

Use the agent definition at `~/.claude/agents/code-reviewer.md`. Provide:
- `{WHAT_WAS_IMPLEMENTED}` — what you just built
- `{PLAN_OR_REQUIREMENTS}` — what it should do
- `{DESCRIPTION}` — brief summary
- List of changed files

**3. Act on feedback:**
- Fix Critical issues immediately
- Fix Important issues before proceeding
- Note Suggestions for later
- Push back if reviewer is wrong (with reasoning)

### Integration with Workflows

| Workflow | When to review |
|----------|---------------|
| Delegate mode (execute skill) | After EACH task |
| Direct mode (execute skill) | After each batch (~3 tasks) |
| Ad-hoc development | Before finalizing |

---

## Receiving Review

### The Response Pattern

```
WHEN receiving code review feedback:

1. READ: Complete feedback without reacting
2. UNDERSTAND: Restate requirement in own words (or ask)
3. VERIFY: Check against codebase reality
4. EVALUATE: Technically sound for THIS codebase?
5. RESPOND: Technical acknowledgment or reasoned pushback
6. IMPLEMENT: One item at a time, verify each
```

### Forbidden Responses

**NEVER:**
- "You're absolutely right!"
- "Great point!" / "Excellent feedback!"
- "Let me implement that now" (before verification)

**INSTEAD:**
- Restate the technical requirement
- Ask clarifying questions
- Push back with technical reasoning if wrong
- Just start working (actions > words)

### Handling Unclear Feedback

```
IF any item is unclear:
  STOP - do not implement anything yet
  ASK for clarification on unclear items

WHY: Items may be related. Partial understanding = wrong implementation.
```

### Source-Specific Handling

**From the user:**
- Trusted — implement after understanding
- Still ask if scope unclear
- Skip to action or technical acknowledgment

**From external reviewers:**
```
BEFORE implementing:
  1. Check: Technically correct for THIS codebase?
  2. Check: Breaks existing functionality?
  3. Check: Reason for current implementation?
  4. Check: Does reviewer understand full context?

IF suggestion seems wrong:
  Push back with technical reasoning

IF conflicts with user's prior decisions:
  Stop and discuss with user first
```

### Implementation Order

```
FOR multi-item feedback:
  1. Clarify anything unclear FIRST
  2. Then implement in this order:
     - Blocking issues (breaks, security)
     - Simple fixes (typos, imports)
     - Complex fixes (refactoring, logic)
  3. Verify each fix individually
  4. Verify no regressions
```

### When to Push Back

Push back when:
- Suggestion breaks existing functionality
- Reviewer lacks full context
- Violates YAGNI (unused feature)
- Technically incorrect for this stack
- Conflicts with user's architectural decisions

**How:** Technical reasoning, not defensiveness. Ask specific questions. Reference working code. Involve user if architectural.

### Acknowledging Correct Feedback

```
✅ "Fixed. [Brief description of what changed]"
✅ "Good catch - [specific issue]. Fixed in [location]."
✅ [Just fix it and show in the code]

❌ "You're absolutely right!"
❌ "Great point!"
❌ ANY gratitude expression
```

---

## Red Flags

**Never:**
- Skip review because "it's simple"
- Ignore Critical issues
- Proceed with unfixed Important issues
- Blindly implement without verification
- Performatively agree with feedback

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Performative agreement | State requirement or just act |
| Blind implementation | Verify against codebase first |
| Batch without testing | One at a time, verify each |
| Assuming reviewer is right | Check if breaks things |
| Avoiding pushback | Technical correctness > comfort |

## Integration

**Related skills:**
- `execute` — includes review as part of delegate mode
- `verify` — verify work before claiming completion
