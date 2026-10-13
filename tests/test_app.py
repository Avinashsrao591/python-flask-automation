import time
import pytest

from app import create_app


def test_job_completes(client):
    import time

    response = client.post(
        "/api/jobs",
        json={"job_type": "smoke"}
    )

    assert response.status_code == 202
    job_id = response.get_json()["job_id"]

    deadline = time.monotonic() + 30

    while time.monotonic() < deadline:
        job_response = client.get(f"/api/jobs/{job_id}")
        job = job_response.get_json()

        if job["status"] in ("passed", "failed"):
            break

        time.sleep(0.1)

    assert job["status"] == "passed", (
        f"Job did not pass. Details: {job}"
    )

    assert job["result"]["exit_code"] == 0
    assert "passed" in job["result"]["output"].lower()

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_home_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.content_type.startswith("text/html")
    assert b"Python Flask Automation Dashboard" in response.data



def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_unknown_endpoint(client):
    response = client.get("/invalid-endpoint")

    assert response.status_code == 404


def test_create_job(client):
    response = client.post(
        "/api/jobs",
        json={"job_type": "smoke"}
    )

    assert response.status_code == 202

    data = response.get_json()
    assert data["job_type"] == "smoke"
    assert data["status"] == "queued"
    assert data["job_id"]


def test_reject_invalid_job_type(client):
    response = client.post(
        "/api/jobs",
        json={"job_type": "unknown"}
    )

    assert response.status_code == 400


def test_get_job(client):
    create_response = client.post(
        "/api/jobs",
        json={"job_type": "api"}
    )

    assert create_response.status_code == 202

    job_id = create_response.get_json()["job_id"]

    response = client.get(f"/api/jobs/{job_id}")

    assert response.status_code == 200
    assert response.get_json()["job_id"] == job_id


def test_job_not_found(client):
    response = client.get("/api/jobs/nonexistent")

    assert response.status_code == 404
