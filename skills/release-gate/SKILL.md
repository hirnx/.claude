---
name: release-gate
description: Use when preparing a release or build — full cumulative diff review, branch safety, data validation, cross-commit pattern detection, and risk scoring. Auto-triggers on release-related prompts.
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

## Step 0: Check for Handoff

1. Look for `.claude/handoffs/*-to-release-gate.md`
2. If found → read it, pre-load quality-gate findings if quality-gate ran first
3. If not found → run full process as normal

After consuming the handoff, delete the handoff file.

---

## The Process

### Step 1: Environment Check

```bash
# Current branch
rtk git branch --show-current

# Working directory clean?
rtk git status

# Find last release commit (by commit message, not tag)
# Case-insensitive, matches variations: "Release 1.2.3", "release 1.2.3 (v5)", "Live 0.154.0 v154", etc.
rtk git log --oneline --grep="[Rr]elease\|[Ll]ive" | head -10
```

**Finding the last release commit:** This project uses commit messages instead of git tags. The message format varies — "Release x.y.z", "release x.y.z", "Release x.y.z (vy)", "Live x.y.z vN", etc. Do a case-insensitive search for "release" and "live" in commit messages. Present the matches to the user and confirm which one is the last release baseline.

Store this commit SHA as `<last-release>` — all subsequent steps use it as the baseline.

**Immediate NO-GO if:**
- Working directory is dirty (uncommitted changes)
- On wrong branch (should be develop or release/*)

**If no release commit found:** Ask the user for a reference commit to use as the baseline.

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

Also read `~/.claude/context/quality-checks.md` (if exists) for additional release-specific checks added by the postmortem skill.

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
rtk git diff <last-release> --name-only | grep -i "local"
```

If localization files changed:
- **WARNING:** "Localization files modified. Confirm Google Sheet has been synced."

### Step 6: Full Release Diff Review

Review everything that changed between the last release and current HEAD. This is the most important step — it catches issues that individual commits or quality-gate runs may have missed.

**Priority order: Cumulative state first, then per-commit analysis.** Individual commits may each be clean, but the combined result is what ships. Always review the cumulative diff before drilling into commits.

#### Phase A: Cumulative State Review (HIGHEST PRIORITY)

**This is the most critical phase.** Two commits can each be individually correct but produce a broken state when combined. Example: commit 1 adds a null check that returns early, commit 2 adds logic after it that assumes execution continues — each is fine alone, together it's dead code or a logic error.

```bash
# The FULL cumulative diff — this is what's actually shipping
rtk git diff <last-release>..HEAD
```

Review the cumulative diff as if it were a single massive code review. Focus on:

1. **Combined logic correctness** — Does the total set of changes make sense together? Do additions from different commits interact correctly?
2. **State consistency** — Are all variables, fields, and configs in a valid final state? Something set in commit A and overwritten in commit B — is the final value correct?
3. **Complete feature integration** — For each new feature across commits: is it fully wired? Are there loose ends (methods defined but never called, events subscribed but never fired)?
4. **Data-code alignment** — Do SO/config values match what the code expects in its final state?
5. **Cumulative null safety** — New code paths added across commits: are all null checks consistent in the combined flow?
6. **Cumulative API surface** — Public methods added/changed across commits: is the final API clean and consistent?

**Read changed files in their current state, not just the diff.** The diff shows what changed, but reading the full file reveals how changes from different commits sit together.

```bash
# List all changed files
rtk git diff <last-release>..HEAD --name-only

# For key files (especially those touched in multiple commits), read the full current state
```

#### Phase B: Per-Commit Analysis

```bash
# All commits since last release
rtk git log <last-release>..HEAD --oneline
```

Categorize each commit:
- **Feature** — new functionality
- **Fix** — bug fix
- **Data** — SO/config/asset only
- **Refactor** — structural, no behavior change
- **Unknown** — vague message, needs closer look

Score each commit as LOW / MEDIUM / HIGH risk:

| Signal | Risk |
|---|---|
| Large diff (20+ files) | HIGH |
| Vague message ("misc", "update", "fix") | HIGH |
| Touches shared/utility code | HIGH |
| Data-only commit (no code change) | MEDIUM — SetDirty risk |
| Late-stage commit (last 24h before release) | MEDIUM |
| Clean, small, clear message | LOW |

#### Phase C: Cross-Commit Pattern Detection

Scan the full commit range for these patterns:

| Pattern | What To Look For | Why It Matters |
|---|---|---|
| **Cumulative breakage** | Changes across commits that are individually safe but broken together | **The #1 thing to catch** — per-commit review misses this entirely |
| **File churn** | Same file modified in 3+ commits | Unstable area, higher regression risk — read the CURRENT state of these files |
| **Add-then-remove** | Code/data added in one commit, reverted in another | Debugging artifacts or incomplete work may remain |
| **Data without code** | `.asset`/`.json` changed but no corresponding `.cs` change | Data-code mismatch |
| **Code without data** | New code references SO fields that weren't updated | Runtime errors waiting to happen |
| **Config oscillation** | Config values changed back and forth | Which value is correct for production? |
| **Test data lifecycle** | Test markers (`// TEST_DATA`, `isTest`, `localhost`) added but never removed | Test data shipping to production |
| **Orphaned code** | New methods/classes added but never called | Dead code or missing integration |

#### Phase D: Focused Review

Based on cumulative review and patterns:

1. **Cumulative issues** → these are the highest priority, fix before release
2. **Hot files** (most churn) → read the FULL CURRENT file, not just diffs — the combined state matters
3. **HIGH risk commits** → read full diff with `rtk git show <sha>`
4. **Flagged patterns** → investigate the specific files involved
5. **LOW risk commits** → skim only

#### Phase E: Feed Into Verdict

All findings from Phases A-D feed into Step 7's consolidated report. Do not generate a separate report here — go straight to Step 7.

### Step 7: Consolidated Verdict

Combine ALL findings from Steps 1-6 into a single report:

```
═══ RELEASE GATE REPORT ═══

BRANCH: [current branch]
LAST RELEASE: [commit SHA + message]
COMMITS SINCE: [count]

STEPS 1-5 FINDINGS:
  NO-GO:
    ✗ [from Steps 1-5: branch safety, data, code, localization]
  WARNINGS:
    ⚠ [from Steps 1-5]

STEP 6 — CUMULATIVE REVIEW:
  CUMULATIVE STATE FLAGS:
    ✗ [issues where combined commits create a problem]
  CROSS-COMMIT FLAGS:
    ⚠ [pattern] — [files/details]
  COMMIT RISK:
    HIGH: [count] — [list]
    MEDIUM: [count]
    LOW: [count]
  HOT FILES:
    [file] — modified in [N] commits

RELEASE SUMMARY:
  Features: [list]
  Fixes: [list]
  Data/config changes: [list]
  Breaking changes: [list]

VERDICT: GO ✓ / NO-GO ✗
  [If NO-GO: specific items that must be resolved]
═════════════════════════════
```

### Step 8: Iteration Loop

If NO-GO items or critical CUMULATIVE STATE FLAGS exist:

1. Present the report
2. User fixes issues (or asks Claude to fix them)
3. After fixes, re-run Steps 3-7 (skip environment and branch checks — those don't change)
4. Repeat until clean or user explicitly accepts remaining warnings

**Do NOT skip the re-run.** Fixes can introduce new issues — especially cumulative state problems.

---

## Quick Reference

| Step | Key Activities | Success Criteria |
|------|---------------|------------------|
| 0 | Handoff check | Load quality-gate findings if available |
| 1 | Environment check | Correct branch, clean directory, release tag found |
| 2 | Branch safety | All hotfixes merged |
| 3 | Data validation | No test data, all assets committed |
| 4 | Code safety | No debug leaks |
| 5 | Localization | Sheet synced |
| 6 | Full release diff review | Cumulative state reviewed, commits scored, cross-commit patterns flagged |
| 7 | Consolidated verdict | Single report combining Steps 1-6, unambiguous GO/NO-GO |
| 8 | Iteration loop | Re-run after fixes until clean |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Releasing from wrong branch | Always check current branch first |
| Forgetting hotfix merge-back | Branch safety check catches this |
| Skipping localization sync | Localization check reminds you |
| Releasing with dirty working directory | Environment check catches this |
| Reviewing per-commit but skipping cumulative state | Phase A is HIGHEST PRIORITY — always do it first |
| Trusting that each clean commit means the release is clean | Commits interact — the cumulative state is what ships |
| Skipping re-run after fixes | Fixes can introduce new cumulative issues |
| No release tags exist, Step 6 breaks | Ask user for reference commit or use initial commit |

## Integration

**Auto-triggered by:** UserPromptSubmit hook (release keywords)
**Manually triggered by:** `/release-check` command
**Related skills:**
- `quality-gate` — pre-merge review (should run before release-gate)
- `postmortem` — if release issues found, feeds back into checks
