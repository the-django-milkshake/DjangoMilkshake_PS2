import requests
import json
import operator
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from .models import *
from .forms import *
from django.contrib.auth import authenticate , login
from django.contrib.auth.decorators import login_required

def alphavantage_api(request):
 	user2=requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=MSFT&apikey=CAEP52JD28UXF203", verify=False)
 	rep1 = user2.json()
 	return render (request,'alphavantage.html',context = {'rep1':rep1})


def worlddata_api(request):
 	user1=requests.get("https://www.worldtradingdata.com/api/v1/stock?symbol=AAPL,MSFT,HSBA.L&api_token=gQyyyasOQgy3oooDiOjWGSWxoSFmTXCUnq0ulQD9YAp44FeuznQVFG722kGh", verify=False)
 	rep = user1.json()
 	return render (request,'worlddata.html',context = {'rep':rep})


def signup(request):
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)
			return redirect('dash')
			
	else:
		form = SignupForm()

	if request.user.is_authenticated:
		return render(request, 'signup.html', {'form': form, 'logged_in_user': True, 'username': request.user.get_username()})
	else:
		return render(request, 'signup.html', {'form': form, 'logged_in_user': False})


def home(request):
	if request.user.is_authenticated:
		return render(request,'index.html', {'logged_in_user': request.user.get_username()})
	else:
		return render(request,'index.html', {'logged_in_user': False})


@login_required(login_url='/')
def dash(request):
	return render(request, 'dashboard.html')