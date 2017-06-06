# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-06 15:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('date_modification', models.DateTimeField(auto_now=True, verbose_name='Modification date')),
                ('is_active', models.BooleanField(default=True, editable=False, verbose_name='Active')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Name')),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='companies', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Company',
                'verbose_name_plural': 'Companies',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Invite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Creation date')),
                ('date_modification', models.DateTimeField(auto_now=True, verbose_name='Modification date')),
                ('is_active', models.BooleanField(default=True, editable=False, verbose_name='Active')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('date_sent', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='Sent date')),
                ('activation_key', models.CharField(blank=True, editable=False, max_length=255, null=True, verbose_name='Activation key')),
                ('company', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='invites', to='core.Company', verbose_name='Company')),
                ('user', models.OneToOneField(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invite', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Invite',
                'verbose_name_plural': 'Invites',
                'ordering': ['-date_creation'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='invite',
            unique_together=set([('company', 'email')]),
        ),
    ]
