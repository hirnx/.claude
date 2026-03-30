# Unity C# — Integrate Patterns

## Implementation Conventions

When implementing integration code in Unity projects:
- Use `[SerializeField] private` for Inspector-assigned references
- Use singleton access patterns where the reference project does
- Place event subscriptions in `OnEnable`/`OnDisable` or `Start`/`OnDestroy` (match the reference)

## Phase 3b: Asset & Addressable Setup

After code integration, check if the migrated system uses addressable assets or asset bundles. This is common for systems with themed/downloadable content.

**Step 1 — Discover asset dependencies:**
- Grep the system scripts for addressable-related patterns: `Addressable`, `LoadAsset`, `AssetReference`, `AssetBundle`, `bundleAddress`, `DownloadBundle`, `Loader.Load`, `IDownloader`, `ILoader`
- Identify what assets the system expects to load at runtime (prefabs, sprites, data, bundles)
- Check if the system has an addressable controller class
- Read `asset-management.md` context doc if it exists for type mappings

**Step 2 — Check reference project setup:**
- In the reference project, find how addressable groups are organized for this system
- Identify the addressable keys/addresses used
- Note which assets are remote vs local bundles

**Step 3 — Audit target project:**
- Check if the required addressable groups exist in the target project
- Check if the assets referenced by the system scripts are marked as addressable
- List any missing addressable entries, groups, or labels

**Step 4 — Report & guide:**
Since addressable configuration is done in the Unity Editor (not code), produce a clear checklist:
- Which assets need to be added to which addressable groups
- What addresses/keys to assign
- Whether bundles should be local or remote
- Any addressable profiles or build settings needed

Add this checklist to the verification checklist in Phase 4. If there are code-side changes needed (e.g. missing address constants, loader initialization), implement those directly.

## Verification Checklist Additions

```
- [ ] Open Unity — confirm no compile errors
- [ ] <specific prefab> — assign <SerializeField reference> in Inspector
- [ ] Play scene — trigger <specific action>, verify <expected behavior>
- [ ] <specific UI> — confirm <visual element> appears/hides correctly
- [ ] Addressables — <specific assets> marked addressable with correct keys
- [ ] Addressables — <specific bundle group> exists with correct build settings
```
