# Generated by Django 3.1.4 on 2020-12-09 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer_portal', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rental_service',
            name='d_date',
            field=models.DateField(default='2000-01-01'),
            preserve_default=False,
        ),
    ]
