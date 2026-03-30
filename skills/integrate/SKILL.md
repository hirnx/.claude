---
name: integrate
description: Use when completing integration of a migrated system — wiring external callsites, callbacks, initialization, and event subscriptions. Triggers after code compiles but external wiring is missing.
---

# Integrate

## Overview

Completes the integration of a migrated system by discovering external callsites in the reference project, mapping them to the target project, and implementing them group by group. Handles "phase 2" after scripts are migrated and compiling.

## When to Use

- User says "complete integration", "wire up callbacks", "connect the migrated system"
- A system's scripts have been migrated and compile, but external wiring is missing
- Initialization callbacks, reward hooks, UI triggers, event subscriptions need connecting

**Do NOT use when:**
- Scripts don't compile yet (use error-fixer first)
- Building a new feature from scratch (use code-plan)
- Simple one-file integration (just do it directly)

---

## Input

The skill needs three pieces of information. Ask for any that aren't provided:

1. **System name** — e.g. "Event System"
2. **System folder path** in the target project — e.g. `src/features/events/`
3. **System namespace(s)** — e.g. `app.features.events`

Also check:
- The Reference Projects table in `CLAUDE.md` for the source project path
- The migrations context doc in `.claude/context/migrations/` for prior migration notes

---

## State File

All discovery and progress is persisted in:
`.claude/context/migrations/<system-slug>-integration.md`

This file survives across sessions. If it already exists from a previous run, read it and resume from where it left off instead of re-running discovery.

---

## Process

### Phase 1: Discover

**Goal:** Find every place in the reference project where the migrated system's classes are used *outside* the system itself.

1. Glob the system folder in the **target project** for all source files
2. Extract public class/interface names from each file (read the class declarations)
3. For each class name, use **LSP "Find All References"** in the **reference project**
   - LSP gives accurate callsite data — actual usages, not string matches
   - **Fallback:** If LSP is unavailable or returns incomplete results, fall back to Grep-based discovery. Note the fallback in the state file so the user knows results may include false positives
4. Filter out self-references — any hit inside the system folder itself
5. For each external hit, capture:
   - File path (relative to reference project root)
   - Line number
   - 1–2 line code snippet showing the usage
   - Which class and member (method/property/event) is being used
6. Auto-group findings by the reference file's folder or namespace:
   - e.g. `Managers/`, `OrderSystem/`, `Analytics/`, `FX/UI/`
   - Use folder structure as the primary grouping signal
7. Write findings to the state file:

```markdown
# <System> Integration Points

**Status:** Discovery complete — awaiting confirmation
**Source:** <reference project path>
**System folder:** <target project system folder path>
**System namespace(s):** <namespaces>
**Discovery method:** LSP | Grep (fallback)

## Group: <Category Name>
- [ ] **<ReferenceScript.cs>** — `<ClassName>.<MethodOrProperty>` used at line X
  - Snippet: `<1-2 line code snippet>`
  - Target equivalent: <pending>

## Group: <Category Name>
...

## Skipped (self-references filtered out)
<count> files excluded
```

8. Present the grouped findings to the user in the conversation

### Phase 2: Confirm

1. Present all groups to user for review
2. User can:
   - **Remove** integration points that aren't needed (e.g. debug-only utilities)
   - **Reorder** groups by priority
   - **Split or merge** groups
   - **Add** integration points the discovery missed
3. Update the state file with confirmed groups
4. State file status → `Confirmed — ready for implementation`

Do NOT proceed to Phase 3 until user explicitly confirms.

### Phase 3: Implement

Implement **all groups consecutively** without pausing between them. For each group:

**Step 1 — Read reference:**
Open the reference file(s) for this group. Read the relevant integration code:
- `using` statements
- Properties/fields referencing the system
- Method calls, event subscriptions, lifecycle hooks
- Any helper methods wrapping system calls

**Step 2 — Locate target equivalent:**
Use LSP/Grep to find the corresponding class in the target project.

If no exact match exists:
- Search for similar class names, method signatures, or folder structure
- If no candidate found at all: add to "unresolved" list, move to next integration point

**Step 3 — Read target file:**
Understand its current structure. Find the right insertion points — don't just append blindly.

**Step 4 — Implement:**
Add the integration code following project conventions:
- Import/using statement for the system's namespace/module
- Property/field to access the system
  - Use the project's standard dependency injection or reference pattern
- Method calls at the correct lifecycle points (match the reference's placement)
- Event subscriptions with proper cleanup (subscribe/unsubscribe or on/off patterns)
- Helper/wrapper methods if the reference uses them

**Step 5 — Update state file:**
Mark the integration point as `[x]` done with the target file path.

After **all groups** are implemented, proceed to Phase 3b. All feedback, review, and approval happens at the end — not between groups.

### Phase 3b: Platform-Specific Setup

After code integration, check if the migrated system requires platform-specific setup (asset loading, configuration, build settings, etc.).

If the project has a `.claude/project-profile.md`, load platform-specific integration patterns from `~/.claude/skills/integrate/patterns/` matching the platform.

Available: `patterns/unity-csharp.md` (Addressable assets, Inspector references, build settings)

If no platform patterns exist, check the reference project for any non-code setup requirements and produce a checklist for manual configuration.

### Phase 4: Finalize

After all groups are processed:

**1. Summary table:**

```
============================================
   INTEGRATION SUMMARY
============================================

System: <name>
Groups processed: <N>

| Group              | Status                    | Files Modified          |
|--------------------|---------------------------|-------------------------|
| <name>             | Done                      | <file1.cs>, <file2.cs>  |
| <name>             | Skipped — <reason>        | —                       |

Unresolved:
- <integration point> — <reason it couldn't be mapped>
```

**2. Context doc update:**
- Update state file status → `Complete` (or `Partial — N unresolved`)
- Each integration point marked done/skipped with target file path
- Update state file status

**3. Verification checklist:**
Generate concrete items tied to specific integration points:

```
============================================
   VERIFICATION CHECKLIST
============================================

- [ ] Build — confirm no compile errors
- [ ] <specific component> — assign required references/config
- [ ] Run — trigger <specific action>, verify <expected behavior>
- [ ] <specific UI/interface> — confirm visual elements work correctly
- [ ] <specific callback> — verify it fires at the right lifecycle moment
- [ ] Platform setup — complete items from Phase 3b checklist
...
```

Each item must be specific — no generic "test everything" entries.

**4. Final verification pass:**
Review every edited file. Check that each changed line is aligned with the task. Remove anything extra.

---

## Resuming a Previous Run

If `.claude/context/migrations/<system-slug>-integration.md` already exists:

1. Read it and check the status
2. If `Discovery complete — awaiting confirmation` → go to Phase 2
3. If `Confirmed — ready for implementation` → go to Phase 3, start from the first unchecked `[ ]` item
4. If `Complete` or `Partial` → inform user it's already done, ask if they want to re-run or extend

---

## Rules

- **Targeted file reads only** — state which files you plan to read and why. If >5 files, list and get confirmation.
- **Follow existing patterns** — match the target project's conventions, don't import the reference project's style.
- **One group at a time** — don't batch multiple groups without approval.
- **LSP first, grep fallback** — always try LSP for accurate callsite discovery. Note when falling back.
- **Ask when unsure** — if the target equivalent is ambiguous, ask. Don't guess file paths or class names.
- **Update context docs** — after completion, update `.claude/context/` per `CLAUDE.md` rules.
