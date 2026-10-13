
from pathlib import Path

from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    request,
    send_from_directory,
)

from app.job_manager import JobManager

jobs_bp = Blueprint("jobs", __name__)
job_manager = JobManager()

ALLOWED_JOB_TYPES = {"smoke", "regression", "api", "ui"}


@jobs_bp.post("/api/jobs")
def create_job():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    job_type = data.get("job_type")

    if not isinstance(job_type, str) or job_type not in ALLOWED_JOB_TYPES:
        return jsonify({
            "error": "job_type must be smoke, regression, api, or ui"
        }), 400

    job = job_manager.create_job(job_type)
    return jsonify(job), 202


@jobs_bp.get("/api/jobs")
def list_jobs():
    return jsonify({"jobs": job_manager.list_jobs()}), 200


@jobs_bp.get("/api/jobs/<job_id>")
def get_job(job_id):
    job = job_manager.get_job(job_id)

    if job is None:
        return jsonify({"error": "Job not found"}), 404

    return jsonify(job), 200


@jobs_bp.get("/reports/<job_id>")
def view_report(job_id):
    job = job_manager.get_job(job_id)

    if not job or not job.get("report"):
        abort(404)

    report_dir = Path(current_app.root_path).parent / "reports"
    report_name = Path(job["report"]).name

    if report_name != f"{job_id}.html":
        abort(404)

    report_path = report_dir / report_name

    if not report_path.is_file():
        abort(404)

    return send_from_directory(
        str(report_dir),
        report_name,
        mimetype="text/html",
    )
