from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from jobs.models import Job
from jobs.forms import JobApplicationForm
from skills.models import Skill, UserSkill
from agents.job_agent import JobAgent

class JobRecommenderTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='jobtest', password='password123')
        self.user.profile.target_role = 'Python Developer'
        self.user.profile.save()

        # Create skills
        python_skill = Skill.objects.create(name='Python', category='Programming Language')
        django_skill = Skill.objects.create(name='Django', category='Web Framework')
        docker_skill = Skill.objects.create(name='Docker', category='Cloud & DevOps')

        # Assign user skills
        UserSkill.objects.create(user=self.user, skill=python_skill, is_extracted=True)
        UserSkill.objects.create(user=self.user, skill=django_skill, is_extracted=True)

        # Create Job
        job = Job.objects.create(
            title='Python Developer',
            company='Test Company',
            description='Looking for Python and Django developer with Docker experience.',
            experience_level='Entry Level'
        )
        job.required_skills.add(python_skill, django_skill, docker_skill)

    def test_job_recommender(self):
        """Test JobAgent recommendation ranking and skill gap breakdown."""
        agent = JobAgent()
        recs = agent.recommend_jobs(self.user)

        self.assertGreater(len(recs), 0)
        top_rec = recs[0]
        self.assertIn('Python', top_rec.matched_skills)
        self.assertIn('Django', top_rec.matched_skills)
        self.assertIn('Docker', top_rec.missing_skills)
        self.assertGreater(top_rec.match_score, 50)

    def test_job_application_rejects_non_pdf_resume_upload(self):
        upload = SimpleUploadedFile(
            'not-a-resume.pdf',
            b'not a PDF',
            content_type='application/pdf',
        )
        form = JobApplicationForm(
            data={
                'full_name': 'Test User',
                'email': 'test@example.com',
                'phone': '1234567890',
                'experience_years': '0-1 years',
                'resume': '',
                'cover_letter': '',
            },
            files={'custom_resume_file': upload},
            user=self.user,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('valid PDF', str(form.errors))
