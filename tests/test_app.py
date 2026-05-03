from copy import deepcopy
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app, activities

initial_activities = deepcopy(activities)

client = TestClient(app)


def reset_activities():
    activities.clear()
    activities.update(deepcopy(initial_activities))


def test_get_activities_returns_expected_structure():
    # Arrange
    reset_activities()

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert all("participants" in activity for activity in data.values())


def test_signup_adds_participant_to_activity():
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    email = "alex@mergington.edu"

    # Act
    response = client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{quote(activity_name)}/signup?email={quote(email)}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_delete_participant_removes_participant():
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{quote(activity_name)}/participants/{quote(email)}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_delete_missing_participant_returns_404():
    # Arrange
    reset_activities()
    activity_name = "Chess Club"
    email = "nonexistent@mergington.edu"

    # Act
    response = client.delete(f"/activities/{quote(activity_name)}/participants/{quote(email)}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
