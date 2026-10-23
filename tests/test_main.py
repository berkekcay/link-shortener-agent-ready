import uuid

import pytest
from fastapi.testclient import TestClient

import main
from main import app

client = TestClient(app)

ALIAS_FORMAT_ERROR = {"detail": "alias must be 1-32 characters: letters, digits, '-' or '_'"}


def new_alias() -> str:
    """A fresh alias per test, because links.db persists between runs."""
    return "t-" + uuid.uuid4().hex[:12]


@pytest.fixture
def fresh_db(tmp_path, monkeypatch):
    """Point the app at an empty database for tests that depend on which ids exist."""
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "links.db")
    main.init_db()


def test_shorten_and_redirect():
    r = client.post("/shorten", json={"url": "https://example.com"})
    assert r.status_code == 200
    code = r.json()["code"]
    assert code
    r2 = client.get(f"/{code}", follow_redirects=False)
    assert r2.status_code == 307
    assert r2.headers["location"] == "https://example.com"


def test_rejects_bad_url():
    r = client.post("/shorten", json={"url": "ftp://nope"})
    assert r.status_code == 400


def test_unknown_code_404():
    r = client.get("/does-not-exist", follow_redirects=False)
    assert r.status_code == 404


def test_custom_alias_is_used_as_code_and_redirects():
    alias = new_alias()

    r = client.post("/shorten", json={"url": "https://example.com/aliased", "alias": alias})

    assert r.status_code == 200
    assert r.json() == {"code": alias, "short_url": f"/{alias}"}
    r2 = client.get(f"/{alias}", follow_redirects=False)
    assert r2.status_code == 307
    assert r2.headers["location"] == "https://example.com/aliased"


def test_custom_alias_already_taken_returns_409():
    alias = new_alias()
    first = client.post("/shorten", json={"url": "https://example.com/first", "alias": alias})
    assert first.status_code == 200

    r = client.post("/shorten", json={"url": "https://example.com/second", "alias": alias})

    assert r.status_code == 409
    assert r.json() == {"detail": "alias already taken"}
    r2 = client.get(f"/{alias}", follow_redirects=False)
    assert r2.headers["location"] == "https://example.com/first"


def test_custom_alias_equal_to_generated_code_returns_409():
    generated = client.post("/shorten", json={"url": "https://example.com/generated"})
    code = generated.json()["code"]

    r = client.post("/shorten", json={"url": "https://example.com/other", "alias": code})

    assert r.status_code == 409
    assert r.json() == {"detail": "alias already taken"}
    r2 = client.get(f"/{code}", follow_redirects=False)
    assert r2.headers["location"] == "https://example.com/generated"


def test_generated_code_skips_code_taken_by_alias(fresh_db):
    # In an empty database the alias row gets id 1, so the next generated code would be
    # encode(2) == "c". Taking "c" as an alias forces that collision.
    taken = client.post("/shorten", json={"url": "https://example.com/alias-c", "alias": "c"})
    assert taken.status_code == 200

    r = client.post("/shorten", json={"url": "https://example.com/generated"})

    assert r.status_code == 200
    code = r.json()["code"]
    assert code != "c"
    assert client.get(f"/{code}", follow_redirects=False).headers["location"] == (
        "https://example.com/generated"
    )
    assert client.get("/c", follow_redirects=False).headers["location"] == (
        "https://example.com/alias-c"
    )


@pytest.mark.parametrize(
    "alias",
    ["", "a" * 33, "has space", "a/b", "what?", "frag#", "100%", "dot.ted", "ümlaut"],
)
def test_custom_alias_with_invalid_format_returns_400(alias):
    r = client.post("/shorten", json={"url": "https://example.com", "alias": alias})

    assert r.status_code == 400
    assert r.json() == ALIAS_FORMAT_ERROR


def test_custom_alias_at_max_length_is_accepted():
    alias = new_alias().ljust(32, "x")

    r = client.post("/shorten", json={"url": "https://example.com", "alias": alias})

    assert r.status_code == 200
    assert r.json()["code"] == alias


@pytest.mark.parametrize("alias", ["docs", "redoc", "shorten"])
def test_custom_alias_reserved_name_returns_400(alias):
    r = client.post("/shorten", json={"url": "https://example.com", "alias": alias})

    assert r.status_code == 400
    assert r.json() == {"detail": "alias is reserved"}


def test_custom_alias_null_generates_code():
    r = client.post("/shorten", json={"url": "https://example.com/null-alias", "alias": None})

    assert r.status_code == 200
    code = r.json()["code"]
    assert code
    r2 = client.get(f"/{code}", follow_redirects=False)
    assert r2.headers["location"] == "https://example.com/null-alias"


def test_custom_alias_with_bad_url_returns_400_and_does_not_reserve_alias():
    alias = new_alias()

    bad = client.post("/shorten", json={"url": "ftp://nope", "alias": alias})

    assert bad.status_code == 400
    assert bad.json() == {"detail": "url must start with http:// or https://"}
    assert client.get(f"/{alias}", follow_redirects=False).status_code == 404
    good = client.post("/shorten", json={"url": "https://example.com", "alias": alias})
    assert good.status_code == 200
    assert good.json()["code"] == alias
