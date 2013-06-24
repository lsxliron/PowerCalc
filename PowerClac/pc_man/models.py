from django.db import models

#from filebrowser.fields import FileBrowseField
# Create your models here.

OS_CHOCIES = (
	('UNIX','Unix'),
	('WINDOWS','Windows'),
	)

SW_CHOICES = (
	('MATLAB','Matlab'),
	('TEST','Test'),
	)
	


class client(models.Model):
	client_name = models.CharField(max_length=50)
	client_password = models.CharField(max_length=50)
	client_username = models.CharField(max_length=50)
	client_ip = models.CharField(max_length=50)
	client_port = models.IntegerField(default=80)
	client_os = models.CharField(max_length=8,choices =  OS_CHOCIES)
	
    

	def save(self, *args, **kwargs):
		print "OVERWRITE!!!!!!"
		super(client, self).save(*args, **kwargs)

class software(models.Model):
	software_path = models.CharField(max_length=100)
	software_client = models.ForeignKey(client)
	software_name = models.CharField(max_length=10, choices = SW_CHOICES)
	software_test = models.FilePathField(path="/")


class matlab_command(models.Model):
	command_keyword = models.CharField(max_length=50)
	m_file_path = models.CharField(max_length=50)
	output_path = models.CharField(max_length=50)
	client_name = models.ForeignKey(client)
	software_name = models.ForeignKey(software)
