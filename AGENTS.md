# Agent guide: link shortener

A tiny FastAPI + SQLite service. `POST /shorten` stores a URL and returns a short code;
`GET /{code}` redirects to it (307). Codes are the base62-encoded row id.

## Where things are

| Path | What it holds |
| --- | --- |
| `main.py` | The whole app: DB setup, `encode()`, request model, both routes |
| `tests/test_main.py` | Behavioral tests through FastAPI's `TestClient` |
| `tests/AGENTS.md` | Rules for writing tests; read it before touching `tests/` |
| `docs/TASKS.md` | The three feature tasks; work on one at a time |
| `.claude/skills/implement-task/` | The step-by-step procedure for implementing a task |
| `links.db` | SQLite file created at import time; gitignored, safe to delete |

## Commands

Run from the repository root.

```bash
python -m venv .venv && .venv/Scripts/activate   # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest                                           # all tests must pass before you stop
uvicorn main:app --reload                        # http://localhost:8000/docs
```

## Product boundaries

In scope: storing a URL, returning a short code, redirecting, and the tasks in
`docs/TASKS.md` (custom alias, click counter, expiry).

Out of scope unless a person asks: user accounts or auth, a web UI, analytics beyond a
click count, a different database or an ORM, background jobs, rate limiting, splitting
`main.py` into packages. Keep it one small service.

## Invariants

- Only `http://` and `https://` URLs are accepted; anything else is HTTP 400.
- An unknown code is HTTP 404 with `{"detail": "unknown code"}`.
- Custom aliases match `[A-Za-z0-9_-]{1,32}`; `docs`, `redoc`, `shorten` are reserved (400);
  a taken alias or code is 409. Add new top-level routes to `RESERVED_ALIASES`.
- Errors use `HTTPException`, so bodies are `{"detail": "..."}`; no tracebacks.
- Every new behavior gets a success test and at least one failure test.

## Change workflow

1. **Understand**: read the task, `main.py` and the related tests. Say what should change.
2. **Test**: add a failing behavioral test first (see `tests/AGENTS.md`).
3. **Implement**: make the smallest change in `main.py` that passes it.
4. **Verify**: run `pytest`; all old and new tests must pass. Summarize what changed.

For a whole task, follow the `implement-task` skill.

## Ask a person before

Adding a dependency, changing the DB schema in a way that drops data, deleting tests,
or pushing to git.
