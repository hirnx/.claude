# Release Readiness Check

Run release readiness validation before building/shipping.

## Input

The user provides: `$ARGUMENTS`

No arguments expected. Runs full release gate.

## Steps

1. **Invoke release-gate skill** — Load and follow `~/.claude/skills/release-gate/SKILL.md`

## Rules

- This command is a thin wrapper — all logic lives in the release-gate skill
