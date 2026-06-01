"""Tests for credential resolution and the daily-quota counter (no network)."""

from __future__ import annotations

import json

from plib_cli.config import Credentials, QuotaCounter, load_credentials


def test_quota_counts_and_resets(tmp_path) -> None:
    counter = QuotaCounter(path=tmp_path / "quota.json", limit=3)
    assert counter.used() == 0
    assert counter.remaining() == 3
    counter.increment()
    counter.increment()
    assert counter.used() == 2
    assert counter.remaining() == 1


def test_quota_resets_on_date_rollover(tmp_path) -> None:
    path = tmp_path / "quota.json"
    path.write_text(json.dumps({"date": "2000-01-01", "count": 9}), encoding="utf-8")
    counter = QuotaCounter(path=path, limit=10)
    assert counter.used() == 0  # stale date → reset
    assert counter.remaining() == 10


def test_credentials_from_env(monkeypatch) -> None:
    monkeypatch.setenv("PLIB_EMAIL", "a@b.com")
    monkeypatch.setenv("PLIB_PASSWORD", "secret")
    creds = load_credentials()
    assert creds == Credentials("a@b.com", "secret")


def test_credentials_from_secrets_dir(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("PLIB_EMAIL", raising=False)
    monkeypatch.delenv("PLIB_PASSWORD", raising=False)
    secrets = tmp_path / "secrets"
    secrets.mkdir()
    (secrets / "email").write_text("u@pku.edu.cn\n", encoding="utf-8")
    (secrets / "password").write_text("pw\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    # Avoid picking up a real ~/.config credentials file in CI/dev.
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    creds = load_credentials()
    assert creds == Credentials("u@pku.edu.cn", "pw")
