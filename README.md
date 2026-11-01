# Job Hunt Kit
Claude Code helps you run a job search from this folder. It learns how you write from your own writing, builds a complete CV by interviewing you, then drafts a resume and cover letter for each job you apply to. It never invents facts: everything in a draft traces back to something you said or gave it.

Your personal data lives in a `workspace/` folder inside this repository. That folder is never committed to Git, so it stays on your computer.

## Setup
1. Install uv. Open Terminal and run:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   Then close and reopen Terminal.
2. Install [Claude Code](https://claude.com/claude-code) and sign in.
3. Clone this repository and open the folder in Claude Code.
4. In Claude Code's terminal, run:
   ```bash
   uv run scripts/hunt.py init
   ```

## How to use it
Say these to Claude, in this order. Each one starts a guided step.

1. **"Use build-writing-corpus with these files. Include only passages I wrote."** Give it a few emails or documents you wrote yourself.
2. **"Use learn-candidate-voice to build my personal writing style."** Correct anything that sounds wrong, then approve.
3. **"Use assemble-master-cv. Interview me about every job, school, and project I've had."** This is the long step. Keep everything; short resumes come later.
4. **"Use create-targeted-resume for this job."** Paste the job posting.
5. **"Use write-cover-letter for that job."**
6. **"Use review-application to check it."** Then submit the application yourself.

Repeat steps 4 to 6 for each job.

## Keep your data safe
- Everything you paste or let Claude read is sent to Anthropic. Only share your own writing and work history. Never share other people's emails, passwords, or account numbers.
- Back up your work now and then:
  ```bash
  uv run scripts/hunt.py backup
  ```
  This saves a zip to `~/Documents/job-hunt-kit-backups`.
- To see where things stand:
  ```bash
  uv run scripts/hunt.py status
  ```

## More
`docs/workflows.md` explains the layout and every command. `docs/privacy.md` has the full data rules. `docs/data-model.md` describes the JSON files for anyone editing them by hand.
