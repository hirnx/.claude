---
name: error-fix
description: Use when compiler errors, console logs, exception traces, or error screenshots are shared. Triggers on error codes, console output format, exception types, build errors.
---

# Error Fix

## Overview

Parallel error-fixing skill. Parses compiler errors, groups by root cause, dispatches parallel fixer agents, then runs a review agent to merge and verify results. Iterates up to 3 cycles.

## When to Use

- Compiler error codes (e.g. CS####, E####, TS####, etc.)
- Console output showing compiler/build errors
- Exception types (NullReferenceException, TypeError, etc.)
- Phrases like "compiler error", "build error", "build failed", "these errors", "fix this"
- Screenshots showing console/build output

**Do NOT use when:**
- Runtime logic bugs (no compiler errors) — use the `debug` skill instead
- Performance issues
- Feature requests or refactoring

---

## Step 0: Check for Handoff

Before starting Phase 1, check for a handoff file:

1. Look for `.claude/handoffs/debug-to-error-fix.md`
2. If found → read it, pre-load root cause findings, honor `Skip` list
3. If not found → run full Phase 1 as normal

| Handoff field | What it skips |
|---|---|
| Decisions (root cause) | Root cause investigation — already done by debug |
| Files touched | File discovery — already identified |
| Skip | Phase 1 grouping — errors already isolated to root cause |

**Staleness check:** If new errors appeared since handoff was written, fall back to full Phase 1.

After consuming the handoff, delete the handoff file.

---

## Phase 1 — Parse, Context Load & Group

**Iteration counter:** One full Phase 1–4 cycle = one iteration. Starts at 1 per
skill invocation. Max = 3 full cycles.

### Step 1a — Input Normalization

Extract all errors from the input regardless of format:

| Input type | Action |
|---|---|
| Screenshot | Extract all visible CS#### codes and messages via image analysis |
| Single error line | Treat as a list of one |
| Multi-line paste | Parse line by line, extract all `CS####` entries |
| Mixed | Combine all extracted errors into one flat list |

Normalize each to: `{ code, message, file, line }`

**Zero-error case:** If no CS#### codes are found, check if the input contains
runtime exceptions, linker errors, or warnings-only. Report what was found and
ask the user to provide compiler errors before proceeding. Do not dispatch agents.

### Step 1b — Context Pre-loading (before grouping)

Context must be loaded **before** grouping — migration context affects root-cause
detection.

**On re-loop iterations (iteration 2+):** Reuse context loaded in iteration 1.
Re-read individual source files as needed for new errors — context reuse means
skipping the doc reads only, not file reads.

1. Read `CLAUDE.md` for project-specific overrides and conventions.
2. If the project has a `.claude/project-profile.md`, load platform-specific patterns from `~/.claude/skills/error-fix/patterns/` matching the platform.
3. If project-local context docs exist (e.g. `.claude/context/migrations/`), load relevant ones — known fixes take priority over re-deriving them.
4. Store loaded context as excerpts: copy only the relevant paragraphs/sections (≤200 words per agent). Do not pass full files.

### Step 1c — Grouping Rules

Group by **root cause**, not by error code or file.
**Cascade detection runs first and wins over all other rules.**

**Cascade detection:** Identify errors that are downstream symptoms of another
error in the list. Signals: multiple errors reference the same missing type/member;
an error in file B references a type that is itself the subject of another listed
error. Collapse cascade errors into the root error's group. When uncertain whether B is a cascade of A, treat them as separate groups — over-grouping causes one agent to receive unrelated errors, which underperforms compared to keeping them separate.

| Rule | Example |
|---|---|
| Cascade: error B disappears if A is fixed | Collapse into A's group (wins over all) |
| Same missing type in N files | 8× "type not found" errors for `FooClass` → one group |
| Same missing member on same class | All "member missing" errors for `GetCount()` → one group |
| Unrelated errors in the same file | Two separate groups |
| Unrelated errors in different files | Separate groups |
| Same error code, different root causes | Separate groups |

**Single-group case:** One group → one agent dispatched. Review agent still runs.

### Step 1d — File Touch Map

After grouping, build: `{ groupId → [files likely to be modified] }`

Flag any file appearing in 2+ groups as a **shared file**. This map is built after
grouping is complete. When error B (which would have touched file X) is collapsed
into group A, file X is added to group A's touch map entry — cascade effects are
automatically reflected. Pass the full map to every fixer agent and the review agent.

---

## Phase 2 — Status Announcement & Parallel Dispatch

### Status Message

Before dispatching any agents, print:

```
Fixing N error group(s) in parallel:
- Agent 1 → [CS####] <short description> (<X> files affected)
- Agent 2 → [CS####] <short description>
- Agent 3 → [CS####] <short description>
⚡ All agents running simultaneously...
```

Agent indices are 1-based, assigned in order of listing, and stable across all output.
If N = 1, the message still prints with one entry — no special case.

### Dispatch Rule — CRITICAL

**All agents MUST be dispatched in a single response as multiple Agent tool calls.**
Do NOT await one agent before dispatching the next. Sequential dispatch defeats the
purpose and removes all time savings.

### Per-Agent Prompt Contents

Each sub-agent receives:

1. **Agent index** — 1-based, matches the status message
2. **Assigned error group** — normalized `{ code, message, file, line }` entries
3. **File touch map** — full map with shared-file flags
4. **Shared-file write rule** — see below
5. **Context excerpt** — relevant paragraphs from pre-loaded docs (≤200 words per agent)
6. **Error-fix pattern library** — full patterns from the "Error-Fix Pattern Library"
   section of this skill, embedded inline in the prompt
7. **Fix rules** — see below
8. **Output contract** — see below

### Shared-File Write Rule

> **For any file flagged as shared in the file touch map: do NOT write to it.**
> Instead, output your intended changes for that file in the CHANGES block only.
> The review agent will apply all changes to shared files after all agents complete,
> preventing one agent from overwriting another's edits.
>
> For files not flagged as shared: write normally, then report in CHANGES.

### Fix Rules

Pass these to every fixer agent:

- Read the file before editing it
- Prefer additive fixes: wrappers, aliases, overloads — do not modify existing callers
- Fix the root cause once — do not fix each symptom separately
- One root cause can produce many errors; one fix resolves all of them
- For shared files: output intended changes in CHANGES only, do not write

### Agent Output Contract

Each fixer agent must return:

```
STATUS: DONE | BLOCKED
AGENT: <index>

CHANGES:
- <file path> | lines <N-M> or "new file" | <what was done> | <why>
(for shared files: describe the full intended change — the review agent applies it)

BLOCKED REASON: <only if STATUS is BLOCKED — what decision or missing asset prevented the fix>
```

**BLOCKED behavior:** BLOCKED agents report and halt. The orchestrator surfaces the
BLOCKED REASON to the user after Phase 3. All other non-blocked agents continue
unaffected. BLOCKED groups are excluded from Phase 4 re-loops.

---

## Error-Fix Pattern Library

> This section is embedded in every fixer agent's prompt. Agents cannot load
> skills via the Skill tool — they receive this library inline in their prompt.

If the project has a `.claude/project-profile.md`, load the platform-specific pattern library from `~/.claude/skills/error-fix/patterns/` matching the platform. The pattern library contains error code mappings and fix recipes for the project's language/framework.

Available: `patterns/unity-csharp.md` (CS#### error codes, assembly boundaries, namespace patterns)

**Without a platform pattern library**, fixer agents use general principles:
- Read the error message and trace to root cause
- Prefer additive fixes (wrappers, aliases, overloads) over modifying existing callers
- Fix root cause once — don't fix each symptom separately
- Search the codebase before creating new types (it may exist under a different name/namespace)

---

## Phase 3 — Review Agent

### Completion Summary

After all fixer agents return, print:

```
All agents complete:
- Agent 1 → <summary from CHANGES, or "BLOCKED: <reason>">
- Agent 2 → <summary from CHANGES>
- Agent 3 → <summary from CHANGES>
```

If any BLOCKED agents exist, also print:
`⚠️ Agent(s) X blocked — manual attention needed: <reasons>`

If both BLOCKED agents and unresolvable conflicts occur in the same cycle, list both.

Then print: `🔍 Running review agent on changed files...`

### Review Agent Prompt Contents

Dispatch one review agent. It receives:

1. **File touch map** — which files were touched and by which agent indices
2. **All fixer agent CHANGES outputs** — exact records (file, line range, what, why);
   for shared-file entries these are intentions not yet applied to disk
3. **Current content of all non-shared touched files** — read fresh (fixer agents
   have already written these)
4. **Shared files to apply** — list of shared files with all agents' intended
   CHANGES for each; review agent applies them in agent-index order
5. **Refactor scope rule** — only lines in any agent's CHANGES output are in scope
6. **Conflict resolution instructions** — see below
7. **Output contract** — see below

### Review Agent Responsibilities (in order)

1. **Apply shared-file changes** — for each shared file, apply all agents' intended
   CHANGES in agent-index order. Verify the merged result before writing.
2. **Refactor changed code** — only lines/methods appearing in any agent's CHANGES
   output. Do not touch untouched code.
3. **Resolve conflicts** — if merged shared-file output contains duplication or
   signature inconsistency, fix it during the apply step.

### Conflict Resolution

If a shared-file conflict **cannot be resolved automatically** (e.g., two agents
added a method with the same name but incompatible signatures): do NOT write the
file. Report:

```
⚠️ Unresolvable conflict in <file path>:
  Agent <N>: <description>
  Agent <M>: <description>
  Manual resolution required.
```

Skip Phase 4 for conflicted files. Continue for others.

### Review Agent Output Contract

```
SHARED FILES APPLIED:
- <file path> | agents merged: <indices>

REFACTORS:
- <file path> | lines <N-M> | <what> | <why>

UNRESOLVABLE CONFLICTS:
- <file path> | <description>
(or "none")
```

---

## Phase 4 — Iterative Verification

After the review agent completes, the orchestrator performs a **best-effort static
analysis pass** by reading all changed files. This is LLM reasoning over file
content — not a build trigger. The user runs a build to confirm compilation.

Flag only **high-confidence issues**:
- A type was added but its `using` statement is absent in its consumer file
- A call site visibly passes the wrong number of arguments to a newly added overload

**Do not flag** null-safety or other speculative concerns — these require data-flow
analysis and produce false positives.

### Re-loop Normalization

Phase 4 produces natural-language observations. Before re-entering Phase 1, format
each finding as a pseudo-error:
`{ code: "STATIC", message: "<observation>", file: "<path>", line: "<N if known>" }`
Phase 1 groups these as it would real errors.

### Loop Control

**If high-confidence issues found AND iteration < 3:**
Increment counter. Loop back to Phase 1. Reuse loaded context docs; re-read source
files as needed for the new errors.

**If iteration = 3 and issues remain:**
```
⚠️ Stopping after 3 iterations. Remaining issues require manual attention:
- <list of unresolved issues>
```
Halt.

**If no high-confidence issues found:**
```
✅ Done. (Iteration <N> of 3)
<X> error group(s) fixed across <Y> files.
Review pass: <Z> refactor(s) applied.

Files changed:
- path/to/File1
- path/to/File2
```

---

## Context Update Rule

After all work is complete (clean Phase 4 or max iterations reached), update
`.claude/context/` docs per the rules in `CLAUDE.md` if the fixes revealed
new project knowledge (type mappings, renamed members, patterns).
Keep entries concise — facts and mappings only, no narrative.
