# Generated by Django 3.1.4 on 2020-12-19 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='detail',
            field=models.CharField(default='random', max_length=400),
        ),
    ]
