# Pre-Merge Quality Review

Run pre-merge quality checks on the current branch before merging to develop.

## Input

The user provides: `$ARGUMENTS`

Optional flags:
- `--quick` — Run BLOCKER checks only (fast mode)
- No arguments — Full quality gate review

## Steps

1. **Invoke quality-gate skill** — Load and follow `~/.claude/skills/quality-gate/SKILL.md`
2. **Pass arguments** — If `--quick` was specified, use Quick Mode from the skill

## Rules

- Diff against the detected target branch (develop for feature branches, release/* for hotfixes)
- Never skip the iteration loop (re-run after fixes)
- This command is a thin wrapper — all logic lives in the quality-gate skill
