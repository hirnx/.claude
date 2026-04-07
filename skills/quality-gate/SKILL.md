---
name: quality-gate
description: Use when work is ready to merge — pre-merge quality review with fresh-context code review, automated pattern checks, and known footgun matching. Auto-triggers on merge-related prompts.
---

# Quality Gate

## Overview

Fresh-context quality review before merging to any branch. Combines AI code review with automated pattern checks and project-specific footgun matching.

**Core principle:** Catch issues before they reach the target branch — not after.

## When to Use

- User says "merge", "ready to merge", "done with feature", "branch is ready", "let's merge to develop"
- User invokes `/pre-merge`
- After completing a feature branch (auto-suggested by routing)

**Do NOT use when:**
- Work is still in progress (use verify instead)
- Code review feedback is being addressed (use review instead)

---

## Step 0: Check for Handoff

1. Look for `.claude/handoffs/*-to-quality-gate.md`
2. If found → read it, pre-load what was implemented and files changed
3. If not found → gather context from git diff

After consuming the handoff, delete the handoff file.

---

## The Process

### Step 1: Gather Scope

Determine what's being merged and into which branch:

```bash
# What branch are we on?
rtk git branch --show-current

# Detect merge target
# hotfix/* → likely merging into release/* branch
# feature/* → likely merging into develop
# If unclear → ask the user
```

**Target branch detection:**
- `hotfix/*` branch → diff against the corresponding `release/*` branch
- `feature/*` branch → diff against `develop`
- If ambiguous → ask: "Which branch are you merging into?"

```bash
# What's changed vs target branch?
rtk git diff <target-branch> --stat

# Full diff for review
rtk git diff <target-branch>
```

If the diff is too large, focus on `.cs` files first, then data/config files.

### Step 2: Automated Pattern Checks

Run these checks against the diff. Categorize findings as BLOCKER, WARNING, or INFO.

Also read `~/.claude/context/quality-checks.md` (if exists) for additional checks added by the postmortem skill.

**BLOCKER (must fix before merge):**

| Check | How | Why |
|---|---|---|
| Merge conflict markers | Grep for `<<<<<<<`, `=======`, `>>>>>>>` in changed files | Broken code |
| Orphaned .meta files | For each added/deleted asset file, verify matching .meta exists/removed | Unity build breaks |
| Known test data patterns | Grep changed files for: `localhost`, `isTest.*true`, `// TEST_DATA`, `999`, `test_`, known test server URLs | Test data in production |
| Debug.Log in production code | Grep changed `.cs` files (excluding Editor/) for `Debug.Log\|Debug.LogWarning\|Debug.LogError` without `#if` guard | Console spam in production |
| Missing SetDirty | In changed Editor/ `.cs` files, find SO field assignments without nearby SetDirty call | Editor changes lost |

**WARNING (should fix):**

| Check | How | Why |
|---|---|---|
| Null reference risks | In changed code, find `.something` access on results of `GetComponent`, `Find`, casts (`as`), dictionary lookups without null checks | Runtime crashes |
| Long methods | Changed methods exceeding 60 lines | Maintainability |
| Code duplication | Compare new code against existing patterns in the same system | Divergent implementations |
| Missing localization | New user-facing strings (in UI code) without localization keys | Untranslated text |
| Unused variables | Variables declared but never used in changed files | Dead code |
| Coroutine cleanup | New coroutines started without matching StopCoroutine/StopAllCoroutines in OnDestroy | Memory leaks |

**INFO (worth knowing):**

| Check | How |
|---|---|
| Files changed count | From git diff --stat |
| Blast radius summary | For each changed public method, count callers |
| Breaking changes | Public API signature changes |

### Step 3: Fresh-Context Code Review

Dispatch the `code-reviewer` agent with the enhanced checklist. Provide:
- Full diff (or summary if too large)
- List of automated check results from Step 2
- Any change manifest from the implementation session (if available)
- Known footguns from `~/.claude/context/footguns.md` (if exists)
- Quality checks from `~/.claude/context/quality-checks.md` (if exists)

The code-reviewer should specifically check:
1. **Blast radius** — are all callers of changed methods still compatible?
2. **Data integrity** — any SO/config changes that need validation?
3. **Architecture** — do changes respect existing patterns?
4. **Edge cases** — null handling, empty collections, boundary conditions

### Step 4: Generate Report

Present findings in structured format:

```
═══ QUALITY GATE REPORT ═══

BLOCKERS (must fix):
  ✗ [description] — [file:line]

WARNINGS (should fix):
  ⚠ [description] — [file:line]

INFO:
  ℹ [summary]

CHANGE SUMMARY:
  [Auto-generated summary of what changed and why]
  [Breaking changes highlighted]

RECOMMENDATION: PASS / FIX REQUIRED
════════════════════════════
```

### Step 5: Iteration Loop

If BLOCKERS or WARNINGS exist:

1. Present the report
2. User fixes issues (or asks Claude to fix them)
3. After fixes, re-run Steps 2-4 automatically
4. Repeat until clean (or user explicitly accepts remaining warnings)

**Do NOT skip the re-run.** Fixes can introduce new issues.

---

## Quick Mode

When invoked with `/pre-merge --quick` or when user says "quick check":
- Run ONLY BLOCKER checks (Step 2 blockers)
- Skip fresh-context code review (Step 3)
- Skip change summary generation
- Output: PASS (no blockers) or FAIL (blockers found)

Target: under 30 seconds.

---

## Quick Reference

| Step | Key Activities | Success Criteria |
|------|---------------|------------------|
| 1 | Gather diff scope | Know what's changing |
| 2 | Automated checks | All BLOCKERS identified |
| 3 | AI code review | Structural issues caught |
| 4 | Report | Clear PASS/FAIL with reasons |
| 5 | Iteration | Re-run until clean |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping re-run after fixes | Always re-run — fixes can introduce new issues |
| Treating all warnings as blockers | Only blockers prevent merge |
| Running on wrong branch | Verify branch before starting |
| Reviewing against main instead of develop | Always diff against develop |
| Alert fatigue from false positives | Keep BLOCKER list tight — high confidence only |

## Red Flags

**Never:**
- Claim "PASS" without running checks
- Skip the iteration loop
- Ignore BLOCKER findings
- Run quality gate on uncommitted changes (commit first)

## Integration

**Auto-triggered by:** UserPromptSubmit hook (merge keywords)
**Manually triggered by:** `/pre-merge` command
**Related skills:**
- `review` — code review skill (quality-gate uses code-reviewer agent)
- `verify` — verification before completion claims
- `postmortem` — if issues found in production, feeds back into quality checks
