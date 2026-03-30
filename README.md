# Claude Code Skills System

A comprehensive, self-contained skill system for Claude Code with 16+ specialized skills for structured software development. Platform-specific patterns are pluggable via project profiles. No external plugins required.

---

## Overview

This system extends Claude Code with **16 specialized skills**, **slash commands**, and **custom agents** that cover the full development lifecycle: from creative design through implementation, review, and verification.

Each skill encodes domain-specific workflows, iron laws, and quality gates — so Claude doesn't just write code, it follows the same discipline a senior engineer would.

---

## Architecture

```
~/.claude/
├── CLAUDE.md                 # Global configuration and rules
├── README.md                 # You are here
├── settings.json             # Permissions, hooks, plugin config
├── plans/                    # Design specs and implementation plans
├── commands/                 # User-invocable slash commands
│   ├── localize.md
│   └── sheet-import.md
├── agents/                   # Agent definitions for subagent dispatch
│   └── code-reviewer.md
└── skills/                   # Auto-discovered skill definitions
    └── <name>/
        ├── SKILL.md          # Entry point (auto-discovered)
        └── ...               # Support files, scripts, prompts
```

**Per-project overrides** live in `<project>/.claude/`:

```
<project>/.claude/
├── CLAUDE.md                 # Project-specific rules and learned rules
├── context/                  # Persistent project knowledge docs
├── plans/                    # Specs and implementation plans
├── project-profile.md        # Platform and domain context (optional)
└── settings.local.json       # Project-specific settings
```

---

## Skills

Skills are the core of this system. Each is a structured workflow with explicit phases, quality gates, and discipline rules. Auto-discovered from `~/.claude/skills/<name>/SKILL.md`.

### Skill Map

```
╔══════════════════════════════════════════════════════════════════════════╗
║                              SKILL SYSTEM                                ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║                           ┌──────────┐                                   ║
║                           │ ROUTING  │ ◄── session start                 ║
║                           └────┬─────┘                                   ║
║            ┌───────────────────┼───────────────────┐                     ║
║            ▼                   ▼                   ▼                     ║
║  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐             ║
║  │    CREATION     │ │    QUALITY      │ │      DATA       │             ║
║  │                 │ │                 │ │                 │             ║
║  │  brainstorm ─┐  │ │  inspect        │ │  localize       │             ║
║  │  design ───┐ │  │ │  refactor       │ │  sheet-import   │             ║
║  │  forge     │ │  │ │  review         │ │                 │             ║
║  │            │ │  │ │                 │ └─────────────────┘             ║
║  │         ┌──┘ │  │ │                 │                                 ║
║  │         ▼    ▼  │ └─────────────────┘ ┌─────────────────┐             ║
║  │       plan      │                     │    DEBUGGING    │             ║
║  │         │       │                     │                 │             ║
║  │         ▼       │                     │  error-fix      │             ║
║  │      execute    │                     │  debug          │             ║
║  │         │       │                     │                 │             ║
║  │         ▼       │                     └─────────────────┘             ║
║  │      integrate  │                                                     ║
║  │                 │  ┌─────────────────┐                                ║
║  └─────────────────┘  │     SYSTEM      │                                ║
║                       │                 │                                ║
║                       │  context        │                                ║
║                       │  routing        │                                ║
║                       │                 │                                ║
║                       └─────────────────┘                                ║
║                                                                          ║
║  ┌───────────────────────────────────────────────────────────────────┐   ║
║  │  VERIFY  ◄── called after ANY skill claims completion             │   ║
║  └───────────────────────────────────────────────────────────────────┘   ║
║                                                                          ║
║  Common flows:                                                           ║
║  brainstorm ──► plan ──► execute ──► integrate ──► verify                ║
║  debug ──► error-fix ──► verify                                          ║
║  design ──► plan ──► execute ──► review ──► verify                       ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

### Design & Planning


| Skill          | Purpose                                                                                                                          | Key Discipline                                                             |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| **brainstorm** | Co-design features through collaborative dialogue. Explores intent, proposes 2-3 approaches with trade-offs, writes design spec. | Hard gate: no code until design is approved. One question at a time.       |
| **design**     | Create detailed, executable coding plans. Surfaces assumptions via reverse-prompting before touching code.                       | 4 phases: Understand, Discover, Plan, Confirm. Never code during planning. |
| **plan**       | Write implementation plans assuming zero context. Bite-sized tasks, exact code, no placeholders.                                 | Every step = one action (2-5 min). No TBD, no "similar to Task N".         |


### Implementation


| Skill         | Purpose                                                                                                                 | Key Discipline                                                                     |
| ------------- | ----------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **execute**   | Run plans via 3 modes: **direct** (sequential), **delegate** (subagents + review), **dispatch** (parallel independent). | Mode selection is critical. Delegate includes two-stage review per task.           |
| **integrate** | Wire migrated systems — callsites, callbacks, initialization, event subscriptions.                                      | LSP-driven discovery. Group-by-group confirmation. Persists state across sessions. |
| **forge**     | Full lifecycle management for skills, commands, and agents. Create, edit, rename, delete with auto-reference updates.   | Wizard-guided creation. Enriches from project-profile.md.                          |


### Quality & Review


| Skill        | Purpose                                                                                                                      | Key Discipline                                                         |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| **inspect**  | Audit source files against comprehensive checklist: null safety, memory leaks, performance, architecture.                     | Scored report with commit recommendation. No false positives.          |
| **refactor** | Improve code structure while preserving identical behavior. Caching, extraction, state machines, pooling, dead code removal. | Iron law: "Same behaviour, better code." Public API must be preserved. |
| **review**   | Full code review cycle — dispatch reviewer agent, handle feedback with technical rigor.                                      | Technical correctness > comfort. Push back when reviewer is wrong.     |
| **verify**   | Enforce evidence-before-claims. Non-negotiable gate before any "done" statement.                                             | Iron law: no completion claims without fresh verification evidence.    |


### Debugging & Error Fixing


| Skill         | Purpose                                                                                                                      | Key Discipline                                                                 |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **error-fix** | Fix compiler errors. Parses, groups by root cause, dispatches parallel fixer agents, runs review agent.                      | Cascade detection. Max 3 iteration cycles. Shared-file conflict resolution.    |
| **debug**     | Systematic root-cause investigation for runtime bugs and unexpected behavior.                                                | Iron law: no fixes without root cause investigation first. 4 mandatory phases. |


### Data & Localization


| Skill            | Purpose                                                                                                             | Key Discipline                                                                           |
| ---------------- | ------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **localize**     | Translate strings to multiple languages, generate keys, preview, and append to Google Sheet.                         | Append-only. Preview table before write. Slash command: `/localize`                      |
| **sheet-import** | Import Google Sheet data into Unity ScriptableObject `.asset` files. Field mapping, match-on logic, saved mappings. | Never modify `m_`* fields. Always confirm before writing. Slash command: `/sheet-import` |


### System


| Skill       | Purpose                                                                            | Key Discipline                                                                  |
| ----------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| **routing** | Route incoming requests to the correct skill(s) at conversation start.             | Max 2 skills per task. Most specific wins. Decision tree with skill categories. |
| **context** | Persist project-specific knowledge in `.claude/context/` docs for future sessions. | Project-local only. Facts and mappings, no narrative. One topic per file.       |


---

## Slash Commands

Commands are user-invocable via `/<name>` in the Claude Code prompt.


| Command         | Backing Skill | What It Does                                         |
| --------------- | ------------- | ---------------------------------------------------- |
| `/localize`     | localize      | Translate strings and append to Google Sheet         |
| `/sheet-import` | sheet-import  | Import sheet data into Unity ScriptableObject assets |


---

## Agents

Agents are dispatched by skills as subagents — they are not auto-loaded.


| Agent             | Dispatched By                       | Role                                                       |
| ----------------- | ----------------------------------- | ---------------------------------------------------------- |
| **code-reviewer** | `review`, `execute` (delegate mode) | Reviews completed steps against plans and coding standards |


---

## Skill Chains

Skills are designed to flow into each other. Common workflows:

```
brainstorm  →  plan  →  execute  →  verify
debug  →  error-fix  →  verify
design  →  integrate  →  review  →  verify
any task  →  review  →  verify
```

**Valid combos:** `debug` hands off to `error-fix` | `brainstorm` flows into `plan` | `plan` flows into `execute` | any skill can invoke `verify` or `review`

**Never combine:** `brainstorm` + `execute` (design must complete first) | `error-fix` + `refactor` (fix first, refactor separately) | `inspect` + `refactor` (review first, then act)

---

## Key Principles

These rules are enforced across all skills:


| Principle                                                            | Enforced By            |
| -------------------------------------------------------------------- | ---------------------- |
| **Evidence before claims** — never say "done" without proof          | `verify`               |
| **Root cause before fixes** — no guessing, no "quick fixes"          | `debug`                |
| **Design before code** — approval gates prevent wasted effort        | `brainstorm`, `design` |
| **No placeholders** — every plan step has exact code                 | `plan`                 |
| **Same behavior, better code** — refactors preserve the public API   | `refactor`             |
| **Technical correctness over comfort** — push back on wrong feedback | `review`               |
| **Targeted reads only** — never bulk-read the codebase               | All skills             |


---

## Creating New Artifacts

Use the **forge** skill to create, edit, rename, or delete any artifact:

```
"make a skill for X"       → creates ~/.claude/skills/<name>/SKILL.md
"new command for Y"         → creates ~/.claude/commands/<name>.md
"forge an agent for Z"      → creates ~/.claude/agents/<name>.md
"rename skill X to Y"       → renames + updates all references
"delete command X"           → removes + cleans up references
```

---

## Conventions

- **Skills** use `SKILL.md` as entry point inside `skills/<name>/` directories
- **Commands** use `<name>.md` directly in `commands/` — VSCode registers these as slash commands
- **Support directories** for commands use a different name than the command file (e.g., `localize.md` + `localize-data/`)
- **No `.md` files** in support directories (they would become slash commands)
- **Local artifacts** use the `LOCAL.` prefix (e.g., `LOCAL.SKILL.md`)
- **Naming:** verb-first, lowercase-hyphens (e.g., `fix-errors`, not `error-fixer`)

---

*Built for Claude Code. Self-contained. No external dependencies.*