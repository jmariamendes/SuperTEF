# Generated by Django 4.1.1 on 2022-10-20 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servtef', '0021_alter_empresa_ultimonsu'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogTrans',
            fields=[
                ('NSU_TEF', models.IntegerField(primary_key=True, serialize=False)),
                ('dataLocal', models.DateField()),
                ('horaLocal', models.TimeField()),
                ('NSU_HOST', models.IntegerField()),
                ('dataHoraHost', models.DateTimeField()),
                ('codEmp', models.IntegerField()),
                ('codLoja', models.IntegerField()),
                ('codPDV', models.IntegerField()),
                ('numLogico', models.CharField(max_length=20)),
                ('codTRN', models.CharField(max_length=20)),
                ('statusTRN', models.CharField(max_length=20)),
                ('codResp', models.IntegerField()),
                ('msgResp', models.CharField(max_length=50)),
                ('numCartao', models.CharField(max_length=20)),
                ('valorTrans', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
    ]
