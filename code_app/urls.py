from django.conf.urls import url,include
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    url(r'^world',views.worlddata_api,name="world"),
    url(r'^alpha',views.alphavantage_api,name="alpha"),
    url(r'^dashboard', views.dash, name="dash"),
    url(r'^signup',views.signup ,name = "signup"),
    url(r'^login',auth_views.LoginView.as_view(),name = "login"),
    url(r'^logout', auth_views.LogoutView.as_view(), name="logout"),
    url(r'^$',views.home,name="home"),
]
