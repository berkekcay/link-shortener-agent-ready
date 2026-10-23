---
name: implement-task
description: Use when implementing a feature from docs/TASKS.md (custom alias, click counter, expiry) or any other change to the link shortener's behavior. Walks through tests first, the smallest change, pytest, and a summary.
---

# Implement a link-shortener task

Follow these steps in order. Stop and ask if the task is unclear or needs something listed
under "Ask a person before" in `AGENTS.md`.

1. **Read.** Open `AGENTS.md`, the chosen task in `docs/TASKS.md`, and `tests/AGENTS.md`.
   Work on that one task only.
2. **Inspect.** Read `main.py` (the table, `encode()`, the request model and both routes)
   and `tests/test_main.py`. Note anything the task interacts with, for example how codes
   are generated or how the database is shared between runs.
3. **State the plan.** Before editing, write down:
   - the expected behavior, including status codes and response bodies for success and
     each failure;
   - the files you will change;
   - edge cases (empty or odd input, collisions with existing codes, values that repeat).
4. **Write a failing test.** Add behavioral tests in `tests/test_main.py` following
   `tests/AGENTS.md`: at least one success and one failure case. Run them and confirm they
   fail for the right reason (the feature is missing, not a typo):

   ```bash
   pytest tests/test_main.py -k <new_test_name>
   ```

5. **Implement the smallest change** in `main.py` that makes the tests pass. Keep existing
   behavior and response shapes. If the table needs a new column, add it so an existing
   `links.db` still works (or explain why it must be recreated).
6. **Run everything.**

   ```bash
   pytest
   ```

   All original and new tests must pass. Fix and re-run until they do.
7. **Summarize** in this shape:

   ```text
   Task:
   Behavior:
   Files changed:
   Tests added:
   pytest result:
   Remaining risks:
   ```
