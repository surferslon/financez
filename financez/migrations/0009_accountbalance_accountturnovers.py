# Generated by Django 3.0 on 2019-12-26 15:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('financez', '0008_auto_20191225_1424'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountTurnovers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('dr_total', models.FloatField(default=0.0)),
                ('cr_total', models.FloatField(default=0.0)),
                ('acc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='financez.Account')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='financez.Currency')),
            ],
        ),
        migrations.CreateModel(
            name='AccountBalance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('total', models.FloatField(default=0.0)),
                ('acc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='financez.Account')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='financez.Currency')),
            ],
        ),
    ]
