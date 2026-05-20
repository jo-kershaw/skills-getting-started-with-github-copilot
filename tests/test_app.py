from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities_returns_activities():
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert activity_name in data
    assert isinstance(data[activity_name]["participants"], list)


def test_signup_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@example.com"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    participants = client.get("/activities").json()[activity_name]["participants"]
    assert email in participants

    # Cleanup
    client.delete(f"/activities/{activity_name}/signup?email={email}")


def test_duplicate_signup_returns_400():
    # Arrange
    activity_name = "Programming Class"
    email = "duplicate@example.com"

    # Act
    first_response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )
    duplicate_response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert first_response.status_code == 200
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up"

    # Cleanup
    client.delete(f"/activities/{activity_name}/signup?email={email}")


def test_unregister_removes_participant():
    # Arrange
    activity_name = "Gym Class"
    email = "removeme@example.com"
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    participants = client.get("/activities").json()[activity_name]["participants"]
    assert email not in participants


def test_unregister_missing_participant_returns_404():
    # Arrange
    activity_name = "Art Studio"
    email = "missingparticipant@example.com"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
