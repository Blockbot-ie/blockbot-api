# Generated by Django 3.1.7 on 2021-04-20 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bb', '0004_user_strategy_pair_no_of_failed_attempts'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchange',
            name='sign_up_url',
            field=models.CharField(blank=True, max_length=1000, verbose_name='SignUp URL'),
        ),
    ]