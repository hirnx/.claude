---
name: sheet-import
description: Use when importing data from Google Sheets into Unity ScriptableObject .asset files. Fetches sheet data, maps columns to fields, and applies changes with confirmation.
---

# Sheet Import

## Overview

Imports data from Google Sheets into Unity ScriptableObject `.asset` files. Supports single-file and glob-based multi-file imports with field mapping, match-on logic, and saved mapping reuse. Handles Unity object references via C# Editor script fallback.

## When to Use

- User wants to import/sync data from a Google Sheet to .asset files
- User says "import sheet", "update assets from sheet", "sheet import"
- Bulk data updates from spreadsheet to ScriptableObjects

**Do NOT use when:**
- Creating new .asset files from scratch
- Non-ScriptableObject data imports
- Sheet has no structured column/row format

## Project Resolution

Determine the current project name from the git repository root directory name (as-is, no transformation).
- `beachside-town` → `~/.claude/skills/sheet-import/projects/beachside-town/`
- `merge-fever-part2` → `~/.claude/skills/sheet-import/projects/merge-fever-part2/`

Create the project folder if it doesn't exist. Use it for all temp data and mappings.

---

## Step 1 — Parse Arguments

Parse `$ARGUMENTS` to extract:

- `mapping=<name>` — optional. Name of a saved mapping in `~/.claude/skills/sheet-import/projects/<project-name>/db/mappings/<name>.json`.
- `spreadsheet=<name>` — friendly spreadsheet name.
- `tab=<name>` — tab name within the spreadsheet.
- Asset path — single file path or glob (e.g. `Assets/Tag/**/*.asset`). Everything before the first newline that is not a named parameter.
- `match on: <field>` — optional line in the body. Dot-path supported (e.g. `itemId.stringId`).
- Mapping instructions — all remaining lines after the asset path and `match on` declaration.

**If `mapping=` is provided:**
- Load `~/.claude/skills/sheet-import/projects/<project-name>/db/mappings/<name>.json`.
- Apply any other provided parameters as overrides (e.g. `tab=` overrides the saved tab).
- If the file does not exist, stop and tell the user: "No saved mapping named '<name>' found."

**Parameter resolution order:** explicit argument > saved mapping value.

---

## Step 2 — Resolve Spreadsheet

Look up the spreadsheet name in `~/.claude/skills/sheet-import/db/spreadsheets.json`:

```json
{
  "spreadsheets": [
    { "name": "GameBalance", "id": "1CXstq..." }
  ]
}
```

If the name is not found:
- Tell the user: "Spreadsheet '<name>' is not in the database. Please provide its Google Sheets ID (from the URL)."
- After the user provides the ID, ask: "Save '<name>' with this ID to the database for future use?" If yes, append it to `spreadsheets.json`.

---

## Step 3 — Resolve Glob

If the asset path contains `*`:
- Expand the glob pattern on disk relative to the project root.
- If zero files match: stop immediately and tell the user: "No `.asset` files matched the pattern '<pattern>'."
- If files matched: proceed. You will show the count in the Plan step.

**`match on` requirement:** If the asset path is a glob and no `match on` field is present (from arguments or saved mapping), ask the user to provide it before continuing.

---

## Step 4 — Fetch

Run the fetcher script:

```bash
python "~/.claude/skills/sheet-import/scripts/fetch.py" "<spreadsheet_id>" "<tab_name>"
```

This writes `~/.claude/skills/sheet-import/projects/<project-name>/temp_data.json`.

If the script exits with an error, stop and show the error to the user.

---

## Step 5 — Preview

Read `temp_data.json`. Display a markdown table of the fetched data:
- Show all column headers as the table header row.
- Show the first 5 data rows (or all rows if fewer than 5).
- Show the total row count below the table.

---

## Step 6 — Plan

Build the full change plan before asking for confirmation.

**Single-file asset path:**
- If the sheet has exactly 1 data row: apply that row to the file.
- If the sheet has multiple rows and `match on` is provided: find the row where the match-on column equals the current value of that field in the asset. Apply that row. Skip and report all others.
- If the sheet has multiple rows and no `match on`: list all rows and ask the user: "Which row should I apply to this file?" Wait for their response before proceeding.

**Glob asset path (one row per file):**
- For each resolved `.asset` file: read the file, find the value of the match-on field, find the sheet row where the same column matches that value.
- Build the change plan: for each file and each mapped field, show `old value → new value`.
- Report files that have no matching sheet row (will be skipped).
- Report sheet rows that have no matching asset file (will be skipped).

**Field safety checks (apply to every planned field change):**
- If a field name starts with `m_` or is one of `fileID`, `guid`, `type` (inside an object reference), refuse to include it in the plan and tell the user.
- If a field's current YAML value matches `{fileID: ..., guid: ..., type: ...}` — it is a Unity object reference. Exclude it from the YAML plan and flag it separately (see Fallback section below).
- If a field does not exist in the asset file, skip that file/field and report it.

**Present the plan** as a table:
```
File | Field | Old Value | New Value
-----|-------|-----------|----------
Assets/…/Sub.asset | dropChance | 0.25 | 0.35
Assets/…/Sub.asset | maxStack | 3 | 5
```

If any fields were blocked (internal or object references), list them clearly below the table.

---

## Step 7 — Confirm

Ask once:

> "Apply these N changes across M files?"

Do not proceed until the user explicitly confirms. If they say no or ask to change anything, go back to clarifying before re-planning.

**Stale data check:** If more than 30 minutes have passed since `fetched_at` in `temp_data.json`, or if the user asked any questions or did anything between the preview and this confirmation, re-run Step 4 before applying.

---

## Step 8 — Apply

For each file in the plan (one at a time):

1. Read the `.asset` file content.
2. For each mapped field:
   - **Flat scalar:** find the line `fieldName: value` and replace `value`.
   - **Nested struct (dot-path):** find the parent key, then the child key on the next indented line, and replace its value only.
   - **Scalar array:** replace the array block with new values, one `- value` per matching sheet row.
3. Write the updated content back to the file.
4. If the file cannot be parsed as YAML or a write fails: skip it, report the error, continue with remaining files.

**Never modify any field not explicitly named in the mapping instructions.**

---

## Step 9 — Object Reference Fallback (if any blocked fields exist)

For each field blocked because it is a Unity object reference:

Tell the user: "`<fieldName>` in `<file>` contains a Unity object reference — YAML editing is not safe here."

Ask: "I can generate a temporary C# Editor script to apply this field. Want me to?"

If yes:
1. Generate `Assets/Editor/SheetImportTemp.cs` — a `[MenuItem("Tools/Sheet Import Temp")]` script that uses `AssetDatabase` to load the target asset and set the field. Hardcode all values from `temp_data.json` inline in the C# source. Do not read the JSON file at runtime.
2. Tell the user: "Switch to Unity (it will recompile), then run **Tools > Sheet Import Temp** from the menu bar. Come back and tell me when it's done."
3. Wait for the user to confirm it ran.
4. If success: delete `Assets/Editor/SheetImportTemp.cs` and report.
5. If Unity reports a compilation error: diagnose from the error and offer a corrected script. Do not delete the temp file until it has run successfully.

---

## Step 10 — Save Mapping

If this was a loaded saved mapping: update `last_run` in `~/.claude/skills/sheet-import/projects/<project-name>/db/mappings/<name>.json` to the current ISO timestamp.

If this was an ad-hoc import: ask:
> "Save this as a reusable mapping for next time? If yes, give it a name (e.g. `mine-board-drop-rates`)."

If the user provides a name, create `~/.claude/skills/sheet-import/projects/<project-name>/db/mappings/<name>.json`:
```json
{
  "name": "<name>",
  "spreadsheet": "<spreadsheet_name>",
  "tab": "<tab_name>",
  "assets": "<asset_path_or_glob>",
  "match_on": "<match_on_field_or_null>",
  "instructions": "<mapping instructions verbatim>",
  "created_at": "<ISO timestamp>",
  "last_run": "<ISO timestamp>"
}
```

---

## Step 11 — Report

Show a final summary:
- Files updated (count and list)
- Fields changed per file
- Rows/files skipped and why
- Any fields that used the C# fallback

---

## Rules (always apply)

- **Never modify a field not named in the mapping instructions.**
- **Never modify `m_*` fields, `fileID`, `guid`, or `type` inside object references.**
- **Always confirm before writing.** One confirmation for the whole batch.
- **Never write to the database without user confirmation** (except updating `last_run`).
- **Never overwrite a saved mapping's instructions** without the user explicitly asking.
- A field whose YAML value is `{fileID: ..., guid: ..., type: ...}` is an object reference — never edit it via YAML, always offer the C# fallback.
