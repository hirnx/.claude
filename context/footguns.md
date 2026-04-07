**Purpose:** Known project-specific pitfalls that Claude and developers should be aware of. Grows via the postmortem skill after production incidents.

## Unity / Editor

- **SetDirty on SO changes:** Any code modifying ScriptableObject fields in Editor context must call `EditorUtility.SetDirty(target)`. Without it, changes appear in the editor but don't persist to disk and won't show in git. This has caused "changes lost" incidents.

- **Prefab override leaks:** Modifying prefab instances at runtime can cause unexpected serialization. Always work on instantiated copies, never on the prefab asset directly.

## Board Event Storage

- **CloudBoardDataSaveStrategy stringId collision:** Each board event feature (MSB, MineBoard, MiniGrid, DailyPuzzle) stores its board data via `CloudBoardDataSaveStrategy`, keyed by the component's `stringId` in `PlayerGameDataManager`. If two features share the same `stringId`, one feature's data overwrites the other — and deserialization crashes because the dictionary key types differ (MSB uses `Dictionary<int, string>`, MineBoard uses `Dictionary<string, string>` with `"row-col"` keys). **When adding or cloning a board event prefab, always verify the `CloudBoardDataSaveStrategy` component has a unique `stringId`.** Incident: MineBoard shipped with `stringId: MultiStageBoardEvent` (copied from MSB), causing `FormatException` on MSB load.

## Data / Configuration

- **Test data in production:** Test server URLs, test reward values, `isTest` flags, and placeholder data have shipped to production. Always verify SO data before release. Use `// TEST_DATA` markers for grep-ability.

- **Localization sheet sync:** After updating the Google Sheet with new/changed strings, the localization must be synced to the project. Forgetting this step ships untranslated or stale strings.

## Git / Branching

- **Hotfix merge-back:** When releasing a hotfix from a release branch, those changes must be merged back to develop. Forgetting this causes the fix to be lost in the next develop release.

- **Editor-only changes invisible to git:** Changes made through Unity Editor custom windows may not trigger git diffs if SetDirty wasn't called. Check for modified .asset files before release.

## AI / Claude-Specific

- **Cascading fix spiral:** When Claude fixes one issue and it causes another, fixing that causes another, etc. Root cause: jumping to fixes without understanding blast radius. Prevention: always follow the Fix Protocol (CLAUDE.md Quality Rules).

- **Assumption blindness:** Claude assumes a method returns non-null, or a field has a default value, or a callback is always set. These implicit assumptions cause runtime crashes. Prevention: state assumptions explicitly in Change Manifests.
