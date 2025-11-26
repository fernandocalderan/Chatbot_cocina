from app.jobs.retention_cleanup import run_retention


def test_retention_job_runs():
    # Should not raise and should log; no side effects expected
    run_retention()
