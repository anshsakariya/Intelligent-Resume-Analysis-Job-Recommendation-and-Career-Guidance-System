import os
import sys
import django

# Configure UTF-8 encoding for Windows terminal
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

def clear_all_registered_users(keep_superusers=True):
    """
    Deletes registered user data from the database.
    By default, preserves superusers/admins unless specified otherwise.
    """
    if keep_superusers:
        users_to_delete = User.objects.filter(is_superuser=False)
    else:
        users_to_delete = User.objects.all()

    count = users_to_delete.count()
    if count == 0:
        print("[INFO] No registered user data found to delete.")
        return

    print(f"[WARNING] Found {count} registered user(s) to delete.")
    users_to_delete.delete()
    print(f"[SUCCESS] Successfully deleted {count} registered user(s) and all associated profiles/data!")

if __name__ == '__main__':
    keep = True
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        keep = False
    
    print("--- Clearing Registration Data ---")
    clear_all_registered_users(keep_superusers=keep)
