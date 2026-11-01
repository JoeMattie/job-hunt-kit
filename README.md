# Job Hunt Kit
A private workspace where an AI coding agent (Claude Code, or Codex) helps one person run a job search: learn their writing voice from their own writing, build an exhaustive master CV through interviews, then draft an evidence-backed resume and cover letter for each posting. Nothing is invented: every fact in a draft traces back to something you said or supplied. Everything personal stays on your computer in an ignored `workspace/` folder.

## For the candidate: start here
You do not need to know how to code. You will type a few commands in a terminal and otherwise just talk to Claude.

**One-time setup (whoever set this up can do this with you)**
1. Install Python 3.10 or newer. On a Mac, open Terminal and run `python3 --version`; if it offers to install developer tools, accept.
2. Install Claude Code and sign in (https://claude.com/claude-code).
3. Get this folder onto your computer. Either clone the private GitHub repository (the owner adds your GitHub account as a collaborator) or have the owner copy the folder over. See `docs/publishing.md`.
4. Open the folder in Claude Code and run, in its terminal:
   ```bash
   python3 scripts/hunt.py init
   ```
   This creates your private `workspace/` folder. It is never uploaded to GitHub.

**Doing the work, in order**
Each line is something you say to Claude in this folder. It reads the matching skill and walks you through it.
1. "Use build-writing-corpus with these files. Include only passages I wrote." Give it a few emails, documents, or messages you wrote yourself. It keeps only your own words and asks when authorship is unclear.
2. "Use learn-candidate-voice to build my personal writing style." It shows you a style profile and two short sample drafts. Correct anything that sounds wrong, then approve.
3. "Use assemble-master-cv. Interview me about every role, education item, and project, preserving all details." This is the long step, often several sessions. Keep everything, even old or minor items; short resumes are generated later.
4. For each job: run `python3 scripts/hunt.py new-job "Company" "Role" --url https://...`, then say "Use create-targeted-resume for this application folder and this job description" and paste the posting text.
5. "Use write-cover-letter for that application, using my approved voice."
6. "Use review-application to check the packet." Read the review, make edits, and submit the application yourself. The kit never submits anything.

**Keeping your data safe**
- Anything you paste or let Claude read is sent to the AI provider (Anthropic for Claude Code). Only give it your own writing. Do not import other people's emails, shared inboxes, or anything containing passwords or account numbers.
- Your whole job search lives in `workspace/`. Back it up regularly:
  ```bash
  python3 scripts/hunt.py backup
  ```
  This writes a dated zip to `~/Documents/job-hunt-kit-backups` (or `--dest` a folder you choose). Keep it private.
- See `docs/privacy.md` for the full rules.

**Checking where things stand**
```bash
python3 scripts/hunt.py status
```
Lists your CV progress, writing samples, voice approval, and every application with its status.

## How it fits together
- `.agents/skills/`: six workflow skills. `.claude/skills/` links to the same files so Claude Code lists them as slash commands and triggers them by description. `AGENTS.md` routes requests; `CLAUDE.md` points Claude at it.
- `templates/`: empty JSON data contracts and Markdown output templates.
- `workspace/`: ignored personal data, source excerpts, full CV, generated voice skill, and job packets.
- `scripts/hunt.py`: bookkeeping only. It initializes, registers writing samples, renders the full CV, scaffolds applications, validates references, backs up, and exports with Pandoc. The agent does all synthesis and writing.
- `docs/`: workflow, data model, privacy, and publishing guidance.

JSON is the canonical editable data; Markdown is the review format. The master CV keeps every detail and short resumes are generated as separate views. IDs connect sources to claims to resume and letter evidence, so every sentence in a draft can be traced back to its evidence.

## Commands
```bash
python3 scripts/hunt.py init
python3 scripts/hunt.py status
python3 scripts/hunt.py add-sample path/to/authored-excerpt.txt --id sample-001 --genre email --locator 'selected email, authored body' --authorship candidate
python3 scripts/hunt.py render-cv
python3 scripts/hunt.py new-job acme coordinator --description path/to/job.txt
python3 scripts/hunt.py validate
python3 scripts/hunt.py refresh-snapshot acme-coordinator
python3 scripts/hunt.py backup
python3 scripts/hunt.py export workspace/applications/acme-coordinator/resume.md --format docx
python3 -m unittest discover -s tests -v
```
Notes:
- `add-sample` takes UTF-8 `.txt` or `.md` excerpts. For PDF, DOCX, or mailbox formats, have the agent extract and review the text first; OCR errors, quoted replies, signatures, and other authors must be removed or attributed.
- `validate` flags draft, reviewed, and ready applications whose profile changed since the draft was pinned. After the agent rechecks that packet's evidence, `refresh-snapshot` re-pins it. Submitted, interviewing, and closed applications are not checked.
- `export` needs Pandoc. If it is not installed, ask the agent to produce the DOCX or PDF with its own document tools instead; that is the normal path on a fresh Mac.
- The CLI never fetches URLs or accesses accounts. If a posting cannot be read, paste its description.

## Private remote
A local Git repository is not a hosted private repository. See `docs/publishing.md` for private-only publishing and for giving the candidate access. Personal data is ignored even on a private remote, so the `backup` command is the only copy of your work outside this computer.
