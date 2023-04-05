from django.db import models
from django.contrib.auth.models import User

''' O sistema utiliza o esquema de usuários do Django,  principalmente a tabela User
    A tabela UsuarioTEF é uma extensão de User, um-para-um, onde existe o relacionamento com a empresa a que ele 
    pertence e as suas permissões'''


class Empresa(models.Model):
    codEmp = models.IntegerField(primary_key=True)
    nomeEmp = models.CharField(max_length=50)
    CNPJ = models.CharField(max_length=14)
    ultimoNSU = models.IntegerField(default=0)
    URLServer = models.URLField(null=True)
    endMail = models.EmailField(null=True)
    passMail = models.CharField(max_length=30, null=True)



class Loja(models.Model):
    codLoja = models.IntegerField(primary_key=True)
    empresa = models.ForeignKey(
        Empresa, related_name="lojaemp", on_delete=models.CASCADE
    )
    nomeLoja = models.CharField(max_length=50)
    CNPJ = models.CharField(max_length=14)
    chave = models.BinaryField(max_length=150, null=True)



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
    LastLogin = models.DateTimeField(null=True) # data/hora do último login
    # Transações habilitadas para este PDV

    TransDigitado = models.BooleanField(default=False)
    TransVendaCreditoVista = models.BooleanField(default=False)
    TransVendaCreditoParc = models.BooleanField(default=False)
    TransVendaCreditoSemJuros = models.BooleanField(default=False)
    TransVendaDebito = models.BooleanField(default=False)
    TransCancelamento = models.BooleanField(default=False)


class PerfilUsuario(models.Model):
    codPerfil = models.IntegerField(primary_key=True)
    nomePerfil = models.CharField (max_length=20)


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
    nome_perfil = models.ForeignKey(
        PerfilUsuario, related_name="perfiluser", on_delete=models.CASCADE, null=True
    )

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


class LogTrans(models.Model):
    NSU_TEF = models.IntegerField(primary_key=True)
    dataLocal = models.DateField()
    horaLocal = models.TimeField()
    NSU_HOST = models.IntegerField()
    dataHoraHost = models.DateTimeField()
    codEmp = models.IntegerField()
    codLoja = models.IntegerField()
    codPDV = models.IntegerField()
    numLogico = models.CharField(max_length=20)
    codTRN = models.CharField(max_length=20)
    numParcelas = models.IntegerField(null=True)
    statusTRN = models.CharField(max_length=20)
    codResp = models.IntegerField()
    msgResp=models.CharField(max_length=50)
    numCartao = models.CharField(max_length=20)
    valorTrans = models.DecimalField(decimal_places=2, max_digits=10)
    nomeBan = models.CharField(max_length=50, null=True)
    nomeAdiq = models.CharField(max_length=50, null=True)
    NSU_ConfDesfCanc = models.IntegerField(null=True)
    dataHoraConfDesfCanc = models.DateTimeField(null=True)
    NSU_Canc = models.IntegerField(null=True)
    dataHoraCanc = models.DateTimeField(null=True)

    def __str__(self):
        return (
            f"({self.dataLocal:%Y-%m-%d})"
        )


class Monitoracao(models.Model):
    dataHora = models.DateTimeField()
    mensagem = models.CharField(max_length=2000)


