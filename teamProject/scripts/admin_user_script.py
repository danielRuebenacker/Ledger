from django.contrib.auth.models import User
from ledger.models import UserProfile

# THIS IS FOR TEST PURPOSES ONLY
# TO RUN: python manage.py shell < scripts/adminUserScript.py

admin, _ = User.objects.get_or_create(username="admin")
profile, _ = UserProfile.objects.get_or_create(user=admin)

admin.set_password('admin')
admin.is_superuser = True
admin.is_staff = True
admin.save()
