# Generated by Django 3.2.4 on 2024-06-14 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friendrequest',
            name='status',
            field=models.IntegerField(choices=[(1, 'Requestd'), (2, 'Accepted'), (3, 'Rejected')], default=2),
        ),
    ]