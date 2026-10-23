# Writing tests in `tests/`

These rules apply only when you add or change files in this folder. They don't matter for
reading or explaining the app, so they live here instead of in the root `AGENTS.md`.

- **Public API only.** Call the app through `TestClient` (`client.post("/shorten", ...)`,
  `client.get(f"/{code}", follow_redirects=False)`). Don't import or call `encode()`,
  `get_db()` or SQL directly to check results.
- **Success and failure.** Every behavior you add needs at least one test for the success
  path and one for a failure or edge case (bad input, unknown code, conflict, expired).
- **Independent tests.** A test must pass alone (`pytest tests/test_main.py::test_name`) and
  in any order. Don't rely on codes or row ids created by another test, and don't assume
  the database starts empty unless a fixture makes it so.
- **Assert behavior.** Check status codes, response bodies and the `location` header of
  redirects. Don't assert on private details like table columns or exact generated codes.
- **Name tests after the behavior**: `test_custom_alias_already_taken_returns_409`.

Example:

```python
def test_unknown_code_returns_404():
    response = client.get("/no-such-code", follow_redirects=False)

    assert response.status_code == 404
    assert response.json() == {"detail": "unknown code"}
```
