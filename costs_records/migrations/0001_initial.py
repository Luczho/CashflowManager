# Generated by Django 4.2.7 on 2023-12-12 22:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(help_text='symbol of the company', max_length=10)),
                ('name', models.CharField(max_length=100)),
                ('vat_eu', models.CharField(max_length=20)),
                ('is_contractor', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('currency', models.CharField(max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('number', models.CharField(max_length=50)),
                ('proforma', models.BooleanField(default=False)),
                ('due_date', models.DateField()),
                ('currency', models.CharField(choices=[('EUR', 'Euro'), ('PLN', 'Zloty'), ('USD', 'Dolar'), ('CZK', 'Korona')], default='PLN', max_length=3)),
                ('gross_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('net_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pln_net_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pln_gross_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('vat_rate', models.IntegerField()),
                ('file', models.FilePathField()),
                ('printed', models.BooleanField(default=False)),
                ('in_optima', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Cost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(help_text='unique id of the cost id_created_date_company_symbol ex. 1_2020-01-01_NUT', max_length=50)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('cost_description', models.TextField()),
                ('paid', models.BooleanField(default=False)),
                ('payment_date', models.DateField()),
                ('asap', models.BooleanField(default=False)),
                ('urgent', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='customer_costs', to='costs_records.company')),
                ('invoice', models.OneToOneField(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='costs_records.invoice')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='supplier_costs', to='costs_records.company')),
            ],
        ),
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name', models.CharField(max_length=50)),
                ('currency', models.CharField(choices=[('EUR', 'Euro'), ('PLN', 'Zloty'), ('USD', 'Dolar'), ('CZK', 'Korona'), ('RON', 'Lej'), ('HUF', 'Forint')], default='PLN', max_length=3)),
                ('country_code', models.CharField(max_length=20)),
                ('account_number', models.CharField(max_length=30)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='costs_records.company')),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_name', models.CharField(max_length=50)),
                ('building_number', models.CharField(max_length=20)),
                ('postal_code', models.CharField(max_length=10)),
                ('city', models.CharField(max_length=30)),
                ('company', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='costs_records.company')),
            ],
        ),
    ]
