# Generated by Django 3.0 on 2019-12-28 08:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('financez', '0013_auto_20191228_0803'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='financez.Account'),
        ),
        migrations.AlterField(
            model_name='account',
            name='results',
            field=models.CharField(blank=True, choices=[('inc', 'incomes'), ('exp', 'expenses')], max_length=3, null=True),
        ),
    ]