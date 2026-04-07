---
name: postmortem
description: Use when a production incident occurs — captures what went wrong, updates context docs and quality checks so the system prevents this class of issue in the future.
---

# Postmortem

## Overview

Turn production incidents into prevention. Every incident that reaches production represents a gap in the quality system. This skill closes that gap permanently.

**Core principle:** The system gets smarter after every failure. No incident should happen twice.

## When to Use

- User mentions a production bug, incident, or issue that shipped
- User says "went to prod", "shipped broken", "found in production", "production issue", "prod bug"
- After any issue that made it past quality-gate and release-gate

**Do NOT use when:**
- Bug is caught before merge (quality-gate handles this)
- Bug is caught before release (release-gate handles this)
- Bug is in development (use debug skill)

---

## The Process

### Step 1: Capture the Incident

Ask targeted questions (short, one at a time):

1. **What happened?** — The observable symptom in production
2. **What was the root cause?** — (May need investigation with debug skill first)
3. **When was it introduced?** — Which commit/branch/release
4. **Why wasn't it caught?** — Which gate should have caught it?

### Step 2: Classify the Gap

Which layer failed?

| Layer | Example |
|---|---|
| **Prevention (CLAUDE.md rules)** | Claude made the same type of mistake the rules should prevent |
| **Detection (hooks)** | A hook should have warned but didn't exist |
| **Quality Gate (/pre-merge)** | The pattern check should have caught it but wasn't in the checklist |
| **Release Gate (/release-check)** | The data/config check should have flagged it |
| **Learning (context docs)** | This footgun was known but not documented |

### Step 3: Create Prevention

Based on the gap classification, update the appropriate layer:

**If Prevention gap → update CLAUDE.md:**
- Add a new rule under Quality Rules that would have prevented this
- Keep rules concise and actionable

**If Detection gap → propose new hook:**
- Describe what the hook should detect and when
- User approves, then add to settings.json

**If Quality Gate gap → update ~/.claude/context/quality-checks.md:**
- Add a new check item with: what to check, how to check, severity (BLOCKER/WARNING)
- The quality-gate skill reads this file and includes these checks

**If Release Gate gap → update ~/.claude/context/quality-checks.md:**
- Add a release-specific check item
- The release-gate skill reads this file for additional checks

**If Learning gap → update ~/.claude/context/footguns.md:**
- Add the footgun: what it is, why it's dangerous, how to avoid it

### Step 4: Verify Updates

Read each file that was updated. Confirm:
- New check would have caught this specific incident
- Check is specific enough to avoid false positives
- Check is general enough to catch similar incidents (not just this exact one)

### Step 5: Document the Incident

Append a brief incident record to `~/.claude/context/incidents.md` (create if doesn't exist):

```markdown
### [Date] — [One-line summary]
- **Symptom:** [what happened]
- **Root cause:** [why]
- **Gap:** [which layer failed]
- **Fix:** [what was added to prevent recurrence]
```

---

## Quick Reference

| Step | Key Activities | Success Criteria |
|------|---------------|------------------|
| 1 | Capture incident | Understand what, why, when |
| 2 | Classify gap | Know which layer failed |
| 3 | Create prevention | Update the right layer |
| 4 | Verify updates | New check would catch this |
| 5 | Document | Incident recorded for history |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Too-specific check (only catches this exact bug) | Generalize to the class of bug |
| Too-broad check (false positives) | Be specific about the pattern |
| Skipping verification of the new check | Always verify the check would actually catch it |
| Not updating the right layer | Classify the gap first |
| Adding redundant checks | Read existing checks before adding |

## Integration

**Auto-triggered by:** UserPromptSubmit hook (production incident keywords)
**Feeds into:**
- `context/footguns.md` — known pitfalls
- `context/quality-checks.md` — evolving checklist
- `~/.claude/CLAUDE.md` Quality Rules — behavioral rules
- `~/.claude/settings.json` hooks — new detection hooks
