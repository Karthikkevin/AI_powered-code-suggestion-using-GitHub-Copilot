import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def backup_activities():
    """Backup and restore the in-memory activities dict for each test."""
    orig = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(orig))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Basketball" in data


def test_signup_and_unregister_flow():
    activity = "Basketball"
    email = "testuser@example.com"

    # Ensure clean start
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Signup should succeed
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # Duplicate signup should fail with 400
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp2.status_code == 400

    # Unregister should succeed
    resp3 = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp3.status_code == 200
    assert email not in activities[activity]["participants"]

    # Unregistering again returns 404
    resp4 = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp4.status_code == 404
