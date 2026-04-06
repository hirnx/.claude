---
name: release-gate
description: Use when preparing a release or build — checks branch safety, data validation, localization sync, and debug code. Auto-triggers on release-related prompts.
---

# Release Gate

## Overview

Release readiness validation. Checks everything that could go wrong between "code works on develop" and "build ships to users."

**Core principle:** GO / NO-GO with specific reasons. No ambiguity.

## When to Use

- User says "release", "ready for release", "give build", "cut release", "prepare build", "ready to ship"
- User invokes `/release-check`
- Before any production build

**Do NOT use when:**
- Merging a feature branch (use quality-gate instead)
- Still implementing features (use verify instead)

---

## The Process

### Step 1: Environment Check

```bash
# Current branch
rtk git branch --show-current

# Working directory clean?
rtk git status

# Last release tag
rtk git tag --sort=-creatordate | head -5
```

**Immediate NO-GO if:**
- Working directory is dirty (uncommitted changes)
- On wrong branch (should be develop or release/*)

### Step 2: Branch Safety

Check for unmerged branches that should be in this release:

```bash
# Find all hotfix/release branches
rtk git branch -a | grep -E "hotfix/|release/"

# For each, check if merged into current branch
rtk git branch --merged
rtk git branch --no-merged
```

**NO-GO if:** Any hotfix/* branch is not merged into the release branch.

### Step 3: Data Validation

Also read `.claude/context/quality-checks.md` (if exists) for additional release-specific checks added by the postmortem skill.

Scan for data integrity issues:

| Check | How | Severity |
|---|---|---|
| Test data in SOs | Grep `.asset` files for known test patterns | NO-GO |
| Uncommitted .asset files | Compare .asset files on disk vs staged | NO-GO |
| Suspicious config values | Grep for localhost, 127.0.0.1, test URLs in config files | NO-GO |
| SO field validation | Check for empty required fields, zero values where non-zero expected | WARNING |

### Step 4: Code Safety

| Check | How | Severity |
|---|---|---|
| Debug.Log without guards | Grep `.cs` files (non-Editor) for unguarded Debug.Log | WARNING |
| #if UNITY_EDITOR leaks | Check for UNITY_EDITOR blocks in runtime code that affect logic | WARNING |
| TODO/HACK/FIXME markers | Grep for these in changed files since last tag | INFO |

### Step 5: Localization Check

```bash
# Were any localization-related files changed since last tag?
rtk git diff <last-tag> --name-only | grep -i "local"
```

If localization files changed:
- **WARNING:** "Localization files modified. Confirm Google Sheet has been synced."

### Step 6: Diff Summary

```bash
# Full diff from last release
rtk git diff <last-tag> --stat
rtk git log <last-tag>..HEAD --oneline
```

Generate a release summary: features added, bugs fixed, breaking changes.

### Step 7: Verdict

```
═══ RELEASE GATE REPORT ═══

BRANCH: [current branch]
LAST RELEASE: [tag]
COMMITS SINCE: [count]

NO-GO ITEMS:
  ✗ [description]

WARNINGS:
  ⚠ [description]

RELEASE SUMMARY:
  [Features, fixes, breaking changes]

VERDICT: GO ✓ / NO-GO ✗
═════════════════════════════
```

---

## Quick Reference

| Step | Key Activities | Success Criteria |
|------|---------------|------------------|
| 1 | Environment check | Correct branch, clean directory |
| 2 | Branch safety | All hotfixes merged |
| 3 | Data validation | No test data, all assets committed |
| 4 | Code safety | No debug leaks |
| 5 | Localization | Sheet synced |
| 6 | Diff summary | Clear picture of what's shipping |
| 7 | Verdict | Unambiguous GO/NO-GO |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Releasing from wrong branch | Always check current branch first |
| Forgetting hotfix merge-back | Branch safety check catches this |
| Skipping localization sync | Localization check reminds you |
| Releasing with dirty working directory | Environment check catches this |

## Integration

**Auto-triggered by:** UserPromptSubmit hook (release keywords)
**Manually triggered by:** `/release-check` command
**Related skills:**
- `quality-gate` — pre-merge review (should run before release-gate)
- `postmortem` — if release issues found, feeds back into checks
