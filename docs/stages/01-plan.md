# Stage 1: plan (read-only)

Agent: Claude Code (Opus 5.5), read-only "Plan" subagent. No files were edited.

Prompt:

> I want to implement task 1 ("Custom alias") from docs/TASKS.md. Inspect the repository and
> the task and propose an implementation plan. Do NOT edit any files; this is the planning
> stage only. Start from the repository guidance (CLAUDE.md / AGENTS.md, tests/AGENTS.md and
> the implement-task skill under .claude/skills) the way an agent new to this repo would.

## What the planner found in the current code

1. **Aliases can break automatic codes.** Automatic codes come from the row id and are
   written by an `UPDATE` after the insert. If someone takes alias `"c"` and a later row id
   encodes to `"c"`, that `UPDATE` hits the `UNIQUE` constraint and a plain `POST /shorten`
   returns 500. The automatic path has to handle collisions; an alias check alone is not
   enough.
2. **Some aliases would never redirect.** FastAPI registers `/docs`, `/redoc` and
   `/openapi.json` before `/{code}`, so `GET /docs` serves the docs page. Aliases with `/`
   can't be reached, and spaces, `?`, `#` and `%` make ambiguous URLs.
3. **The database persists between runs.** A test with a fixed alias like `"my-alias"`
   passes once and gets 409 on the next run, which breaks the "independent tests" rule.

## Proposed behavior

| Request | Status | Body |
| --- | --- | --- |
| no alias, or `"alias": null` | 200 | generated code, same as today |
| free alias | 200 | `{"code": alias, "short_url": "/" + alias}`, then `GET` redirects (307) |
| alias already used (alias or generated code) | 409 | `{"detail": "alias already taken"}` |
| empty, too long, or characters outside `[A-Za-z0-9_-]` | 400 | `{"detail": "alias must be 1-32 characters: letters, digits, '-' or '_'"}` |
| reserved (`docs`, `redoc`, `shorten`) | 400 | `{"detail": "alias is reserved"}` |
| bad URL, with or without alias | 400 | existing URL error; the URL is checked first |

Validate by hand and raise `HTTPException` (400) instead of a Pydantic 422, so error bodies
stay `{"detail": "..."}`. Case-sensitive, no trimming. Let the `UNIQUE` constraint detect
conflicts (catch `IntegrityError`) to avoid a check-then-insert race. On the automatic path,
retry with a new row when the generated code is already taken. No schema change.

## Tests to add

Fresh `uuid` aliases per test; one `fresh_db` fixture (temporary `DB_PATH`) only for the
collision test. Success, already-taken, alias equal to a generated code, generated code
skipping an alias that took it (fails today with 500), invalid aliases (parametrized),
reserved aliases, `alias: null`, and a bad URL with an alias not reserving the alias.

## Risks noted

`stats` should be reserved if task 2 is added later. The 32-character limit, the allowed
characters and 400 vs 409 for reserved names are choices the task doesn't specify.
