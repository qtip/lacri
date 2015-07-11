# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Authority',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_enabled', models.BooleanField(default=True)),
                ('common_name', models.CharField(max_length=256)),
                ('slug', models.SlugField()),
                ('key', models.TextField(verbose_name=b'Private key', blank=True)),
                ('cert', models.TextField(verbose_name=b'Public certificate', blank=True)),
                ('usage', models.CharField(default=b'R', max_length=2, choices=[(b'R', b'Root CA'), (b'D', b'Domain'), (b'C', b'Client')])),
                ('parent', models.ForeignKey(blank=True, to='lacri.Authority', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Authority',
                'verbose_name_plural': 'Authorities',
            },
        ),
        migrations.AlterUniqueTogether(
            name='authority',
            unique_together=set([('user', 'slug'), ('user', 'common_name')]),
        ),
    ]
