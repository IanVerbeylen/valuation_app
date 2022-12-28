import datetime

from django.db import models
from django.utils import timezone
from django.contrib import admin

# Create your models here.

# Portfolio
class Portfolio(models.Model):
    portfolio_name = models.CharField("portfolio", max_length=100)
    creation_date = models.DateTimeField("date created")

    def __str__(self):
        return self.portfolio_name

    @admin.display(
        boolean=True,
        ordering="creation_date",
        description="Created recently?",
    )
    def was_created_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.creation_date <= now


# Company
class Company(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    company_name = models.CharField("company name", max_length=100)
    company_valuation = models.IntegerField("company valuation", default=0)
    price_per_share = models.IntegerField("price per share", default=0)
    shares = models.IntegerField("number of shares", default=0)

    def __str__(self):
        return self.company_name
