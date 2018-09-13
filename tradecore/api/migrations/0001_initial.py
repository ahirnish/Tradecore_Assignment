# Generated by Django 2.0.3 on 2018-09-13 12:03

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
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(help_text='content of the post', max_length=255)),
                ('likes', models.IntegerField(default=0, help_text='number of likes')),
                ('unlikes', models.IntegerField(default=0, help_text='number of unlikes')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(help_text='author of the post', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Preference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.BooleanField(help_text='1 for like, 0 for unlike')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('post', models.ForeignKey(help_text='post whose preference to be set', on_delete=django.db.models.deletion.CASCADE, to='api.Post')),
                ('user', models.ForeignKey(help_text='user whose preference to be set', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(blank=True, help_text='location of user', max_length=100, null=True)),
                ('bio', models.CharField(blank=True, help_text='brief description about user', max_length=255, null=True)),
                ('site', models.CharField(blank=True, help_text='website of user', max_length=100, null=True)),
                ('timezone', models.CharField(blank=True, help_text='time zone of user', max_length=100, null=True)),
                ('utc_offset', models.IntegerField(blank=True, help_text='difference in hours from UTC timezone', null=True)),
                ('company_name', models.CharField(blank=True, help_text='name of the company of user', max_length=100, null=True)),
                ('company_role', models.CharField(blank=True, help_text='role of user in the company', max_length=100, null=True)),
                ('facebook_handle', models.CharField(blank=True, help_text='facebook handle of user', max_length=100, null=True)),
                ('twitter_handle', models.CharField(blank=True, help_text='twitter handle of user', max_length=100, null=True)),
                ('github_handle', models.CharField(blank=True, help_text='github handle of user', max_length=100, null=True)),
                ('linkedin_handle', models.CharField(blank=True, help_text='linkedin handle of user', max_length=100, null=True)),
                ('googleplus_handle', models.CharField(blank=True, help_text='googleplus handle of user', max_length=100, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='preference',
            unique_together={('post', 'user')},
        ),
    ]
