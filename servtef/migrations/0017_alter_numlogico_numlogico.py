# Generated by Django 4.0.4 on 2022-09-15 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servtef', '0016_numlogico'),
    ]

    operations = [
        migrations.AlterField(
            model_name='numlogico',
            name='numlogico',
            field=models.CharField(max_length=20),
        ),
    ]
