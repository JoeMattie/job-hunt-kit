# Job Hunt Kit
A private, agent-operated workspace for one candidate's job search. Open this repository in Codex or Claude Code and ask for the next step. No API keys, paid service, or web server required. Python 3.10+ runs the optional local CLI; document export optionally uses Pandoc.

## Start here
1. Run `python3 scripts/hunt.py init` to create an empty local workspace.
2. Ask: “Use build-writing-corpus with these selected files. Include only passages I wrote.” Supply files or explicit message/document selections; account access is not a blanket import instruction.
3. Ask: “Use learn-candidate-voice to build my personal writing style skill.” Review the style profile and calibration drafts.
4. Ask: “Use assemble-master-cv. Interview me about every role, education item, and personal project, preserving all details.”
5. Run `python3 scripts/hunt.py new-job example-company example-role --url https://example.com/job` and ask: “Use create-targeted-resume for this application folder and job description.”
6. Ask: “Use write-cover-letter for that application, using my approved personal voice.”
7. Ask: “Use review-application to check the packet.” Submit it yourself, or explicitly authorize a specific submission separately.

## How it fits together
- `.agents/skills/`: six reusable workflow skills, discovered by Codex. `AGENTS.md` routes requests. Claude Code reads `CLAUDE.md` and opens the same skills explicitly.
- `templates/`: empty JSON data contracts and Markdown output templates.
- `workspace/`: ignored personal data, source excerpts, full CV, generated voice skill, and job packets.
- `scripts/hunt.py`: initialize, register selected text samples, render the full CV, scaffold applications, validate references, and export Markdown with Pandoc.
- `docs/`: workflow, data model, privacy, and publishing guidance.

JSON is the canonical editable data; Markdown is the review format. Retain exhaustive CV details and generate short resumes as separate views. IDs connect sources → claims → resume/letter evidence. The CLI does bookkeeping and validation; the coding agent performs synthesis and writing.

## Commands
```bash
python3 scripts/hunt.py init
python3 scripts/hunt.py add-sample /absolute/path/to/authored-excerpt.txt --id sample-001 --genre email --locator 'selected email, authored body' --authorship candidate
python3 scripts/hunt.py render-cv
python3 scripts/hunt.py new-job acme coordinator --description /absolute/path/to/job.txt
python3 scripts/hunt.py validate
python3 -m unittest discover -s tests -v
python3 scripts/hunt.py export workspace/applications/acme-coordinator/resume.md --format docx
```
Use UTF-8 `.txt`/`.md` excerpts with add-sample. For PDF, DOCX, or mailbox formats, have the agent extract and review text first; OCR errors, quoted replies, signatures, and other authors must be removed or attributed. The CLI does not fetch URLs or access accounts. If a posting cannot be read, paste its description.

## Private remote
A local Git repository is not a hosted private repository. See `docs/publishing.md` for private-only publishing. Personal data is ignored even on a private remote. Back it up separately to a location you control. Skills are repository-local; this does not install them into your ChatGPT personal skill directory.
