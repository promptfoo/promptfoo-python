from pathlib import Path

import yaml

WORKFLOWS_DIR = Path(__file__).resolve().parents[1] / ".github" / "workflows"


def test_setup_node_package_manager_cache_is_disabled() -> None:
    """CI uses a published npm CLI; setup-node should never cache this Python project's packages."""
    matches = 0
    for workflow in sorted(WORKFLOWS_DIR.iterdir()):
        if workflow.suffix not in {".yml", ".yaml"}:
            continue

        jobs = yaml.safe_load(workflow.read_text(encoding="utf-8"))["jobs"]
        for job_name, job in jobs.items():
            for step in job.get("steps", []):
                if not step.get("uses", "").lower().startswith("actions/setup-node@"):
                    continue

                matches += 1
                inputs = step.get("with", {})
                location = f"{workflow.name}, job {job_name}"
                automatic = inputs.get("package-manager-cache")
                assert automatic is False or (isinstance(automatic, str) and automatic.lower() == "false"), (
                    f"{location}: setup-node must explicitly disable package-manager-cache"
                )
                assert inputs.get("cache") in (None, ""), f"{location}: setup-node must not set an explicit cache"

    assert matches, "No actions/setup-node steps found; check that this test still covers the workflows"
