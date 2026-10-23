# Stage 3: review (read-only)

Agent: Claude Code (Opus 5.5), a separate subagent told it may not edit any file. It reviewed
the stage 2 commit against the task, `AGENTS.md`, `tests/AGENTS.md` and the plan, ran the
tests, and probed the API with throwaway `TestClient` snippets.

```text
Decision: ACCEPT

Requirements checked:
- Free alias becomes the code and redirects (307); taken alias returns 409 and the first
  URL survives; alias equal to a generated code returns 409.
- Generated codes skip a code an alias holds (was a 500). Safe because AUTOINCREMENT never
  reuses a deleted id, so the retry loop cannot spin forever.
- Format [A-Za-z0-9_-]{1,32} checked with fullmatch (so "a\n" is rejected), 400 with the
  planned message; reserved docs, redoc, shorten return 400; alias null keeps today's
  behavior; the URL is checked first and a bad URL does not reserve the alias.
- AGENTS.md invariants and product boundaries hold; tests/AGENTS.md rules are followed.

Validation:
- pytest: 22 passed; 22 passed after deleting links.db; 22 passed in reversed order; every
  test also passed when run alone.
- Probes: "a\n", " a" and "openapi.json" return 400; "Docs" is accepted and redirects
  (routes are case-sensitive); alias 123 returns Pydantic's 422.
- Mutation check: with the retry replaced by a re-raise, alias "c" followed by a generated
  POST gave 500 on an empty database. The real code gives 200 with code "d". The collision
  test catches the regression.

Findings (none blocking):
1. The implement notes miscounted the tests: 9 new functions and 19 cases, not 10 and 16.
2. tests/test_main.py was converted from CRLF to LF, so the diff shows the 3 original tests
   as removed and re-added (content unchanged).
3. A non-string alias returns Pydantic's 422 with a list detail; a request without url
   already did that before the change.
4. The collision test depends on encode(2) == "c" in an empty database.

Required changes: none.

Residual risks: "stats" should be reviewed for the reserved list if task 2 adds
/stats/{code}; the length limit, characters, case sensitivity and 400 for reserved names are
design choices; concurrent writers can hit SQLite's "database is locked" (not new).
```

## What I did with the findings

Finding 1 is fixed in `02-implement.md`. Findings 2 to 4 need no change: the line endings
are diff noise only, the 422 for a wrong type matches how the app already treated a missing
`url`, and the collision test is behind a fixture that starts from an empty database.
