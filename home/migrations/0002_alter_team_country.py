# Generated by Django 4.0.1 on 2022-07-06 09:54

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='country',
            field=django_countries.fields.CountryField(max_length=2),
        ),
    ]
