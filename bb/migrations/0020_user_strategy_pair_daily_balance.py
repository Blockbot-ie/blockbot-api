# Generated by Django 3.1.7 on 2021-04-10 11:35

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bb', '0019_auto_20210327_2109'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_Strategy_Pair_Daily_Balance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker_1_balance', models.FloatField(default=0, verbose_name='Ticker 1 Balance')),
                ('ticker_2_balance', models.FloatField(default=0, verbose_name='Ticker 2 Balance')),
                ('is_top_up', models.BooleanField(default=False, verbose_name='active')),
                ('created_on', models.DateField(default=django.utils.timezone.now, verbose_name='created_on')),
                ('user_strategy_pair', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bb.user_strategy_pair')),
            ],
        ),
    ]
