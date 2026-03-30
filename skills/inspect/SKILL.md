---
name: inspect
description: Use when reviewing source files for issues, anti-patterns, and optimization opportunities. Triggers on "review this", "check this code", "is this OK".
---

# Inspect

## Overview

Reviews source files against a comprehensive checklist covering null safety, memory leaks, anti-patterns, performance, architecture, and code quality. Produces a scored report with actionable fixes.

## When to Use

- User says "review this", "check this code", "is this OK"
- User shares source files for feedback
- Before committing significant changes

**Do NOT use when:**
- Reviewing auto-generated files (build artifacts, lock files)
- Third-party library code

---

## Input

User provides file paths to review. If not provided, ask which files to review. Read each file fully before reviewing.

**Skip:** Auto-generated files, third-party library code, config files unless specifically changed.

---

## Review Checklist

### Critical Issues (must fix before commit)

**Null/undefined reference risks:**
- Accessing potentially null/undefined values without checks
- Uninitialized references used directly

**Memory leaks:**
- Event listeners registered but never removed
- Subscriptions not cleaned up on teardown/disposal
- Static references preventing garbage collection
- Resources opened but never closed

**Logic errors:**
- Infinite loops or unbounded recursion
- Race conditions in async code
- Missing break in switch cases

**Security:**
- Hardcoded API keys, tokens, passwords
- Unvalidated external input

### Anti-Patterns

Check against platform-specific anti-patterns if platform patterns are loaded. Generic anti-patterns:
- Expensive operations in hot paths (loops, frequent callbacks)
- String concatenation in loops — use builders
- Allocations in hot paths — pre-allocate
- Polling where events would work

### Architecture

- Class doing too many things — split into focused components
- Deep inheritance chains (>2 levels) — prefer composition
- Tight coupling between components — use events or interfaces
- Multiple booleans managing state — use state machine

### Code Quality

- Methods >30 lines — break into smaller methods
- Classes >500 lines — candidate for split
- Deep nesting (>3 levels) — use early returns
- Magic numbers — define as constants
- Unused imports, commented-out code, empty methods — remove

---

## Output Format

```
============================================
   CODE REVIEW REPORT
============================================

Files Reviewed: [count]

SCORE: [X/10] | [Excellent/Good/Needs Work/Poor]

CRITICAL ISSUES ([count])
  [If none: "None found"]
  1. [file:line] - [title]
     Problem: [what's wrong]
     Fix: [code or suggestion]

WARNINGS ([count])
  1. [file:line] - [title]
     Fix: [suggestion]

OPTIMIZATION ([count])
  1. [file:line] - [what to optimize]
     Impact: [High/Medium/Low]

GOOD PRACTICES FOUND
  - [things done well]

COMMIT RECOMMENDATION: [Safe to commit / Fix critical issues first / Needs refactoring]
```

---

## Rules

- Read the full file before reviewing — do not guess from snippets.
- Always include file name and line number.
- Provide fixes, not just complaints.
- Prioritize: Critical > Warnings > Optimization > Architecture > Quality.
- No false positives — only report real issues.
- Context matters — one-time setup code doesn't need hot-path optimization.
- Acknowledge good code to reinforce good patterns.
- After review, update `.claude/context/` docs per the rules in `CLAUDE.md` if review revealed new project knowledge.

## Platform Patterns

If the project has a `.claude/project-profile.md`, load platform-specific patterns from `~/.claude/skills/inspect/patterns/` matching the platform. These extend the generic checklist with framework-specific checks.

Available: `patterns/unity-csharp.md`
