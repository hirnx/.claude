---
name: refactor
description: Use when refactoring source files to improve quality, performance, and maintainability while preserving behavior. Triggers on "refactor this", "clean up", "improve this file".
---

# Refactor

## Overview

Refactors source files to improve code quality, performance, and maintainability while preserving identical behavior. Analyzes against a pattern library and produces a detailed change report.

## When to Use

- User says "refactor this", "clean up this code", "improve this file"
- User provides source files for refactoring

**Do NOT use when:**
- Auto-generated files
- Third-party library code
- Files under 20 lines
- Changes require behavior modification (use design/plan instead)

---

## Iron Law

**Same behaviour, better code.** Never change what the code does — only change HOW it does it.

## Input

User provides file paths to refactor. If not provided, ask which files. Read each file FULLY before making any changes.

**Skip:** Auto-generated files, third-party library code, files <20 lines.

---

## Process

### Step 1: Analyze (before touching anything)

Read the full file and identify:
1. What does this class/module do? (one sentence)
2. What lifecycle or framework methods does it use?
3. What other components/modules does it depend on?
4. Current size (lines, methods/functions, fields)
5. Component type: Manager / Controller / View / Data / Utility

### Step 2: Identify applicable patterns

Scan the file against these refactoring patterns (apply only what fits):

**Cache expensive operations:**
- Repeated expensive lookups — cache the result

**Extract & split:**
- Class >300 lines or >3 unrelated method groups — split into focused components
- Method >30 lines — extract sub-methods

**Event-driven over polling:**
- Loops checking state changes via booleans — convert to events/callbacks

**State machine over boolean soup:**
- Multiple booleans managing state — replace with enum + state machine

**Interface extraction:**
- Multiple concrete type checks — extract interface

**Encapsulation:**
- Public fields that should be private with accessors

**Collection optimization:**
- LINQ / iteration in hot paths — manual loops with pre-allocated collections
- String concatenation in loops — use builders

**Constants:**
- Magic numbers — extract to constants

**Dead code removal:**
- Unused imports, commented-out code, empty methods, unreachable code

**Early returns:**
- Deep nesting (>3 levels) — flatten with guard clauses

If platform patterns are loaded, also check platform-specific refactoring patterns.

### Step 3: Apply

Apply refactoring. If class needs splitting, create new files with proper namespace and using statements.

### Step 4: Verify

- Same public API preserved
- Code compiles logically
- No behaviour changed
- Serialized/persisted field names preserved if applicable (renaming may break references)

### Step 5: Report

```
============================================
   CODE REFACTOR REPORT
============================================

Files Refactored: [count]

PER FILE:

[filename]
  Before: [X lines, Y methods, Z fields]
  After:  [X lines, Y methods, Z fields]

  Changes:
  1. [PATTERN] - [what changed] — Why: [reason]
  2. ...

  New files created (if split):
  - [NewFile] - [purpose]

IMPACT:
- Lines: [before] > [after]
- Components split: [count]

MANUAL VERIFICATION NEEDED:
- Run tests to verify behaviour unchanged
- Check any serialized/persisted field references
```

---

## Rules

- NEVER change behaviour — refactoring = same output, better structure.
- Preserve public API — don't rename public methods/properties others may use.
- Serialized field caution — changing field names/types may break persistence. Note in report.
- Preserve framework lifecycle methods — don't rename them.
- One step at a time — prioritize by impact, don't refactor everything at once.
- Ask if unsure — if a refactoring might change behaviour, flag it and ask.
- After refactoring, update `.claude/context/` docs per the rules in `CLAUDE.md`.

## Platform Patterns

If the project has a `.claude/project-profile.md`, load platform-specific patterns from `~/.claude/skills/refactor/patterns/` matching the platform. These add framework-specific refactoring patterns and verification steps.

Available: `patterns/unity-csharp.md`
