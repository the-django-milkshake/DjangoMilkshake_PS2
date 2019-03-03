from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.models import TimeStampedModel
import datetime
from django.utils import timezone


class UserStock(TimeStampedModel):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	stock_name = models.CharField(max_length=100)
	price = models.FloatField(default=0)
	number = models.IntegerField(default=0)

class UserStocksTransaction(TimeStampedModel):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	stock_name = models.CharField(max_length=100)
	price = models.FloatField(default=0)
	number = models.IntegerField(default=0)