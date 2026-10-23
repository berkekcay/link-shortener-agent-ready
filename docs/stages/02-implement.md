# Stage 2: implement (implement-task skill)

Agent: Claude Code (Opus 5.5), a fresh general-purpose subagent told to use the
`implement-task` skill and the approved plan in `01-plan.md`. The session had been opened in
the parent folder, so the Skill tool did not list the repo's skills; the agent opened
`.claude/skills/implement-task/SKILL.md` and followed its seven steps in order.

## Step 4: failing tests first

`pytest tests/test_main.py -k alias`, before touching `main.py`:

```text
18 failed, 1 passed, 3 deselected
```

Every failure was an assertion caused by the app ignoring `alias` (200 where 400 or 409 was
expected, or a generated code instead of the alias); none came from a typo or import error.
The one pass is `alias: null`, which protects existing behavior.

## Step 5: the change in `main.py`

- `alias: str | None = None` on the request model; checked by hand against
  `[A-Za-z0-9_-]{1,32}` and the reserved names `docs`, `redoc`, `shorten`, so errors stay
  `{"detail": "..."}` with HTTP 400. The URL is still checked first.
- With an alias, a plain `INSERT`; the `UNIQUE` constraint raises `IntegrityError` on a
  conflict, which becomes 409 `alias already taken`.
- Without an alias, the generated code is retried when an alias already holds it (the row is
  deleted and the next id is used). Before this, that case crashed with a 500.
- No schema change, so an existing `links.db` keeps working.

## Step 6: full run

```text
collected 22 items
tests\test_main.py ......................                                [100%]
22 passed
```

The same result on a second run against the saved `links.db`, and with `links.db` deleted.

## Step 7: summary from the agent

```text
Task: 1. Custom alias
Files changed: main.py, tests/test_main.py
Tests added: 9 test functions, 19 cases (the 3 original tests are unchanged)
pytest result: 22 passed
Remaining risks:
  - "stats" is not reserved; add it if task 2 adds GET /stats/{code}.
  - The 32-character limit, allowed characters and 400 for reserved names are choices the
    task does not specify.
  - A non-string alias such as 123 gets Pydantic's 422 response, not a {"detail": "..."} 400.
  - The collision test relies on how ids map to codes in an empty database.
```
