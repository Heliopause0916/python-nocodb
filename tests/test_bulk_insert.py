import requests
import pytest

from nocodb.infra.requests_client import NocoDBRequestsClient
from nocodb.nocodb import NocoDBProject, APIToken


class DummyResponse:
    """Minimal Response object to mimic requests.Response."""

    def __init__(self, json_data=None, status_code: int = 200):
        self._json_data = json_data or {}
        self.status_code = status_code

    # --- requests.Response methods we rely on ---
    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(response=self)


def test_bulk_insert(monkeypatch):
    """Ensure the client hits the bulk endpoint with correct payload."""

    captured = {}

    def fake_request(self, method, url, *args, **kwargs):  # noqa: D401
        captured["method"] = method
        captured["url"] = url
        captured["json"] = kwargs.get("json")
        return DummyResponse({"success": True})

    # Patch Session.request before the client is instantiated.
    monkeypatch.setattr(requests.sessions.Session, "request", fake_request, raising=True)

    client = NocoDBRequestsClient(APIToken("dummy"), "http://localhost:8080")
    project = NocoDBProject("noco", "myproject")

    rows = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 28}]
    response = client.table_row_bulk_insert(project, "Employees", rows)

    assert response == {"success": True}
    assert captured["method"] == "POST"
    assert (
        captured["url"]
        == "http://localhost:8080/api/v1/db/data/bulk/noco/myproject/Employees"
    )
    assert captured["json"] == rows
