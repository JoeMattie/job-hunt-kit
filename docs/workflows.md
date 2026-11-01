# Operating playbook
## First session
Initialize; ask the candidate for preferred name, contact details for applications, desired roles, geography, and existing CV. Accept incomplete inputs and keep missing facts in open_questions. Collect career inventory and writing samples independently so one does not block the other.

## Build once, improve continuously
Select writings → retain authored excerpts and provenance → learn a draft voice → calibrate → generate the candidate voice skill. Inventory work, education, projects, volunteering, awards, certificates, and publications → interview for missing context → confirm claims → render the exhaustive CV. Keep older detail even when it is not currently useful. Resolve discrepancies by recording both accounts and asking a targeted question; never silently choose the more impressive claim.

## Per job
Capture posting text, URL, company, role, date, and application instructions. Decompose requirements, map confirmed claims, identify real gaps, choose examples, draft resume, draft letter with voice skill, audit, export, and visually inspect. Save original posting even if its link later expires. Revisions stay in the same job folder, with candidate feedback in review.md. A filename is not evidence of approval. Job statuses can be draft, reviewed, ready, submitted, interviewing, closed; update submitted only when the user reports or explicitly performs submission. `uv run scripts/hunt.py status` lists every packet. When the profile changes after a packet was drafted, validate flags the active packet; recheck its evidence, then `refresh-snapshot` it.

## Useful prompts
- “Here are three selected professional emails and a project writeup. Build my corpus, excluding quoted messages.”
- “Interview me one role at a time to assemble an exhaustive CV. Ask about transferable skills and unpaid projects too.”
- “Make a two-page resume for this posting. List requirements I cannot currently evidence.”
- “Write a 250-word cover letter using my approved voice; avoid claiming interest I haven't expressed.”
- “I rewrote the opening. Use my edit as feedback, not permission to add unrelated facts.”

## Export
Draft Markdown first. Optional `export` uses an existing Pandoc installation; it does not download dependencies. PDF output also requires a configured Pandoc PDF engine. When Pandoc is absent, which is the default on a fresh Mac, the agent produces the DOCX or PDF with its own document tools from the final Markdown and saves it beside it in the job folder. Inspect final pages with the relevant document/PDF tools; check page breaks, margins, bullet wrapping, links, and extracted reading order. If export tools are unavailable, deliver Markdown and say what remains. No layout approval is implied by successful export.

## Repository layout
- `.agents/skills/`: the six workflow skills. `.claude/skills/` links to the same files so Claude Code lists them as slash commands and triggers them by description. `AGENTS.md` routes requests; `CLAUDE.md` points Claude at it.
- `templates/`: empty JSON data contracts and Markdown output templates.
- `workspace/`: ignored personal data, source excerpts, full CV, generated voice skill, and job packets. Create it on each machine with `init`; never copy another person's.
- `scripts/hunt.py`: bookkeeping only. It initializes, registers writing samples, renders the full CV, scaffolds applications, validates references, backs up, and exports with Pandoc. The agent does all synthesis and writing.

JSON is the canonical editable data; Markdown is the review format. The master CV keeps every detail and short resumes are generated as separate views. IDs connect sources to claims to resume and letter evidence, so every sentence in a draft can be traced back to its evidence.

## Commands
```bash
uv run scripts/hunt.py init
uv run scripts/hunt.py status
uv run scripts/hunt.py add-sample path/to/authored-excerpt.txt --id sample-001 --genre email --locator 'selected email, authored body' --authorship candidate
uv run scripts/hunt.py render-cv
uv run scripts/hunt.py new-job acme coordinator --url https://example.com/job --description path/to/job.txt
uv run scripts/hunt.py validate
uv run scripts/hunt.py refresh-snapshot acme-coordinator
uv run scripts/hunt.py backup --dest /path/to/private/folder
uv run scripts/hunt.py export workspace/applications/acme-coordinator/resume.md --format docx
uv run python -m unittest discover -s tests -v
```
- `add-sample` takes UTF-8 `.txt` or `.md` excerpts. For PDF, DOCX, or mailbox formats, have the agent extract and review the text first; OCR errors, quoted replies, signatures, and other authors must be removed or attributed.
- `validate` flags draft, reviewed, and ready applications whose profile changed since the draft was pinned. After the agent rechecks that packet's evidence, `refresh-snapshot` re-pins it. Submitted, interviewing, and closed applications are not checked.
- `export` needs Pandoc. If it is not installed, the agent produces the DOCX or PDF with its own document tools instead.
- The CLI never fetches URLs or accesses accounts. If a posting cannot be read, paste its description.
