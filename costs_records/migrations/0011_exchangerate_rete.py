# Generated by Django 4.2.7 on 2024-01-30 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('costs_records', '0010_alter_cost_invoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='exchangerate',
            name='rete',
            field=models.DecimalField(decimal_places=4, max_digits=5, null=True),
        ),
    ]
