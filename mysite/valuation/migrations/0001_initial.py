# Generated by Django 4.1.4 on 2022-12-27 18:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Portfolio",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "portfolio_name",
                    models.CharField(max_length=100, verbose_name="portfolio"),
                ),
                ("creation_date", models.DateTimeField(verbose_name="date created")),
            ],
        ),
        migrations.CreateModel(
            name="Company",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "company_name",
                    models.CharField(max_length=100, verbose_name="company name"),
                ),
                (
                    "company_valuation",
                    models.IntegerField(default=0, verbose_name="company valuation"),
                ),
                (
                    "price_per_share",
                    models.IntegerField(default=0, verbose_name="price per share"),
                ),
                (
                    "portfolio",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="valuation.portfolio",
                    ),
                ),
            ],
        ),
    ]