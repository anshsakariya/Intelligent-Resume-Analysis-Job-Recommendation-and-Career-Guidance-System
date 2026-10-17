from config.wsgi import application
from django.core.management import call_command
from django.db import connection

try:
    # Ensure database tables exist so registration/login never throws 500 error on Vercel
    tables = connection.introspection.table_names()
    if 'auth_user' not in tables:
        call_command('migrate', interactive=False)
    
    # Auto-seed jobs and skills so recommendations are always available
    from jobs.models import Job
    if not Job.objects.exists():
        from utils.seed_db import seed_skills_and_jobs
        seed_skills_and_jobs()
    else:
        # Automatically clean up duplicate jobs if any exist
        from collections import defaultdict
        job_groups = defaultdict(list)
        for j in Job.objects.all().order_by('id'):
            job_groups[(j.title.lower().strip(), j.company.lower().strip())].append(j)
        for group in job_groups.values():
            if len(group) > 1:
                for duplicate_job in group[1:]:
                    duplicate_job.delete()
except Exception as e:
    print(f"Database auto-migration/seed info: {e}")

app = application
