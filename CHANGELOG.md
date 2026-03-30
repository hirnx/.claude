# Changelog

## 2026-03-27 — Skill Chaining Protocol

Implemented handoff protocol between skills using standalone `.claude/handoffs/` files. Skills write state (decisions, files, preferences, skip list) before suggesting the next skill. Receiving skills check for handoffs and skip phases already covered.

Chains: brainstorm→plan→execute→review→verify, debug→error-fix→verify, all→verify.

## 2026-03-27 — Skill Merges

Consolidated 19 skills → 16 by merging related skills:

- `execute-plan` + `subagent-dev` + `parallel-dispatch` → **`execute`** (3 modes: direct, delegate, dispatch)
- `request-review` + `receive-review` → **`review`** (full review cycle: request + receive)

## 2026-03-26 — Skills System Launch

Launched the fully local skills system with 16 skills, replacing the external plugin dependency. All process logic preserved; external coupling removed.

### Skills
- `brainstorm` — creative design exploration
- `plan` — implementation plan writing
- `execute` — plan execution (direct, delegate, dispatch modes)
- `debug` — systematic debugging methodology, adapted for Unity toolchain
- `verify` — evidence-based completion verification
- `review` — code review (request + receive)
- `error-fix` — parallel compiler error fixing
- `design` — feature design with reverse-prompting
- `inspect` — Unity C# code review checklist
- `refactor` — code cleanup preserving behavior
- `integrate` — post-migration callsite wiring
- `localize` — string translation via Google Sheets
- `sheet-import` — Google Sheet data import to Unity assets
- `forge` — skill/command/agent lifecycle management
- `context` — project-local `.claude/context/` doc management
- `routing` — skill selection rules, injected at session start

### Agent
- `code-reviewer` — plan alignment and code quality review agent

### Infrastructure
- Forge reference docs for skill authoring
- Specs and plans in `.claude/plans/` (global and project-local)
- SessionStart hook for routing skill injection
- Inline self-review optimization (checklists instead of subagent review loops)

### Design Decisions
- Git commit/push steps removed (global no-commit rule)
- TDD requirements removed (verify discipline kept)
- Worktree prerequisites removed
- Debug skill adapted for Unity (LSP, CS#### codes, .meta files, asmdef boundaries)
- Verify skill adapted for Unity (compile verification instead of test runs)
- Code-reviewer agent adapted with Unity-specific review points

## 2026-03-25 — Skills & Commands Restructure

Established the `~/.claude/skills/<name>/SKILL.md` folder convention. Created global `CLAUDE.md`. Separated skills (behavior) from commands (user entry points). Moved `localize` and `sheet-import` support files into proper skill folders with project-scoped subdirectories.

## 2026-03-25 — Forge Skill

Created the `forge` skill for artifact lifecycle management — create, edit, rename, deprecate skills/commands/agents with automatic reference updates.
