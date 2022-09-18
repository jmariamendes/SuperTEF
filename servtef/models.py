from django.db import models
from django.contrib.auth.models import User

''' O sistema utiliza o esquema de usuários do Django,  principalmente a tabela User
    A tabela UsuarioTEF é uma extensão de User, um-para-um, onde existe o relacionamento com a empresa a que ele 
    pertence e as suas permissões'''


class Empresa(models.Model):
    codEmp = models.IntegerField(primary_key=True)
    nomeEmp = models.CharField(max_length=50)
    CNPJ = models.CharField(max_length=14)


class Loja(models.Model):
    codLoja = models.IntegerField(primary_key=True)
    empresa = models.ForeignKey(
        Empresa, related_name="lojaemp", on_delete=models.CASCADE
    )
    nomeLoja = models.CharField(max_length=50)
    CNPJ = models.CharField(max_length=14)


class PDV(models.Model):
    codPDV = models.IntegerField()
    loja = models.ForeignKey(
        Loja, related_name="pdvloja", on_delete=models.CASCADE
    )
    empresa = models.ForeignKey(
        Empresa, related_name="pdvemp", on_delete=models.CASCADE
    )
    UsuarioAtivo = models.IntegerField(null=True)  # Usuario logado no PDV no momento
    StatusPDV = models.BooleanField(default=False)  # inicializado/ativo/inativo

    # Transações habilitadas para este PDV

    TransVendaCreditoVista = models.BooleanField(default=False)
    TransVendaCreditoParc = models.BooleanField(default=False)
    TransVendaCreditoSemJuros = models.BooleanField(default=False)
    TransVendaDebito = models.BooleanField(default=False)
    TransCancelamento = models.BooleanField(default=False)


class UsuarioTEF(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    empresa = models.ForeignKey(
        Empresa, related_name="useremp", on_delete=models.CASCADE
    )
    loja = models.ForeignKey(
        Loja, related_name="userloja", on_delete=models.CASCADE
    )

    ''' Perfil do usuário 
            ('1', 'Admin'), ('2', 'Corporativo'), ('3', 'Loja'), ('4', 'PDV')]'''

    perfil_user = models.IntegerField()

    def __str__(self):
        return self.user.username


class Bandeira(models.Model):
    codBan = models.IntegerField()
    nomeBan = models.CharField(max_length=50)

    # Adquirentes = models.ManyToManyField(Adquirente)

    def __str__(self):
        return self.nomeBan


class Adquirente(models.Model):
    codAdiq = models.IntegerField()
    nomeAdiq = models.CharField(max_length=50)
    bandeiras = models.ManyToManyField(Bandeira)

    def __str__(self):
        return self.nomeAdiq


class NumLogico(models.Model):
    empresa = models.ForeignKey(
        Empresa, related_name="logemp", on_delete=models.CASCADE
    )
    loja = models.ForeignKey(
        Loja, related_name="logloja", on_delete=models.CASCADE
    )
    adiq = models.ForeignKey(
        Adquirente, related_name="logadiq", on_delete=models.CASCADE
    )
    numlogico = models.CharField(max_length=20)


class Roteamento(models.Model):
    empresa = models.ForeignKey(
        Empresa, related_name="rotemp", on_delete=models.CASCADE
    )
    loja = models.ForeignKey(
        Loja, related_name="rotloja", on_delete=models.CASCADE
    )
    bandeira = models.ForeignKey(
        Bandeira, related_name="rotban", on_delete=models.CASCADE
    )
    adiq = models.ForeignKey(
        Adquirente, related_name="rotadiq", on_delete=models.CASCADE
    )
    adiq2 = models.ForeignKey(
        Adquirente, related_name="rotadiq2", on_delete=models.CASCADE
    )

