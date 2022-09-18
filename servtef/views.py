from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.forms import modelformset_factory

from . import forms
from .models import UsuarioTEF, Loja, PDV, Bandeira, Adquirente, NumLogico, Roteamento

''' View da tela inicial/dashboard:
        - Template - dashboard.html'''


def dashboard(request):
    if request.user.is_authenticated:
        userTEF = UsuarioTEF.objects.get(user=request.user)

        return render(request, "servtef/dashboard.html", {"userTEF": userTEF}
                      )
    else:
        return redirect("servtef:login")


''' View da tela para a inclusão de novos usuários
    - Utiliza o form da inclusão de usuários do Admin
'''


def register(request):
    if request.method == "GET":
        return render(request, "servtef/register.html", {"form": forms.CustomUserCreationForm, "msg": ""})
    elif request.method == "POST":
        form = forms.CustomUserCreationForm(request.POST)
        # form.full_clean()
        if form.is_valid():
            form.save()
            user = form.save()
            return redirect("servtef:dadosadicionais", user.id)
        else:
            return render(request, "servtef/register.html", {"form": form,

                                                             "msg": ""})


''' View da tela para a inclusão dos dados adicionais dos novos usuários
    '''


def dados_adicionais(request, pk):

    PERFIL_LOJA = [('3', 'Loja'), ('4', 'PDV')]
    PERFIL_CORPORATIVO = [('2', 'Corporativo'),('3', 'Loja'), ('4', 'PDV')]
    LISTA_LOJAS = []
    aux_loja = []
    new_user = User.objects.get(pk=pk) # dados iniciais do usuário a ser incluido
    userTEF = UsuarioTEF.objects.get(user=request.user) # dados do usuario que está fazendo a inclusão

    if userTEF.perfil_user == 1 or userTEF.perfil_user == 2: # usuário admin ou corporativo
        form_user = forms.DadosAdicionaisUsuarioForm()
        if userTEF.perfil_user == 2:
            form_user.fields['perfil_user'].choices = PERFIL_CORPORATIVO

        ''' Seleciona todas as lojas pertencentes à empresa, para montar a lista de lojas disponíveis,
            para a qual o novo usuário será relacionado '''

        lojas = Loja.objects.filter (empresa=userTEF.empresa)
        for loja in lojas:
            if loja.codLoja != 9999: # não inclui a loja Dummy
                aux_loja.append(str(loja.codLoja))
                aux_loja.append(loja.nomeLoja)
                LISTA_LOJAS.append(aux_loja[:])
                aux_loja.clear()

        form_user.fields['loja'].choices = LISTA_LOJAS
        codloja = 0
    else: # usuário loja só pode criar usuário da propria loja
        loja = Loja.objects.get (empresa=userTEF.empresa, codLoja=userTEF.loja.codLoja)
        aux_loja.append(str(loja.codLoja))
        aux_loja.append(loja.nomeLoja)
        LISTA_LOJAS.append(aux_loja[:])
        form_user = forms.DadosAdicionaisUsuarioForm()
        form_user.fields['loja'].choices = LISTA_LOJAS
        form_user.fields['perfil_user'].choices = PERFIL_LOJA
        codloja = userTEF.loja

    if request.method == "GET":
        return render(request, "servtef/dados.adicionias.html", {"form": form_user,
                                                                 "usuario": new_user
                                                                 }
                      )
    elif request.method == "POST":
        form = forms.DadosAdicionaisUsuarioForm(request.POST)
        #if form.is_valid():
        data = request.POST
        perfil_user=int(data.get("perfil_user"))
        if codloja == 0:
            if perfil_user == 1 or perfil_user == 2: # usuario admin e corporativo são colocados em uma loja ficticia, 9999
                loja = Loja.objects.get (empresa=userTEF.empresa, codLoja=9999)
            else:
                loja = Loja.objects.get (empresa=userTEF.empresa, codLoja=int(data.get("loja")))
        dados_usuario = UsuarioTEF(user=new_user,
                                   empresa=userTEF.empresa,
                                   loja=loja,
                                   perfil_user=int(data.get("perfil_user"))
                                   )
        dados_usuario.save()
        return render(request, "servtef/msg.generica.html", {"msg": "Inclusão de usuario realizada com sucesso"})


''' View da tela para a exibição de todos os usuarios, de uma loja ou de uma empresa, dependendo do perfil do usuário
    logado
    - Template - usuarios.html'''


def usuarios(request, oper):

    userTEF = UsuarioTEF.objects.get(user=request.user) # dados adicionais do usuario que está fazendo a alteração/exclusão

    if userTEF.perfil_user == 1 or userTEF.perfil_user == 2: # usuário admin ou corporativo,exibe todos os usuários da empresa
        lista_usuarios = UsuarioTEF.objects.filter(Q(empresa=userTEF.empresa) &
                                                   Q(perfil_user__gt=userTEF.perfil_user)
                                                   ).order_by('loja')
    else: # usuario de uma loja
        lista_usuarios = UsuarioTEF.objects.filter(Q(loja=userTEF.loja) &
                                                   Q(perfil_user__gt=userTEF.perfil_user)
                                                   ).order_by('user')  # exibe todos os usuários da loja

    return render(request, "servtef/usuarios.html", {"usuarios": lista_usuarios,
                                                     "userTEF": userTEF,
                                                     "operacao": oper,
                                                     }
                  )


''' View da tela para a exclusão de um usuario, selecionado à partir da lista de usuários (usuario.html)
    - Template - exclui.user.html'''


def exclui_user(request, pk):

    userTEF = UsuarioTEF.objects.get(user=request.user) # dados adicionais do usuario que está fazendo a exclusão
    userExc = User.objects.get(pk=pk)

    if request.method == "GET":
        return render(request, "servtef/exclui.user.html", {"usuario": userExc
                                                            }
                      )
    elif request.method == "POST":
        data = request.POST
        opcao= data.get("opcao")
        if opcao == "confirma":
            userExc.delete()
            #userExc.save()
        return render(request, "servtef/msg.generica.html", {"msg": "Exclusão de usuário realizada com sucesso"})


''' View da tela para a inclusão de loja
    - Template - inclui.loja.html'''


def IncluiLoja(request):

    EMPRESA = []
    aux_emp = []

    userTEF = UsuarioTEF.objects.get(user=request.user) # dados do usuario que está fazendo a inclusão
    aux_emp.append(str(userTEF.empresa.codEmp))
    aux_emp.append(userTEF.empresa.nomeEmp)
    EMPRESA.append(aux_emp[:])
    form_loja = forms.LojaForm()
    form_loja.fields['empresa'].choices = EMPRESA

    if request.method == "GET":
        msg = "Informe os dados da loja a incluir"
        return render(request, "servtef/inclui.loja.html", {"form": form_loja,
                                                            "usuario": userTEF,
                                                            "msg": msg
                                                            }
                      )
    elif request.method == "POST":
        form = forms.LojaForm(request.POST)
        data = request.POST
        try:
            loja = Loja.objects.get(Q(empresa=userTEF.empresa) &
                                    Q(codLoja=int(data.get("codLoja")))
                                    )
        except Loja.DoesNotExist:
            dados_loja = Loja(codLoja=int(data.get("codLoja")),
                              empresa=userTEF.empresa,
                              nomeLoja=data.get("nomeLoja"),
                              CNPJ=data.get("CNPJ")
                              )
            dados_loja.save()
        else:
            msg = f'Loja {(data.get("codLoja"))} já existe !!!'
            return render(request, "servtef/inclui.loja.html", {"form": form_loja,
                                                                "usuario": userTEF,
                                                                "msg": msg
                                                                }
                          )
        msg = f'Inclusão da loja {data.get("nomeLoja")} realizada com sucesso'
        return render(request, "servtef/msg.generica.html", {"msg": msg})


''' View da tela para a alteração e exclusão de loja. A view trabalha com 2 templates, da seguinte forma:
    1. Apresenta o template para capturar o código da loja a ser alterada/excluida.
    2. Se a loja existir, apresenta o template com os dados da loja a ser alterada/excluida
    3. Após o usuário confirmar a alteração/exclusão no segundo template, é feita a operação no banco de dados
    - Templates - ler.codigo.html e altera.exclui.loja.html'''


def AlteraExcluiLoja(request, oper):

    EMPRESA = []
    aux_emp = []
    titulo = ''
    msg = ''
    dados_iniciais = {}

    userTEF = UsuarioTEF.objects.get(user=request.user) # dados do usuario que está fazendo a operação
    aux_emp.append(str(userTEF.empresa.codEmp))
    aux_emp.append(userTEF.empresa.nomeEmp)
    EMPRESA.append(aux_emp[:])
    if oper == 'altera':
        msg = "Informe o código da loja a alterar"
        titulo = "Alteração de loja"
    else:
        msg = "Informe o código da loja a excluir"
        titulo = "Exclusão de loja"

    if request.method == "GET":
        form_cod = forms.CodigoForm()
        return render(request, "servtef/ler.codigo.html", {"form": form_cod,
                                                           "usuario": userTEF,
                                                           "msg": msg,
                                                           "titulo": titulo
                                                           }
                      )
    elif request.method == "POST":
        data = request.POST
        if data.get("codigo"): # este é o POST do primeiro template, de leitura de código
            try:
                loja = Loja.objects.get(Q(empresa=userTEF.empresa) &
                                        Q(codLoja=int(data.get("codigo")))
                                        )
            except Loja.DoesNotExist:
                form_cod = forms.CodigoForm()
                msg = f'Loja {(data.get("codigo"))} não existe !!!'
                return render(request, "servtef/ler.codigo.html", {"form": form_cod,
                                                                   "usuario": userTEF,
                                                                   "msg": msg,
                                                                   "titulo": titulo
                                                                   }
                              )
            else:
                dados_iniciais['codLoja'] = data.get("codigo")
                dados_iniciais['nomeLoja'] = loja.nomeLoja
                dados_iniciais['CNPJ'] = loja.CNPJ
                form_loja = forms.LojaForm(initial=dados_iniciais)
                form_loja.fields['empresa'].choices = EMPRESA
                cod_loja = int(form_loja.get_initial_for_field(form_loja.fields['codLoja'], 'codLoja'))
                if oper == 'altera':
                    msg = "Informe os campos a alterar"
                    titulo = "Alteração de loja"
                    #form_loja.fields['codLoja'].disabled = True
                else:
                    msg = "Confirme a exclusão da loja"
                    titulo = "Exclusão de loja"
                    #form_loja.fields['codLoja'].disabled = True
                    form_loja.fields['nomeLoja'].disabled = True
                    form_loja.fields['CNPJ'].disabled = True
                return render(request, "servtef/altera.exclui.loja.html", {"form": form_loja,
                                                                           "usuario": userTEF,
                                                                           "msg": msg,
                                                                           "titulo": titulo,
                                                                           "oper": oper
                                                                           }
                              )
        else: # é o POST do segundo template, com os dados da loja
            form_loja = forms.LojaForm(request.POST)
            cod_loja = int(data.get('codLoja'))
            if oper == 'altera':
                dados_loja = Loja(codLoja=cod_loja,
                                  empresa=userTEF.empresa,
                                  nomeLoja=data.get("nomeLoja"),
                                  CNPJ=data.get("CNPJ")
                                  )
                dados_loja.save()
                msg = f'Loja {cod_loja} alterada com sucesso'
            else:
                lojaExc = Loja.objects.get(Q(empresa=userTEF.empresa) &
                                           Q(codLoja=cod_loja)
                                           )
                lojaExc.delete()
                #lojaExc.save()
                msg = f'Loja {cod_loja} excluida com sucesso'
            return render(request, "servtef/msg.generica.html", {"msg": msg})


def IncluiPDV(request):

    LISTA_LOJAS = []
    aux_loja = []

    userTEF = UsuarioTEF.objects.get(user=request.user) # dados do usuario que está fazendo a inclusão
    form_PDV = forms.PDVForm()
    if userTEF.perfil_user == 1 or userTEF.perfil_user == 2: # usuário admin ou corporativo
        form_PDV = forms.PDVForm()
        lojas = Loja.objects.filter (empresa=userTEF.empresa)
        for loja in lojas: # inicializa a lista de todas as lojas da empresa
            if loja.codLoja != 9999: # não inclui a loja Dummy
                aux_loja.append(str(loja.codLoja))
                aux_loja.append(loja.nomeLoja)
                LISTA_LOJAS.append(aux_loja[:])
                aux_loja.clear()
        form_PDV.fields['codLoja'].choices = LISTA_LOJAS
        codloja = 0
    else: # usuário loja só pode criar PDV da propria loja
        loja = Loja.objects.get (empresa=userTEF.empresa, codLoja=userTEF.loja.codLoja)
        aux_loja.append(str(loja.codLoja))
        aux_loja.append(loja.nomeLoja)
        LISTA_LOJAS.append(aux_loja[:])
        form_PDV.fields['codLoja'].choices = LISTA_LOJAS
        codloja = userTEF.loja
    if request.method == "GET":
        msg = "Informe os dados do PDV a incluir"
        return render(request, "servtef/inclui.PDV.html", {"form": form_PDV,
                                                           "usuario": userTEF,
                                                           "msg": msg
                                                           }
                      )
    elif request.method == "POST":
        form = forms.PDVForm(request.POST)
        data = request.POST
        loja = Loja.objects.get (empresa=userTEF.empresa, codLoja=int(data.get("codLoja")))

        try:
            pdv = PDV.objects.get(Q(empresa=userTEF.empresa) &
                                  Q(loja=loja.codLoja) &
                                  Q(codPDV=int(data.get("codPDV")))
                                  )
        except PDV.DoesNotExist:
            dados_pdv = PDV.objects.create (loja=loja,
                                            empresa=userTEF.empresa,
                                            codPDV=int(data.get("codPDV")),
                                            UsuarioAtivo=0,
                                            TransVendaCreditoVista=bool(data.get('TransVendaCreditoVista')),
                                            TransVendaCreditoParc=bool(data.get('TransVendaCreditoParc')),
                                            TransVendaCreditoSemJuros=bool(data.get('TransVendaCreditoSemJuros')),
                                            TransVendaDebito=bool(data.get('TransVendaDebito')),
                                            TransCancelamento=bool(data.get('TransCancelamento')),
                                            )
            dados_pdv.save()
        else:
            msg = f'PDV {(data.get("codPDV"))} já existe !!!'
            return render(request, "servtef/inclui.loja.html", {"form": form_PDV,
                                                                "usuario": userTEF,
                                                                "msg": msg
                                                                }
                          )
        msg = f'Inclusão do PDV {data.get("codPDV")} realizada com sucesso'
        return render(request, "servtef/msg.generica.html", {"msg": msg})


''' View para a exibição de todos os PDV´s, de uma loja ou de uma empresa, dependendo do perfil do usuário
    logado. Recebe com parâmetro qual a operação vai ser executada, alteração ou exclusão
    - Template - lista.PDV.html'''


def ListaPDV(request, oper):

    userTEF = UsuarioTEF.objects.get(user=request.user) # dados adicionais do usuario que está fazendo a alteração/exclusão

    if userTEF.perfil_user == 1 or userTEF.perfil_user == 2: # usuário admin ou corporativo,exibe todos os PDV´s da empresa
        lista_PDV = PDV.objects.filter(empresa=userTEF.empresa).order_by('loja')
    else: # usuario gerente de uma loja
        lista_PDV = PDV.objects.filter(empresa=userTEF.empresa, loja=userTEF.loja.codLoja
                                       ).order_by('codPDV')  # exibe todos os PDV´s da loja

    return render(request, "servtef/lista.PDV.html", {"pdvs": lista_PDV,
                                                      "userTEF": userTEF,
                                                      "operacao": oper,
                                                      }
                  )


class ExcluiPDV(DeleteView):
    model = PDV
    template_name = "servtef/exclui.PDV.html"

    def get_success_url(self):
        return reverse_lazy("servtef:dashboard")


class AlteraPDV(UpdateView):
    model = PDV
    fields = ['TransVendaCreditoVista',
              'TransVendaCreditoParc',
              'TransVendaCreditoSemJuros',
              'TransVendaDebito',
              'TransCancelamento'
              ]

    template_name = "servtef/altera.PDV.html"

    def get_success_url(self):
        return reverse_lazy("servtef:dashboard")


class IncluiBandeira(CreateView):
    model = Bandeira
    fields = ['codBan',
              'nomeBan',
             ]

    template_name = "servtef/inclui.Bandeira.html"

    def get_success_url(self):
        return reverse_lazy("servtef:dashboard")


def IncluiAdiq(request):
    LISTA_BANDEIRAS = []
    aux_ban = []

    userTEF = UsuarioTEF.objects.get(user=request.user) # dados do usuario que está fazendo a inclusão
    form_Adiq = forms.AdiqForm()
    '''bandeiras = Bandeira.objects.all ()
    for bandeira in bandeiras: # inicializa a lista de bandeiras
        aux_ban.append(str(bandeira.codBan))
        aux_ban.append(bandeira.nomeBan)
        LISTA_BANDEIRAS.append(aux_ban[:])
        aux_ban.clear()
        form_Adiq.fields['bandeiras'].choices = LISTA_BANDEIRAS'''

    if request.method == "GET":
        msg = ''
        return render(request, "servtef/inclui.Adiq.html", {"form": form_Adiq,
                                                            "usuario": userTEF,
                                                            "msg": msg
                                                            }
                      )
    elif request.method == "POST":
        form_Adiq = forms.AdiqForm(request.POST)
        data = request.POST
        try:
            adiq = Adquirente.objects.get(codAdiq=int(data.get("codAdiq")))
        except Adquirente.DoesNotExist:
            dados_adiq = Adquirente.objects.create (codAdiq=int(data.get("codAdiq")),
                                                    nomeAdiq=data.get("nomeAdiq")
                                                    )

            dados_adiq.save()
            # bandeiras = data.get('bandeiras')
            bandeiras = form_Adiq['bandeiras'].value()
            for bandeira in bandeiras:
                dados_adiq.bandeiras.add(bandeira)
        else:
            msg = f'Adquirente {(data.get("codAdiq"))} já existe !!!'
            form_Adiq.fields['bandeiras'].choices = LISTA_BANDEIRAS
            return render(request, "servtef/inclui.Adiq.html", {"form": form_Adiq,
                                                                "usuario": userTEF,
                                                                "msg": msg
                                                                }
                          )
        msg = f'Inclusão da Adquirente {data.get("nomeAdiq")} realizada com sucesso'
        return render(request, "servtef/msg.generica.html", {"msg": msg})


class ListaAdiq(ListView):
    model = Adquirente
    fields = ['codAdiq',
              'nomeAdiq',
              'bandeiras'
              ]

    template_name = "servtef/lista.Adiq.html"

    def get_success_url(self):
        return reverse_lazy("servtef:dashboard")


class AlteraAdiq(UpdateView):
    model = Adquirente
    fields = ['codAdiq',
              'nomeAdiq',
              'bandeiras'
              ]

    template_name = "servtef/alteraAdiq.html"

    def get_success_url(self):
        return reverse_lazy("servtef:dashboard")


''' View da tela para o cadastramento de número lógico de uma adquirente para uma loja
    - Template - inclui.num.logico.html'''


def IncluiNumLogico(request):

    LISTA_LOJAS = []
    LISTA_ADIQS = []
    aux_loja = []
    aux_adiq = []

    userTEF = UsuarioTEF.objects.get(user=request.user) # dados do usuario que está fazendo a inclusão
    form_num = forms.NumLogicoForm()
    if userTEF.perfil_user == 1 or userTEF.perfil_user == 2: # usuário admin ou corporativo
        form_num = forms.NumLogicoForm()
        lojas = Loja.objects.filter (empresa=userTEF.empresa)
        for loja in lojas: # inicializa a lista de todas as lojas da empresa
            if loja.codLoja != 9999: # não inclui a loja Dummy
                aux_loja.append(str(loja.codLoja))
                aux_loja.append(loja.nomeLoja)
                LISTA_LOJAS.append(aux_loja[:])
                aux_loja.clear()
        form_num.fields['codLoja'].choices = LISTA_LOJAS
    else: # usuário loja só pode criar numero logico da propria loja
        loja = Loja.objects.get (empresa=userTEF.empresa, codLoja=userTEF.loja.codLoja)
        aux_loja.append(str(loja.codLoja))
        aux_loja.append(loja.nomeLoja)
        LISTA_LOJAS.append(aux_loja[:])
        form_num.fields['codLoja'].choices = LISTA_LOJAS

    adiqs = Adquirente.objects.all()
    for adiq in adiqs: # inicializa a lista de todas as adquirentes
        aux_adiq.append(str(adiq.codAdiq))
        aux_adiq.append(adiq.nomeAdiq)
        LISTA_ADIQS.append(aux_adiq[:])
        aux_adiq.clear()
    form_num.fields['codAdiq'].choices = LISTA_ADIQS
    if request.method == "GET":
        msg = f'Informe os dados para inclusão'
        return render(request, "servtef/inclui.num.logico.html", {"form": form_num,
                                                                  "usuario": userTEF,
                                                                  "msg": msg,
                                                                  }
                      )
    elif request.method == "POST":
        form_num = forms.NumLogicoForm()
        data = request.POST
        loja = Loja.objects.get (empresa=userTEF.empresa, codLoja=int(data.get("codLoja")))
        adiq = Adquirente.objects.get (codAdiq=int(data.get("codAdiq")))
        try:
            num_log = NumLogico.objects.get(empresa=userTEF.empresa, loja=loja, adiq=adiq)
        except NumLogico.DoesNotExist:
            dados_num = NumLogico(loja=loja,
                                  empresa=userTEF.empresa,
                                  adiq=adiq,
                                  numlogico=int(data.get("numLogico"))
                                  )
            dados_num.save()
            msg = f'Inclusão do número logico da loja {loja.nomeLoja} realizada com sucesso'
            return render(request, "servtef/msg.generica.html", {"msg": msg})
        else:
            msg = f'Num. lógico para {loja.nomeLoja}/{adiq.nomeAdiq} já existe !!!'
            form_num.fields['codAdiq'].choices = LISTA_ADIQS
            form_num.fields['codLoja'].choices = LISTA_LOJAS
            return render(request, "servtef/inclui.Adiq.html", {"form": form_num,
                                                                "usuario": userTEF,
                                                                "msg": msg
                                                                }
                          )


''' View da tela para o cadastramento de número lógico de uma adquirente para uma loja
    - Template - inclui.num.logico.html'''


def ListaNumLogico(request, oper):

    userTEF = UsuarioTEF.objects.get(user=request.user) # dados do usuario que está fazendo a operação

    if userTEF.perfil_user == 1 or userTEF.perfil_user == 2: # usuário admin ou corporativo
        lojas = Loja.objects.filter (empresa=userTEF.empresa)
    else: # usuário loja só pode criar numero logico da propria loja
        lojas = Loja.objects.get (empresa=userTEF.empresa, codLoja=userTEF.loja.codLoja)

    if request.method == "GET":
        return render(request, "servtef/lista.num.logico.html", {"lojas": lojas,
                                                                 "usuario": userTEF,
                                                                 "oper": oper,
                                                                 }
                      )


def AlteraNumLogico(request, pk):

    userTEF = UsuarioTEF.objects.get(user=request.user) # dados do usuario que está fazendo a operação
    loja = Loja.objects.get (empresa=userTEF.empresa, codLoja=pk)
    NumLogFormSet = modelformset_factory(NumLogico, fields=('adiq', 'numlogico'), extra=0,
                                         )
    if request.method == "GET":
        form=forms.NumLogicoForm()

        formset = NumLogFormSet(queryset=NumLogico.objects.filter(empresa=userTEF.empresa, loja=pk))
        return render(request, "servtef/altera.num.logico.html", {"form": formset,
                                                                  "loja": loja,
                                                                  "usuario": userTEF,
                                                                  }
                      )
    elif request.method == "POST":
        formset = NumLogFormSet(request.POST)
        formset.save()
        msg = f'Alteração do número logico da loja {loja.nomeLoja} realizada com sucesso'
        return render(request, "servtef/msg.generica.html", {"msg": msg})


''' View da tela para o roteamento das transações de uma loja, de uma bandeira para uma adquirente
    - Template - inclui.roteamento.html'''


def IncluiRoteamento(request, pk):

    LISTA_BANDEIRAS = []
    LISTA_ADIQS = []
    aux_ban = []
    aux_adiq = []

    userTEF = UsuarioTEF.objects.get(user=request.user) # dados do usuario que está fazendo a inclusão
    form_rot = forms.RoteamentoForm()
    bandeiras = Bandeira.objects.all ()
    adiqs = NumLogico.objects.filter (empresa=userTEF.empresa, loja=pk)
    loja = Loja.objects.get (empresa=userTEF.empresa, codLoja=pk)
    for adiq in adiqs: # inicializa a lista de todas as adquirentes para a loja selecionada
        # nomeadiq = Adquirente.objects.get (codAdiq=adiq.id)
        aux_adiq.append(str(adiq.adiq.codAdiq))
        aux_adiq.append(adiq.adiq.nomeAdiq)
        LISTA_ADIQS.append(aux_adiq[:])
        aux_adiq.clear()
    form_rot.fields['codAdiq'].choices = LISTA_ADIQS
    form_rot.fields['codAdiq2'].choices = LISTA_ADIQS
    for bandeira in bandeiras: # inicializa a lista de todas as bandeiras
        aux_ban.append(str(bandeira.codBan))
        aux_ban.append(bandeira.nomeBan)
        LISTA_BANDEIRAS.append(aux_ban[:])
        aux_ban.clear()
    form_rot.fields['codBan'].choices = LISTA_BANDEIRAS
    if request.method == "GET":
        return render(request, "servtef/inclui.roteamento.html", {"form": form_rot,
                                                                  "usuario": userTEF,
                                                                  "loja": loja
                                                                  }
                      )
    elif request.method == "POST":
        form_rot = forms.RoteamentoForm(request.POST)
        data = request.POST
        bandeiras = form_rot['codBan'].value()
        for bandeira in bandeiras: # inclui o roteamento para adquirente, para cada bandeira selecionada
            tabBan = Bandeira.objects.get (codBan=bandeira)
            try:
                adiq1 = Adquirente.objects.get (codAdiq=int(data.get("codAdiq")), bandeiras=tabBan)
            except Adquirente.DoesNotExist: # a bandeira selecionada para roteamento não é capturada pela adquirente
                msg = f'Bandeira {tabBan.nomeBan} não é capturada pela adquirente primária !!!'
                form_rot.fields['codAdiq'].choices = LISTA_ADIQS
                form_rot.fields['codAdiq2'].choices = LISTA_ADIQS
                form_rot.fields['codBan'].choices = LISTA_BANDEIRAS
                return render(request, "servtef/inclui.roteamento.html", {"form": form_rot,
                                                                          "usuario": userTEF,
                                                                          "msg": msg
                                                                          }
                              )
            try:
                adiq2 = Adquirente.objects.get (codAdiq=int(data.get("codAdiq2")), bandeiras=tabBan)
            except Adquirente.DoesNotExist: # a bandeira selecionada para roteamento não é capturada pela adquirente
                msg = f'Bandeira {tabBan.nomeBan} não é capturada pela adquirente secundária !!!'
                form_rot.fields['codAdiq'].choices = LISTA_ADIQS
                form_rot.fields['codAdiq2'].choices = LISTA_ADIQS
                form_rot.fields['codBan'].choices = LISTA_BANDEIRAS
                return render(request, "servtef/inclui.roteamento.html", {"form": form_rot,
                                                                          "usuario": userTEF,
                                                                          "msg": msg
                                                                          }
                              )
            try:
                roteamento = Roteamento.objects.get (empresa=userTEF.empresa,
                                                     loja=loja,
                                                     bandeira=tabBan
                                                     )
            except Roteamento.DoesNotExist:
                roteamento = Roteamento(empresa=userTEF.empresa,
                                        loja=loja,
                                        bandeira=tabBan,
                                        adiq=adiq1,
                                        adiq2=adiq2,
                                        )
                roteamento.save()
            else:
                roteamento.delete()
                roteamento = Roteamento(empresa=userTEF.empresa,
                                        loja=loja,
                                        bandeira=tabBan,
                                        adiq=adiq1,
                                        adiq2=adiq2,
                                        )
                roteamento.save()
        msg = f'Roteamento da loja {loja.nomeLoja} realizada com sucesso'
        return render(request, "servtef/msg.generica.html", {"msg": msg})


