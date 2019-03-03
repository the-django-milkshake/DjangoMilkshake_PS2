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
import pandas as pd
import os
from django.conf import settings

@login_required()
def stock(request, *args, **kwargs):
	abbr = kwargs['abbr']
	name = getStockNameFromTicker(abbr)
	return render(request, 'stock.html', {'abbr':abbr, 'name':name})


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


@login_required()
def dash(request):
	if request.method == 'POST':
		form = AddStockTransactionForm(request.POST)
		if form.is_valid():
			stock_name = form.cleaned_data.get('stock_name')
			number = form.cleaned_data.get('number')
			price = getStockPrice(stock_name)
			trans = UserStocksTransaction.objects.create(user_id=request.user.id, stock_name=stock_name, number=number, price=price)
			try:
				userstock = UserStock.objects.get(user_id=request.user.id, stock_name=stock_name)
				userstock.price = (userstock.number * userstock.price + number * price)/(userstock.number + number)
				userstock.number += number
				userstock.save()
			except UserStock.DoesNotExist:
				UserStock.objects.create(user_id=request.user.id, stock_name=stock_name, number=number, price=price)

	stock_dataset = UserStock.objects.filter(user=request.user.id)
	stock_data = []
	for stock in stock_dataset:
		current = getStockPrice(stock.stock_name)
		if current >= stock.price:
			profit_bool = True
			diff = current - stock.price
		else:
			profit_bool = False
			diff = stock.price - current
		diff = diff/current * 100
		stock_data.append({'user': stock.user, 'stock_name': stock.stock_name,'ticker': getStockTickerFromName(stock.stock_name), 'price': stock.price, 'number': stock.number, 'current_price': current, 'profit_bool': profit_bool, 'diff': diff})
	return render(request, 'dashboard.html', {'user_stock_data': stock_data, 'form': AddStockTransactionForm()})

"""			Helper functions   			"""

def getStockPrice(stock_name):
	df = pd.read_csv(os.path.join(settings.BASE_DIR, 'code_app/sp500tickersandnames.csv'))
	i = 0
	for name in df['Names']:
		if name == stock_name:
			n = df['Tickers'][i]
			break
		i += 1
	filename=os.path.join(settings.BASE_DIR,'code_app/{}csv.csv'.format(n))
	if os.path.exists(filename):
		df = pd.read_csv(filename)
	else:
		API_URL = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={}&datatype=csv&apikey=CAEP52JD28UXF203".format(n)
		response = requests.get(API_URL)
		dfx = response.text
		f = open(filename, 'w')
		f.write(dfx)
		f.close()
		df = pd.read_csv(filename)
	price = df['adjusted_close'][0]
	return price


def getStockTickerFromName(stock_name):
	df = pd.read_csv(os.path.join(settings.BASE_DIR, 'code_app/sp500tickersandnames.csv'))
	i = 0
	for name in df['Names']:
		if name == stock_name:
			n = df['Tickers'][i]
			return n
		i += 1
	return None


def getStockNameFromTicker(stock_ticker):
	df = pd.read_csv(os.path.join(settings.BASE_DIR, 'code_app/sp500tickersandnames.csv'))
	i = 0
	for ticker in df['Tickers']:
		if ticker == stock_ticker:
			n = df['Names'][i]
			return n
		i += 1
	return None


# def alphavantage_api(request):
#  	user2=requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=MSFT&apikey=CAEP52JD28UXF203", verify=False)
#  	rep1 = user2.json()
#  	return render (request,'alphavantage.html',context = {'rep1':rep1})


# def worlddata_api(request):
#  	user1=requests.get("https://www.worldtradingdata.com/api/v1/stock?symbol=AAPL,MSFT,HSBA.L&api_token=gQyyyasOQgy3oooDiOjWGSWxoSFmTXCUnq0ulQD9YAp44FeuznQVFG722kGh", verify=False)
#  	rep = user1.json()
#  	return render (request,'worlddata.html',context = {'rep':rep})