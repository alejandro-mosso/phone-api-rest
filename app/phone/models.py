from django.db import models

# Create your models here.
# After adding new model run in command line:
#   python3 manage.py makemigrations
#   python3 manage.py migrate
#   python3 manage.py runserver 0.0.0.0:9000


class FileUpload(models.Model):
    numbers = models.FileField(blank=False, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)
