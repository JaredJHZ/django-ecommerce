# Generated by Django 3.0.5 on 2020-05-09 05:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20200509_0522'),
    ]

    operations = [
        migrations.RenameField(
            model_name='billingaddress',
            old_name='street_adress',
            new_name='street_address',
        ),
    ]