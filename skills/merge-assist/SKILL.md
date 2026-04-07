---
name: merge-assist
description: "**[DEPRECATED]** Replaced by git-assist. Use when pulling changes from another branch, merging branches, or resolving merge conflicts — AI-assisted conflict analysis and resolution."
---

# Merge Assist

## Overview

AI-assisted branch merging with contextual conflict resolution. Fetches from a source branch, attempts fast-forward, and when conflicts arise, analyzes both sides using git history and code context to present intelligent resolution options to the user.

**Core principle:** The user always decides. Claude analyzes, recommends, and applies — never auto-resolves without confirmation. **Never commit or push — only stage.**

## Iron Law — Protected Branches

```
PROTECTED BRANCHES: develop, main, master, release/*, Release_*

These branches are SOURCE-ONLY. You may PULL FROM them, never MERGE INTO them.
```

**Before ANY merge operation, check the CURRENT branch (the target).** If the current branch matches any protected pattern: **STOP IMMEDIATELY.**

```
STOP. You are on '<branch>', which is a protected branch.
This skill only pulls FROM protected branches into feature/working branches.
It never merges INTO develop, main, or release branches.

Switch to your working branch first.
```

**No exceptions.** Not even if the user explicitly asks. If they insist, explain: "Merging into protected branches should go through a PR/MR workflow, not direct merge."

**This check runs BEFORE Step 1 (pre-flight). It is the very first thing that happens.**

## When to Use

- "Pull from develop", "merge develop into my branch", "update from develop"
- "Pull latest", "sync with develop", "bring in changes from X"
- "Resolve conflicts", "help with merge conflicts"
- User invokes `/merge-assist`

**Do NOT use when:**
- Merging feature into develop/main (that's a PR — use quality-gate instead)
- Rebasing (different workflow, not covered here)
- Cherry-picking specific commits

---

## Step 0: Parse Arguments

Parse `$ARGUMENTS` to extract:

- `source=<branch>` — branch to merge from. Defaults to `develop`. Accepts: branch name, `origin/branch`, or remote tracking ref.
- `--dry-run` — show what would happen without actually merging.

If no arguments provided, default source is `develop`.

---

## Step 1: Pre-Flight Checks

Before touching anything, verify the workspace is safe.

```bash
rtk git status
```

**Check for:**

| Condition | Action |
|-----------|--------|
| Uncommitted changes (staged or unstaged) | **STOP.** Tell user: "You have uncommitted changes. Commit or stash them first." Do NOT proceed. |
| Untracked files only | OK to proceed (untracked files won't conflict) |
| Clean working directory | OK to proceed |
| Already in a merge state | **STOP.** Tell user: "A merge is already in progress. Run `git merge --abort` to cancel it, or resolve the existing conflicts first." |

Record the current branch name and HEAD commit for rollback reference.

```bash
rtk git branch --show-current
rtk git rev-parse HEAD
```

---

## Step 2: Fetch & Analyze

Fetch the latest from remote and compare:

```bash
rtk git fetch origin
rtk git log --oneline HEAD..origin/<source> -- | head -20
```

**Three outcomes:**

| Outcome | Detection | Action |
|---------|-----------|--------|
| **Already up-to-date** | No commits in `HEAD..origin/<source>` | Report "Already up-to-date with `<source>`." and stop. |
| **Fast-forward possible** | Current HEAD is an ancestor of source tip | Go to Step 3A |
| **Merge required** | Branches have diverged (commits on both sides) | Go to Step 3B |

Show the user what's coming in:

```
Incoming from <source>: <N> commit(s)

  abc1234 feat: add daily reward popup
  def5678 fix: null check in GameManager
  ghi9012 chore: update balance sheet values
```

If `--dry-run`: show this summary and stop.

---

## Step 3A: Fast-Forward

```bash
rtk git merge origin/<source> --ff-only
```

Report success:

```
Fast-forward merge complete.
  <source> → <current-branch>
  <N> commit(s) applied.
  HEAD is now at <new-hash> <message>
```

Done. No conflicts possible in fast-forward. Do NOT commit or push.

---

## Step 3B: Merge (May Conflict)

```bash
git merge origin/<source> --no-commit
```

Using `--no-commit` so we can inspect before finalizing.

**Two outcomes:**

| Outcome | Detection | Action |
|---------|-----------|--------|
| **Clean merge** | Exit code 0, no conflict markers | Go to Step 4 (Clean) |
| **Conflicts** | Exit code 1, `git status` shows UU/AA/DD files | Go to Step 5 (Conflict Resolution) |

---

## Step 4: Clean Merge Summary

No conflicts. Show what merged:

```
Clean merge — no conflicts.

Files changed: <N>
  M  Assets/Scripts/GameManager.cs
  A  Assets/Prefabs/NewPopup.prefab
  M  Assets/Data/balance.asset
  ...

Incoming commits: <N>
  abc1234 feat: add daily reward popup
  def5678 fix: null check in GameManager
```

All changes are staged. Report:

```
All changes staged and ready. Review them with `git diff --staged`.
The user will commit manually when ready.
```

Do NOT commit. Do NOT push. The skill's job ends at staging.

---

## Step 5: Conflict Resolution

This is the core of the skill. Handle each conflict with full context.

### Step 5a: Inventory Conflicts

```bash
rtk git status
```

Build the conflict list. Classify each file:

| File Type | Classification | Resolution Strategy |
|-----------|---------------|---------------------|
| `.cs` source files | **Code conflict** | Full contextual analysis (Step 5b) |
| `.asset` / `.prefab` (Unity YAML) | **Unity data conflict** | Component-level analysis, usually take-one-side |
| `.meta` files | **Meta conflict** | Pair with corresponding asset — follow the asset's decision |
| Binary files (textures, audio) | **Binary conflict** | Can only take one side — ask user |
| Config / JSON / XML | **Config conflict** | Field-level analysis |
| Other text files | **Text conflict** | Standard diff analysis |

Present the inventory:

```
Conflicts detected: <N> file(s)

  [Code]   Assets/Scripts/GameManager.cs
  [Code]   Assets/Scripts/PlayerData.cs
  [Data]   Assets/Data/rewards.asset
  [Meta]   Assets/Scripts/NewClass.cs.meta
  [Binary] Assets/Textures/icon.png
```

### Step 5b: Analyze Each Conflict

For each conflicted file, build a **conflict card**. Process in this order:
1. Code conflicts first (most complex, need user attention)
2. Unity data conflicts
3. Meta/binary (often auto-resolvable based on earlier decisions)

**For each file:**

1. **Read the conflicted file** — find all `<<<<<<<` / `=======` / `>>>>>>>` blocks
2. **Count conflict hunks** — a file may have multiple conflict regions
3. **Read git log for both sides:**
   ```bash
   rtk git log --oneline HEAD..origin/<source> -- <file>
   rtk git log --oneline origin/<source>..HEAD -- <file>
   ```
4. **Understand both sides** — what did each branch change and WHY?
5. **Classify the conflict** (see table below)
6. **Generate recommendation**

**Conflict classifications:**

| Type | Signal | Typical Recommendation |
|------|--------|----------------------|
| **Independent additions** | Both sides added code in the same region, but the changes are unrelated | Keep both — order them logically |
| **Competing edits** | Both sides modified the same line/block differently | Needs user choice — explain trade-offs |
| **Refactor vs Feature** | One side restructured code, other added to old structure | Usually keep refactor + re-apply feature on new structure |
| **Delete vs Modify** | One side deleted code/file, other modified it | Ask user — is the deletion intentional? |
| **Trivial** | Whitespace, import ordering, auto-generated regions | Auto-resolve with recommendation |

### Step 5c: Present Conflict Cards

Present one card per file. For files with multiple hunks, present all hunks in one card.

**Card format:**

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

RECOMMENDATION: <what Claude thinks is the right call and why>

  [A] <recommended option — described clearly>
  [B] <alternative option>
  [C] <alternative option>
  [D] Show raw diff — I'll tell you what to do
  [E] Skip — I'll resolve this file manually later
═══════════════════════════
```

**Option rules:**
- Always include a recommended option as [A]
- Always include "Show raw diff" and "Skip" as final options
- For "Keep both" recommendations: describe the merged result briefly
- For "independent additions": [A] Keep both, [B] Keep ours, [C] Keep theirs
- For "competing edits": [A] and [B] are the two sides, [C] is "combine" if feasible
- Never exceed 5 options

**Special: Unity .asset / .prefab conflicts:**

Unity YAML conflicts need component-level analysis:
- Identify which GameObjects/components changed on each side
- If different components changed → keep both (merge YAML blocks)
- If same component changed → present the specific field differences
- For `.meta` files: follow the decision of the corresponding asset/script. If the paired file was deleted on one side, take the other side's `.meta`.

**Special: Binary files:**

```
═══ CONFLICT <N> of <total> ═══
File: Assets/Textures/icon.png
Type: Binary — cannot merge, must choose one side

OURS: Modified <date> (commit <hash>)
THEIRS: Modified <date> (commit <hash>)

  [A] Keep ours
  [B] Keep theirs
  [E] Skip — resolve manually
═══════════════════════════
```

### Step 5d: Collect & Apply Decisions

Wait for the user to respond to each card.

**If user picks a lettered option:** Apply immediately.

| Choice | Action |
|--------|--------|
| Keep ours | `git checkout --ours <file> && git add <file>` |
| Keep theirs | `git checkout --theirs <file> && git add <file>` |
| Keep both (code) | Read the conflict, merge both changes intelligently using code understanding, write the resolved file, `git add <file>` |
| Keep both (Unity YAML) | Merge the YAML blocks preserving both sides' components/fields, write resolved file, `git add <file>` |
| Raw diff | Show the raw conflict markers and wait for user instructions |
| Skip | Leave conflicted, note in summary |
| Custom instruction | User tells you exactly what to do — apply it |

**After applying each resolution:**
- Read the resolved file back
- Verify no remaining conflict markers in that file
- If markers remain (from a multi-hunk file where only some were resolved), report and continue

**Batch mode:** If user says "keep theirs for all .asset files" or "keep ours for everything except GameManager.cs" — apply the batch rule, still show summary of what was done.

### Step 5e: Resolve Remaining

After all cards are addressed:

```bash
# Check if any conflicts remain
rtk git status
```

If unresolved files remain (user skipped some):
```
Unresolved conflicts remaining:
  Assets/Scripts/SomeFile.cs (skipped)

These must be resolved before the merge can complete.
Options:
  [1] Show me these conflicts now
  [2] I'll resolve them manually — leave the merge in progress
  [3] Abort the entire merge
```

---

## Step 6: Verify & Finalize

After all conflicts are resolved:

### Static Check

Read all resolved files and check for:
- Remaining conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`) — **BLOCKER**
- Duplicate method signatures (from merging both sides) — **WARNING**
- Missing `using` statements (if new types came from the source branch) — **WARNING**
- Orphaned `.meta` files (file deleted on one side but .meta kept) — **WARNING**

Report any findings before finalizing.

### Finalize — Stage Only

```
═══ MERGE SUMMARY ═══
Source: origin/<source> → <current-branch>
Incoming commits: <N>

Conflicts resolved: <resolved> of <total>
  GameManager.cs — kept both (null check + analytics event)
  rewards.asset — kept theirs (newer balance values)
  icon.png — kept ours

Skipped: <count> (if any)
  SomeFile.cs — left for manual resolution

Verification: <PASS / WARNINGS>

All resolved files are staged. Review with `git diff --staged`.
Commit manually when ready.
═══════════════════════
```

**Do NOT commit. Do NOT push. The skill's job ends at staging resolved files.**

---

## Rollback

If anything goes wrong at any point, or user wants to abort:

```bash
git merge --abort
```

Always remind the user: "The merge has been aborted. Your branch is back to where it was before."

---

## Quick Reference

| Step | Key Activities | Success Criteria |
|------|---------------|------------------|
| 0 | Parse arguments | Source branch identified |
| 1 | Pre-flight checks | Clean working directory confirmed |
| 2 | Fetch & analyze | Know if FF, clean merge, or conflicts |
| 3A | Fast-forward | Applied cleanly |
| 3B | Merge attempt | Conflicts identified |
| 4 | Clean merge | Changes staged, user notified |
| 5 | Conflict resolution | Each conflict has a user decision |
| 6 | Verify & stage | No markers remain, all resolved files staged (never committed) |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Auto-resolving without asking | NEVER resolve a conflict without user confirmation |
| Merging with uncommitted changes | Always check git status first |
| Losing the rollback path | Record HEAD before starting, always offer abort |
| Treating .asset as plain text | Use Unity YAML component-level analysis |
| Resolving .meta without checking paired file | .meta follows its paired asset/script decision |
| Showing raw diffs instead of context | Always explain WHAT each side did and WHY |
| Running reset --hard without confirmation | Destructive — always ask first |

## Red Flags

**Never:**
- **MERGE INTO protected branches (develop, main, master, release/*, Release_*) — NO EXCEPTIONS**
- **Run `git commit` or `git push` — EVER. Only stage files. User commits manually.**
- Auto-resolve conflicts without user confirmation
- Run `git merge --abort` without asking (user may want partial resolution)
- Run `git reset --hard` without explicit user request
- Modify files that aren't part of the conflict
- Skip the static verification check
- Finalize a merge with remaining conflict markers

## Integration

**Manually triggered by:** `/merge-assist` command
**Auto-triggered by:** UserPromptSubmit hook (merge/pull keywords)
**Related skills:**
- `quality-gate` — run after merge to verify quality before pushing
- `error-fix` — if merged code has compiler errors
