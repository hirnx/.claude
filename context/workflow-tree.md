# Global Workflow Tree

> **Purpose:** Visual map of all global skills, commands, agents, and their relationships. Reference when onboarding or choosing which skill to invoke.

## Directory Structure

```
~/.claude/
├── CLAUDE.md                          # Global config & rules
│
├── skills/                            # Skill definitions
│   ├── routing/SKILL.md               # Session start — skill selection
│   │
│   ├── ── INTAKE PHASE ──
│   ├── brainstorm/SKILL.md            # Creative design exploration
│   ├── plan/SKILL.md                  # Implementation planning from specs
│   ├── debug/SKILL.md                 # Systematic root-cause debugging
│   │
│   ├── ── EXECUTION PHASE ──
│   ├── execute/SKILL.md               # Plan execution (direct/delegated/parallel)
│   ├── error-fix/SKILL.md             # Compiler errors, exceptions, logs
│   ├── refactor/SKILL.md              # Code cleanup & restructuring
│   ├── integrate/SKILL.md             # Post-migration wiring & callbacks
│   ├── localize/SKILL.md              # String translation → Google Sheet
│   ├── sheet-import/SKILL.md          # Google Sheet → Unity .asset files
│   ├── git-assist/SKILL.md            # Branch ops, merge, conflict resolution
│   │
│   ├── ── VERIFICATION PHASE ──
│   ├── inspect/SKILL.md               # Code review & anti-pattern detection
│   ├── verify/SKILL.md                # Evidence-based completion check
│   ├── review/SKILL.md                # Code review dispatch & feedback
│   │
│   ├── ── GATE PHASE ──
│   ├── quality-gate/SKILL.md          # Pre-merge quality review
│   ├── release-gate/SKILL.md          # Release readiness check
│   │
│   ├── ── POST-INCIDENT ──
│   ├── postmortem/SKILL.md            # Incident learning loop
│   │
│   ├── ── META ──
│   ├── context/SKILL.md               # Project context doc management
│   └── forge/SKILL.md                 # Create/edit/rename skills & commands
│
├── commands/                          # User-invocable (/slash commands)
│   ├── localize.md          ──→ localize skill
│   ├── sheet-import.md      ──→ sheet-import skill
│   ├── git-assist.md        ──→ git-assist skill
│   ├── pre-merge.md         ──→ quality-gate skill
│   └── release-check.md     ──→ release-gate skill
│
├── agents/                            # Subagent definitions
│   └── code-reviewer.md              # Reviews steps against plans & standards
│
└── context/                           # Global context docs
    ├── footguns.md                    # Read before making changes
    ├── quality-checks.md             # Read during gate reviews
    └── workflow-tree.md              # This file
```

## Workflow Flow

```
routing ─→ brainstorm/plan/debug ─→ execute ─→ verify/inspect ─→ quality-gate ─→ release-gate
              (intake)              (work)      (check)            (merge)         (ship)
                                      │
                                      ├─ error-fix    (errors)
                                      ├─ refactor     (cleanup)
                                      ├─ integrate    (wiring)
                                      ├─ localize     (i18n)
                                      ├─ sheet-import (data)
                                      └─ git-assist   (git ops)
```

## Global Rules (enforced at all phases)

- Never commit/push/delete branches
- Protected branches: `develop`, `main`, `master`, `release/*`, `Release_*`
- Fix Protocol (Light vs Full) based on blast radius
- SetDirty enforcement for ScriptableObject edits
- Always use `rtk` prefix for CLI commands
