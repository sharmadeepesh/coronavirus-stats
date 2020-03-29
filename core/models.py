from django.db import models

# Create your models here.
class Country(models.Model):
	name = models.CharField(max_length=50)
	slug = models.CharField(max_length=50)
	def __str__(self):
		return str(self.name)