# Data contracts (schema_version 1)
Keep stable, unique IDs. Use JSON `null` for unknown dates rather than guessing. Dates may be `YYYY`, `YYYY-MM`, or `YYYY-MM-DD`; record precision. All paths stored in source records are relative to workspace; opaque connector locators are allowed as source locators. Do not store access tokens or signed URLs.

## profile.json
`candidate`: name, email, phone, location, links. `preferences`: target_roles, location_constraints, resume_pages, cover_letter_words.
`sources[]`: `{id, kind, locator, captured_at, notes}`. Kinds include interview, document, email, message, portfolio. Sources are career evidence, distinct from corpus samples.
`entries[]`: `{id, kind, organization, title, start, end, location, narrative, claim_ids, details}`. Kind is work, education, project, volunteering, certification, award, publication, or other. `details` is an unrestricted object for exhaustive context: course work, degree status, team size, tools, methods, problems, individual vs team contribution, outcomes, lessons, links, and transitions. `narrative` retains the long-form story. Never truncate the master to fit a resume. An end of null means unknown; use the string `present` for a current role.
`claims[]`: `{id, entry_id, text, status, source_refs, tags, metrics}`. Status is proposed, confirmed, disputed, or retired. `source_refs[]` uses `{source_id, locator}` where locator identifies page/paragraph, message/date, or interview answer. Confirmation requires evidence and candidate verification; an interview answer can be the evidence. `metrics[]` records `{value, unit, basis, attribution, exact}`. Do not convert a team result to personal credit or estimates to exact numbers.
`open_questions[]`: strings or objects with question, related IDs, and resolution.

## corpus.json
`samples[]`: `{id, path, sha256, genre, locator, authorship, approved, notes}`. Authorship is candidate, mixed, or unknown. Include only the candidate-authored selected passages in the file. `approved` means suitable for style learning, not approval of career claims. Deduplicate before learning. Preserve a holdout sample for calibration where possible.

## voice/profile.json
`status`: unlearned, draft, or approved. `sample_ids` references approved candidate-authored corpus samples. `registers` differentiates professional correspondence, casual writing, and compressed resume bullets. `rules[]`: `{trait, instruction, sample_ids, confidence}`. Include observable examples and context; no psychological inference. `avoid[]` contains candidate preferences. `calibration` records explicit approval and feedback. The generated `workspace/voice/SKILL.md` references this JSON and the authorized sample IDs.

## application.json
Store inside a per-job directory with `job.md`, `resume.md`, `cover-letter.md`, and `review.md`. `requirements[]`: `{id, text, priority, source_locator, claim_ids, gap}`. Priority is required or preferred. Empty claim_ids must carry an honest gap. `evidence[]`: `{artifact, locator, claim_ids}` ties each factual resume bullet / letter assertion to confirmed claims. `artifact` is resume.md or cover-letter.md; locator is a stable paragraph/bullet label in review notes, not a visible citation in the submitted document. Candidate contact data comes directly from profile. `profile_snapshot_sha256` pins the profile used for the draft; validator detects later changes. Revalidate and refresh the hash intentionally after rechecking.

The CLI validates IDs, required linkage, voice approval dependencies, and snapshot freshness. It cannot prove that prose is truthful or that citations actually support it; review the original evidence.
