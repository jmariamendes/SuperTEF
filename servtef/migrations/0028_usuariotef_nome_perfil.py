# Generated by Django 4.1.1 on 2022-11-16 19:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('servtef', '0027_perfilusuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuariotef',
            name='nome_perfil',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='perfiluser', to='servtef.perfilusuario'),
        ),
    ]
