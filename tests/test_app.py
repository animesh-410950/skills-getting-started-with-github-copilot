from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_signup_participant_adds_email_to_activity():
    activity_name = "Chess Club"
    email = "teststudent@example.com"

    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    if email in participants:
        client.delete(f"/activities/{activity_name}/unregister?email={email}")

    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    updated_response = client.get("/activities")
    assert email in updated_response.json()[activity_name]["participants"]


def test_unregister_participant_removes_email_from_activity():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    activities_response = client.get("/activities")
    assert email not in activities_response.json()[activity_name]["participants"]
