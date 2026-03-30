---
name: localize
description: Use when translating English strings. Generates localization keys, translates to target languages, and appends to Google Sheet.
---

# Localize

## Overview

Localization skill. Takes English strings, generates keys, translates to target languages, previews in a table, and appends to a Google Sheet after confirmation.

## When to Use

- User provides English strings to localize
- User says "localize", "translate these strings"
- New UI text needs to be added to the localization sheet

**Do NOT use when:**
- Updating existing translations (this skill only appends)
- Non-game text (technical docs, code comments)

## Project Resolution

Determine the current project name from the git repository root directory name (as-is, no transformation).
- `beachside-town` → `~/.claude/skills/localize/projects/beachside-town/`
- `merge-fever-part2` → `~/.claude/skills/localize/projects/merge-fever-part2/`

Create the project folder if it doesn't exist. Use it for all temp/project-specific data.

---

## Input

The user provides: `$ARGUMENTS`

Each line is one English string to localize.

## Steps

1. **Parse** — split `$ARGUMENTS` by newlines, trim whitespace, skip empty lines.
2. **Generate keys** — for each English string, generate a key:
   - Lowercase → replace spaces with `_` → remove non `a-z0-9_` → collapse `__` → trim `_` → truncate 60 chars (break at last `_`)
   - Empty result → `untitled_key`
3. **Translate** — translate each string to these languages (in this exact order):
   German, Korean, Japanese, French, Spanish (es-ES), Portuguese, Russian, Italian, Chinese (Simplified), Chinese (Traditional)
   - Translate naturally, preserving meaning and tone
   - Keep placeholders like `{0}`, `%s`, `<color>` etc. untranslated
   - For game UI strings, prefer concise translations
4. **Preview** — show the user a markdown table: Key | English | German | Korean | Japanese | French | Spanish [es-ES] | Portuguese | Russian | Italian | Chinese (Simplified) | Chinese (Traditional)
5. **Ask** — "Append these to the sheet?"
6. **Append** — only after confirmation, write a JSON file and run the append script:
   - Create `~/.claude/skills/localize/projects/<project-name>/temp_rows.json` with format: `[["key","english","german",...], ...]`
   - Each inner array is one row in column order: Key, English, German, Korean, Japanese, French, Spanish [es-ES], Portuguese, Russian, Italian, Chinese (Simplified), Chinese (Traditional)
   - Run: `python ~/.claude/skills/localize/scripts/localize.py ~/.claude/skills/localize/projects/<project-name>/temp_rows.json`
7. **Report** — show how many rows were appended.

## Rules

- **NEVER** remove or update existing rows in the sheet. Only append.
- Always show preview before appending.
- Keep translations contextually appropriate for a mobile game UI.
