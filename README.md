# Job Hunt Kit
Claude Code helps you run a job search from this folder. It learns how you write from your own writing, builds a complete CV by interviewing you, then drafts a resume and cover letter for each job you apply to. It never invents facts: everything in a draft traces back to something you said or gave it.

You never need to type commands. You talk to Claude, and Claude does the rest. Your personal data stays in a `workspace/` folder on your computer that is never uploaded.

## Setup
1. Install [Claude Code](https://claude.com/claude-code) and sign in.
2. Get this folder onto your computer: clone it, or use "Code → Download ZIP" on GitHub and unzip it.
3. Open the folder in Claude Code.

That's it. The first time Claude needs a small helper tool, it will ask you before installing it.

## Using it
Paste a job posting and say:

**"Help me apply for this job."**

Claude saves the posting, then builds whatever it still needs before it can write truthfully:

- **Your details.** Name, contact information, and the kinds of roles you want.
- **Your writing samples.** A few emails or documents you wrote yourself, so your cover letters sound like you. Claude shows you a style profile to approve.
- **Your work history.** Claude interviews you about every job, school, and project. This is the long part and usually takes a few sittings. Keep everything; short resumes come later.

Then it drafts the resume and cover letter, reviews them against your history and the posting, and hands them to you. You submit the application yourself.

After the first job, all of that is already built, and each new posting takes one conversation.

Don't have a posting yet? Say **"Use start-job-search"** and Claude will set things up and start the interview.

## Going one step at a time
Each of these runs a single stage on its own:

- "Use build-writing-corpus with these files. Include only passages I wrote."
- "Use learn-candidate-voice to build my personal writing style."
- "Use assemble-master-cv. Interview me about every job, school, and project I've had."
- "Use create-targeted-resume for this job."
- "Use write-cover-letter for that job."
- "Use review-application to check it."

## Keep your data safe
- Everything you paste or let Claude read is sent to Anthropic. Only share your own writing and work history. Never share other people's emails, passwords, or account numbers.
- Say **"Back up my job search"** now and then. Claude saves a dated zip to `~/Documents/job-hunt-kit-backups`.
- Say **"Where do things stand?"** to see your progress.

## More
`docs/workflows.md` explains the layout and the commands Claude runs. `docs/privacy.md` has the full data rules. `docs/data-model.md` describes the JSON files for anyone editing them by hand.
