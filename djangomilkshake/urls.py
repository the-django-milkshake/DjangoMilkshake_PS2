
from django.contrib import admin
from django.urls import path,include
from django.views.generic.base import TemplateView
from code_app import views
urlpatterns = [
    #path('',views.fun),
    path('admin/', admin.site.urls),
    path('',include('code_app.urls')),
]
