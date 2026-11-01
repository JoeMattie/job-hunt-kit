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
python3 scripts/hunt.py init
```
Then use the private publish command above. A bundle preserves committed source and history; it does not create a hosted repository or contain ignored candidate data. Keep the resulting repository private. This workspace uses repository-scoped skills; no global installation is needed.
