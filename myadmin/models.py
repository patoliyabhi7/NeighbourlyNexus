from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Chairman(models.Model):
	gender = models.CharField(max_length=30)
	phone = models.BigIntegerField()
	reg_date = models.DateField()
	user = models.OneToOneField(User, on_delete=models.CASCADE)

	class Meta:
		db_table = 'chairman'