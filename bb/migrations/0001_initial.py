# Generated by Django 3.1.7 on 2022-10-21 19:15

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_cryptography.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, unique=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('user_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_connected', models.BooleanField(default=False, verbose_name='Connected')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'db_table': 'bb_user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Exchange',
            fields=[
                ('exchange_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=150, verbose_name='Exchange Name')),
                ('display_name', models.CharField(blank=True, max_length=150, verbose_name='Display Name')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_on')),
                ('sign_up_url', models.CharField(blank=True, max_length=1000, verbose_name='SignUp URL')),
            ],
        ),
        migrations.CreateModel(
            name='Pairs',
            fields=[
                ('pair_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('symbol', models.CharField(blank=True, max_length=50, verbose_name='Symbol')),
                ('ticker_1', models.CharField(blank=True, max_length=50, verbose_name='Ticker 1')),
                ('ticker_2', models.CharField(blank=True, max_length=50, verbose_name='Ticker 2')),
                ('ticker_1_min_value', models.FloatField(blank=True, null=True, verbose_name='Ticker 1 Min Value')),
                ('ticker_2_min_value', models.FloatField(blank=True, null=True, verbose_name='Ticker 2 Min Value')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_on')),
            ],
        ),
        migrations.CreateModel(
            name='Strategy',
            fields=[
                ('strategy_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=150, verbose_name='Strategy Name')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_on')),
            ],
        ),
        migrations.CreateModel(
            name='User_Exchange_Account',
            fields=[
                ('user_exchange_account_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=255, verbose_name='Exchange Account Name')),
                ('api_key', django_cryptography.fields.encrypt(models.CharField(blank=True, max_length=255, verbose_name='API Key'))),
                ('api_secret', django_cryptography.fields.encrypt(models.CharField(blank=True, max_length=255, verbose_name='API Secret'))),
                ('api_password', django_cryptography.fields.encrypt(models.CharField(blank=True, max_length=255, verbose_name='API Password'))),
                ('sub_account_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Sub-account Name')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('modified_on', models.DateTimeField(default=django.utils.timezone.now, verbose_name='modified_on')),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_on')),
                ('exchange', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bb.exchange')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='User_Strategy_Pair',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('pair', models.CharField(blank=True, max_length=50, verbose_name='Pair')),
                ('initial_first_symbol_balance', models.FloatField(blank=True, null=True, verbose_name='Initial First Symbol Balance')),
                ('initial_second_symbol_balance', models.FloatField(blank=True, null=True, verbose_name='Initial Second Symbol Balance')),
                ('current_currency', models.CharField(blank=True, max_length=50, verbose_name='Current Currency')),
                ('current_currency_balance', models.FloatField(blank=True, null=True, verbose_name='Current Currency Balance')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('modified_on', models.DateTimeField(default=django.utils.timezone.now, verbose_name='modified_on')),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_on')),
                ('no_of_failed_attempts', models.IntegerField(default=0, verbose_name='Number of Failed Attempts')),
                ('strategy', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bb.strategy')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('user_exchange_account', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bb.user_exchange_account')),
            ],
        ),
        migrations.CreateModel(
            name='UserStory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stage', models.IntegerField(default=1, verbose_name='Story Stage')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='User_Strategy_Pair_Daily_Balance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.FloatField(default=0, verbose_name='Pair Price')),
                ('hodl_value', models.FloatField(default=0, verbose_name='HODL Value')),
                ('strategy_value', models.FloatField(default=0, verbose_name='Strategy Value')),
                ('is_top_up', models.BooleanField(default=False, verbose_name='active')),
                ('created_on', models.DateField(default=django.utils.timezone.now, verbose_name='created_on')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('user_strategy_pair', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bb.user_strategy_pair')),
            ],
        ),
        migrations.CreateModel(
            name='Strategy_Supported_Pairs',
            fields=[
                ('strategy_pair_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_on')),
                ('pair', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bb.pairs')),
                ('strategy', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bb.strategy')),
            ],
        ),
        migrations.CreateModel(
            name='Strategies_Suggested',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time_utc', models.DateTimeField(verbose_name='start_time_utc')),
                ('target_currency', models.CharField(blank=True, max_length=50, verbose_name='Target Currency')),
                ('tick', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='Tick')),
                ('pair', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bb.strategy_supported_pairs')),
            ],
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('order_id', models.CharField(editable=False, max_length=50, primary_key=True, serialize=False)),
                ('market', models.CharField(blank=True, max_length=50, verbose_name='Market')),
                ('side', models.CharField(blank=True, max_length=50, verbose_name='Side')),
                ('size', models.FloatField(default=0, verbose_name='Order Size')),
                ('size_symbol', models.CharField(blank=True, max_length=50, verbose_name='Size Symbol')),
                ('filled', models.FloatField(default=0, verbose_name='Filled')),
                ('filled_price', models.FloatField(default=0, verbose_name='Filled Price')),
                ('fee', models.FloatField(default=0, verbose_name='Fee')),
                ('status', models.CharField(blank=True, max_length=50, verbose_name='Status')),
                ('amount', models.FloatField(default=0, verbose_name='Amount')),
                ('modified_on', models.DateTimeField(default=django.utils.timezone.now, verbose_name='modified_on')),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created_on')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('user_strategy_pair', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bb.user_strategy_pair')),
            ],
        ),
        migrations.CreateModel(
            name='Exchange_Supported_Pairs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exchange', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bb.exchange')),
                ('pair', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bb.pairs')),
            ],
        ),
    ]
