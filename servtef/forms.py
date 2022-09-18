from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Bandeira, Adquirente


class CodigoForm(forms.Form):

    codigo = forms.IntegerField(required=True)


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

    TransVendaCreditoVista = forms.BooleanField(label='Venda Credito a Vista', required=False)
    TransVendaCreditoParc = forms.BooleanField(label='Venda Credito Parcelada', required=False)
    TransVendaCreditoSemJuros = forms.BooleanField(label='Venda Credito Parcelada s/ Juros', required=False)
    TransVendaDebito = forms.BooleanField(label='Venda Débito', required=False)
    TransCancelamento = forms.BooleanField(label='Cancelamento', required=False)


class DadosAdicionaisUsuarioForm(forms.Form):

    PERFIL = [('1', 'Admin'), ('2', 'Corporativo'), ('3', 'Loja'), ('4', 'PDV')]

    # loja = forms.IntegerField(label='Loja', required=False)
    loja = forms.ChoiceField(label='Loja',
                             widget=forms.Select)
    perfil_user = forms.ChoiceField(label='Perfil do usuário',
                                    widget=forms.RadioSelect,
                                    choices=PERFIL)

    '''admin = forms.BooleanField(label='Admin', required=False)
    corporativo = forms.BooleanField(label='Corporativo', required=False)
    operador_loja = forms.BooleanField(label='Operador Loja', required=False)
    operador_pdv = forms.BooleanField(label='Operador PDV', required=False)'''


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)


