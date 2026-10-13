
import requests

BASE_URL = "http://127.0.0.1:5000"


def test_health_api():
    response = requests.get(
        f"{BASE_URL}/health",
        timeout=10
    )

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_smoke_job_api():
    response = requests.post(
        f"{BASE_URL}/api/jobs",
        json={"job_type": "smoke"},
        timeout=10
    )

    assert response.status_code == 202

    data = response.json()
    assert data["job_type"] == "smoke"
    assert data["status"] in ("queued", "running", "passed")
    assert data["job_id"]


def test_reject_invalid_job_api():
    response = requests.post(
        f"{BASE_URL}/api/jobs",
        json={"job_type": "invalid"},
        timeout=10
    )

    assert response.status_code == 400


def test_unknown_job_api():
    response = requests.get(
        f"{BASE_URL}/api/jobs/nonexistent-job-id",
        timeout=10
    )

    assert response.status_code == 404
