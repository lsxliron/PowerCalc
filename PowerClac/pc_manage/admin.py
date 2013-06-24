from django.contrib import admin
from pc_manage.models import software, client, matlab_command
from django import forms
from custom_widgets import CustomPasswordInput

from django.db import models



class ClientAdmin(admin.ModelAdmin):
	fieldsets = [
	('User Information',     {'fields':['client_username', 'client_password',]}),
	('Client Information',   {'fields':['client_name', 'client_ip','client_port','client_os']}),
	]

	formfield_overrides = {models.CharField: {'widget':forms.PasswordInput}}
	#Convert to input password
	# def formfield_for_dbfield(self, db_field, **kwargs):
	# 	if db_field.name == 'client_password':
	# 		kwargs['widget'] = CustomPasswordInput
	# 	return super(ClientAdmin, self).formfield_for_dbfield(db_field,**kwargs)


	
class SoftwareAdmin(admin.ModelAdmin):
	fieldsets = [
	('Software Information', {'fields':['software_name','software_test','software_client']}),
	]


	#Enable filechooser
	formfield_overrides = {models.FilePathField: {'widget': forms.FileInput }}

	
	

	



class MatlabAdmin(admin.ModelAdmin):
	fieldsets = [
		('Matlab Command', {'fields':['command_keyword','m_file_path','output_path',
			'client_name', 'software_name']}),
	]




admin.site.register(software, SoftwareAdmin)
admin.site.register(client,ClientAdmin)
admin.site.register(matlab_command, MatlabAdmin)
