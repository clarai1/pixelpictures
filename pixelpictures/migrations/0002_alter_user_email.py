# Generated by Django 4.1.4 on 2023-02-12 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pixelpictures", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
