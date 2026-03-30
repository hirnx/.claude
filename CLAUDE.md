# Global Configuration

## Skill Visual Indicator

When any skill is invoked, print the following before doing anything else:

```
⚡ Using skill: [skill-name]
```

## Skills

All global skills live in `~/.claude/skills/<name>/SKILL.md`.

| Skill | Trigger | Path |
|---|---|---|
| error-fix | Compiler errors, console logs, exception traces, error screenshots | `skills/error-fix/SKILL.md` |
| design | New features, complex refactors, migrations touching multiple files | `skills/design/SKILL.md` |
| inspect | "review this", "check this code", file review requests | `skills/inspect/SKILL.md` |
| refactor | "refactor this", "clean up", "improve this file" | `skills/refactor/SKILL.md` |
| integrate | "complete integration", "wire up callbacks", post-migration wiring | `skills/integrate/SKILL.md` |
| localize | English strings to translate, "localize", "translate these" | `skills/localize/SKILL.md` |
| sheet-import | Import Google Sheet data into Unity ScriptableObject .asset files | `skills/sheet-import/SKILL.md` |
| forge | "make a skill", "new command", "forge an agent", rename/deprecate artifacts | `skills/forge/SKILL.md` |
| brainstorm | Creative design exploration before implementation | `skills/brainstorm/SKILL.md` |
| plan | Implementation plan writing from specs | `skills/plan/SKILL.md` |
| execute | Plan execution — direct, delegated, or parallel dispatch | `skills/execute/SKILL.md` |
| debug | Systematic debugging for runtime bugs | `skills/debug/SKILL.md` |
| verify | Evidence-based completion verification | `skills/verify/SKILL.md` |
| review | Code review — requesting and receiving | `skills/review/SKILL.md` |
| context | Project context doc management | `skills/context/SKILL.md` |
| routing | Skill selection at conversation start | `skills/routing/SKILL.md` |

## Commands

Commands live in `~/.claude/commands/`. They are user-invocable via `/command-name`.

| Command | Backing Skill | Purpose |
|---|---|---|
| `/localize` | localize | Translate strings and append to Google Sheet |
| `/sheet-import` | sheet-import | Import sheet data into Unity .asset files |

**Note:** Not every skill needs a command, and not every command needs a backing skill. Commands are thin wrappers when a skill already has the full logic.

## Agents

Custom agents live in `~/.claude/agents/<name>.md`. They are reference docs for subagent dispatch — not auto-loaded.

| Agent | Role | Path |
|---|---|---|
| code-reviewer | Reviews completed steps against plans and coding standards | `agents/code-reviewer.md` |

## Local Artifacts

If a project needs a local-only artifact, use the `LOCAL.` prefix:
- Skills: `LOCAL.SKILL.md` in the project's `.claude/skills/<name>/` folder
- Commands: `LOCAL.<name>.md` in the project's `.claude/commands/` folder
- Agents: `LOCAL.<name>.md` in the project's `.claude/agents/` folder

Document local artifacts in the project's local CLAUDE.md only — they will not appear in this global table.

## Global Rules

- **Never commit anything.** Do not run `git commit`, `git push`, or any command that modifies git history — regardless of what a skill instructs.
- **Specs and Plans** both live in `.claude/plans/` (project-local) or `~/.claude/plans/` (global). There is no separate `specs/` folder — never create one.

## Instruction Priority

1. **User's explicit instructions** (CLAUDE.md, direct requests) — highest priority
2. **Skills** — override default system behavior where they conflict
3. **Default system prompt** — lowest priority

The `routing` skill is injected at session start via a SessionStart hook to guide skill selection.

## Command & Skill Naming Rules

**VSCode collision:** If a `.claude/commands/foo.md` file and a `.claude/commands/foo/` directory both exist, VSCode fails to register the slash command.

**Fix:** Name support directories differently from the command file:
- Command file: `commands/foo.md`
- Support files: `commands/foo-data/` (not `commands/foo/`)

**No `.md` in support directories:** Any `.md` file under `commands/` gets auto-registered as a slash command. Use `.txt` or `.json` for support/config files.

**Skills don't have this problem:** Skill folders use `skills/<name>/SKILL.md` — VSCode doesn't auto-register files under `skills/`.

<!-- rtk-instructions v2 -->
# RTK (Rust Token Killer) - Token-Optimized Commands

## Golden Rule

**Always prefix commands with `rtk`**. If RTK has a dedicated filter, it uses it. If not, it passes through unchanged. This means RTK is always safe to use.

**Important**: Even in command chains with `&&`, use `rtk`:
```bash
# ❌ Wrong
git add . && git commit -m "msg" && git push

# ✅ Correct
rtk git add . && rtk git commit -m "msg" && rtk git push
```

## RTK Commands by Workflow

### Build & Compile (80-90% savings)
```bash
rtk cargo build         # Cargo build output
rtk cargo check         # Cargo check output
rtk cargo clippy        # Clippy warnings grouped by file (80%)
rtk tsc                 # TypeScript errors grouped by file/code (83%)
rtk lint                # ESLint/Biome violations grouped (84%)
rtk prettier --check    # Files needing format only (70%)
rtk next build          # Next.js build with route metrics (87%)
```

### Test (90-99% savings)
```bash
rtk cargo test          # Cargo test failures only (90%)
rtk vitest run          # Vitest failures only (99.5%)
rtk playwright test     # Playwright failures only (94%)
rtk test <cmd>          # Generic test wrapper - failures only
```

### Git (59-80% savings)
```bash
rtk git status          # Compact status
rtk git log             # Compact log (works with all git flags)
rtk git diff            # Compact diff (80%)
rtk git show            # Compact show (80%)
rtk git add             # Ultra-compact confirmations (59%)
rtk git commit          # Ultra-compact confirmations (59%)
rtk git push            # Ultra-compact confirmations
rtk git pull            # Ultra-compact confirmations
rtk git branch          # Compact branch list
rtk git fetch           # Compact fetch
rtk git stash           # Compact stash
rtk git worktree        # Compact worktree
```

Note: Git passthrough works for ALL subcommands, even those not explicitly listed.

### GitHub (26-87% savings)
```bash
rtk gh pr view <num>    # Compact PR view (87%)
rtk gh pr checks        # Compact PR checks (79%)
rtk gh run list         # Compact workflow runs (82%)
rtk gh issue list       # Compact issue list (80%)
rtk gh api              # Compact API responses (26%)
```

### JavaScript/TypeScript Tooling (70-90% savings)
```bash
rtk pnpm list           # Compact dependency tree (70%)
rtk pnpm outdated       # Compact outdated packages (80%)
rtk pnpm install        # Compact install output (90%)
rtk npm run <script>    # Compact npm script output
rtk npx <cmd>           # Compact npx command output
rtk prisma              # Prisma without ASCII art (88%)
```

### Files & Search (60-75% savings)
```bash
rtk ls <path>           # Tree format, compact (65%)
rtk read <file>         # Code reading with filtering (60%)
rtk grep <pattern>      # Search grouped by file (75%)
rtk find <pattern>      # Find grouped by directory (70%)
```

### Analysis & Debug (70-90% savings)
```bash
rtk err <cmd>           # Filter errors only from any command
rtk log <file>          # Deduplicated logs with counts
rtk json <file>         # JSON structure without values
rtk deps                # Dependency overview
rtk env                 # Environment variables compact
rtk summary <cmd>       # Smart summary of command output
rtk diff                # Ultra-compact diffs
```

### Infrastructure (85% savings)
```bash
rtk docker ps           # Compact container list
rtk docker images       # Compact image list
rtk docker logs <c>     # Deduplicated logs
rtk kubectl get         # Compact resource list
rtk kubectl logs        # Deduplicated pod logs
```

### Network (65-70% savings)
```bash
rtk curl <url>          # Compact HTTP responses (70%)
rtk wget <url>          # Compact download output (65%)
```

### Meta Commands
```bash
rtk gain                # View token savings statistics
rtk gain --history      # View command history with savings
rtk discover            # Analyze Claude Code sessions for missed RTK usage
rtk proxy <cmd>         # Run command without filtering (for debugging)
rtk init                # Add RTK instructions to CLAUDE.md
rtk init --global       # Add RTK to ~/.claude/CLAUDE.md
```

## Token Savings Overview

| Category | Commands | Typical Savings |
|----------|----------|-----------------|
| Tests | vitest, playwright, cargo test | 90-99% |
| Build | next, tsc, lint, prettier | 70-87% |
| Git | status, log, diff, add, commit | 59-80% |
| GitHub | gh pr, gh run, gh issue | 26-87% |
| Package Managers | pnpm, npm, npx | 70-90% |
| Files | ls, read, grep, find | 60-75% |
| Infrastructure | docker, kubectl | 85% |
| Network | curl, wget | 65-70% |

Overall average: **60-90% token reduction** on common development operations.
<!-- /rtk-instructions -->