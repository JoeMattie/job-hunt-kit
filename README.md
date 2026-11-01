# Job Hunt Kit
Claude Code helps you run a job search from this folder. It learns how you write from your own writing, builds a complete CV by interviewing you, then drafts a resume and cover letter for each job you apply to. It never invents facts: everything in a draft traces back to something you said or gave it.

You never need to type commands. You talk to Claude, and Claude does the rest. Your personal data stays in a `workspace/` folder on your computer that is never uploaded.

## Setup
1. Install [Claude Code](https://claude.com/claude-code) and sign in.
2. Get this folder onto your computer: clone it, or use "Code → Download ZIP" on GitHub and unzip it.
3. Open the folder in Claude Code and say:

   **"Use start-job-search."**

   Claude sets up your workspace, asks a few questions about you, and explains what comes next. If it needs to install a small helper tool, it will ask you first.

## What to say next
Each of these starts a guided step. Do them in order the first time.

1. **"Use build-writing-corpus with these files. Include only passages I wrote."** Give it a few emails or documents you wrote yourself.
2. **"Use learn-candidate-voice to build my personal writing style."** Correct anything that sounds wrong, then approve.
3. **"Use assemble-master-cv. Interview me about every job, school, and project I've had."** This is the long step. Keep everything; short resumes come later.
4. **"Use create-targeted-resume for this job."** Paste the job posting.
5. **"Use write-cover-letter for that job."**
6. **"Use review-application to check it."** Then submit the application yourself.

Repeat steps 4 to 6 for each job.

## Keep your data safe
- Everything you paste or let Claude read is sent to Anthropic. Only share your own writing and work history. Never share other people's emails, passwords, or account numbers.
- Say **"Back up my job search"** now and then. Claude saves a dated zip to `~/Documents/job-hunt-kit-backups`.
- Say **"Where do things stand?"** to see your progress.

## More
`docs/workflows.md` explains the layout and the commands Claude runs. `docs/privacy.md` has the full data rules. `docs/data-model.md` describes the JSON files for anyone editing them by hand.
