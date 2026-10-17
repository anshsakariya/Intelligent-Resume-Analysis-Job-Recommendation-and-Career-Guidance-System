import os
import sys

# Ensure current working directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from skills.models import Skill
from jobs.models import Job

def seed_skills_and_jobs():
    print("Seeding Skill database...")
    skills_data = [
        ('Python', 'Programming Language'),
        ('Django', 'Web Framework'),
        ('Flask', 'Web Framework'),
        ('FastAPI', 'Web Framework'),
        ('SQL', 'Database'),
        ('PostgreSQL', 'Database'),
        ('MySQL', 'Database'),
        ('MongoDB', 'Database'),
        ('Redis', 'Database'),
        ('Java', 'Programming Language'),
        ('JavaScript', 'Programming Language'),
        ('TypeScript', 'Programming Language'),
        ('React', 'Web Framework'),
        ('Node.js', 'Web Framework'),
        ('HTML', 'Programming Language'),
        ('CSS', 'Programming Language'),
        ('Bootstrap', 'Web Framework'),
        ('Machine Learning', 'Data Science & AI'),
        ('Data Science', 'Data Science & AI'),
        ('Pandas', 'Data Science & AI'),
        ('NumPy', 'Data Science & AI'),
        ('Scikit-learn', 'Data Science & AI'),
        ('TensorFlow', 'Data Science & AI'),
        ('PyTorch', 'Data Science & AI'),
        ('NLTK', 'Data Science & AI'),
        ('Docker', 'Cloud & DevOps'),
        ('AWS', 'Cloud & DevOps'),
        ('Git', 'Tools & Version Control'),
        ('GitHub', 'Tools & Version Control'),
        ('REST API', 'Web Framework'),
        ('Celery', 'Cloud & DevOps'),
        ('Linux', 'Tools & Version Control'),
        ('Testing', 'Tools & Version Control'),
        ('Generative AI', 'Data Science & AI'),
    ]

    skill_objs = {}
    for name, category in skills_data:
        skill, created = Skill.objects.get_or_create(
            name=name,
            defaults={'category': category}
        )
        skill_objs[name] = skill

    print(f"Total Skills in DB: {Skill.objects.count()}")

    print("Seeding Realistic Job Listings...")
    jobs_data = [
        {
            'title': 'Python Developer',
            'company': 'TechFlow Solutions (Sample)',
            'description': 'We are looking for a skilled Python Developer to build robust backend web applications using Django and REST APIs. You will work closely with database engineers to integrate PostgreSQL and Redis caching.',
            'required': ['Python', 'Django', 'SQL', 'PostgreSQL', 'REST API', 'Git'],
            'preferred': ['Docker', 'Redis', 'Celery', 'AWS'],
            'exp': 'Entry Level',
            'location': 'Remote / San Francisco',
            'salary': '$85,000 - $110,000 / yr',
            'type': 'Full-Time',
        },
        {
            'title': 'Django Developer',
            'company': 'NexGen Digital (Sample)',
            'description': 'Seeking an experienced Django Web Developer to design scalable database schemas, implement secure user authentication, and create custom Django REST Framework endpoints for enterprise web applications.',
            'required': ['Django', 'Python', 'REST API', 'PostgreSQL', 'Git', 'HTML', 'CSS'],
            'preferred': ['Docker', 'Redis', 'Testing', 'Bootstrap'],
            'exp': 'Mid Level',
            'location': 'Hybrid / New York',
            'salary': '$105,000 - $130,000 / yr',
            'type': 'Full-Time',
        },
        {
            'title': 'Data Analyst',
            'company': 'Alpha Insights Corp (Sample)',
            'description': 'Looking for a detail-oriented Data Analyst to collect, process, and analyze complex datasets using Python, Pandas, and SQL. You will create visual executive dashboards and report trends.',
            'required': ['Python', 'SQL', 'Pandas', 'NumPy', 'Data Science'],
            'preferred': ['Scikit-learn', 'PostgreSQL', 'Git'],
            'exp': 'Entry Level',
            'location': 'Remote / Chicago',
            'salary': '$75,000 - $95,000 / yr',
            'type': 'Full-Time',
        },
        {
            'title': 'Data Scientist',
            'company': 'Quantum AI Analytics (Sample)',
            'description': 'Develop statistical models and predictive machine learning algorithms on large datasets. Requires expertise in Python, Pandas, NumPy, Scikit-learn, and SQL database queries.',
            'required': ['Python', 'Data Science', 'Machine Learning', 'Pandas', 'NumPy', 'Scikit-learn', 'SQL'],
            'preferred': ['TensorFlow', 'PyTorch', 'Docker', 'AWS'],
            'exp': 'Mid Level',
            'location': 'Remote / Boston',
            'salary': '$120,000 - $150,000 / yr',
            'type': 'Full-Time',
        },
        {
            'title': 'Machine Learning Engineer',
            'company': 'Apex Autonomous Systems (Sample)',
            'description': 'Build, train, deploy, and monitor machine learning models in production environments. Deep experience with PyTorch/TensorFlow, Docker containers, and MLOps workflows required.',
            'required': ['Python', 'Machine Learning', 'PyTorch', 'TensorFlow', 'Scikit-learn', 'Docker', 'Git'],
            'preferred': ['AWS', 'Linux', 'Generative AI', 'REST API'],
            'exp': 'Senior Level',
            'location': 'Remote / Austin',
            'salary': '$150,000 - $185,000 / yr',
            'type': 'Full-Time',
        },
        {
            'title': 'AI Engineer',
            'company': 'Cognitive Innovations (Sample)',
            'description': 'Design, build, and evaluate Generative AI and LLM-powered autonomous agents. Requires proficiency in Python, Prompting, LangChain/OpenAI APIs, PyTorch, and cloud deployment.',
            'required': ['Python', 'Generative AI', 'Machine Learning', 'REST API', 'Git', 'Docker'],
            'preferred': ['PyTorch', 'NLTK', 'AWS', 'FastAPI'],
            'exp': 'Mid Level',
            'location': 'Remote / Seattle',
            'salary': '$135,000 - $165,000 / yr',
            'type': 'Full-Time',
        },
        {
            'title': 'Backend Developer',
            'company': 'CloudScale Microservices (Sample)',
            'description': 'Construct microservice architectures using Python, FastAPI/Django, and SQL/NoSQL databases. Focus on API speed, security, CI/CD pipelines, and Redis caching layers.',
            'required': ['Python', 'REST API', 'SQL', 'PostgreSQL', 'Redis', 'Git', 'Linux'],
            'preferred': ['Docker', 'AWS', 'Testing', 'FastAPI'],
            'exp': 'Mid Level',
            'location': 'Hybrid / Denver',
            'salary': '$110,000 - $140,000 / yr',
            'type': 'Full-Time',
        },
        {
            'title': 'Full Stack Developer',
            'company': 'Vanguard Web Systems (Sample)',
            'description': 'Develop end-to-end responsive web applications using React on the frontend and Django/Python on the backend. Experience with modern CSS and REST APIs essential.',
            'required': ['JavaScript', 'React', 'Python', 'Django', 'HTML', 'CSS', 'REST API', 'Git'],
            'preferred': ['PostgreSQL', 'Docker', 'Bootstrap', 'Node.js'],
            'exp': 'Entry Level',
            'location': 'Remote / Toronto',
            'salary': '$90,000 - $115,000 / yr',
            'type': 'Full-Time',
        },
    ]

    for item in jobs_data:
        job, created = Job.objects.get_or_create(
            title=item['title'],
            company=item['company'],
            defaults={
                'description': item['description'],
                'experience_level': item['exp'],
                'location': item['location'],
                'salary': item['salary'],
                'employment_type': item['type'],
                'is_sample_data': True,
            }
        )

        req_objs = [skill_objs[name] for name in item['required'] if name in skill_objs]
        pref_objs = [skill_objs[name] for name in item['preferred'] if name in skill_objs]

        job.required_skills.set(req_objs)
        job.preferred_skills.set(pref_objs)
        job.save()

    print(f"Total Jobs in DB: {Job.objects.count()}")
    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_skills_and_jobs()
