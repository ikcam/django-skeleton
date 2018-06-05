# Generated by Django 2.0.6 on 2018-06-02 01:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0001_initial'),
        ('account', '0001_initial'),
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='company',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='core.Company', verbose_name='Company'),
        ),
        migrations.AddField(
            model_name='notification',
            name='contenttype',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType', verbose_name='Content type'),
        ),
        migrations.AddField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AddField(
            model_name='colaborator',
            name='company',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='users_all', to='core.Company', verbose_name='Company'),
        ),
        migrations.AddField(
            model_name='colaborator',
            name='permissions',
            field=models.ManyToManyField(blank=True, to='auth.Permission', verbose_name='Permissions'),
        ),
        migrations.AddField(
            model_name='colaborator',
            name='roles',
            field=models.ManyToManyField(blank=True, to='core.Role', verbose_name='Roles'),
        ),
        migrations.AddField(
            model_name='colaborator',
            name='user',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
        migrations.AddField(
            model_name='user',
            name='companies',
            field=models.ManyToManyField(blank=True, related_name='_user_companies_+', through='account.Colaborator', to='core.Company', verbose_name='Companies'),
        ),
        migrations.AddField(
            model_name='user',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users_active', to='core.Company', verbose_name='Company'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='colaborator',
            unique_together={('user', 'company')},
        ),
    ]