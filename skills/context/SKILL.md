---
name: context
description: Use when project-specific knowledge is discovered that should be persisted for future sessions — manages .claude/context/ docs.
---

# Context

## Overview

Manages project-local `.claude/context/` documentation. After tasks that reveal new project-specific knowledge (patterns, mappings, architecture decisions, integration details), this skill ensures that knowledge is captured for future sessions.

## When to Use

- After completing a task that revealed new project-specific knowledge
- When context docs need updating due to code changes
- When stale context docs should be cleaned up
- After feature migrations, system integrations, or architecture changes

**Do NOT use when:**
- The knowledge is already in the codebase (code comments, existing docs)
- The knowledge is derivable from git history
- The information is ephemeral (only relevant to current session)

---

## Process

### 1. Check existing context

Before writing anything, scan the project's Context table in its CLAUDE.md:
- Is there an existing doc this fits into?
- Would adding to an existing doc be clearer than creating a new one?

### 2. Write or update

**Fits existing file →** Add the new knowledge there. Keep it concise.

**New topic →** Create a new file at `<project>/.claude/context/<topic>.md`:
- Start with a `**Purpose:**` line explaining what this doc covers
- Use concise facts and mappings — no narrative
- Group related information logically

**Feature migration complete →** Create `<project>/.claude/context/migrations/<feature>.md` and add it to the index in `feature-migration.md`.

### 3. Update the Context table

Add or update the row in the project's CLAUDE.md Context table:

```
| `<path>` | <when to read this doc> |
```

### 4. Clean up stale docs

If the task revealed that existing context is outdated:
- Update facts that changed
- Remove docs that are no longer relevant
- Update the Context table accordingly

---

## Rules

- Context docs are **always project-local** (`<project>/.claude/context/`), never global
- Every doc must have a `**Purpose:**` line at the top
- Keep entries concise — facts and mappings only, no narrative
- One topic per file — don't create catch-all docs
- Check for staleness: if code has changed, context docs may need updating
