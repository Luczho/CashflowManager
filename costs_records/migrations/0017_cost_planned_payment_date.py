# Generated by Django 4.2.7 on 2024-02-17 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costs_records', '0016_alter_invoice_days_to_due_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='cost',
            name='planned_payment_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]