import re
import io
import PyPDF2
from skills.models import Skill

def extract_resume_text(file_obj):
    """
    Extracts raw text from a PDF file using a resilient multi-engine pipeline:
    1. PyPDF2
    2. pypdf
    3. pdfplumber
    4. pdfminer.high_level
    """
    text = ""
    raw_bytes = None

    try:
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
        raw_bytes = file_obj.read()
    except Exception as e:
        print(f"Error reading file stream: {e}")

    if not raw_bytes:
        return ""

    # Engine 1: PyPDF2
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(raw_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"PyPDF2 extraction note: {e}")

    # Engine 2: pypdf (if PyPDF2 returned empty)
    if not text.strip():
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(raw_bytes))
            for page in reader.pages:
                pt = page.extract_text()
                if pt:
                    text += pt + "\n"
        except Exception as e:
            print(f"pypdf extraction note: {e}")

    # Engine 3: pdfplumber (handles intricate text layouts and tables)
    if not text.strip():
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(raw_bytes)) as pdf:
                for page in pdf.pages:
                    pt = page.extract_text()
                    if pt:
                        text += pt + "\n"
        except Exception as e:
            print(f"pdfplumber extraction note: {e}")

    # Engine 4: pdfminer.six
    if not text.strip():
        try:
            from pdfminer.high_level import extract_text as miner_extract
            text = miner_extract(io.BytesIO(raw_bytes)) or ""
        except Exception as e:
            print(f"pdfminer extraction note: {e}")

    # Clean whitespace & linebreaks
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned_text = "\n".join(lines)
    return cleaned_text

def extract_contact_info(text):
    """
    Extracts email and phone number using Regex.
    """
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    email = email_match.group(0) if email_match else ""

    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    phone = phone_match.group(0) if phone_match else ""

    return {'email': email, 'phone': phone}

def detect_resume_sections(text):
    """
    Detects presence of key resume sections with comprehensive keyword matching.
    """
    text_lower = text.lower()
    sections = {
        'summary': any(kw in text_lower for kw in [
            'summary', 'objective', 'profile', 'about me', 'career objective',
            'professional summary', 'seeking a position', 'seeking a'
        ]),
        'education': any(kw in text_lower for kw in [
            'education', 'academic', 'academics', 'qualification', 'qualifications',
            'educational qualification', 'educational background', 'degree',
            'university', 'college', 'institute', 'graduation', 'diploma',
            'b.e', 'b.tech', 'bca', 'mca', 'b.sc', 'm.sc', 'm.tech', 'bachelor',
            'master', 'school', 'hsc', 'ssc', 'cgpa', 'examination'
        ]),
        'experience': any(kw in text_lower for kw in [
            'experience', 'employment', 'work history', 'internship', 'internships',
            'work experience', 'professional experience', 'freelance'
        ]),
        'skills': any(kw in text_lower for kw in [
            'skills', 'technical skills', 'competencies', 'technologies', 'tools',
            'tech stack', 'languages', 'frameworks'
        ]),
        'projects': any(kw in text_lower for kw in [
            'projects', 'academic projects', 'key projects', 'personal projects',
            'project'
        ]),
        'certifications': any(kw in text_lower for kw in [
            'certification', 'certifications', 'certificates', 'courses', 'licenses'
        ]),
        'achievements': any(kw in text_lower for kw in [
            'achievement', 'achievements', 'awards', 'honors', 'hackathon', 'extracurricular'
        ]),
    }
    return sections

def extract_skills_from_text(text):
    """
    Matches text against registered DB skills and common tech skill terms.
    """
    text_lower = text.lower()
    matched_skills = set()

    # Load DB skills
    db_skills = Skill.objects.all()
    if db_skills.exists():
        for skill in db_skills:
            # Word boundary regex search to avoid partial word match (e.g. 'c' matching 'chat')
            pattern = r'\b' + re.escape(skill.name.lower()) + r'\b'
            if re.search(pattern, text_lower):
                matched_skills.add(skill)

    # Standard default skill library backup if DB skills not fully populated
    default_skill_names = [
        'python', 'django', 'flask', 'fastapi', 'sql', 'postgresql', 'mysql', 'sqlite',
        'java', 'javascript', 'typescript', 'react', 'angular', 'vue', 'html', 'css',
        'bootstrap', 'node.js', 'express', 'machine learning', 'data science', 'pandas',
        'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'nltk', 'opencv', 'docker',
        'kubernetes', 'aws', 'azure', 'gcp', 'git', 'github', 'rest api', 'graphql',
        'redis', 'celery', 'linux', 'c++', 'c#', 'php', 'ruby'
    ]

    for skill_name in default_skill_names:
        pattern = r'\b' + re.escape(skill_name) + r'\b'
        if re.search(pattern, text_lower):
            # Check or create DB skill object
            skill_obj, _ = Skill.objects.get_or_create(
                name=skill_name.title() if len(skill_name) > 3 else skill_name.upper(),
                defaults={'category': 'Programming Language'}
            )
            matched_skills.add(skill_obj)

    return list(matched_skills)
