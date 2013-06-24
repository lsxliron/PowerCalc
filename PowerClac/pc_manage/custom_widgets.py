from django import forms
from string import Template
from django.utils.safestring import mark_safe

class CustomPasswordInput (forms.TextInput):
	def render(self, name, value, attrs=None):
		tpl = Template(u'''<input type="password" style="width:220px;/>"''')
		return mark_safe(tpl.substitute(client_password = value))