---
name: verify
description: Use when about to claim work is complete, fixed, or passing — requires running verification and confirming output before making any success claims; evidence before assertions always
---

# Verification Before Completion

## Overview

Claiming work is complete without verification is dishonesty, not efficiency.

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't verified in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What proves this claim?
2. RUN: Execute verification (read files, check output, confirm state)
3. READ: Full output, check for issues
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Files compile | Read changed files, check for syntax/type errors | "Should compile" |
| Bug fixed | Verify the fix addresses root cause | Code changed, assumed fixed |
| Requirements met | Line-by-line checklist against spec | "Looks done" |
| Agent completed | Check actual file changes | Agent reports "success" |
| Refactor preserves behavior | Verify no logic changes | "Only moved code" |
| All files updated | List every changed file | "Updated the relevant files" |

## Red Flags - STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!")
- Trusting agent success reports without checking
- Relying on partial verification
- Thinking "just this once"
- **ANY wording implying success without having run verification**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Agent said success" | Verify independently |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**File changes:**
```
✅ [Read changed files] [Verify syntax correct] [Check logic matches intent] "Changes verified"
❌ "Should be correct" / "Looks right"
```

**Requirements:**
```
✅ Re-read spec → Create checklist → Verify each → Report gaps or completion
❌ "I've implemented everything"
```

**Agent delegation:**
```
✅ Agent reports success → Check actual file diffs → Verify changes → Report actual state
❌ Trust agent report
```

## Step 0: Check for Handoff

Before starting, check for a handoff file:

1. Look for `.claude/handoffs/*-to-verify.md` (any skill can chain to verify)
2. If found → read it, pre-load what was done and what to check
3. If not found → determine what to verify from conversation context

| Handoff field | What it skips |
|---|---|
| Decisions (what was done) | "What should I verify?" gathering |
| Files touched | File discovery — already listed |
| User preferences | Context about deviations or constraints |

After consuming the handoff, delete the handoff file.

---

## When To Apply

**ALWAYS before:**
- ANY variation of success/completion claims
- ANY expression of satisfaction
- ANY positive statement about work state
- Moving to next task
- Delegating to agents

## The Bottom Line

**No shortcuts for verification.**

Check the actual state. Read the actual output. THEN claim the result.

This is non-negotiable.
