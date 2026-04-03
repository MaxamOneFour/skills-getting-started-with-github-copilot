from fastapi.testclient import TestClient
from copy import deepcopy
import pytest

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities before each test."""
    original = deepcopy(app_module.activities)
    try:
        yield
    finally:
        app_module.activities.clear()
        app_module.activities.update(original)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_success():
    email = "testuser@mergington.edu"
    resp = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_duplicate():
    email = "michael@mergington.edu"
    resp = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert resp.status_code == 400


def test_signup_nonexistent_activity():
    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404


def test_delete_participant_success():
    # Remove existing participant
    email = "daniel@mergington.edu"
    resp = client.delete("/activities/Chess%20Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert email not in app_module.activities["Chess Club"]["participants"]


def test_delete_participant_not_found():
    resp = client.delete("/activities/Chess%20Club/signup", params={"email": "noone@mergington.edu"})
    assert resp.status_code == 404
