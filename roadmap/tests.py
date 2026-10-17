from django.test import TestCase
from django.contrib.auth.models import User

from roadmap.models import Roadmap, RoadmapTask
from agents.planner_agent import PlannerAgent

class RoadmapTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='roadmaptest', password='password123')
        self.user.profile.target_role = 'Django Developer'
        self.user.profile.save()

    def test_planner_agent_roadmap_generation(self):
        """Test PlannerAgent generates structured tasks and skill gaps."""
        agent = PlannerAgent()
        roadmap = agent.generate_roadmap(self.user, hours_per_day=3, days_per_week=5)

        self.assertIsInstance(roadmap, Roadmap)
        self.assertEqual(roadmap.hours_per_day, 3)
        self.assertGreater(roadmap.tasks.count(), 0)

        # Test task toggling
        task = roadmap.tasks.first()
        task.status = 'Completed'
        task.save()
        self.assertEqual(RoadmapTask.objects.get(pk=task.pk).status, 'Completed')
