import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Backup original data
    original_activities = activities.copy()
    yield
    # Restore after test
    activities.clear()
    activities.update(original_activities)


def test_root_redirect(client):
    # Arrange: No special setup needed

    # Act: Make GET request to root
    response = client.get("/")

    # Assert: Check for redirect to static/index.html
    assert response.status_code == 200
    assert "RedirectResponse" in str(response.history) or response.url.path == "/static/index.html"


def test_get_activities(client):
    # Arrange: No special setup needed

    # Act: Make GET request to activities
    response = client.get("/activities")

    # Assert: Check response status and structure
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_valid(client):
    # Arrange: No special setup needed

    # Act: Make POST request to signup
    response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")

    # Assert: Check response and that participant was added
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert "test@mergington.edu" in activities_data["Chess Club"]["participants"]


def test_signup_duplicate(client):
    # Arrange: Sign up once
    client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")

    # Act: Attempt to sign up again
    response = client.post("/activities/Chess%20Club/signup?email=duplicate@mergington.edu")

    # Assert: Check for 400 error
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_invalid_activity(client):
    # Arrange: No special setup needed

    # Act: Make POST request with invalid activity
    response = client.post("/activities/Invalid%20Activity/signup?email=test@mergington.edu")

    # Assert: Check for 404 error
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_valid(client):
    # Arrange: Sign up first
    client.post("/activities/Chess%20Club/signup?email=unregister@mergington.edu")

    # Act: Unregister the participant
    response = client.delete("/activities/Chess%20Club/signup?email=unregister@mergington.edu")

    # Assert: Check response and that participant was removed
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert "unregister@mergington.edu" not in activities_data["Chess Club"]["participants"]


def test_unregister_not_signed_up(client):
    # Arrange: No special setup needed

    # Act: Attempt to unregister without signing up
    response = client.delete("/activities/Chess%20Club/signup?email=notsigned@mergington.edu")

    # Assert: Check for 400 error
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]


def test_unregister_invalid_activity(client):
    # Arrange: No special setup needed

    # Act: Make DELETE request with invalid activity
    response = client.delete("/activities/Invalid%20Activity/signup?email=test@mergington.edu")

    # Assert: Check for 404 error
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]