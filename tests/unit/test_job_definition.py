"""Checks resources/jobs/tourism_pipeline.yml without connecting to Databricks."""
import unittest

import yaml

from _helpers import JOB_FILE

EXPECTED_TASKS = 18
LAYER_GATES = {
    # setup task: tasks it must wait for (the whole previous layer)
    "silver_setup": {"ingest_psa", "ingest_psgc", "ingest_dot", "ingest_psa_ds18_pdf"},
    "gold_setup": {"silver_dot", "silver_psa_economy", "silver_population"},
    "analytics": {"gold_run_evidence"},
}


def load_job():
    bundle = yaml.safe_load(JOB_FILE.read_text(encoding="utf-8"))
    jobs = bundle["resources"]["jobs"]
    assert len(jobs) == 1, f"Expected one job in {JOB_FILE.name}, found {list(jobs)}"
    return next(iter(jobs.values()))


class JobDefinitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.job = load_job()
        cls.tasks = {task["task_key"]: task for task in cls.job["tasks"]}

    def test_task_count_and_unique_keys(self):
        keys = [task["task_key"] for task in self.job["tasks"]]
        self.assertEqual(len(keys), len(set(keys)), "Duplicate task_key in the job")
        self.assertEqual(len(keys), EXPECTED_TASKS,
                         "Task count changed: update EXPECTED_TASKS and the Run order diagram")

    def test_every_notebook_path_exists(self):
        for key, task in self.tasks.items():
            with self.subTest(task=key):
                relative = task["notebook_task"]["notebook_path"]
                self.assertTrue(relative.startswith("../../notebooks/"), relative)
                self.assertTrue((JOB_FILE.parent / relative).resolve().is_file(),
                                f"{key}: notebook not found: {relative}")

    def test_dependencies_point_to_existing_tasks(self):
        for key, task in self.tasks.items():
            for dep in task.get("depends_on", []):
                with self.subTest(task=key, depends_on=dep["task_key"]):
                    self.assertIn(dep["task_key"], self.tasks)

    def test_no_dependency_cycles(self):
        state = {}

        def visit(key, path):
            if state.get(key) == "done":
                return
            self.assertNotEqual(state.get(key), "visiting", f"Cycle: {' -> '.join(path + [key])}")
            state[key] = "visiting"
            for dep in self.tasks[key].get("depends_on", []):
                visit(dep["task_key"], path + [key])
            state[key] = "done"

        for key in self.tasks:
            visit(key, [])

    def test_layer_gates_wait_for_the_whole_previous_layer(self):
        for gate, required in LAYER_GATES.items():
            with self.subTest(gate=gate):
                deps = {dep["task_key"] for dep in self.tasks[gate].get("depends_on", [])}
                self.assertEqual(deps, required)

    def test_every_task_has_a_timeout(self):
        self.assertGreater(self.job.get("timeout_seconds", 0), 0, "Job-level timeout missing")
        for key, task in self.tasks.items():
            with self.subTest(task=key):
                self.assertGreater(task.get("timeout_seconds", 0), 0)
                self.assertLessEqual(task["timeout_seconds"], self.job["timeout_seconds"])

    def test_retries_only_on_ingestion_tasks(self):
        for key, task in self.tasks.items():
            if task.get("max_retries", 0) > 0:
                with self.subTest(task=key):
                    self.assertTrue(key.startswith("ingest_"),
                                    "Only tasks that call external sources should retry")

    def test_failure_alerts_and_single_run(self):
        self.assertEqual(self.job.get("max_concurrent_runs"), 1)
        self.assertIn("${var.alert_email}", self.job["email_notifications"]["on_failure"])


if __name__ == "__main__":
    unittest.main()
