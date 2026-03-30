# Unity C# — Error-Fix Patterns

## Error-Fix Pattern Library

> This section is embedded in every fixer agent's prompt. Agents cannot load
> skills via the Skill tool — they receive this library inline in their prompt.

### CS0101 / CS0111 — Duplicate type or member
Two files define the same class/member in the same namespace, usually from an
imported package conflicting with an existing file. Keep the target project's
version. Delete the import. If the deleted file had API others depend on, add
wrappers/aliases to the surviving file.

### CS0104 — Ambiguous reference
Same type name in two namespaces. Identify real implementation vs stub. Revert
stubs to empty. Rewrite consumer to use only the real namespace. Delete files
incorrectly filling stub namespaces.

### CS0115 — No suitable method to override
Base class lacks the `virtual` method the subclass overrides. Add
`public virtual MethodName(...) { }` to the base.

### CS0117 — Missing constant or enum value
Add the missing value. Read existing enum values first to avoid integer
collisions. Check source project for correct value if uncertain.

### CS0246 — Type not found
Decision tree (follow in order):
1. Grep for class name across the whole project. If found under different
   namespace → fix the `using`, do not duplicate.
2. If found in same namespace but inaccessible → check `internal`/asmdef
   boundary (see assembly section below).
3. If it's an interface/abstract → look for equivalent contract in target
   project. Rewrite consumer to use it.
4. Only if not found anywhere → check source project, then copy/adapt.

### CS0103 — Name not in context
Member referenced in a subclass doesn't exist on the base class. Read the
target's base class, then add the missing member or alias an existing one.

### CS1061 — Member missing on type
Member exists in source project but not target. Read the target class first.
If renamed → add wrapper/alias. If missing entirely → read source for
implementation and port it.

### CS1501 — Wrong argument count
Method exists but with fewer parameters. Add an overload matching the call
signature; delegate to the existing method.

### Assembly boundary — `internal` inaccessible from Editor
`internal` members in runtime assembly are not visible from editor assemblies.
Fix: change `internal` → `public`, gated with `#if UNITY_EDITOR`.

## Unity-Specific Context Loading

1. If errors look migration-related (missing members, namespace conflicts,
   type-not-found after import): load migration context docs if they exist.
2. If a relevant `migrations/<feature>.md` exists in `.claude/context/`: load
   it — known fixes take priority over re-deriving them.

## Unity-Specific Fix Rules

- Never fill intentionally empty stub namespaces
- Prefer additive fixes: wrappers, aliases, overloads — do not modify existing callers

## Unity Console Format

Errors typically appear as: `Assets/path/file.cs(line,col): error CS####: message`

## Unity Verification

The user runs a Unity build to confirm compilation. Phase 4 static analysis is
LLM reasoning — not a build trigger.

## Context Update (Unity)

After fixing errors:
- New type mappings, renamed members, enum additions → add to the relevant
  migration doc in `.claude/context/migrations/`
- New patterns or namespace rules → add to `.claude/context/` or create a new
  context file if no existing file fits
