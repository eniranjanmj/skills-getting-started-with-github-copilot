import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def test_activities(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Learn chess strategies",
            "schedule": "Fridays, 3:30 PM",
            "max_participants": 3,
            "participants": ["alex@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(test_activities):
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data(client, test_activities):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == test_activities


def test_signup_adds_participant_and_updates_activity_list(client, test_activities):
    email = "sam@example.com"
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in client.get("/activities").json()["Chess Club"]["participants"]
    assert email in test_activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client, test_activities):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "alex@example.com"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert test_activities["Chess Club"]["participants"] == ["alex@example.com"]


def test_signup_returns_404_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown/signup",
        params={"email": "sam@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant_and_updates_activity_list(client, test_activities):
    email = "alex@example.com"
    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert client.get("/activities").json()["Chess Club"]["participants"] == []
    assert test_activities["Chess Club"]["participants"] == []


def test_unregister_returns_404_for_missing_participant(client):
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "missing@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}


def test_unregister_returns_404_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown/signup",
        params={"email": "sam@example.com"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
