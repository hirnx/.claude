---
name: forge
description: Use when creating, editing, renaming, or deprecating skills, commands, or agents. Triggers on "make a skill", "new command", "forge an agent", "rename X", "deprecate X", or any artifact lifecycle management.
---

# Forge

## Overview

Manages the full lifecycle of Claude Code artifacts — skills, commands, and agents. Handles creation (wizard-guided), editing, renaming, and deprecation with automatic reference updates across all CLAUDE.md files and settings. Forge never deletes files — deletion is always manual.

Incorporates skill authoring principles and reference material in `forge/reference/`. For pressure testing discipline-enforcing skills, see `forge/reference/testing-skills-with-subagents.md`.

## When to Use

- "Make a skill", "new command", "forge an agent", "create"
- "Update the X skill", "change X description", "edit"
- "Rename X to Y"
- "Deprecate X", "remove usage of Y"
- Any artifact lifecycle management

**Do NOT use when:**
- Validating skill effectiveness with pressure tests — see `forge/reference/testing-skills-with-subagents.md`
- Configuring settings.json hooks — use `update-config` skill
- One-off solutions that don't warrant a persistent artifact

---

## Artifact Types

| Type | Global | Local | Convention |
|---|---|---|---|
| Skill | `~/.claude/skills/<name>/SKILL.md` | `<project>/.claude/skills/<name>/LOCAL.SKILL.md` | Folder with SKILL.md + optional support files |
| Command | `~/.claude/commands/<name>.md` | `<project>/.claude/commands/LOCAL.<name>.md` | Flat .md file + optional `<name>-data/` for support files |
| Agent | `~/.claude/agents/<name>.md` | `<project>/.claude/agents/LOCAL.<name>.md` | Agent definition with system prompt and config |

**Local artifact convention:** All local artifacts use the `LOCAL.` prefix (dot separator). Local artifacts are documented in the project's local CLAUDE.md only.

**Skills and commands are independent.** Not every skill needs a command, not every command needs a skill:
- Skill only → auto-triggered or invoked by name
- Skill + thin command wrapper → skill has logic, `/slash-command` for direct invocation
- Command only → standalone action, no auto-triggering needed

---

## Operations

| Operation | Triggers | Flow |
|---|---|---|
| **Create** | "make", "new", "forge", "create" | Research → recommend → wizard → scaffold → write → register |
| **Edit** | "update", "change", "edit" | Research → read → guided changes → update + references → notify |
| **Rename** | "rename X to Y" | Validate → rename files → update frontmatter → auto-update references → notify |
| **Deprecate** | "deprecate", "remove usage", "retire" | Mark deprecated → remove from CLAUDE.md tables → remove cross-references → list files for manual deletion → notify |

---

## Create Flow

### Step 1: Understand and recommend

User describes what they want. Analyze and recommend the artifact type:

- Needs auto-triggering or behavior guidance? → **Skill**
- User-invocable action with arguments? → **Command**
- Dispatched as subprocess with isolated context? → **Agent**

If ambiguous, present options with trade-offs. Back-and-forth until aligned.

Also determine **scope**:
- Used across multiple projects? → **Global** (`~/.claude/`)
- Only this project? → **Local** (`<project>/.claude/`)
- If unclear, recommend global (can be moved later)

### Step 2: Check for existing fit

Before creating anything new, check two things:

**a) Existing artifacts:**
- Could this naturally extend an existing skill/command/agent?
- Propose extending ONLY if:
  - The addition doesn't stretch the original's core purpose
  - The original doesn't lose its main gist
  - The fit is natural, not forced
- If extending would dilute → create new

**b) Web research:**
- Search for existing skills/agents/commands that do something similar
- Check: GitHub skill repos, Anthropic official skills, community collections
- If found: present to user — "There's an existing X that does Y. Use/adapt it, or build custom?"
- If nothing found or web unavailable: proceed with creation

### Step 3: Name

- Suggest a name based on the description, or ask
- Validate: lowercase, hyphens only, no conflicts with existing names
- Check for collisions in the target directory
- Prefer verb-first, active names (`fix-errors` not `error-fixer`)

### Step 4: Gather essentials

Structured wizard — only essential questions, smart defaults from `project-profile.md`.

**For skill** (3 questions max):
1. "What does this skill do?" → generates Overview
2. "When should it trigger?" → generates description frontmatter + When to Use
3. "Walk me through the process" → generates The Process steps

**For command** (2 questions max):
1. "What does this command do when invoked with `/name`?"
2. "Does it need support files?" → creates `<name>-data/` if yes

**For agent** (2 questions max):
1. "What is this agent's role/responsibility?"
2. "What tools does it need access to?"

### Step 5: Enrich with project profile

- Load `.claude/project-profile.md` from the project (if exists)
- Use platform/domain info to enrich generated content

### Step 6: Generate and present

- Load the appropriate template from `forge/templates/`
- Fill with gathered info + profile context
- Present the full draft for approval
- Iterate on feedback until approved

### Step 7: Write and register

- Write the file(s) to the appropriate location
- Update `~/.claude/CLAUDE.md` (or local CLAUDE.md for local artifacts) with the new entry
- Print confirmation with file paths

---

## Edit Flow

1. Identify which artifact to edit
2. Read the current file
3. If adding new capabilities (not cosmetic changes): run web research for existing solutions
4. Guide the user through changes
5. Present updated draft for approval
6. Write changes
7. Auto-update references if name/description changed
8. Notify user of all changes made

---

## Rename Flow

1. Identify artifact and new name
2. Validate new name (no conflicts, correct format)
3. Perform the rename:
   - **Skill:** rename folder, update SKILL.md frontmatter `name:` and `# heading`
   - **Command:** rename .md file, rename `-data/` folder if exists
   - **Agent:** rename .md file
4. Auto-update all references (see Reference Auto-Update Scope)
5. Notify with summary

---

## Deprecate Flow

**Forge NEVER deletes files.** Actual file deletion is always done manually by the user.

1. Identify the artifact
2. Add `**[DEPRECATED]**` to the artifact's frontmatter description
3. Remove entries from CLAUDE.md tables (skills, commands, agents)
4. Remove cross-references from other skills, settings.json hooks, and additionalDirectories
5. List all files/folders the user should manually delete:

```
🗑️ Deprecated: <artifact-name>
References removed from:
- ~/.claude/CLAUDE.md (skills table)
- ~/.claude/settings.json (hook path)

Files to delete manually:
- ~/.claude/skills/<name>/SKILL.md
- ~/.claude/skills/<name>/  (entire folder)
```

6. Do NOT delete, move, or modify the actual artifact files beyond adding the deprecated marker

---

## Reference Auto-Update Scope

Applies to rename, deprecate, and edit (when name/description changes):

| Location | What to check |
|---|---|
| `~/.claude/CLAUDE.md` | Skills, Commands, Agents tables |
| Project `CLAUDE.md` files | Any text mentioning the artifact name |
| `~/.claude/settings.json` | `hooks[].hooks[].command` (file paths), `permissions.additionalDirectories[]` |
| Other skills/agents | Cross-references to the artifact |

After any auto-update, print:
```
📝 Updated references:
- ~/.claude/CLAUDE.md (skills table)
- settings.json (hook path)
- beachside-town/CLAUDE.md (line 26)
```

---

## SKILL.md Authoring Guide

### Frontmatter

Only two fields: `name` and `description` (max 1024 chars total).

- `name`: lowercase, hyphens only
- `description`: starts with "Use when...", describes WHEN to trigger, NOT how the skill works

**CRITICAL:** Never summarize the skill's workflow in the description. Testing shows Claude shortcuts the body when the description contains process details.

```yaml
# BAD: Summarizes workflow
description: Use when executing plans - dispatches subagent per task with code review

# GOOD: Just triggering conditions
description: Use when executing implementation plans with independent tasks
```

### Structure

See `forge/templates/skill.md` for the canonical template. Key sections:

1. **Overview** — core principle in 1-2 sentences
2. **When to Use** — triggers, symptoms, counter-triggers
3. **The Process** — numbered steps or phases
4. **Quick Reference** — scannable table
5. **Common Mistakes** — what goes wrong + fixes

For **discipline-enforcing skills**, add before The Process:
- **Iron Law** — non-negotiable rule in code block
- **No exceptions** list
- **Rationalization table** (Excuse | Reality)
- **Red Flags - STOP** list

### Token Efficiency

- SKILL.md under 500 lines — heavy reference goes in sibling files
- One excellent example per concept, not multi-language
- Use cross-references instead of repeating content
- Move 100+ line reference material to separate files

### Naming

- Verb-first, active voice: `fix-errors` not `error-fixer`
- Gerunds work well for processes: `creating-skills`, `debugging-with-logs`
- Be descriptive: `condition-based-waiting` not `async-helpers`

### Keyword Coverage (CSO)

Use words Claude would search for:
- Error messages, symptoms, synonyms
- Tool names, library names, file types
- Concrete triggers over abstract descriptions

---

## Command Authoring Guide

See `forge/templates/command.md`. Commands are simpler than skills:

- No frontmatter needed
- Clear `## Input` section with `$ARGUMENTS`
- Step-by-step `## Steps`
- `## Rules` for constraints

**Thin wrapper pattern** — when a skill already has the logic:
```markdown
Invoke the `<skill-name>` skill with the user's input: $ARGUMENTS
```

**Support files:** Use `<name>-data/` directory (not `<name>/`) to avoid VSCode collision with the command `.md` file.

---

## Agent Authoring Guide

See `forge/templates/agent.md`. Agents are dispatched subprocesses:

- Clear **Role** section
- **Context Provided** — what the dispatcher gives
- **Tools Available** — which tools it can use
- **Process** — numbered steps
- **Output Contract** — structured return format

---

## Project Profile Enrichment

`project-profile.md` provides platform and domain context for generated content.

- **Location:** `.claude/project-profile.md` (project-local only)
- If not present, forge works generically.

Forge reads the profile but does not create or manage it.

---

## Quick Reference

| Operation | Steps | Key output |
|---|---|---|
| Create | Recommend → research → name → gather → enrich → generate → write | New artifact + CLAUDE.md updated |
| Edit | Identify → read → (research) → guide → write → update refs | Modified artifact + refs updated |
| Rename | Validate → rename files → update frontmatter → update refs | Renamed artifact + all refs updated |
| Deprecate | Mark deprecated → remove refs → list files for manual deletion | Safe retirement, no file deletion |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Creating a new skill when extending an existing one would work | Always check existing artifacts first |
| Summarizing workflow in skill description | Description = WHEN to trigger only |
| Putting support files in same dir as command .md | Use `<name>-data/` to avoid VSCode collision |
| Not updating CLAUDE.md after creating artifact | Forge handles this automatically |
| Creating duplicate global + local versions | One location only — global OR local |
| Stretching an existing skill to fit unrelated functionality | If the fit isn't natural, create new |
