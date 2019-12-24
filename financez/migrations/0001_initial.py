# Generated by Django 3.0 on 2019-12-23 13:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('code', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('total', models.FloatField(default=0.0)),
                ('comment', models.CharField(max_length=1024)),
                ('acc_cr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='acc_cr', to='financez.Account')),
                ('acc_dr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='acc_dr', to='financez.Account')),
                ('curency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='financez.Currency')),
            ],
        ),
    ]