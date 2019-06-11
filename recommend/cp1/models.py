from django.db import models

# Create your models here.
class flightInfo(models.Model):
	flight_no = models.CharField(max_length=10)
	dep_time = models.TimeField()
	dep_loc = models.CharField(max_length = 31)
	arr_time = models.TimeField()
	arr_loc = models.CharField(max_length = 31)
	flight_schedule = models.CharField(max_length = 20)
	norm_price = models.IntegerField()
	dur_time = models.TimeField()