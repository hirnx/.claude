**Purpose:** Evolving checklist of quality checks used by quality-gate and release-gate skills. Grows via the postmortem skill after production incidents. Each check was born from a real failure.

## Pre-Merge Checks (used by quality-gate)

### BLOCKER

| ID | Check | Pattern/Command | Added |
|----|-------|-----------------|-------|
| QM-001 | Merge conflict markers | Grep `<<<<<<<\|=======\|>>>>>>>` in changed files | Initial |
| QM-002 | Orphaned .meta files | For each added/deleted asset, verify .meta pair | Initial |
| QM-003 | Known test data | Grep `localhost\|isTest.*true\|// TEST_DATA\|test_server` | Initial |
| QM-004 | Debug.Log without guard | Grep `Debug\.Log` in non-Editor .cs files without `#if` | Initial |
| QM-005 | Missing SetDirty | SO field assignment in Editor/ code without SetDirty nearby | Initial |

### WARNING

| ID | Check | Pattern/Command | Added |
|----|-------|-----------------|-------|
| QW-001 | Null reference risk | `.something` on GetComponent/Find/as/dictionary result without null check | Initial |
| QW-002 | Long methods | Changed methods > 60 lines | Initial |
| QW-003 | Missing localization | New strings in UI code without localization | Initial |
| QW-004 | Coroutine without cleanup | StartCoroutine without StopCoroutine in OnDestroy | Initial |
| QW-005 | Unused variables | Declared but unused in changed files | Initial |

## Release Checks (used by release-gate)

### NO-GO

| ID | Check | Pattern/Command | Added |
|----|-------|-----------------|-------|
| QR-001 | Unmerged hotfix branches | `git branch --no-merged` for hotfix/* | Initial |
| QR-002 | Dirty working directory | `git status` non-empty | Initial |
| QR-003 | Test data in .asset files | Grep .asset files for test patterns | Initial |
| QR-004 | Uncommitted .asset changes | .asset modified on disk but not staged | Initial |

### WARNING

| ID | Check | Pattern/Command | Added |
|----|-------|-----------------|-------|
| QR-005 | Localization files changed | Check if localization files modified since last tag | Initial |
| QR-006 | Debug.Log in build | Unguarded Debug.Log in runtime code | Initial |
| QR-007 | TODO/HACK/FIXME in release | Grep for markers in changed files since last tag | Initial |

## Adding New Checks

When the postmortem skill identifies a gap, add a new row:
- Use the next ID in sequence (QM-006, QW-006, QR-008, etc.)
- Include the grep pattern or command to detect it
- Set Added to the date the check was added
- Be specific enough to avoid false positives
