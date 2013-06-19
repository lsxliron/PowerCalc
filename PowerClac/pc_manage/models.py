from django.db import models

# Create your models here.

class softwares(models.Model):
	software_name = models.CharField(max_length=50)
	matlab_path = models.CharField(max_length=100)
	remote_password = models.CharField(max_length=50)
	remote_username = models.CharField(max_length=50)
	remote_ip = models.CharField(max_length=50)
	remote_port = models.IntegerField(default=80)

class clients(models.Model):
	client_ip = models.CharField(max_length=50)
