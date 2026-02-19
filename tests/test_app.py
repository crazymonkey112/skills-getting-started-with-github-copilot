import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities_state():
    original_state = copy.deepcopy(activities)

    yield

    activities.clear()
    activities.update(original_state)


def test_get_activities_returns_all_activities_and_no_store_header():
    # Arrange
    expected_activity_count = len(activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.headers.get("Cache-Control") == "no-store"
    payload = response.json()
    assert isinstance(payload, dict)
    assert len(payload) == expected_activity_count


def test_signup_adds_participant_to_activity():
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    assert new_email not in activities[activity_name]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert new_email in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_unknown_activity_returns_404():
    # Arrange
    activity_name = "Unknown Club"
    email = "someone@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant_from_activity():
    # Arrange
    activity_name = "Programming Class"
    participant_email = activities[activity_name]["participants"][0]
    assert participant_email in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 200
    assert participant_email not in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Unregistered {participant_email} from {activity_name}"


def test_unregister_non_enrolled_participant_returns_404():
    # Arrange
    activity_name = "Programming Class"
    email = "notenrolled@mergington.edu"
    assert email not in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_unknown_activity_returns_404():
    # Arrange
    activity_name = "Unknown Club"
    email = "someone@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
