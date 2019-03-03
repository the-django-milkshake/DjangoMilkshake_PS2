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
from django.conf import settings
import pandas as pd
import os
from code_app.machineLearningForStocks import do_ml
from code_app.MonteCarloForStocks import runMonteCarlo
from . import news

@login_required()
def stock(request, *args, **kwargs):
	abbr = kwargs['abbr']
	name = getStockNameFromTicker(abbr)
	current_price = getStockPrice(name)
	yesterday_price = getStockPrice(name, 1)
	percent = (current_price - yesterday_price)/current_price
	greater = True if current_price > yesterday_price else False

	confidence, count = do_ml(abbr)
	recommendation_val = max(count)
	if recommendation_val == 0:
		recommendation = "HOLD"
	elif recommendation_val == -1:
		recommendation = "SELL"
	else:
		recommendation = "BUY"

	profit, loss = runMonteCarlo(abbr)

	return render(request, 'stock.html', {'abbr':abbr, 'name':name, 'current_price': current_price, 'yesterday_price': yesterday_price, 
				 'greater': greater, 'percent':percent, 'recommendation': recommendation, 'profit':profit, 'loss':loss})


@login_required()
def newspage(request):
	stock_dataset = UserStock.objects.filter(user=request.user.id)

	newsfeed = []

	# for stock in stock_dataset:
	a = news.Analysis(stock_dataset[0].stock_name)
	newsfeed.extend(a.run())
		
	newslist = sorted(newsfeed, key=lambda article: article[1], reverse=True)
	return render(request, 'newspage.html', {'newslist':newslist})


@login_required()
def realEstate(request):
	return render(request, 'housing.html')


@login_required()
def search(request):
	if request.method == 'POST':
		try:
			data = request.POST.get('search')
			return redirect('stock', abbr=getStockTickerFromName(data))
		except Exception as e:
			print(e)
			pass
	return redirect('dash')


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
	a = news.Analysis('stocks')
	l = a.run()
	var = []
	for i in l[0:5]:
		var.append('https://www.google.com/search?q='+i[0]+'&source=lnms&tbm=nws')

	if request.user.is_authenticated:
		return render(request,'index.html',{'var':var,'new_list':l,'logged_in_user' : request.user.get_username()})
	else:
		return render(request,'index.html',{'var':var,'new_list':l,'logged_in_user' : False})


@login_required()
def dash(request):
	if request.method == 'POST':
		form = AddStockTransactionForm(request.POST)
		if form.is_valid():
			stock_name = form.cleaned_data.get('stock_name')
			number = form.cleaned_data.get('number')
			price = form.cleaned_data.get('price')
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

	newsfeed = []

	for stock in stock_dataset:
		a = news.Analysis(stock.stock_name)
		newsfeed.append(a.run())
		current = getStockPrice(stock.stock_name)
		if current >= stock.price:
			profit_bool = True
			diff = current - stock.price
		else:
			profit_bool = False
			diff = stock.price - current
		diff = diff/current * 100
		stock_data.append({'user': stock.user, 'stock_name': stock.stock_name,'ticker': getStockTickerFromName(stock.stock_name), 
						'price': stock.price, 'number': stock.number, 'current_price': current, 'profit_bool': profit_bool, 'diff': diff})

	newslist = sorted(newsfeed, key=lambda article: article[1], reverse=True)

	return render(request, 'dashboard.html', {'user_stock_data': stock_data, 'form': AddStockTransactionForm()})

"""			Helper functions   			"""

def getStockPrice(stock_name, past_days=0):
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
	price = df['adjusted_close'][past_days]
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