# Unity C# — Inspect Patterns

## Skip Rules

Skip: Auto-generated Unity files (`.meta`, `.asset`), third-party plugin code (`Plugins/`), editor scripts unless specifically changed.

## Unity Anti-Patterns

- `GetComponent<T>()` / `Find()` / `Camera.main` inside Update — cache in Awake/Start
- `gameObject.tag == "string"` — use `CompareTag()`
- `Invoke("methodName")` / `SendMessage()` — use direct calls or events
- Public fields for Inspector — use `[SerializeField] private`
- `Resources.Load()` at runtime — use Addressables
- `StartCoroutine()` without tracking/stopping in OnDisable
- Heavy work in Awake (other objects may not exist) — move to Start/OnEnable

## Null Reference Risks (Unity-specific)

- GetComponent without null check or RequireComponent
- Accessing destroyed objects after scene unload
- Missing Inspector field assignments ([SerializeField] never set)

## Memory Leaks (Unity-specific)

- Events subscribed in OnEnable but NOT unsubscribed in OnDisable
- Events subscribed in Start/Awake but NOT unsubscribed in OnDestroy
- Static references holding MonoBehaviour/GameObject references
- Coroutines not stopped in OnDisable/OnDestroy
- Addressable handles not released

## Performance & GC (Unity-specific)

- LINQ in Update/hot paths — use manual loops
- String concatenation/interpolation in Update — cache or StringBuilder
- `new List<>()` / `new Dictionary<>()` in Update — pre-allocate
- Boxing (value type to object)
- `WaitForSeconds` not cached — create once as `readonly` field
- Frequent Instantiate/Destroy — use object pooling
- Physics queries without LayerMask or using allocating versions

## Mobile Optimization

- Heavy computation in Update without frame spreading
- `Renderer.material` (creates copy) — use `sharedMaterial` if not modifying
- Canvas with dynamic elements causing full rebuild — separate canvases
- Raycast Target on non-interactive UI elements — disable it
- Large textures not compressed

## Architecture (Unity-specific)

- Game data hardcoded in MonoBehaviour — use ScriptableObjects
- MonoBehaviour used as static utility — convert to plain C# class
- Empty Unity callbacks (Awake, Start, Update) — remove them

## Report Additions

When reviewing Unity C# files, add to the standard report:
- `GC allocations removed` count in OPTIMIZATION section
- `Check SerializeField references in Inspector` in MANUAL VERIFICATION
