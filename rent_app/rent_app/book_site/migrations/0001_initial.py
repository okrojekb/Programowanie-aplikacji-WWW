# Generated by Django 5.1.4 on 2024-12-15 23:19

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
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
                ("title", models.CharField(max_length=127)),
                ("author", models.CharField(max_length=31)),
                ("available", models.BooleanField()),
                ("pub_date", models.DateField()),
                ("date_added", models.DateField(auto_now_add=True)),
            ],
        ),
    ]
