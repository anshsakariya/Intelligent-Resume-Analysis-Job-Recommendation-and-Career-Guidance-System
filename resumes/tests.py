from io import BytesIO
from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError

from resumes.models import Resume, ResumeAnalysis
from resumes.forms import ResumeUploadForm
from resumes.services import extract_resume_text
from resumes.validators import validate_pdf_upload
from agents.resume_agent import ResumeAgent

class ResumeTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='resumetest', password='password123')
        self.user.profile.target_role = 'Python Developer'
        self.user.profile.save()

    def test_resume_agent_analysis(self):
        """Test ResumeAgent section detection, skill parsing, and ATS score calculation."""
        sample_text = """
        John Doe
        Email: john@example.com | Phone: 555-0199
        SUMMARY
        Passionate Python developer building web applications.
        EDUCATION
        B.Tech in Computer Science, State University 2024
        SKILLS
        Python, Django, PostgreSQL, SQL, Git, REST API, HTML, CSS
        EXPERIENCE
        Junior Developer at Tech Co. Built Django endpoints.
        PROJECTS
        AI Resume Analyzer: Built Django application with PyPDF2.
        """
        
        dummy_file = SimpleUploadedFile("resume.pdf", b"%PDF-1.4 dummy pdf content", content_type="application/pdf")
        resume = Resume.objects.create(user=self.user, file=dummy_file, extracted_text=sample_text)

        agent = ResumeAgent()
        analysis = agent.analyze_resume(resume)

        self.assertIsInstance(analysis, ResumeAnalysis)
        self.assertGreater(analysis.ats_score, 50)
        self.assertIn("Contains a clear, dedicated Education section.", analysis.strengths)

    def test_resume_upload_rejects_non_pdf_content_with_pdf_extension(self):
        upload = SimpleUploadedFile(
            'not-a-resume.pdf',
            b'<html>not a pdf</html>',
            content_type='application/pdf',
        )
        form = ResumeUploadForm(files={'file': upload})

        self.assertFalse(form.is_valid())
        self.assertIn('valid PDF', str(form.errors))

    def test_resume_text_extraction_accepts_open_file_objects(self):
        reader = SimpleNamespace(
            pages=[SimpleNamespace(extract_text=lambda: 'Candidate profile')],
        )
        with patch('resumes.services.PyPDF2.PdfReader', return_value=reader):
            extracted = extract_resume_text(BytesIO(b'%PDF-1.4'))

        self.assertEqual(extracted, 'Candidate profile')

    def test_resume_upload_enforces_serverless_request_size_limit(self):
        upload = SimpleUploadedFile(
            'large-resume.pdf',
            b'%PDF-' + (b'0' * (4 * 1024 * 1024)),
            content_type='application/pdf',
        )

        with self.assertRaisesMessage(ValidationError, 'File size exceeds 4MB'):
            validate_pdf_upload(upload)
