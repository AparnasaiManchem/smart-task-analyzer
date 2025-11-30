from django.test import TestCase
from .scoring import calculate_scores
from datetime import date, timedelta

class ScoringTests(TestCase):

    def test_overdue_task_has_higher_priority(self):
        tasks = [
            {"id": 1, "title": "Overdue", "due_date": (date.today() - timedelta(days=2)).isoformat(), "estimated_hours": 2, "importance": 5, "dependencies": []},
            {"id": 2, "title": "Future task", "due_date": (date.today() + timedelta(days=10)).isoformat(), "estimated_hours": 2, "importance": 5, "dependencies": []}
        ]
        result = calculate_scores(tasks)
        self.assertEqual(result[0]["title"], "Overdue")

    def test_high_importance_task_ranked_higher(self):
        tasks = [
            {"id": 1, "title": "Low importance", "due_date": None, "estimated_hours": 2, "importance": 3, "dependencies": []},
            {"id": 2, "title": "High importance", "due_date": None, "estimated_hours": 2, "importance": 10, "dependencies": []}
        ]
        result = calculate_scores(tasks)
        self.assertEqual(result[0]["title"], "High importance")

    def test_circular_dependency_detection(self):
        tasks = [
            {"id": 1, "title": "A", "due_date": None, "estimated_hours": 1, "importance": 5, "dependencies": [2]},
            {"id": 2, "title": "B", "due_date": None, "estimated_hours": 1, "importance": 5, "dependencies": [1]},
        ]
        result = calculate_scores(tasks)
        flags = [task.get("flags", {}) for task in result]
        self.assertTrue(any(f.get("circular_dependency") for f in flags))
