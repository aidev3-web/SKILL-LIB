---
name: no-emoji-check
description: "Check a drafted message, commit, or document for emoji before it's sent/committed — emoji should only appear if the user explicitly asked for them. Use this whenever about to finalize a commit message, PR description, chat reply, or document draft, or when asked to review a draft for style compliance."
---

# No-emoji check

## What this is for

Default writing style should not include emoji unless the user has explicitly
asked for them somewhere in the current request. This skill is the portable
check for that rule — the same rule usually only lives in a project's own
`CLAUDE.md`, which other agents/tools never read.

## Complexity contract

- **Cost**: 1 pass over the draft text, no external calls.
- **Applicability boundary**: only checks for literal emoji characters
  (Unicode emoji ranges) in the given text — does not judge tone, does not
  rewrite the text, does not check anything else about style.
- **Fallback**: if the draft is code (not prose — e.g. a source file), skip
  this check entirely; emoji-in-code has a different set of rules this skill
  doesn't cover.

## The rule

1. Scan the draft for emoji characters.
2. If any are found **and** the user did not explicitly ask for emoji
   anywhere in the current request, flag each one with its position and
   suggest a plain-text alternative (or removal).
3. If the user did ask for emoji, or none are found, say so and move on —
   don't invent a finding to justify having run the check.

## Judgment calls

If unsure whether a word (e.g. "checkmark") is being used as literal emoji
or plain text, check the actual Unicode codepoint — plain words are never a
false positive under this rule, only real emoji characters are.
