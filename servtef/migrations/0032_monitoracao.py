# Generated by Django 4.1.1 on 2023-04-05 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servtef', '0031_empresa_endmail_empresa_passmail'),
    ]

    operations = [
        migrations.CreateModel(
            name='Monitoracao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataHora', models.DateTimeField()),
                ('mensagem', models.CharField(max_length=2000)),
            ],
        ),
    ]
