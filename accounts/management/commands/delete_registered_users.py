from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Deletes registered user data from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Delete all users including superusers',
        )

    def handle(self, *args, **options):
        if options['all']:
            users = User.objects.all()
            user_type = "ALL"
        else:
            users = User.objects.filter(is_superuser=False)
            user_type = "non-superuser"

        count = users.count()
        if count == 0:
            self.stdout.write(self.style.WARNING("No registered users found to delete."))
            return

        users.delete()
        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {count} {user_type} registered user(s) and their associated data."))
