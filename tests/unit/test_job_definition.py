"""Checks resources/jobs/tourism_pipeline.yml without connecting to Databricks."""
import re
import unittest

import yaml

from _helpers import JOB_FILE, REPO_ROOT

RESOURCES_README = REPO_ROOT / "resources" / "README.md"


def layer_of(task):
    """Layer folder of a task's notebook, e.g. '02_silver'."""
    return task["notebook_task"]["notebook_path"].split("/")[-2]


class JobDefinitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bundle = yaml.safe_load(JOB_FILE.read_text(encoding="utf-8")) or {}
        jobs = bundle.get("resources", {}).get("jobs", {})
        if len(jobs) != 1:
            raise ValueError(f"Expected exactly one job in {JOB_FILE.name}, found {list(jobs)}")
        cls.job = next(iter(jobs.values()))
        cls.task_list = cls.job.get("tasks", [])
        cls.tasks = {task["task_key"]: task for task in cls.task_list}

    def deps(self, key):
        return {dep["task_key"] for dep in self.tasks[key].get("depends_on", [])}

    def ancestors(self, key):
        seen, stack = set(), list(self.deps(key))
        while stack:
            current = stack.pop()
            if current not in seen and current in self.tasks:
                seen.add(current)
                stack.extend(self.deps(current))
        return seen

    def test_task_keys_are_unique(self):
        keys = [task["task_key"] for task in self.task_list]
        self.assertTrue(keys, "The job has no tasks")
        self.assertEqual(len(keys), len(set(keys)), "Duplicate task_key in the job")

    def test_every_notebook_path_exists(self):
        for key, task in self.tasks.items():
            with self.subTest(task=key):
                relative = task.get("notebook_task", {}).get("notebook_path", "")
                self.assertTrue(relative.startswith("../../notebooks/"), f"{key}: unexpected path {relative!r}")
                self.assertTrue((JOB_FILE.parent / relative).resolve().is_file(),
                                f"{key}: notebook not found: {relative}")

    def test_dependencies_point_to_existing_tasks(self):
        for key in self.tasks:
            for dep in self.deps(key):
                with self.subTest(task=key, depends_on=dep):
                    self.assertIn(dep, self.tasks, f"{key} depends on unknown task {dep}")

    def test_no_dependency_cycles(self):
        state = {}

        def visit(key, path):
            if state.get(key) == "done":
                return
            self.assertNotEqual(state.get(key), "visiting", f"Cycle: {' -> '.join(path + [key])}")
            state[key] = "visiting"
            for dep in self.deps(key):
                if dep in self.tasks:
                    visit(dep, path + [key])
            state[key] = "done"

        for key in self.tasks:
            visit(key, [])

    def test_each_layer_starts_after_the_whole_previous_layer(self):
        """The first task(s) of every layer must (directly or indirectly) wait for every task of the layer before.

        Layers come from the notebook folders (01_ingestion_bronze, 02_silver, 03_gold, 04_analytics), so adding a task
        to a layer needs no change here, but a task that the next layer does not wait for fails.
        """
        layers = {}
        for key, task in self.tasks.items():
            layers.setdefault(layer_of(task), set()).add(key)
        ordered = sorted(layers)
        for previous, current in zip(ordered, ordered[1:]):
            entries = [key for key in layers[current] if not (self.deps(key) & layers[current])]
            for entry in entries:
                with self.subTest(layer=current, entry_task=entry):
                    missing = sorted(layers[previous] - self.ancestors(entry))
                    self.assertFalse(missing, f"{entry} can start before these {previous} tasks finish: {missing}")

    def test_every_task_has_a_timeout(self):
        job_timeout = self.job.get("timeout_seconds", 0)
        self.assertGreater(job_timeout, 0, "Job-level timeout_seconds is missing")
        for key, task in self.tasks.items():
            with self.subTest(task=key):
                self.assertGreater(task.get("timeout_seconds", 0), 0, f"{key} has no timeout_seconds")
                self.assertLessEqual(task["timeout_seconds"], job_timeout, f"{key} timeout exceeds the job timeout")

    def test_retries_only_on_ingestion_tasks(self):
        for key, task in self.tasks.items():
            if task.get("max_retries", 0) > 0:
                with self.subTest(task=key):
                    self.assertTrue(key.startswith("ingest_"), "Only tasks that call external sources should retry")

    def test_failure_alerts_and_single_run(self):
        self.assertEqual(self.job.get("max_concurrent_runs"), 1, "max_concurrent_runs must be 1")
        on_failure = self.job.get("email_notifications", {}).get("on_failure", [])
        self.assertIn("${var.alert_email}", on_failure, "email_notifications.on_failure must include ${var.alert_email}")

    def test_resources_readme_lists_every_task(self):
        """resources/README.md (task table, and the Mermaid diagram if present) matches the job's tasks."""
        readme = RESOURCES_README.read_text(encoding="utf-8")
        section = re.search(r"^### Tasks\n(.*?)(?=^#{2,3} )", readme, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(section, "resources/README.md has no '### Tasks' section")
        table_keys = set(re.findall(r"^\|[^|]*\|\s*`([a-z0-9_]+)`\s*\|", section.group(1), re.MULTILINE))
        self.assertEqual(table_keys, set(self.tasks), "Update the Tasks table in resources/README.md")
        mermaid = re.search(r"```mermaid\n(.*?)```", readme, re.DOTALL)
        if mermaid:
            missing = sorted(key for key in self.tasks if not re.search(rf"\b{key}\b", mermaid.group(1)))
            self.assertFalse(missing, f"Add these tasks to the Run order diagram: {missing}")


if __name__ == "__main__":
    unittest.main()
