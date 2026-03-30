# Unity C# — Refactor Patterns

## Analysis Additions

When analyzing Unity C# files, also identify:
- What MonoBehaviour lifecycle methods does it use? (Awake, Start, Update, OnEnable, OnDisable, OnDestroy)
- What other Unity components/systems does it depend on? (GetComponent, Find, Camera.main)

## Unity-Specific Refactoring Patterns

**Cache references:**
- `GetComponent<T>()`, `Camera.main`, `transform` repeated access — cache in Awake
- `WaitForSeconds` / `WaitForEndOfFrame` — cache as `readonly` fields

**Data extraction:**
- >5 config fields on a MonoBehaviour — extract to ScriptableObject

**Coroutine cleanup:**
- `new WaitForSeconds()` inline — cache. Coroutines not tracked — store handle, stop in OnDisable

**Encapsulation:**
- `public` fields for Inspector — `[SerializeField] private` with property if needed

**Singleton cleanup:**
- Missing null check, missing OnDestroy cleanup — add standard pattern

**Object pooling:**
- Frequent Instantiate/Destroy — pool and recycle

**Dead code (Unity-specific):**
- Empty Unity methods (Awake, Start, Update with no body) — remove

## Verification Additions

- SerializeField names preserved (renaming breaks Inspector references)
- Preserve Unity callbacks — don't rename Awake, Start, Update, etc.

## Report Additions

Add to the standard refactor report:
- `GC allocations removed: [count] (estimated)` in IMPACT section
- `Check SerializeField references in Inspector` in MANUAL VERIFICATION
- `Check prefab references if components were moved` in MANUAL VERIFICATION
- `Run the scene to verify behaviour unchanged` in MANUAL VERIFICATION
