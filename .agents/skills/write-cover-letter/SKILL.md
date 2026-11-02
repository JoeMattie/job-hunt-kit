---
name: write-cover-letter
description: Write or revise a targeted cover letter in the candidate’s learned personal writing style using confirmed career evidence and the saved job posting.
---

# Write Cover Letter

1. Read AGENTS.md and docs/data-model.md, then run `uv run -q scripts/hunt.py status`. If there is no application folder with a drafted resume.md for this job, follow create-targeted-resume first; it handles every earlier prerequisite and the voice choice. Then read the application folder, canonical profile, and, on a learned packet, workspace/voice/SKILL.md plus its approved profile. On a neutral packet write plain, direct prose and follow any preferences the candidate stated.
2. Use the saved posting and requirement map. Verify recipient name from supplied/verified information; otherwise use Hiring Team. Select one or two confirmed examples that explain relevance rather than repeating every resume bullet.
3. Draft cover-letter.md using the candidate's register, sentence patterns, and explicit preferences. Default to the preferred word count. Tie experience to actual job work. Express enthusiasm, personal motivations, or company affinity only if the candidate supplied them; an evidence-based statement of fit is sufficient. No stock flattery, no invented personal connections, no brochure language about the candidate.
4. Record each factual assertion's claim IDs in application.json evidence. Company/posting facts require locators in review.md. Keep source notes out of the final letter. Do not disclose private personal details merely because they appear in samples.
5. In review.md report two concrete voice choices with supporting sample IDs, or on a neutral packet write "neutral draft by candidate choice" and the preferences applied. Read the letter aloud mentally, remove filler and repetition, and ensure it contributes something beyond the resume. Apply candidate edits as preferences; do not infer new career facts from stylistic feedback.
6. If you added any claim (for example a stated motivation on `candidate-statements`), the profile changed since the resume was pinned: recheck the packet's evidence, then run `uv run -q scripts/hunt.py refresh-snapshot JOB-ID`. Run validate and continue to review-application. Save revisions in the existing job folder; do not send or submit.
