---
name: learn-candidate-voice
description: Learn and generate a candidate-specific personal writing style skill from approved attributed samples, and update it from candidate feedback.
---

# Learn Candidate Voice

1. Read AGENTS.md and docs/data-model.md, then run `uv run -q scripts/hunt.py status`. If there are no approved writing samples, follow build-writing-corpus first and return here. Read workspace/corpus.json and the approved candidate-authored excerpts. Do not learn from the repository creator's prose, imported job postings, or fabricated samples.
2. Identify observable patterns: directness, sentence length, contractions, vocabulary, paragraphing, openings/closings, humor, punctuation, evidence use, and genre differences. Link each rule to sample IDs and confidence. Separate explicit preferences from inferred tendencies. Avoid personality or demographic inference.
3. Write workspace/voice/profile.json with status draft. Reserve an approved sample as holdout where feasible and check that your rules explain it. If evidence is sparse, state limitations and ask for another professional sample when necessary.
4. Show the candidate a compact style profile and two short calibration drafts based only on confirmed career facts (or clearly hypothetical non-career content). Ask for corrections and approval. Do not mark approved based on silence or a previous corpus selection.
5. Apply feedback and record approval in calibration. Generate workspace/voice/SKILL.md with name candidate-writing-style, description triggering for this candidate's resumes, cover letters, and professional writing, and concise instructions to read profile.json relative to that file. Include register-specific rules, approved sample references, and explicit no-invented-facts guidance. Keep identifying material within ignored workspace.
6. Resume and letter workflows must read this generated skill and its profile. After corpus changes, assess whether approval remains valid; substantial rule changes return to draft. Run validator. Preserve approval history in workspace/voice/feedback.md.
