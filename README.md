# Claude Code Skills System

A self-contained skill system for Claude Code with 20 specialized skills, 5 slash commands, and custom agents covering the full development lifecycle. No external plugins required.

---

## Architecture

```
~/.claude/
├── CLAUDE.md                 # Global configuration and rules
├── README.md                 # You are here
├── settings.json             # Permissions, hooks, plugin config
├── commands/                 # Slash commands (/localize, /git-assist, etc.)
├── agents/                   # Subagent definitions (code-reviewer)
├── workflow/                  # Workflow docs
│   ├── workflow-tree.md      #   Directory & skill structure map
│   └── workflow-flowchart.md #   Full visual flowchart (showcase)
├── context/                  # Global reference docs
│   ├── footguns.md           #   Known pitfalls
│   └── quality-checks.md    #   Gate review checklist
├── plans/                    # Specs and implementation plans
└── skills/                   # Auto-discovered skill definitions
    └── <name>/SKILL.md
```

---

## Skills (20)

| Phase | Skills |
|-------|--------|
| **Routing** | routing |
| **Design & Planning** | brainstorm, plan |
| **Implementation** | execute, integrate, forge |
| **Debugging** | error-fix, debug |
| **Quality & Review** | inspect, refactor, review, verify |
| **Gate & Release** | quality-gate, release-gate, postmortem |
| **Data & Localization** | localize, sheet-import |
| **Git & Ops** | git-assist |
| **System** | context |

Each skill lives in `skills/<name>/SKILL.md` with its own workflows, iron laws, and quality gates.

---

## Commands

| Command | Skill | Purpose |
|---------|-------|---------|
| `/localize` | localize | Translate strings, append to Google Sheet |
| `/sheet-import` | sheet-import | Import sheet data into Unity .asset files |
| `/git-assist` | git-assist | Branch, merge, conflict resolution |
| `/pre-merge` | quality-gate | Pre-merge quality review |
| `/release-check` | release-gate | Release readiness check |

---

## Agents

| Agent | Dispatched By | Role |
|-------|---------------|------|
| **code-reviewer** | review, execute | Reviews steps against plans and standards |

---

## Workflow

See [workflow-tree.md](workflow/workflow-tree.md) for the full directory structure and [workflow-flowchart.md](workflow/workflow-flowchart.md) for the visual flowchart.

```
PROMPT → ROUTE → PLAN → EXECUTE → VERIFY → GATE → SHIP
                                                    │
                                         postmortem ◀┘ → context updated → next cycle smarter
```

---

## Key Principles

- **Evidence before claims** — `verify` gates all completion
- **Root cause before fixes** — `debug` investigates first
- **Design before code** — `brainstorm`/`plan` gate implementation
- **Blast radius check** — grep all callers before editing
- **Feedback loop** — `postmortem` updates checks for future cycles

---

## Creating Artifacts

Use the **forge** skill: `"make a skill for X"`, `"new command for Y"`, `"rename skill X to Y"`

## Conventions

- Skills: `skills/<name>/SKILL.md` — auto-discovered
- Commands: `commands/<name>.md` — auto-registered as slash commands
- Local artifacts: `LOCAL.` prefix (e.g., `LOCAL.SKILL.md`)

---

*Built for Claude Code. Self-contained. No external dependencies.*
