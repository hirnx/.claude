---
name: git-assist
description: Use when performing local git operations — creating branches, pulling/merging from branches, resolving conflicts, switching branches, stashing, or viewing status/log/diff.
---

# Git Assist

## Overview

AI-assisted local git operations. Creates branches, pulls from remote branches with contextual conflict resolution, switches branches, stashes work, and shows status/log/diff — all without ever committing, pushing, or deleting anything.

**Core principle:** Local only, stage only, delete nothing. The user commits and pushes manually. Claude handles everything up to that point.

## Iron Laws

```
1. NEVER run `git commit` — user commits manually
2. NEVER run `git push` — not even branches, not even tags, NOTHING to remote
3. NEVER run `git branch -d`, `git branch -D`, or any branch deletion
4. NEVER run `git push origin --delete` or any remote deletion
5. NEVER run `git tag -d` or any tag deletion
6. NEVER modify protected branches (develop, main, master, release/*, Release_*)
7. NEVER switch/create branches with uncommitted changes — STOP and tell user to commit or stash first

These apply in ALL modes, including bypass/dangerous permission mode.
No exceptions. Not even if the user explicitly asks.
```

**Protected branches are SOURCE-ONLY.** Pull FROM them, never merge INTO them, never checkout and modify them directly. Before any merge/checkout operation, check the current and target branch against protected patterns.

## When to Use

- "Create a branch", "new branch", "make a test branch"
- "Pull from develop", "merge develop", "sync with develop"
- "Switch to X", "checkout X"
- "Stash my changes", "pop stash"
- "Show status", "show log", "what changed"
- "Resolve conflicts", "help with merge conflicts"
- User invokes `/git-assist`

**Do NOT use when:**
- Merging feature INTO develop/main (that's a PR workflow)
- Rebasing (different workflow)
- Cherry-picking specific commits
- Any operation that modifies the remote

---

## Operations

### Operation: Create Branch

**Triggers:** "create branch", "new branch", "make a test branch", "branch off"

```bash
git checkout -b <branch-name>
```

**Rules:**
- If no name provided, ask for one
- Suggest names following project convention: `feature/`, `test/`, `demo/`, `fix/`
- If creating from a specific base: `git checkout -b <name> <base>`
- **If uncommitted changes exist (staged or unstaged): STOP.** Tell user: "You have uncommitted changes. Commit or stash them before creating a new branch." Do NOT proceed.
- Report the new branch name and base commit

**Never:**
- Push the new branch to remote (`git push -u origin`) — user does this manually
- Delete the branch they were on

---

### Operation: Switch Branch

**Triggers:** "switch to", "checkout", "go to branch"

```bash
git checkout <branch-name>
```

**Rules:**
- **If uncommitted changes exist (staged or unstaged): STOP.** Tell user: "You have uncommitted changes. Commit or stash them before switching branches." Do NOT proceed. Do NOT offer to carry changes over.
- If branch doesn't exist locally, check if it exists on remote and offer to track it: `git checkout -b <name> origin/<name>`
- Show what branch they switched from and to

**Never:**
- Switch branches with uncommitted changes — EVER
- Force checkout (`git checkout -f`) — EVER, regardless of user request

---

### Operation: Pull / Merge from Branch

**Triggers:** "pull from", "merge X into", "sync with", "update from"

This is the full merge-with-conflict-resolution flow.

#### Step 1: Pre-Flight

```bash
git status
git branch --show-current
git rev-parse HEAD
```

| Condition | Action |
|-----------|--------|
| Uncommitted changes | **STOP.** "Commit or stash first." |
| Already in merge state | **STOP.** "Merge in progress. Abort or resolve first." |
| Current branch is protected | **STOP.** "You're on `<branch>`, a protected branch. Switch to a working branch first." |
| Clean | Proceed |

#### Step 2: Fetch & Analyze

```bash
git fetch origin
git log --oneline HEAD..origin/<source> -- | head -20
```

Show incoming commits. If `--dry-run`, stop here.

#### Step 3: Merge

**Try fast-forward first:**
```bash
git merge origin/<source> --ff-only
```

If ff fails, fall back:
```bash
git merge origin/<source> --no-commit
```

| Outcome | Action |
|---------|--------|
| Fast-forward | Report success. Done. |
| Clean merge | Report staged changes. Done. |
| Conflicts | Enter conflict resolution (Step 4) |

#### Step 4: Conflict Resolution

**4a — Inventory:** List all conflicted files, classify by type:

| File Type | Classification |
|-----------|---------------|
| `.cs` | Code conflict — full contextual analysis |
| `.asset` / `.prefab` | Unity data — component-level YAML analysis |
| `.meta` | Meta — follows paired asset/script decision |
| Binary | Binary — take one side only |
| Other text | Standard diff analysis |

**4b — Analyze:** For each conflict, read the file, read git log for both sides, understand WHY each side changed.

**4c — Present conflict cards:**

```
═══ CONFLICT <N> of <total> ═══
File: <path>
Type: <classification>
Hunks: <count>

OURS (<current-branch>):
  <what our side did, in plain language>
  Commit(s): <hash> "<message>"

THEIRS (<source>):
  <what their side did, in plain language>
  Commit(s): <hash> "<message>"

RECOMMENDATION: <what Claude thinks and why>

  [A] <recommended option>
  [B] <alternative>
  [C] <alternative>
  [D] Show raw diff
  [E] Skip — resolve manually later
═══════════════════════════
```

**Option rules:**
- Recommended option is always [A]
- Always include "Show raw diff" and "Skip"
- Never exceed 5 options
- Unity .asset/.prefab: component-level analysis, usually take-one-side
- Binary: can only take one side
- `.meta` files: follow paired asset/script decision

**4d — Apply decisions:**

| Choice | Action |
|--------|--------|
| Keep ours | `git checkout --ours <file> && git add <file>` |
| Keep theirs | `git checkout --theirs <file> && git add <file>` |
| Keep both | Intelligently merge using code understanding, write file, `git add <file>` |
| Raw diff | Show conflict markers, wait for instructions |
| Skip | Leave conflicted |
| Batch | "keep theirs for all .asset files" — apply rule, show summary |

**4e — Verify:** Read resolved files, check for remaining markers, duplicate signatures, missing usings.

#### Step 5: Summary

```
═══ MERGE SUMMARY ═══
Source: origin/<source> → <current-branch>
Incoming commits: <N>
Conflicts resolved: <N> of <N>
  <file> — <decision>

All resolved files are staged. Review with `git diff --staged`.
Commit manually when ready.
═══════════════════════
```

**Do NOT commit. Do NOT push. Skill ends at staging.**

#### Rollback

```bash
git merge --abort
```

Always available. Always ask before running.

---

### Operation: Stash

**Triggers:** "stash", "save my changes", "stash and switch"

| Action | Command |
|--------|---------|
| Stash current changes | `git stash push -m "<description>"` |
| List stashes | `git stash list` |
| Pop latest stash | `git stash pop` |
| Apply specific stash | `git stash apply stash@{N}` |

**Rules:**
- Always use `-m` with a descriptive message when stashing
- Show what was stashed (file count, summary)
- When popping, warn if there might be conflicts
- **Never** drop stashes (`git stash drop`) — user does this manually

---

### Operation: Status / Log / Diff

**Triggers:** "status", "what changed", "show log", "diff", "show me"

| Request | Command |
|---------|---------|
| Status | `git status` |
| Recent log | `git log --oneline -20` |
| Diff (unstaged) | `git diff` |
| Diff (staged) | `git diff --staged` |
| Diff vs branch | `git diff <branch>` |
| File history | `git log --oneline -- <file>` |
| Branch list | `git branch -a` |

Present results cleanly. For large diffs, summarize by file then offer to show specific files in detail.

---

## Quick Reference

| Operation | What it does | What it NEVER does |
|-----------|-------------|-------------------|
| Create branch | `git checkout -b` locally | Push to remote |
| Switch branch | `git checkout` | Force checkout without asking |
| Pull/Merge | Fetch + merge + resolve conflicts | Commit or push |
| Stash | Save/restore work-in-progress | Drop stashes |
| Status/Log/Diff | Read-only info | Nothing destructive |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Auto-resolving conflicts | NEVER — user decides every conflict |
| Any operation with uncommitted changes | STOP — user must commit or stash first, never proceed |
| Forgetting to check protected branch | Iron Law check runs FIRST |
| Pushing new branch to remote | NEVER — user pushes manually |
| Deleting branches | NEVER — not even merged ones |
| Force checkout losing changes | Always warn, offer stash |

## Red Flags

**Never:**
- **Run `git commit` — EVER**
- **Run `git push` — EVER (not branches, not tags, NOTHING to remote)**
- **Run `git branch -d` or `git branch -D` — EVER (no branch deletion)**
- **Run `git push origin --delete` — EVER**
- **Merge INTO protected branches (develop, main, master, release/*, Release_*)**
- **Switch branches or create branches with uncommitted changes — STOP and tell user to commit/stash first**
- **Run `git reset --hard` — EVER**
- **Run `git checkout -f` — EVER**
- **Drop stashes (`git stash drop`)**
- Auto-resolve conflicts without user confirmation
- Modify files that aren't part of a conflict

## Integration

**Triggered by:** `/git-assist` command ONLY. No auto-detection hook — this skill never runs unless explicitly invoked.
**Related skills:**
- `quality-gate` — run after merge to verify quality
- `error-fix` — if merged code has compiler errors
