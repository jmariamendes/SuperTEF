# Generated by Django 4.1.1 on 2022-12-08 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servtef', '0029_empresa_urlserver_loja_chave'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loja',
            name='chave',
            field=models.BinaryField(max_length=150, null=True),
        ),
    ]
