import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def test_activities(monkeypatch):
    # Arrange
    activities = {
        "Chess Club": {
            "description": "Test activity",
            "schedule": "Fridays",
            "max_participants": 2,
            "participants": ["registered@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(test_activities):
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_root_redirects_to_static_index(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_available_activities(client, test_activities):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == test_activities


def test_signup_adds_participant(client, test_activities):
    # Arrange
    email = "new@example.com"

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in test_activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client, test_activities):
    # Arrange
    email = "registered@example.com"

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up for this activity"}
    assert test_activities["Chess Club"]["participants"] == [email]


def test_signup_rejects_unknown_activity(client, test_activities):
    # Arrange
    email = "new@example.com"

    # Act
    response = client.post("/activities/Unknown%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert test_activities["Chess Club"]["participants"] == ["registered@example.com"]


def test_unregister_removes_participant(client, test_activities):
    # Arrange
    email = "registered@example.com"

    # Act
    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert test_activities["Chess Club"]["participants"] == []


def test_unregister_rejects_unknown_activity(client, test_activities):
    # Arrange
    email = "registered@example.com"

    # Act
    response = client.delete("/activities/Unknown%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert test_activities["Chess Club"]["participants"] == [email]


def test_unregister_rejects_unregistered_participant(client, test_activities):
    # Arrange
    email = "not-registered@example.com"

    # Act
    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}
    assert test_activities["Chess Club"]["participants"] == ["registered@example.com"]