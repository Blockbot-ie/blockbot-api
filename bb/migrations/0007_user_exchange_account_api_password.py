# Generated by Django 3.1.7 on 2021-03-08 07:23

from django.db import migrations, models
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ('bb', '0006_auto_20210303_0658'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_exchange_account',
            name='api_password',
            field=django_cryptography.fields.encrypt(models.CharField(blank=True, max_length=255, verbose_name='API Password')),
        ),
    ]
