from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Event(models.Model):
	title = models.CharField(max_length=50)
	description = models.TextField()
	image = models.TextField()
	from_date = models.DateField()
	to_date = models.DateField()
	price = models.BigIntegerField()

	class Meta:
		db_table = 'event'

class Meeting(models.Model):
	subject = models.CharField(max_length=50)
	venue = models.CharField(max_length=50)
	date = models.DateField()
	time = models.TimeField()

	class Meta:
		db_table = 'meeting'

class Maintenance(models.Model):
	year = models.CharField(max_length=50)
	description = models.TextField()
	from_date = models.DateField()
	to_date = models.DateField()
	amount = models.BigIntegerField()

	class Meta:
		db_table = 'maintenance'

class Snotice(models.Model):
	title = models.CharField(max_length=50)
	description = models.TextField()
	datetime = models.DateTimeField()

	class Meta:
		db_table = 'snotice'