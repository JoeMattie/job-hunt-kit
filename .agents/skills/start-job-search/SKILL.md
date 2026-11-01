---
name: start-job-search
description: First-time setup and orientation for the candidate's job search. Use when the candidate is new, asks how to get started, or when workspace/ does not exist yet.
---

# Start Job Search

1. Read AGENTS.md. The candidate is not expected to use a terminal; you run every command. Check that `uv` is on PATH. If it is not, explain in one sentence that a small local bookkeeping script needs it, show the official installer command `curl -LsSf https://astral.sh/uv/install.sh | sh`, and ask for permission before running it. Then run `uv run scripts/hunt.py init`. It is safe to repeat and never overwrites existing data.
2. Open workspace/profile.json. If the candidate name is empty, ask in one short batch for: preferred name as it should appear on applications, email and phone for applications, city or region, target roles, any location or remote constraints, and whether they have an old resume or CV they can share (any format). Accept partial answers; record anything missing in open_questions. Save to profile.json and run `uv run scripts/hunt.py validate`.
3. Explain the plan in plain words: writing samples lead to a learned voice; a career interview builds the master CV, which is the long part and usually takes several sessions; then each job gets a resume, a cover letter, and a review. State that the candidate always submits applications themselves and that nothing personal is ever uploaded to GitHub.
4. If the candidate arrived with a job posting, save it now with `uv run scripts/hunt.py new-job COMPANY ROLE --url URL` and paste the text into its job.md, then return to the posting after the prerequisites below. Otherwise ask whether to begin with writing samples or career history; the two are independent. Hand off to build-writing-corpus or assemble-master-cv accordingly. Do not start inventing an inventory from this conversation or from the repository.
5. Run `uv run scripts/hunt.py status` and show the result. Tell the candidate they can say "where do things stand" at any time for this view, and "back up my job search" to get a dated zip of their data saved outside the repository.
