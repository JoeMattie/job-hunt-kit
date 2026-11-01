# Publish only to a private repository
This project intentionally contains no candidate data. On a machine with GitHub CLI authenticated:
```bash
gh repo create job-hunt-kit --private --source=. --remote=origin --push
gh repo view --json visibility,url
```
Check visibility is PRIVATE. If the name already exists, inspect it first; choose a new name rather than overwriting another repository. Do not change an existing remote's visibility or collaborators as part of setup.

For a Git bundle delivery:
```bash
git clone --origin bundle /path/to/job-hunt-kit.bundle job-hunt-kit
cd job-hunt-kit
git remote remove bundle
uv run scripts/hunt.py init
```
Then use the private publish command above. To give the candidate access to the private repository, add their GitHub account as a collaborator (`gh repo edit --add-collaborator USERNAME` or the repository settings page) and have them `git clone` it. Alternatively copy the folder to their machine directly; the ignored `workspace/` folder is theirs and must be created with `init` on their machine, not copied from someone else's.

A bundle preserves committed source and history; it does not create a hosted repository or contain ignored candidate data. Keep the resulting repository private. This workspace uses repository-scoped skills; no global installation is needed.
