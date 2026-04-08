# Claude Code Workflow Flowchart

> **Purpose:** Visual flowchart of the full workflow system — routing, work phases, toolkit, quality loop, and context management.

## System Overview

```
╔═════════════════════════════════════════════════════════════════════════╗
║                      CLAUDE CODE WORKFLOW ENGINE                      ║
║                   Custom Skills + Context + Automation                ║
╚═════════════════════════════════════════════════════════════════════════╝

   User Prompt
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  ROUTING                                                               │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │  Classify task ──→ Match skill ──→ Load only relevant context    │ │
│  │                                                                   │ │
│  │  "fix this error"   ──→  error-fix                               │ │
│  │  "migrate feature"  ──→  plan → execute → integrate              │ │
│  │  "translate these"  ──→  localize                                │ │
│  │  "review for merge" ──→  quality-gate                            │ │
│  │  "refactor this"    ──→  refactor                                │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  WORK PHASE                                                            │
│                                                                        │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌────────────┐ │
│  │  brainstorm    │ │  plan         │ │  debug        │ │  error-fix │ │
│  │  ───────────── │ │  ──────────── │ │  ───────────  │ │  ──────────│ │
│  │  Explore       │ │  Spec out     │ │  Root-cause   │ │  Compiler &│ │
│  │  intent &      │ │  steps &      │ │  analysis     │ │  runtime   │ │
│  │  design        │ │  files        │ │  before fix   │ │  errors    │ │
│  └───────┬───────┘ └───────┬───────┘ └───────┬───────┘ └─────┬──────┘ │
│          └────────────┬────┴──────────────────┴───────────────┘        │
│                       ▼                                                │
│              ┌─────────────────┐                                       │
│              │     execute     │                                       │
│              │  ─────────────  │                                       │
│              │  Direct, or     │                                       │
│              │  parallel via   │                                       │
│              │  subagents      │                                       │
│              └────────┬────────┘                                       │
└───────────────────────┼─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  TOOLKIT                                                               │
│                                                                        │
│  ┌─────────────────────────┐    ┌─────────────────────────┐           │
│  │  /localize              │    │  /sheet-import           │           │
│  │  ─────────────────────  │    │  ─────────────────────── │           │
│  │                         │    │                          │           │
│  │  English strings        │    │  Google Sheet            │           │
│  │       │                 │    │       │                  │           │
│  │       ▼                 │    │       ▼                  │           │
│  │  Generate keys          │    │  Fetch rows & columns    │           │
│  │       │                 │    │       │                  │           │
│  │       ▼                 │    │       ▼                  │           │
│  │  Translate to           │    │  Map to SO fields        │           │
│  │  12+ languages          │    │       │                  │           │
│  │       │                 │    │       ▼                  │           │
│  │       ▼                 │    │  Write .asset files      │           │
│  │  Append to              │    │  with confirmation       │           │
│  │  Google Sheet           │    │                          │           │
│  └─────────────────────────┘    └──────────────────────────┘           │
│                                                                        │
│  ┌─────────────────────────┐    ┌─────────────────────────┐           │
│  │  /git-assist            │    │  refactor / integrate    │           │
│  │  ─────────────────────  │    │  ─────────────────────── │           │
│  │  Branch, merge,         │    │  Code cleanup,           │           │
│  │  conflict resolution    │    │  post-migration wiring   │           │
│  │  with AI analysis       │    │  callbacks & events      │           │
│  └─────────────────────────┘    └─────────────────────────┘           │
└───────────────────────┬─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  QUALITY LOOP                                                          │
│                                                                        │
│  ┌────────────┐    ┌──────────────┐    ┌──────────────┐               │
│  │  verify     │──→│  inspect     │──→│  review       │               │
│  │  ────────── │    │  ──────────  │    │  ──────────  │               │
│  │  Evidence   │    │  Anti-pattern│    │  Code review │               │
│  │  before     │    │  detection & │    │  dispatch &  │               │
│  │  claiming   │    │  file scan   │    │  feedback    │               │
│  └─────────────┘    └──────────────┘    └──────┬───────┘               │
│                                                 │                      │
│                 ┌───────────────────────────────┘                      │
│                 ▼                                                      │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                        /pre-merge                                 │ │
│  │                                                                   │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐      │ │
│  │  │ Blast Radius   │  │ Footguns Check │  │ SetDirty Check │      │ │
│  │  │ All callers of │  │ Known pitfalls │  │ SO editor code │      │ │
│  │  │ changed methods│  │ from context/  │  │ must call it   │      │ │
│  │  │ are verified   │  │ footguns.md    │  │                │      │ │
│  │  └────────────────┘  └────────────────┘  └────────────────┘      │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐      │ │
│  │  │ Change Manifest│  │ Test Data Scan │  │ Git Safety     │      │ │
│  │  │ Files, blast   │  │ No hardcoded   │  │ No commits,    │      │ │
│  │  │ radius, data   │  │ test values    │  │ no pushes,     │      │ │
│  │  │ impact summary │  │ left behind    │  │ no deletions   │      │ │
│  │  └────────────────┘  └────────────────┘  └────────────────┘      │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                 │                                                      │
│                 ▼                                                      │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                       /release-check                              │ │
│  │  Full diff review → Branch safety → Risk scoring → Ship / No-Ship│ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                 │                                                      │
│                 ▼                                                      │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │                        postmortem                                 │ │
│  │  Incident? → Capture cause → Update footguns.md & quality-checks │ │
│  │                                        │                          │ │
│  │                                        ▼                          │ │
│  │                            Feeds back into next cycle             │ │
│  └───────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  CONTEXT MANAGEMENT                                                    │
│                                                                        │
│  .claude/context/                      .claude/plans/                  │
│  ┌──────────────────────────┐         ┌──────────────────────────┐    │
│  │  feature-migration.md    │         │  Specs & implementation  │    │
│  │  ├── Migration workflow  │         │  plans live here         │    │
│  │  └── Feature index ─────────┐     └──────────────────────────┘    │
│  │                          │  │                                      │
│  │  migrations/             │  │      Learned Rules                   │
│  │  ├── msb-event.md       ◀──┘      ┌──────────────────────────┐    │
│  │  ├── mineboard.md        │         │  Self-correcting rules   │    │
│  │  └── <feature>.md        │         │  in project CLAUDE.md    │    │
│  │                          │         │  ── accumulate over time │    │
│  │  asset-management.md     │         │  ── higher # wins        │    │
│  │  localization-system.md  │         └──────────────────────────┘    │
│  │  footguns.md ◀── postmortem                                        │
│  │  quality-checks.md ◀── postmortem                                  │
│  │  workflow-flowchart.md   │                                         │
│  └──────────────────────────┘                                         │
│                                                                        │
│  Load on demand ── never bulk-read ── update after every task          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  TOKEN OPTIMIZATION (RTK)                                              │
│                                                                        │
│  Every CLI command prefixed with `rtk` ──→ 60-90% token savings       │
│                                                                        │
│  rtk git status ──→ compact     rtk cargo build ──→ errors only       │
│  rtk git diff   ──→ minimal     rtk vitest run  ──→ failures (99%)    │
│  rtk gh pr view ──→ condensed   rtk tsc         ──→ grouped (83%)     │
└─────────────────────────────────────────────────────────────────────────┘
```

## Flow Summary

```
  PROMPT ──→ ROUTE ──→ PLAN ──→ EXECUTE ──→ VERIFY ──→ GATE ──→ SHIP
                        │                      ▲         │
                        │         fix ◀────────┘         │
                        │                                │
                        └── toolkit: localize,           │
                            sheet-import, git-assist     │
                                                         │
                                              postmortem ◀┘
                                                  │
                                                  ▼
                                          context updated
                                         (footguns, checks)
                                                  │
                                                  ▼
                                         next cycle is smarter
```
