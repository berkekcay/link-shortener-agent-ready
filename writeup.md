# Week 4 writeup: an agent-ready link shortener

Agent: Claude Code (Opus 5.5) in the Claude desktop app. Task: 1, custom alias.

**1. What is in `AGENTS.md`, and why is it broadly available?** What the service does, a file
map, commands, product boundaries (no auth, UI or ORM), invariants (http/https only, error
bodies, alias rules) and the understand, test, implement, verify loop. Any task needs this,
even a question about the code, and it fits in 58 lines.

**2. What did I scope, and when does it load?** The test rules in `tests/AGENTS.md`: public API
only, a success and a failure case, independent tests, behavior assertions. They load when
the agent works on a file under `tests/`. A question about how codes are generated doesn't
need them. I moved `test_main.py` into `tests/` so the rule has its own folder.

**3. What does the workflow encode?** `.claude/skills/implement-task/SKILL.md` has seven steps:
read the task and guidance, inspect `main.py` and the tests, state the behavior and files,
write a failing test, make the smallest change, run `pytest`, then summarize in a fixed block
with remaining risks.

**4. How does Claude Code find each artifact?**

| Artifact | Claude Code mechanism |
| --- | --- |
| `AGENTS.md` | Claude Code reads `CLAUDE.md`, so the root `CLAUDE.md` imports it with `@AGENTS.md` and loads it at session start |
| `tests/AGENTS.md` | `tests/CLAUDE.md` imports it; Claude Code loads a subfolder's `CLAUDE.md` only when it works on files there |
| skill | `.claude/skills/<name>/SKILL.md` (Agent Skills format); the name and description are listed at session start, the body loads on `/implement-task` or when the task matches |

My session was opened in the parent folder before the skill existed, so it wasn't listed;
the implementing agent opened `SKILL.md` and followed it step by step.

**5. What did planning and review add?** The read-only planner found three problems before
any code existed. An alias like `c` would make a later automatic code collide and turn a
plain `POST /shorten` into a 500. Aliases like `docs` or `redoc` would never redirect,
because FastAPI's own routes match first. And since `links.db` persists, a test with a fixed
alias passes once and fails on the next run. All three became tests, and the test for the
first one failed before the fix. The reviewer answered ACCEPT after running the suite
reversed and one test at a time and breaking the retry loop in memory to prove the collision
test catches it. It also caught that I had miscounted the new tests. Each stage's output is in
`docs/stages/`, in its own commit.

**6. What did I learn?** The most useful context was the facts you can't see from one file: codes are row ids, the database survives between runs, and FastAPI
routes shadow some paths. Short always-on guidance plus scoped rules kept each stage focused,
and keeping planning and review read-only made them look for problems instead of writing
code. Since tools look for different file names, one shared `AGENTS.md` plus small pointer files
avoids writing the same guidance twice.
