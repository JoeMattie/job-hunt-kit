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

Claude saves the posting, then builds whatever it still needs before it can write truthfully, in this order:

- **Your details.** Name, contact information, and the kinds of roles you want.
- **Your work history.** Give Claude any old resumes, transcripts, or certificates you have, in any format, and it starts from those. It will also ask about work that never made it onto a resume, like a project you ran for a friend or family member. Describe it in a couple of sentences, hand over any files, or point Claude at the emails and spreadsheets about it, and it writes it up for you. Then it interviews you to confirm what is still accurate and fill in what the resumes left out. Every question is optional. For old jobs you only half remember, Claude looks up what that role involves at that company, or suggests typical duties itself, and gives you a checklist to tick. This is the long part and may take a few sittings. Keep everything; short resumes come later.
- **Your writing samples.** A few emails or documents you wrote yourself, so your cover letters sound like you. Claude shows you a style profile to approve. If you would rather not dig up samples, say so and Claude writes plain drafts instead.

Then it drafts the resume and cover letter, reviews them against your history and the posting, and hands them to you. You submit the application yourself.

After the first job, all of that is already built, and each new posting takes one conversation.

Don't have a posting yet? Say **"Use start-job-search"** and Claude will set things up and start the interview.

## Going one step at a time
Each of these runs a single stage on its own:

- "Use assemble-master-cv. Interview me about every job, school, and project I've had."
- "Use capture-project. Here is something that isn't on my resume."
- "Use build-writing-corpus with these files. Include only passages I wrote."
- "Use learn-candidate-voice to build my personal writing style."
- "Use create-targeted-resume for this job."
- "Use write-cover-letter for that job."
- "Use review-application to check it."

## Keep your data safe
- Everything you paste or let Claude read is sent to Anthropic. Only share your own writing and work history. Never share other people's emails, passwords, or account numbers.
- Say **"Back up my job search"** now and then. Claude saves a dated zip to `~/Documents/job-hunt-kit-backups`.
- Say **"Where do things stand?"** to see your progress.

## More
`docs/workflows.md` explains the layout and the commands Claude runs. `docs/privacy.md` has the full data rules. `docs/data-model.md` describes the JSON files for anyone editing them by hand.
