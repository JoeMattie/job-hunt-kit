---
name: review-application
description: Audit a job-specific resume and cover letter for factual support, requirement coverage, personal voice, privacy, and document readiness.
---

# Review Application

1. Read AGENTS.md. If no application folder exists for the job, or resume.md or cover-letter.md still holds template placeholders, follow create-targeted-resume or write-cover-letter first. Then read the saved posting, profile, voice skill/profile, application.json, and the actual drafts. Run `uv run scripts/hunt.py validate` first; resolve stale snapshot warnings by rechecking evidence before refreshing its hash.
2. Check every factual assertion against confirmed claims and their original sources. Check that every assertion has an evidence record and that every cited claim actually supports its wording. Verify dates, numbers, degree status, exact titles, team attribution, contact details, and links. Automated linkage checks cannot establish truth or complete coverage.
3. Compare requirement map with the original posting. Report uncovered requirements and inaccessible/stale posting information. Never fix a gap by embellishment.
4. Compare prose against approved voice rules and examples. Check register, forced quirks, fabricated motivation, repetition, placeholders, internal citations, and accidental disclosure. Confirm final exported text contains no review notes.
5. If DOCX/PDF was requested, export with `uv run scripts/hunt.py export`; when Pandoc is absent, produce the file from the final Markdown with your own document tools (docx/pdf skills) into the same job folder. Inspect each page and extracted reading order. Set layout_checked only after actual visual review; successful conversion alone is insufficient. If no tool can render or inspect the file, leave it false and report that limitation.
6. Write an actionable review.md. Set facts_checked and voice_checked only after the corresponding review. Candidate approval is separate; do not populate approved_by without explicit approval. Do not submit. List the concrete remaining actions, or say the packet is ready for candidate review.
