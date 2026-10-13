import re
import time
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_ROOT / "reports"

TEST_PATHS = {
    "smoke": "automation_tests/smoke",
    "regression": "automation_tests/regression",
    "api": "automation_tests/api",
    "ui": "automation_tests/ui",
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


class JobManager:
    def __init__(self):
        self._jobs = {}
        self._lock = Lock()
        self._executor = ThreadPoolExecutor(max_workers=2)

    def create_job(self, job_type):
        
        job_id = str(uuid4())

        job = {
            "job_id": job_id,
            "job_type": job_type,
            "status": "queued",
            "created_at": utc_now(),
            "started_at": None,
            "finished_at": None,
            "result": None,
            "error": None,
            "report": None,
            "duration_seconds": None,
        }

        with self._lock:
            self._jobs[job_id] = job

        self._executor.submit(self._execute_job, job_id, job_type)
        return job.copy()

    
    def _execute_job(self, job_id, job_type):
        with self._lock:
            job = self._jobs[job_id]
            job["status"] = "running"
            job["started_at"] = utc_now()

        start_time = time.monotonic()

        try:
            REPORT_DIR.mkdir(parents=True, exist_ok=True)

            test_path = TEST_PATHS[job_type]
            report_path = REPORT_DIR / f"{job_id}.html"

            command = [
                sys.executable,
                "-m",
                "pytest",
                test_path,
                "-v",
                f"--html={report_path}",
                "--self-contained-html",
            ]

            # Execute Pytest and capture the real process result.
            completed = subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )

            output = completed.stdout
            error_output = completed.stderr

            def extract_count(pattern):
                match = re.search(pattern, output)
                return int(match.group(1)) if match else 0

            tests_passed = extract_count(r"(\d+) passed")
            tests_failed = extract_count(r"(\d+) failed")
            tests_skipped = extract_count(r"(\d+) skipped")

            failure_summary = [
                line.strip()
                for line in output.splitlines()
                if line.strip().startswith("FAILED ")
            ]

            result = {
                "exit_code": completed.returncode,
                "output": output[-12000:],
                "stderr": error_output[-4000:],
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "tests_skipped": tests_skipped,
                "failure_summary": failure_summary,
            }

            if completed.returncode == 0:
                result["message"] = (
                    "Pytest execution completed successfully"
                )
                status = "passed"
                error = None
            else:
                result["message"] = (
                    "Pytest reported failures or an execution error"
                )
                status = "failed"
                error = (
                    error_output[-4000:]
                    or "Pytest returned a nonzero exit code"
                )

        except subprocess.TimeoutExpired:
            status = "failed"
            result = None
            error = "Test execution exceeded 300 seconds"

        except Exception as exc:
            status = "failed"
            result = None
            error = str(exc)

        finally:
            duration = round(time.monotonic() - start_time, 2)

        with self._lock:
            job = self._jobs[job_id]
            job["status"] = status
            job["result"] = result
            job["error"] = error
            job["finished_at"] = utc_now()
            job["duration_seconds"] = duration

            report_path = REPORT_DIR / f"{job_id}.html"

            if report_path.is_file():
                job["report"] = str(
                    report_path.relative_to(PROJECT_ROOT)
                )


    def get_job(self, job_id):
        with self._lock:
            job = self._jobs.get(job_id)
            return job.copy() if job else None

    def list_jobs(self):
        with self._lock:
            return [job.copy() for job in self._jobs.values()]
