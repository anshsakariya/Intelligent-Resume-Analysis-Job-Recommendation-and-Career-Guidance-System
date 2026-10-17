from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import Profile
from resumes.models import Resume, ResumeAnalysis
from skills.models import Skill, UserSkill

class AccountsTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )

    def test_profile_signal_creation(self):
        """Test that profile is automatically created when a User is created."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.full_name, 'Test User')
        self.assertEqual(self.user.profile.target_role, 'Python Developer')

    def test_profile_update(self):
        """Test updating profile target role and career goal."""
        profile = self.user.profile
        profile.target_role = 'Django Developer'
        profile.years_of_experience = 3
        profile.save()

        updated_profile = Profile.objects.get(user=self.user)
        self.assertEqual(updated_profile.target_role, 'Django Developer')
        self.assertEqual(updated_profile.years_of_experience, 3)

    def test_registration_form_accepts_password_matching_security_policy(self):
        """Registration should accept a strong password and a valid phone number."""
        from accounts.forms import UserRegistrationForm
        form_data = {
            'username': 'testuser123',
            'email': 'newuser@example.com',
            'phone': '9876543210',
            'password1': 'Skyline-Maple-Train-47!',
            'password2': 'Skyline-Maple-Train-47!',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())

    def test_registration_rejects_short_password(self):
        from accounts.forms import UserRegistrationForm
        form = UserRegistrationForm(data={
            'username': 'shortpassuser',
            'email': 'shortpass@example.com',
            'phone': '9876543210',
            'password1': 'short',
            'password2': 'short',
        })

        self.assertFalse(form.is_valid())

    def test_register_view_redirects_to_login(self):
        """Test successful registration redirects user to login page."""
        from django.urls import reverse
        response = self.client.post(reverse('register'), {
            'username': 'newuser99',
            'email': 'newuser99@example.com',
            'phone': '9876543210',
            'password1': 'Skyline-Maple-Train-47!',
            'password2': 'Skyline-Maple-Train-47!',
        })
        self.assertRedirects(response, reverse('login'))

    def test_logout_requires_post(self):
        from django.urls import reverse
        self.client.force_login(self.user)

        response = self.client.get(reverse('logout'))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(self.client.session.get('_auth_user_id'))

    def test_logout_post_logs_user_out(self):
        from django.urls import reverse
        self.client.force_login(self.user)

        response = self.client.post(reverse('logout'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_repeated_failed_logins_are_throttled(self):
        from django.conf import settings
        from django.http import HttpResponse
        from django.urls import reverse
        from unittest.mock import patch

        with patch('accounts.views.render', return_value=HttpResponse()):
            for _ in range(settings.AXES_FAILURE_LIMIT - 1):
                response = self.client.post(reverse('login'), {
                    'username': self.user.username,
                    'password': 'incorrect-password',
                })
                self.assertEqual(response.status_code, 200)

            response = self.client.post(reverse('login'), {
                'username': self.user.username,
                'password': 'incorrect-password',
            })
        self.assertEqual(response.status_code, 429)
    def test_duplicate_email_disallowed(self):
        """Test registration rejects an email address that is already registered."""
        from accounts.forms import UserRegistrationForm
        form_data = {
            'username': 'unique_user',
            'email': 'test@example.com', # existing email from setUp
            'phone': '9876543210',
            'password1': 'Skyline-Maple-Train-47!',
            'password2': 'Skyline-Maple-Train-47!',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'], ['A user with that email address already exists.'])

    def test_duplicate_username_is_rejected(self):
        """Registration should respect the database's unique username constraint."""
        from accounts.forms import UserRegistrationForm
        form = UserRegistrationForm(data={
            'username': 'same_user',
            'email': 'user1@example.com',
            'phone': '9876543210',
            'password1': 'Saffron-Trail-Planet-49!',
            'password2': 'Saffron-Trail-Planet-49!',
        })
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())
        form.save()

        duplicate = UserRegistrationForm(data={
            'username': 'same_user',
            'email': 'user2@example.com',
            'phone': '9876543211',
            'password1': 'Velvet-Cedar-Cloud-73!',
            'password2': 'Velvet-Cedar-Cloud-73!',
        })
        self.assertFalse(duplicate.is_valid())
        self.assertIn('username', duplicate.errors)

    def test_dashboard_uses_current_skill_gap_before_roadmap_exists(self):
        """The dashboard should calculate skill chart values after resume analysis."""
        self.client.force_login(self.user)
        resume = Resume.objects.create(user=self.user, extracted_text='Python Django developer')
        ResumeAnalysis.objects.create(resume=resume)
        python_skill = Skill.objects.create(name='Python')
        docker_skill = Skill.objects.create(name='Docker')
        UserSkill.objects.create(user=self.user, skill=python_skill, is_extracted=True)
        UserSkill.objects.create(user=self.user, skill=docker_skill, is_extracted=True)
        UserSkill.objects.create(
            user=self.user,
            skill=docker_skill,
            is_target=True,
            is_extracted=False,
        )

        response = self.client.get('/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(response.context['existing_skills'], ['Python', 'Docker'])
        self.assertIn('PostgreSQL', response.context['missing_skills'])
        self.assertNotIn('Python', response.context['missing_skills'])
        self.assertNotIn('Docker', response.context['missing_skills'])

    def test_dashboard_shows_zero_mastered_skills_before_resume_analysis(self):
        """Saved skills should not appear as mastered until a resume is analyzed."""
        self.client.force_login(self.user)
        python_skill = Skill.objects.create(name='Python')
        UserSkill.objects.create(user=self.user, skill=python_skill, is_extracted=True)

        response = self.client.get('/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['existing_skills'], [])
        self.assertContains(response, 'Mastered (0)')

    def test_dashboard_analyzes_resume_without_existing_ats_analysis(self):
        """The ATS chart should have computed metric values when analysis is missing."""
        self.client.force_login(self.user)
        resume = Resume.objects.create(
            user=self.user,
            extracted_text=(
                'SUMMARY\nPython developer\n'
                'EDUCATION\nB.Tech Computer Science\n'
                'SKILLS\nPython, Django, PostgreSQL, SQL, Git, REST API\n'
                'EXPERIENCE\nBuilt Django endpoints\n'
                'PROJECTS\nResume Analyzer with Django API'
            ),
        )

        response = self.client.get('/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ResumeAnalysis.objects.filter(resume=resume).exists())
        self.assertGreater(response.context['latest_analysis'].skills_score, 0)
        self.assertGreater(len(response.context['existing_skills']), 0)
        self.assertContains(response, str(response.context['latest_analysis'].skills_score))
