from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import User

from .models import Bandeira, Adquirente


class CodigoForm(forms.Form):

    codigo = forms.IntegerField(required=True)


class NomeLojaForm(forms.Form):

    codLoja = forms.ChoiceField(label='Loja',
                                widget=forms.Select)


class RoteamentoForm(forms.Form):

    codBan = forms.MultipleChoiceField(label='Bandeiras',
                                       widget=forms.SelectMultiple)

    codAdiq = forms.ChoiceField(label='Adquirente Prim.',
                                widget=forms.Select)

    codAdiq2 = forms.ChoiceField(label='Adquirente Sec.',
                                widget=forms.Select)


class NumLogicoForm(forms.Form):

    codLoja = forms.ChoiceField(label='Loja',
                                widget=forms.Select)

    codAdiq = forms.ChoiceField(label='Nome da Adquirente',
                                widget=forms.Select)

    numLogico = forms.CharField(label='Número lógico',
                                max_length=20,
                                required=True
                                )


class AdiqForm(forms.Form):

    codAdiq = forms.IntegerField(label='Adquirente', required=True)
    nomeAdiq = forms.CharField(label='Nome da Adquirente',
                               required=True,
                               max_length=50
                               )

    bandeiras = forms.ModelMultipleChoiceField(queryset=Bandeira.objects.all(),
                                               label='Bandeiras',
                                               )


class LojaForm(forms.Form):

    empresa = forms.ChoiceField(label='Empresa',
                                widget=forms.Select,
                                disabled=True)
    codLoja = forms.IntegerField(label='Loja', required=True)
    nomeLoja = forms.CharField(label='Nome da loja',
                               required=True,
                               max_length=50
                               )
    CNPJ = forms.CharField(label='CNPJ',
                           required=True,
                           max_length=14
                           )


class PDVForm(forms.Form):

    TRANS = [('1', 'Crédito a vista'),
              ('2', 'Crédito Parc. c/ juros'),
              ('3', 'Crédito Parc. s/ juros'),
              ('4', 'Débito'),
              ('5', 'Cancelamento')
              ]

    codLoja = forms.ChoiceField(label='Loja',
                                widget=forms.Select)

    codPDV = forms.IntegerField(label='PDV', required=True)

    TransDigitado = forms.BooleanField(label='Transação Digitada', required=False)
    TransVendaCreditoVista = forms.BooleanField(label='Venda Credito a Vista', required=False)
    TransVendaCreditoParc = forms.BooleanField(label='Venda Credito Parcelada', required=False)
    TransVendaCreditoSemJuros = forms.BooleanField(label='Venda Credito Parcelada s/ Juros', required=False)
    TransVendaDebito = forms.BooleanField(label='Venda Débito', required=False)
    TransCancelamento = forms.BooleanField(label='Cancelamento', required=False)


class DadosAdicionaisUsuarioForm(forms.Form):

    # PERFIL = [('1', 'Admin'), ('2', 'Corporativo'), ('3', 'Loja'), ('4', 'PDV')]

    # loja = forms.IntegerField(label='Loja', required=False)
    loja = forms.ChoiceField(label='Loja',
                             widget=forms.Select)
    perfil_user = forms.ChoiceField(label='Perfil do usuário',
                                    widget=forms.RadioSelect,
                                    )


class SelecaoPendForm(forms.Form):

    """ Form para seleção dos registros pendentes a listar """

    codLoja = forms.ChoiceField(label='Loja',
                                widget=forms.Select)

    dataInicial = forms.DateField(label="Data inicial",
                                  widget=forms.SelectDateWidget,
                                  )
    dataFinal = forms.DateField(label="Data final",
                                widget=forms.SelectDateWidget)


class RegLogPendForm(forms.Form):

    """ Form para exibição de um registro do Log, para tratamento de pendência"""

    NSU_TEF = forms.IntegerField(label="NSU TEF", disabled=True)
    NSU_HOST = forms.IntegerField(label="NSU Adquirente", disabled=True)
    dataHoraHost = forms.DateTimeField(label="Data/Hora", disabled=True)
    nomeLoja = forms.CharField(label="Loja",
                               max_length=50, disabled=True)
    codPDV = forms.IntegerField(label="PDV", disabled=True)
    codTRN = forms.CharField(label="Transação",
                             max_length=20, disabled=True)
    numCartao = forms.CharField(label="Cartão",
                                max_length=20, disabled=True)
    valorTrans = forms.DecimalField(label="Valor",
                                    decimal_places=2,
                                    max_digits=10, disabled=True)
    nomeBan = forms.CharField(label="Bandeira",
                              max_length=50, disabled=True)
    nomeAdiq = forms.CharField(label="Adquirente",
                               max_length=50, disabled=True)


class SelecaoLogForm(forms.Form):

    """ Form para seleção dos registros do Log a listar """

    STATUS_TRN = [('999', 'Todas'),
                  ('Efetuada', 'Efetuada'),
                  ('Negada', 'Negada'),
                  ('Cancelada', 'Cancelada'),
                  ('Desfeita', 'Desfeita'),
                  ('Pendente', 'Pendente'),
                  ('TimeOut', 'TimeOut')
                  ]

    codLoja = forms.ChoiceField(label='Loja',
                                widget=forms.Select)

    dataInicial = forms.DateField(label="Data inicial",
                                  widget=forms.SelectDateWidget,
                                  )
    dataFinal = forms.DateField(label="Data final",
                                widget=forms.SelectDateWidget)
    statusTRN = forms.ChoiceField(label='Status Transação',
                                  widget=forms.Select,
                                  choices=STATUS_TRN)
    nomeAdiq = forms.ChoiceField(label='Adquirente',
                                 widget=forms.Select
                                 )
    nomeBan = forms.ChoiceField(label='Bandeiras',
                                widget=forms.Select)


class RegLogForm(forms.Form):

    """ Form para exibição de um registro do Log """

    NSU_TEF = forms.IntegerField(label="NSU TEF", disabled=True)
    NSU_HOST = forms.IntegerField(label="NSU Adquirente", disabled=True)
    dataHoraHost = forms.DateTimeField(label="Data/Hora", disabled=True)
    nomeLoja = forms.CharField(label="Loja",
                               max_length=50, disabled=True)
    codPDV = forms.IntegerField(label="PDV", disabled=True)
    codTRN = forms.CharField(label="Transação",
                             max_length=20, disabled=True)
    numParcelas = forms.IntegerField(label="Parcelas",
                                     disabled=True)
    statusTRN = forms.CharField(label="Status",
                                max_length=20, disabled=True)
    codResp = forms.IntegerField(label="Cod. Retorno",
                                 disabled=True)
    msgResp = forms.CharField(label="Msg. Retorno",
                              max_length=50, disabled=True)
    numCartao = forms.CharField(label="Cartão",
                                max_length=20, disabled=True)
    valorTrans = forms.DecimalField(label="Valor",
                                    decimal_places=2,
                                    max_digits=10, disabled=True)
    nomeBan = forms.CharField(label="Bandeira",
                              max_length=50, disabled=True)
    nomeAdiq = forms.CharField(label="Adquirente",
                               max_length=50, disabled=True)


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)


