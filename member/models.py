from django.db import models
from django.contrib.auth.models import User
from myadmin.models import *
from chairman.models import *


# Create your models here.

class Member(models.Model):
	gender = models.CharField(max_length=30)
	phone = models.BigIntegerField()
	house_no = models.CharField(max_length=100)
	total_members= models.CharField(max_length=10)
	reg_date = models.DateField()
	user = models.OneToOneField(User, on_delete=models.CASCADE)

	class Meta:
		db_table = 'Member'

class Complain(models.Model):
	subject = models.CharField(max_length=30)
	description = models.TextField()
	date_time = models.DateTimeField()
	member = models.ForeignKey(Member, on_delete=models.CASCADE)

	class Meta:
		db_table = 'complain'

class Maintenance_Payment(models.Model):
	order_id = models.TextField()
	payment_id = models.TextField()
	signature = models.TextField()
	date_time = models.DateTimeField()
	date = models.DateField()
	member = models.ForeignKey(Member, on_delete=models.CASCADE)
	maintenance = models.ForeignKey(Maintenance, on_delete=models.CASCADE)

	class Meta:
		db_table = 'maintenance_payment'

class Event_Payment(models.Model):
	order_id = models.TextField()
	payment_id = models.TextField()
	signature = models.TextField()
	date_time = models.DateTimeField()
	date = models.DateField()
	member = models.ForeignKey(Member, on_delete=models.CASCADE)
	event = models.ForeignKey(Event, on_delete=models.CASCADE)

	class Meta:
		db_table = 'event_payment'