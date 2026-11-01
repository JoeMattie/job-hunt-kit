---
name: write-cover-letter
description: Write or revise a targeted cover letter in the candidate’s learned personal writing style using confirmed career evidence and the saved job posting.
---

# Write Cover Letter

1. Read AGENTS.md and docs/data-model.md, then run `uv run scripts/hunt.py status`. If there is no application folder with a drafted resume.md for this job, follow create-targeted-resume first; it handles every earlier prerequisite. If the voice is not approved, follow build-writing-corpus and learn-candidate-voice, or obtain explicit permission for a neutral provisional draft. Then read the application folder, canonical profile, and workspace/voice/SKILL.md plus its approved profile.
2. Use the saved posting and requirement map. Verify recipient name from supplied/verified information; otherwise use Hiring Team. Select one or two confirmed examples that explain relevance rather than repeating every resume bullet.
3. Draft cover-letter.md using the candidate's register, sentence patterns, and explicit preferences. Default to preferred word count. Tie experience to actual job work. Express enthusiasm, personal motivations, or company affinity only if the candidate supplied them; an evidence-based statement of fit is sufficient. Avoid stock flattery and invented personal connections.
4. Record each factual assertion's claim IDs in application.json evidence. Company/posting facts require locators in review.md. Keep source notes out of the final letter. Do not disclose private personal details merely because they appear in samples.
5. Report two concrete voice choices with supporting sample IDs in review.md. Read the letter aloud mentally, remove filler and repetition, and ensure it contributes something beyond the resume. Apply candidate edits as preferences; do not infer new career facts from stylistic feedback.
6. Run validation and review-application. Save revisions in the existing job folder; do not send or submit.
