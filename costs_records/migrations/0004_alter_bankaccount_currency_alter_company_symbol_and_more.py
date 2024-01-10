# Generated by Django 4.2.7 on 2023-12-26 14:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('costs_records', '0003_alter_invoice_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankaccount',
            name='currency',
            field=models.CharField(choices=[('EUR', 'EUR'), ('PLN', 'PLN'), ('USD', 'USD'), ('CZK', 'CZK'), ('RON', 'RON'), ('HUF', 'HUF')], default='PLN', max_length=3),
        ),
        migrations.AlterField(
            model_name='company',
            name='symbol',
            field=models.CharField(help_text='Symbol of the company, ex. NUT, SPX', max_length=10),
        ),
        migrations.AlterField(
            model_name='cost',
            name='invoice',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='invoice_cost', to='costs_records.invoice'),
        ),
        migrations.AlterField(
            model_name='cost',
            name='payment_date',
            field=models.DateField(blank=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='currency',
            field=models.CharField(choices=[('EUR', 'EUR'), ('PLN', 'PLN'), ('USD', 'USD'), ('CZK', 'CZK')], default='PLN', max_length=3),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='file',
            field=models.FileField(null=True, upload_to='invoices'),
        ),
    ]