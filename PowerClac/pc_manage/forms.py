from django import forms
from django.contrib import admin
from django.forms.widgets import PasswordInput
from pc_manage.models import software, client, matlab_command

class TestForm(forms.ModelForm):
	#class Meta:
	#	model = client
	
	def __init__(self, *args, **kwargs):
		super(TestForm, self).__init__(*args, **kwargs)
		self.fields['user_password'] = froms.CharField(label='1234')