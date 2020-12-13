# Generated by Django 3.1.4 on 2020-12-13 04:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer_portal', '0002_rental_service_d_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rental_History',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('p_date', models.DateField()),
                ('d_date', models.DateField()),
                ('s_odometer', models.FloatField()),
                ('e_odometer', models.FloatField()),
                ('d_odometer_limit', models.FloatField()),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='customer_portal.customer')),
                ('d_location', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='his_d_loaction', to='customer_portal.location')),
                ('invoice', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='customer_portal.invoice')),
                ('p_location', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='his_p_loaction', to='customer_portal.location')),
                ('payment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='customer_portal.payment')),
                ('vin', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='customer_portal.vehicle')),
            ],
        ),
    ]