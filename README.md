# Job Hunt Kit

An AI coding agent runs your job search from this folder. It builds a complete record of your work history by interviewing you, learns how you write from your own writing, and drafts a resume and cover letter for each job you apply to. Nothing is invented: every line in a draft traces back to something you said or handed over.

You talk; the agent does the work. You never type commands. Everything personal stays in a `workspace/` folder on your computer that is never uploaded.

## Setup

1. Get this folder onto your computer. Clone it, or download it as a ZIP from GitHub and unzip it.
2. Open the folder in your AI coding agent.

That's all. The first time the agent needs a small helper tool, it asks you before installing it.

## Using it

Paste a job posting and say:

> Help me apply for this job.

The agent saves the posting, then builds what it needs before it can write truthfully, in this order:

1. **Your details.** Name, contact information, and the kinds of roles you want.
2. **Your work history.** Hand over any old resumes, transcripts, or certificates, in any format. The agent starts from those, then interviews you to confirm what is still accurate and fill in what they left out. Every question is optional. For old jobs you only half remember, it offers a checklist of typical duties to tick. It also asks about work that never made it onto a resume, such as a project you ran for a friend or family member; describe it in a couple of sentences, hand over any files, or point it at the emails and spreadsheets about it, and it writes it up for you. This is the long part and may take a few sittings.
3. **Your writing voice.** A few emails or documents you wrote yourself, so your cover letters sound like you. You review and approve a short style profile. If you would rather not dig up samples, say so and the agent writes plain drafts instead.

Then it drafts the resume and cover letter, checks them against your history and the posting, produces the files, and asks for your approval. You submit the application yourself.

After the first job, all of that is already built. Each new posting takes one conversation.

## Other things to say

| Say | What happens |
|---|---|
| Use start-job-search | Set up and start the interview without a posting |
| Use capture-project. Here is something that isn't on my resume. | Write up one project, gig, or volunteer effort |
| Use assemble-master-cv | Work on your full history |
| Use create-targeted-resume for this job | Resume only |
| Use write-cover-letter for that job | Cover letter only |
| Use review-application to check it | Final check of a packet |
| Where do things stand? | Progress and the status of every application |
| Back up my job search | A dated zip of your data, saved outside this folder |

## Keep your data safe

- Everything you paste or let the agent read is sent to the agent's provider. Share your own writing and work history only. Never share other people's emails, passwords, or account numbers.
- Back up now and then. The backup zip is the only copy of your work outside this computer.
- Full rules are in `docs/privacy.md`.

## Under the hood

`AGENTS.md` tells the agent how to work here and routes requests to the skills in `.agents/skills/`. `docs/workflows.md` explains the layout and the commands the agent runs. `docs/data-model.md` describes the JSON files.
