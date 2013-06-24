from django.shortcuts import render_to_response, render
from django.core.context_processors import csrf
from django.template import RequestContext

def index(request):
	c={}
	c.update(csrf(request))
	return render_to_response ("config.html",c,RequestContext(request))
