from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def reset_activities():
    """Reset the in-memory activity store before and after each test."""
    # Arrange: save the original state
    original_state = deepcopy(activities)

    # Act: yield control to the test
    yield

    # Assert/cleanup: restore the original data
    activities.clear()
    activities.update(deepcopy(original_state))


@pytest.fixture
def client():
    """Provide a TestClient for calling the API."""
    return TestClient(app)


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_all_activity_names(client):
    # Arrange
    expected_names = {
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Soccer Team",
        "Basketball Club",
        "Art Club",
        "Drama Club",
        "Debate Team",
        "Science Club",
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_names.issubset(response.json().keys())


def test_signup_success_adds_email_to_activity(client, reset_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@example.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }

    updated_response = client.get("/activities")
    assert email in updated_response.json()[activity_name]["participants"]


def test_signup_fails_when_email_is_already_registered(client, reset_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_signup_fails_for_unknown_activity(client, reset_activities):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@example.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_success_removes_email_from_activity(client, reset_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }

    updated_response = client.get("/activities")
    assert email not in updated_response.json()[activity_name]["participants"]


def test_unregister_fails_for_unknown_activity(client, reset_activities):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@example.com"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_fails_when_email_is_not_registered(client, reset_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "notregistered@example.com"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is not registered for this activity"
    }
