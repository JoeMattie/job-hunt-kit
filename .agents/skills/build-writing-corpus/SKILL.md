---
name: build-writing-corpus
description: Build an attributed corpus from candidate-selected documents, emails, and messages for personal writing style learning.
---

# Build Writing Corpus

1. Read AGENTS.md and docs/data-model.md. Initialize workspace if absent. Ask only for selections or authorship that cannot be established; never harvest an account by default.
2. Record the selection scope and provenance in workspace/corpus/selection.md. Extract selected text using appropriate document tools. Preserve original selections locally only when requested; keep normalized UTF-8 excerpts for learning.
3. Separate candidate-authored prose from recipients, quoted threads, signatures, boilerplate, templates, and AI-written text. Exclude uncertain passages until authorship is clarified. Redact secrets and third-party private details without altering linguistic features unnecessarily.
4. Use `uv run scripts/hunt.py add-sample TEXTFILE --id ID --genre GENRE --locator LOCATOR --authorship candidate` for reviewed excerpts. The explicit invocation records approval for learning. Mixed/unknown records remain unapproved. Detect duplicates by hash; note near duplicates and avoid overweighting one thread.
5. Aim for varied professional samples; a few short samples support only tentative rules. Record missing genres rather than inventing them. Keep a holdout for calibration where feasible.
6. Validate the corpus. Report approved sample IDs, genres, exclusions, and limits. Hand off to learn-candidate-voice; do not treat samples as verified career history.
