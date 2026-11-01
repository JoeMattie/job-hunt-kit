---
name: assemble-master-cv
description: Assemble or update an exhaustive structured master CV from candidate-provided work, education, projects, interviews, and supporting evidence.
---

# Assemble Master Cv

1. Read AGENTS.md and docs/data-model.md. Use workspace/profile.json as canonical source; do not overwrite it with a shorter resume. Read existing records before editing.
2. Inventory every role, education item (including incomplete programs), personal project, volunteering role, certificate, award, and publication. Ask one focused batch at a time about dates, exact titles, responsibilities, tools, context, decisions, collaborators, outcomes, and links. Include career breaks only as the candidate wishes; do not infer reasons.
3. Create stable source, entry, and claim IDs. Preserve exhaustive narrative and arbitrary structured details. Record team vs individual attribution and exact vs approximate metrics with basis. Confirm candidate assertions through interview responses or selected evidence. Use proposed/disputed for unresolved statements and retain conflict notes.
4. Keep dates at known precision. Never upgrade attendance to a completed degree, familiarity to expertise, or a personal project to employment. Preserve superseded claims as retired rather than erasing their provenance.
5. Show a review of new facts and uncertainties; confirmation may be established by the candidate explicitly providing the fact. Ask only questions needed for truth or attribution. Keep open questions and continue independent inventory.
6. Run `python3 scripts/hunt.py validate` and `python3 scripts/hunt.py render-cv`. If validate reports that an active application's profile changed, recheck that packet's evidence against the new facts before running `refresh-snapshot` on it. Review workspace/master-cv.md against the JSON, including details and evidence. This is an exhaustive inventory with status labels, not a submission-ready resume.
