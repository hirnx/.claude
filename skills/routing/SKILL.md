---
name: routing
description: Use at conversation start to determine which skills apply to the user's request — maps situations to skills, prevents overloading.
---

# Routing

## Instruction Priority

1. **User's explicit instructions** (CLAUDE.md, direct requests) — highest priority
2. **Skills** — override default system behavior where they conflict
3. **Default system prompt** — lowest priority

If CLAUDE.md says "don't do X" and a skill says "always do X," follow the user's instructions.

## Decision Tree

```
User request →
├── Compiler errors / build failures → error-fix
├── Runtime bug / unexpected behavior → debug (→ may hand off to error-fix)
├── "Review this" / check code → inspect
├── "Refactor" / clean up → refactor
├── "Plan this" / design feature → brainstorm (full or light mode based on complexity)
├── "Make a skill/command/agent" → forge
├── Feature migration wiring → integrate
├── Translation / localization → localize
├── Sheet data import → sheet-import
├── Executing an existing plan → execute (direct, delegate, or dispatch mode)
├── About to claim "done" → verify
├── Code review → review
├── "Ready to merge" / done with feature → quality-gate
├── "Release" / ready for build → release-gate
├── Production incident / prod bug → postmortem
└── Context docs need updating → context
```

## Rules

- **Most specific skill wins.** Use `error-fix` for compiler errors, not `debug`. Use `inspect` for code review, not a general read.
- **Maximum 2 skills concurrently** — one primary, one supporting. Sequential chains (brainstorm → plan → execute → review → verify) are fine — each skill completes before the next starts.
- **If unsure, ask** — don't load multiple skills hoping one fits.

## Skill Categories

**Rigid** (follow exactly, don't adapt away discipline):
- `error-fix` — parallel dispatch protocol must be followed
- `verify` — evidence before assertions, no shortcuts
- `brainstorm` — design before implementation, full checklist
- `quality-gate` — all checks must run, no shortcuts
- `release-gate` — GO/NO-GO is binary, no "probably fine"
- `postmortem` — must update at least one prevention layer

**Flexible** (adapt principles to context):
- `debug` — methodology adapts to the problem
- `inspect` — review depth varies by file complexity
- `refactor` — scope varies by request

## Skill Combinations

**Work well together:**
- `debug` finds root cause → `error-fix` applies fix
- `brainstorm` designs feature → `plan` creates implementation plan
- `plan` creates plan → `execute` implements it
- Any implementation skill → `verify` before claiming done
- Any completed work → `review` for quality check
- Any implementation chain → `quality-gate` before merging to develop
- `quality-gate` passes → merge → `release-gate` before building
- Production incident → `postmortem` (updates quality checks for future)

**Don't combine:**
- `brainstorm` + `execute` (design before implementing)
- `error-fix` + `refactor` (fix first, refactor separately)
- `inspect` + `refactor` (review first, then decide to refactor)
- `quality-gate` + `release-gate` (quality-gate first, then release-gate — sequential gates, not concurrent)
- `postmortem` + `quality-gate` (postmortem captures and updates checks, quality-gate runs checks — don't mix)

## Chain Awareness

When a skill completes and suggests a next skill via suggest-and-confirm, routing validates the chain:

1. Check `.claude/handoffs/` for a handoff file matching the suggested transition
2. If handoff exists → pass the handoff path to the next skill so it can read it in Step 0
3. If no handoff exists → next skill runs its full process (cold start)

**Known chains:**
```
brainstorm → plan → execute → review → verify → quality-gate
brainstorm (light) → execute → review → verify → quality-gate
debug → error-fix → verify
debug → verify (direct fix)
all skills → verify
quality-gate passes → merge
release-gate passes → release
postmortem → updates context docs + quality checks
```

Routing should not block a chain transition — it validates and passes context, not gatekeeps.

## Complexity Classification

Before invoking a skill, classify the task as **light** or **full** mode. This determines how much ceremony the skill applies.

**Weigh all signals together — no single signal decides:**

| Signal | Leans Light | Leans Full |
|--------|------------|------------|
| Change scope | Small, well-defined change | Structural change, new patterns, cross-cutting concerns |
| Intent clarity | User's request is unambiguous | Ambiguous scope, multiple interpretations |
| Language cues | Tone suggests a quick task (e.g. "just", "simple", "quick", etc.) | Tone suggests deliberate design work (e.g. "design", "architect", "system", etc.) |
| Cause clarity | Cause and fix are obvious | Cause is unclear, could span multiple systems |
| Spec provided | No spec (task is self-evident) | User provides or expects a spec |

**Rules:**
- If most signals lean light → light mode
- If any signal **strongly** leans full (e.g. ambiguous scope even if tone is casual) → full mode
- Ambiguity defaults to full
- User can override explicitly ("give me the full treatment" → full, "just do it" → light)

**Announce with the skill indicator:**
```
⚡ Using skill: [skill-name] (light)
⚡ Using skill: [skill-name]           ← full is the default, no label needed
```

## Visual Indicator

When invoking any skill, print:
```
⚡ Using skill: [skill-name]
```
