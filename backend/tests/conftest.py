"""All automated tests are offline, independent of a developer's paid-mode settings."""
import httpx
import pytest


@pytest.fixture(autouse=True)
def offline_provider_default(monkeypatch):
    monkeypatch.setenv("MYSTERY_DIALOGUE_PROVIDER", "scripted")
    monkeypatch.setenv("MYSTERY_ALLOW_PAID_AI", "false")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("MYSTERY_OPENAI_MODEL", raising=False)

    async def deny_live_http(*_args, **_kwargs):
        raise AssertionError("Live outbound HTTP is disabled in tests; inject MockTransport.")

    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", deny_live_http)
