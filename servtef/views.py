from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.forms import modelformset_factory
from django.core.paginator import Paginator

import datetime

from . import forms
from .models import UsuarioTEF, Empresa, Loja, PDV, LogTrans, Bandeira, Adquirente, NumLogico, Roteamento, PerfilUsuario

parametros = {}

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
    PERFIL_LOJA = [('3', 'Gerente Loja'), ('4', 'Operador PDV')]
    PERFIL_CORPORATIVO = [('2', 'Corporativo'), ('3', 'Gerente Loja'), ('4', 'Operador PDV')]
    LISTA_LOJAS = []
    PERFIL_USUARIO = []
    aux_loja = []
    aux = []
    new_user = User.objects.get(pk=pk)  # dados iniciais do usuário a ser incluido
    userTEF = UsuarioTEF.objects.get(user=request.user)  # dados do usuario que está fazendo a inclusão
    form_user = forms.DadosAdicionaisUsuarioForm()

    """ Monta a tabela de perfil, de acordo com o perfil do usuário que está incluindo """

    lista_perfil = PerfilUsuario.objects.filter(codPerfil__gte=userTEF.perfil_user)
    for perfil in lista_perfil:
        aux.append(str(perfil.codPerfil))
        aux.append(perfil.nomePerfil)
        PERFIL_USUARIO.append(aux[:])
        aux.clear()
    form_user.fields['perfil_user'].choices = PERFIL_USUARIO

    if userTEF.perfil_user == 1 or userTEF.perfil_user == 2:  # usuário admin ou corporativo

        ''' Seleciona todas as lojas pertencentes à empresa, para montar a lista de lojas disponíveis,
            para a qual o novo usuário será relacionado '''

        lojas = Loja.objects.filter(empresa=userTEF.empresa)
        for loja in lojas:
            if loja.codLoja != 9999:  # não inclui a loja Dummy
                aux_loja.append(str(loja.codLoja))
                aux_loja.append(loja.nomeLoja)
                LISTA_LOJAS.append(aux_loja[:])
                aux_loja.clear()
        form_user.fields['loja'].choices = LISTA_LOJAS
        codloja = 0
    else:  # usuário loja só pode criar usuário da propria loja
        loja = Loja.objects.get(empresa=userTEF.empresa, codLoja=userTEF.loja.codLoja)
        aux_loja.append(str(loja.codLoja))
        aux_loja.append(loja.nomeLoja)
        LISTA_LOJAS.append(aux_loja[:])
        form_user.fields['loja'].choices = LISTA_LOJAS
        codloja = userTEF.loja

    if request.method == "GET":
        return render(request, "servtef/dados.adicionias.html", {"form": form_user,
                                                                 "usuario": new_user
                                                                 }
                      )
    elif request.method == "POST":
        form = forms.DadosAdicionaisUsuarioForm(request.POST)
        # if form.is_valid():
        data = request.POST
        perfil_user = int(data.get("perfil_user"))
        if codloja == 0:
            if perfil_user == 1 or perfil_user == 2:  # usuario admin e corporativo são colocados em uma loja ficticia, 9999
                loja = Loja.objects.get(empresa=userTEF.empresa, codLoja=9999)
            else:
                loja = Loja.objects.get(empresa=userTEF.empresa, codLoja=int(data.get("loja")))
        nome_perfil = PerfilUsuario.objects.get(codPerfil=int(data.get("perfil_user")))
        dados_usuario = UsuarioTEF(user=new_user,
                                   empresa=userTEF.empresa,
                                   loja=loja,
                                   perfil_user=int(data.get("perfil_user")),
                                   nome_perfil=nome_perfil
                                   )
        dados_usuario.save()
        return render(request, "servtef/msg.generica.html", {"msg": "Inclusão de usuario realizada com sucesso"})


''' View da tela para a exibição de todos os usuarios, de uma loja ou de uma empresa, dependendo do perfil do usuário
    logado
    - Template - usuarios.html'''


def usuarios(request, oper):
    userTEF = UsuarioTEF.objects.get(
        user=request.user)  # dados adicionais do usuario que está fazendo a alteração/exclusão

    if userTEF.perfil_user == 1 or userTEF.perfil_user == 2:  # usuário admin ou corporativo,exibe todos os usuários da empresa
        lista_usuarios = UsuarioTEF.objects.filter(Q(empresa=userTEF.empresa) &
                                                   Q(perfil_user__gt=userTEF.perfil_user)
                                                   ).order_by('loja')
    else:  # usuario de uma loja
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
    userTEF = UsuarioTEF.objects.get(user=request.user)  # dados adicionais do usuario que está fazendo a exclusão
    userExc = User.objects.get(pk=pk)

    if request.method == "GET":
        return render(request, "servtef/exclui.user.html", {"usuario": userExc
                                                            }
                      )
    elif request.method == "POST":
        data = request.POST
        opcao = data.get("opcao")
        if opcao == "confirma":
            userExc.delete()
            return render(request, "servtef/msg.generica.html", {"msg": "Exclusão de usuário realizada com sucesso"})
        else:
            return render(request, "servtef/dashboard.html", {"userTEF": userTEF})


""" View da tela de relatório de usuários 
"""


def ListaUsuarios(request):

    LISTA_LOJAS = []
    aux_loja = []

    userTEF = UsuarioTEF.objects.get(user=request.user)  # dados do usuario que está a operação

    """ Monta o form para a exibição das lojas a selecionar"""

    if userTEF.perfil_user == 1 or userTEF.perfil_user == 2:  # usuário admin ou corporativo
        form_loja = forms.NomeLojaForm()

        ''' Seleciona todas as lojas pertencentes à empresa, para montar a lista de lojas disponíveis,
        '''

        lojas = Loja.objects.filter(empresa=userTEF.empresa)
        aux_loja.append('9999')
        aux_loja.append('Todas')
        LISTA_LOJAS.append(aux_loja[:])
        aux_loja.clear()
        for loja in lojas:
            if loja.codLoja != 9999:  # não inclui a loja Dummy
                aux_loja.append(str(loja.codLoja))
                aux_loja.append(loja.nomeLoja)
                LISTA_LOJAS.append(aux_loja[:])
                aux_loja.clear()

        form_loja.fields['codLoja'].choices = LISTA_LOJAS
        codloja = 0
    else:  # usuário loja só pode listar usuário da propria loja
        loja = Loja.objects.get(empresa=userTEF.empresa, codLoja=userTEF.loja.codLoja)
        aux_loja.append(str(loja.codLoja))
        aux_loja.append(loja.nomeLoja)
        LISTA_LOJAS.append(aux_loja[:])
        form_loja = forms.NomeLojaForm()
        form_loja.fields['codLoja'].choices = LISTA_LOJAS
        codloja = userTEF.loja

    if request.method == "GET":
        return render(request, "servtef/ler.loja.html", {"form": form_loja,
                                                         "usuario": userTEF,
                                                         }
                      )
    elif request.method == "POST":
        form_loja = forms.NomeLojaForm(request.POST)
        data = request.POST
        opcao = data.get("opcao")
        if opcao == "confirmar":
            codloja = int(data.get("codLoja"))
            return redirect("servtef:listadadosusuarios", 1, codloja)
        elif opcao == "cancela":
            return render(request, "servtef/dashboard.html", {"userTEF": userTEF})


''' View da tela para exibição dos dados dos usuários, de acordo com a loja selecionada na tela ListaUsuarios
    - Template - servtef/lista.Usuarios.html'''


def ListaDadosUsuarios(request, page, loja):
    global parametros

    if loja != 9999:
        queryset = UsuarioTEF.objects.filter(loja=loja,
                                             ).order_by("loja")
    else:  # seleciona registros de todas as lojas
        queryset = UsuarioTEF.objects.all().order_by("loja")

    if not queryset:
        return render(request, "servtef/msg.generica.html", {"msg": "Não existem usuários para esta loja"})

    paginator = Paginator(queryset, per_page=9)
    page_object = paginator.get_page(page)

    context = {"page_obj": page_object, "codloja": loja}

    return render(request, "servtef/lista.Usuarios.html", context)


''' View da tela para a inclusão de loja
    - Template - inclui.loja.html'''


def IncluiLoja(request):
    EMPRESA = []
    aux_emp = []

    userTEF = UsuarioTEF.objects.get(user=request.user)  # dados do usuario que está fazendo a inclusão
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

    userTEF = UsuarioTEF.objects.get(user=request.user)  # dados do usuario que está fazendo a operação
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
        if data.get("codigo"):  # este é o POST do primeiro template, de leitura de código
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
                    # form_loja.fields['codLoja'].disabled = True
                else:
                    msg = "Confirme a exclusão da loja"
                    titulo = "Exclusão de loja"
                    # form_loja.fields['codLoja'].disabled = True
                    form_loja.fields['nomeLoja'].disabled = True
                    form_loja.fields['CNPJ'].disabled = True
                return render(request, "servtef/altera.exclui.loja.html", {"form": form_loja,
                                                                           "usuario": userTEF,
                                                                           "msg": msg,
                                                                           "titulo": titulo,
                                                                           "oper": oper
                                                                           }
                              )
        else:  # é o POST do segundo template, com os dados da loja
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
                # lojaExc.save()
                msg = f'Loja {cod_loja} excluida com sucesso'
            return render(request, "servtef/msg.generica.html", {"msg": msg})


''' View da tela para a exibição das lojas . 
    - Templates - lista.Lojas.html'''


def ListaLojas(request, page, oper):

    userTEF = UsuarioTEF.objects.get(user=request.user)  # dados do usuario que está fazendo a operação

    """ Exibe a(s) loja(s) a selecionar """

    if userTEF.perfil_user == 1 or userTEF.perfil_user == 2:  # usuário admin ou corporativo
        lojas = Loja.objects.filter(empresa=userTEF.empresa,
                                    ).exclude(
            codLoja=9999
        ).order_by(
            'codLoja'
        )
        """ Monta os dados para paginação"""
        paginator = Paginator(lojas, per_page=8)
        page_object = paginator.get_page(page)
        context = {"page_obj": page_object, "paginacao": True, "operacao": oper}
    else:  # usuário loja só pode listar registros da propria loja
        lojas = Loja.objects.get(empresa=userTEF.empresa, codLoja=userTEF.loja.codLoja)
        context = {"loja": lojas, "paginacao": False, "operacao": oper}

    return render(request, "servtef/lista.Lojas.html", context)


''' View da tela para a exibição das adquirentes e bandieras cadastradas para a loja selecionada em 
    ListaLojas  
    
    - Templates - lista.DadosLoja.html'''


def ListaDadosLoja(request, pk, page):

    userTEF = UsuarioTEF.objects.get(user=request.user)  # dados do usuario que está fazendo a operação
    loja = Loja.objects.get(empresa=userTEF.empresa, codLoja=pk)

    """ Seleciona as adquirentes cadastradas para a loja"""

    adquirentes = NumLogico.objects.filter(empresa=userTEF.empresa, loja=pk)

    """ Seleciona as bandeiras cadastradas para a loja"""

    bandeiras = Roteamento.objects.filter(empresa=userTEF.empresa, loja=pk)

    if request.method == "GET":
        return render(request, "servtef/lista.DadosLoja.html", {"usuario": userTEF,
                                                                "nomeloja": loja.nomeLoja,
                                                                "adiqs": adquirentes,
                                                                "bands": bandeiras,
                                                                "page": page
                                                                }
                      )


def IncluiPDV(request):
    LISTA_LOJAS = []
    aux_loja = []

    userTEF = UsuarioTEF.objects.get(user=request.user)  # dados do usuario que está fazendo a inclusão
    form_PDV = forms.PDVForm()
    if userTEF.perfil_user == 1 or userTEF.perfil_user == 2:  # usuário admin ou corporativo
        form_PDV = forms.PDVForm()
        lojas = Loja.objects.filter(empresa=userTEF.empresa)
        for loja in lojas:  # inicializa a lista de todas as lojas da empresa
            if loja.codLoja != 9999:  # não inclui a loja Dummy
                aux_loja.append(str(loja.codLoja))
                aux_loja.append(loja.nomeLoja)
                LISTA_LOJAS.append(aux_loja[:])
                aux_loja.clear()
        form_PDV.fields['codLoja'].choices = LISTA_LOJAS
        codloja = 0
    else:  # usuário loja só pode criar PDV da propria loja
        loja = Loja.objects.get(empresa=userTEF.empresa, codLoja=userTEF.loja.codLoja)
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
        loja = Loja.objects.get(empresa=userTEF.empresa, codLoja=int(data.get("codLoja")))

        try:
            pdv = PDV.objects.get(Q(empresa=userTEF.empresa) &
                                  Q(loja=loja.codLoja) &
                                  Q(codPDV=int(data.get("codPDV")))
                                  )
        except PDV.DoesNotExist:
            dados_pdv = PDV.objects.create(loja=loja,
                                           empresa=userTEF.empresa,
                                           codPDV=int(data.get("codPDV")),
                                           UsuarioAtivo=0,
                                           TransDigitado=bool(data.get('TransDigitado')),
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
    userTEF = UsuarioTEF.objects.get(
        user=request.user)  # dados adicionais do usuario que está fazendo a alteração/exclusão

    if userTEF.perfil_user == 1 or userTEF.perfil_user == 2:  # usuário admin ou corporativo,exibe todos os PDV´s da empresa
        lista_PDV = PDV.objects.filter(empresa=userTEF.empresa).order_by('loja')
    else:  # usuario gerente de uma loja
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
    fields = ['TransDigitado',
              'TransVendaCreditoVista',
              'TransVendaCreditoParc',
              'TransVendaCreditoSemJuros',
              'TransVendaDebito',
              'TransCancelamento'
              ]

    template_name = "servtef/altera.PDV.html"

    def get_success_url(self):
        return reverse_lazy("servtef:dashboard")


''' View para a exibição dos dados de um PDV, para uma deteerminada loja
    - Template - lista.DadosPDV.html'''


def RelatorioPDV(request, pk, page):

    TRANS = ['Crédito a vista',
             'Crédito Parc. c/ juros',
             'Crédito Parc. s/ juros',
             'Débito',
             'Cancelamento'
             ]
    userTEF = UsuarioTEF.objects.get(user=request.user)  # dados adicionais do usuario que está fazendo a operação
    loja = Loja.objects.get(empresa=userTEF.empresa, codLoja=pk)
    lista_PDV = PDV.objects.filter(empresa=userTEF.empresa, loja=loja.codLoja
                                       ).order_by('codPDV')  # exibe todos os PDV´s da loja

    if request.method == "GET":
        return render(request, "servtef/lista.DadosPDV.html", {"usuario": userTEF,
                                                               "nomeloja": loja.nomeLoja,
                                                               "pdvs": lista_PDV,
                                                               "page": page,
                                                               "trans": TRANS
                                                               }
                      )


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

    userTEF = UsuarioTEF.objects.get(user=request.user)  # dados do usuario que está fazendo a inclusão
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
            dados_adiq = Adquirente.objects.create(codAdiq=int(data.get("codAdiq")),
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

    queryset = Adquirente.objects.all ().order_by ('nomeAdiq')

    template_name = "servtef/lista.Adiq1.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['oper'] = "altera"
        return context

    def get_success_url(self):
        return reverse_lazy("servtef:dashboard")


class RelatorioAdiq(ListView):
    model = Adquirente
    fields = ['codAdiq',
              'nomeAdiq',
              'bandeiras'
              ]

    queryset = Adquirente.objects.all ().order_by ('nomeAdiq')

    template_name = "servtef/lista.Adiq1.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['oper'] = "relat"
        return context

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

    userTEF = UsuarioTEF.objects.get(user=request.user)  # dados do usuario que está fazendo a inclusão
    form_num = forms.NumLogicoForm()
    if userTEF.perfil_user == 1 or userTEF.perfil_user == 2:  # usuário admin ou corporativo
        form_num = forms.NumLogicoForm()
        lojas = Loja.objects.filter(empresa=userTEF.empresa)
        for loja in lojas:  # inicializa a lista de todas as lojas da empresa
            if loja.codLoja != 9999:  # não inclui a loja Dummy
                aux_loja.append(str(loja.codLoja))
                aux_loja.append(loja.nomeLoja)
                LISTA_LOJAS.append(aux_loja[:])
                aux_loja.clear()
        form_num.fields['codLoja'].choices = LISTA_LOJAS
    else:  # usuário loja só pode criar numero logico da propria loja
        loja = Loja.objects.get(empresa=userTEF.empresa, codLoja=userTEF.loja.codLoja)
        aux_loja.append(str(loja.codLoja))
        aux_loja.append(loja.nomeLoja)
        LISTA_LOJAS.append(aux_loja[:])
        form_num.fields['codLoja'].choices = LISTA_LOJAS

    adiqs = Adquirente.objects.all()
    for adiq in adiqs:  # inicializa a lista de todas as adquirentes
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
        loja = Loja.objects.get(empresa=userTEF.empresa, codLoja=int(data.get("codLoja")))
        adiq = Adquirente.objects.get(codAdiq=int(data.get("codAdiq")))
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
    userTEF = UsuarioTEF.objects.get(user=request.user)  # dados do usuario que está fazendo a operação

    if userTEF.perfil_user == 1 or userTEF.perfil_user == 2:  # usuário admin ou corporativo
        lojas = Loja.objects.filter(empresa=userTEF.empresa)
    else:  # usuário loja só pode criar numero logico da propria loja
        lojas = Loja.objects.get(empresa=userTEF.empresa, codLoja=userTEF.loja.codLoja)

    if request.method == "GET":
        return render(request, "servtef/lista.num.logico.html", {"lojas": lojas,
                                                                 "usuario": userTEF,
                                                                 "oper": oper,
                                                                 }
                      )


def AlteraNumLogico(request, pk):
    userTEF = UsuarioTEF.objects.get(user=request.user)  # dados do usuario que está fazendo a operação
    loja = Loja.objects.get(empresa=userTEF.empresa, codLoja=pk)
    NumLogFormSet = modelformset_factory(NumLogico, fields=('adiq', 'numlogico'), extra=0,
                                         )
    if request.method == "GET":
        # form = forms.NumLogicoForm()
        queryset = NumLogico.objects.filter(empresa=userTEF.empresa, loja=pk)
        if not queryset:
            msg = f'Não existe número lógico cadastrado para a loja {loja.nomeLoja}'
            return render(request, "servtef/msg.generica.html", {"msg": msg})

        formset = NumLogFormSet(queryset=queryset)
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

    userTEF = UsuarioTEF.objects.get(user=request.user)  # dados do usuario que está fazendo a inclusão
    form_rot = forms.RoteamentoForm()
    bandeiras = Bandeira.objects.all()
    adiqs = NumLogico.objects.filter(empresa=userTEF.empresa, loja=pk)
    loja = Loja.objects.get(empresa=userTEF.empresa, codLoja=pk)
    for adiq in adiqs:  # inicializa a lista de todas as adquirentes para a loja selecionada
        # nomeadiq = Adquirente.objects.get (codAdiq=adiq.id)
        aux_adiq.append(str(adiq.adiq.codAdiq))
        aux_adiq.append(adiq.adiq.nomeAdiq)
        LISTA_ADIQS.append(aux_adiq[:])
        aux_adiq.clear()
    form_rot.fields['codAdiq'].choices = LISTA_ADIQS
    form_rot.fields['codAdiq2'].choices = LISTA_ADIQS
    for bandeira in bandeiras:  # inicializa a lista de todas as bandeiras
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
        for bandeira in bandeiras:  # inclui o roteamento para adquirente, para cada bandeira selecionada
            tabBan = Bandeira.objects.get(codBan=bandeira)
            try:
                adiq1 = Adquirente.objects.get(codAdiq=int(data.get("codAdiq")), bandeiras=tabBan)
            except Adquirente.DoesNotExist:  # a bandeira selecionada para roteamento não é capturada pela adquirente
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
                adiq2 = Adquirente.objects.get(codAdiq=int(data.get("codAdiq2")), bandeiras=tabBan)
            except Adquirente.DoesNotExist:  # a bandeira selecionada para roteamento não é capturada pela adquirente
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
                roteamento = Roteamento.objects.get(empresa=userTEF.empresa,
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


''' View da tela para exibição dos dados da empresa. 
    Não existe tela para criação, alteração e deleção da empresa.
    Como é a entidade maior do sistema, ela será criada no on board do sistema, pelo admin. 
    - Template - inclui.roteamento.html'''


class ListaEmpresa(DetailView):
    model = Empresa

    fields = ['codAdiq',
              'nomeAdiq',
              'bandeiras'
              ]

    template_name = "servtef/lista.Empresa.html"


'''class ListaPendencias(ListView):

    model = LogTrans

    fields = ['NSU_TEF',
              'dataLocal',
              'horaLocal',
              'NSH_HOST',
              'dataHoraHost',
              'codLoja',
              'codPDV',
              'codTRN',
              'statusTRN',
              'codResp',
              'msgResp',
              'valorTrans',
              'nomeAdiq',
              'nomeBan'
              ]

    print(f'loja {lojaGlobal}')
    queryset = LogTrans.objects.filter(codLoja=lojaGlobal,
                                       statusTRN="Pendente",
                                       codResp=0).order_by("dataHoraHost")
    paginate_by = 6
    template_name = "servtef/lista.Pendencias.html"

    def get_success_url(self):
        return reverse_lazy("servtef:dashboard")'''

''' View da tela para exibição dos registros pendentes, de acordo com o filtro
    feito na tela SelecionaPendencias
    - Template - servtef/lista.Pendencias.html'''


def ListaPendencias(request, page):
    global parametros

    dt_inicial = parametros["dt_inicial"]
    dt_final = parametros["dt_final"]
    loja = parametros["codLoja"]

    if loja != 9999:
        queryset = LogTrans.objects.filter(codLoja=loja,
                                           dataLocal__gte=dt_inicial,
                                           dataLocal__lte=dt_final,
                                           statusTRN="Pendente",
                                           codResp=0).order_by("dataHoraHost")
    else:  # seleciona pendendias de todas as lojas
        queryset = LogTrans.objects.filter(dataLocal__gte=dt_inicial,
                                           dataLocal__lte=dt_final,
                                           statusTRN="Pendente",
                                           codResp=0).order_by("dataHoraHost")

    if not queryset:
        return render(request, "servtef/msg.generica.html", {"msg": "Não existem pendencias para esta seleção"})

    paginator = Paginator(queryset, per_page=6)
    page_object = paginator.get_page(page)

    context = {"page_obj": page_object}

    return render(request, "servtef/lista.Pendencias.html", context)


''' View da tela para seleção dos registros pendentes a listar.
    O filtro dos registros será através da loja e data inicial/final
    - Template - servtef/seleciona.Pend.html'''


def SelecionaPendencias(request):
    global parametros

    lojaSel = 0
    LISTA_LOJAS = []
    aux_loja = []

    userTEF = UsuarioTEF.objects.get(user=request.user)  # dados do usuario que está fazendo a inclusão
    form_Sel = forms.SelecaoPendForm()
    if userTEF.perfil_user == 1 or userTEF.perfil_user == 2:  # usuário admin ou corporativo
        form_Sel = forms.SelecaoPendForm()
        lojas = Loja.objects.filter(empresa=userTEF.empresa)
        aux_loja.append('9999')
        aux_loja.append('Todas')
        LISTA_LOJAS.append(aux_loja[:])
        aux_loja.clear()
        for loja in lojas:  # inicializa a lista de todas as lojas da empresa
            if loja.codLoja != 9999:  # não inclui a loja Dummy
                aux_loja.append(str(loja.codLoja))
                aux_loja.append(loja.nomeLoja)
                LISTA_LOJAS.append(aux_loja[:])
                aux_loja.clear()
        form_Sel.fields['codLoja'].choices = LISTA_LOJAS
        codloja = 0
    else:  # usuário loja só pode tratar penencias da propria loja
        loja = Loja.objects.get(empresa=userTEF.empresa, codLoja=userTEF.loja.codLoja)
        aux_loja.append(str(loja.codLoja))
        aux_loja.append(loja.nomeLoja)
        LISTA_LOJAS.append(aux_loja[:])
        form_Sel.fields['codLoja'].choices = LISTA_LOJAS
        codloja = userTEF.loja
    if request.method == "GET":
        msg = " "
        return render(request, "servtef/seleciona.Pend.html", {"form": form_Sel,
                                                               "usuario": userTEF,
                                                               "msg": msg,
                                                               "codLoja": lojaSel
                                                               }
                      )
    elif request.method == "POST":
        form_Sel = forms.SelecaoPendForm(request.POST)
        data = request.POST
        opcao = data.get("opcao")
        if opcao == "confirma":
            lojaSel = int(data.get('codLoja'))
            data = form_Sel["dataFinal"].value()
            data_final = datetime.datetime(int(data[-4:]), int(data[3:5]), int(data[0:2]))
            data = form_Sel["dataInicial"].value()
            data_inicial = datetime.datetime(int(data[-4:]), int(data[3:5]), int(data[0:2]))
            # print(f'dt inicial {data_inicial.date()}')
            # print(f'dt final {data_final.date()}')
            if data_inicial.date() > data_final.date() or data_inicial.date() > datetime.date.today():
                return render(request, "servtef/msg.generica.html", {"msg": "Data inicial inválida"})
            elif data_final.date() > datetime.date.today():
                return render(request, "servtef/msg.generica.html", {"msg": "Data final inválida"})
            else:
                parametros = {"codLoja": lojaSel,
                              "dt_inicial": data_inicial.date(),
                              "dt_final": data_final.date(),
                              }
                return redirect("servtef:listapendencias", 1)
        else:
            return render(request, "servtef/dashboard.html", {"userTEF": userTEF})


''' View da tela para tratamento de transações pendentesr.
    O registro a ser tratado foi selecionada na tela ListaPendencias
    
    - Template - servtef/resolve.Pend.html'''


def TrataPendencia(request, pk):
    userTEF = UsuarioTEF.objects.get(user=request.user)  # dados do usuario que está fazendo a inclusão
    reg_Log = LogTrans.objects.get(NSU_TEF=pk)
    loja = Loja.objects.get(empresa=reg_Log.codEmp,
                            codLoja=reg_Log.codLoja
                            )
    num_cartao = reg_Log.numCartao
    num_cartao = f'{num_cartao[-4:]:*>{len(num_cartao)}}'
    nomeTrans = ''

    match reg_Log.codTRN:

        case 'Cancelamento':
            nomeTrans = "CANCELAMENTO"
        case 'CredVista':
            nomeTrans = "CRÉDITO A VISTA"
        case 'CredParc':
            nomeTrans = f"PARCELADO SEM JUROS"
        case 'CredParcComJuros':
            nomeTrans = f"PARCELADO COM JUROS"
        case 'Debito':
            nomeTrans = "DÉBITO"

    valor_inicial = {'NSU_TEF': reg_Log.NSU_TEF,
                     'NSU_HOST': reg_Log.NSU_HOST,
                     'dataHoraHost': reg_Log.dataHoraHost,
                     'nomeLoja': loja.nomeLoja,
                     'codPDV': reg_Log.codPDV,
                     'codTRN': nomeTrans,
                     'numCartao': num_cartao,
                     'valorTrans': reg_Log.valorTrans,
                     'nomeBan': reg_Log.nomeBan,
                     'nomeAdiq': reg_Log.nomeAdiq
                     }

    form_Log = forms.RegLogPendForm(initial=valor_inicial)

    if request.method == "GET":
        return render(request, "servtef/resolve.Pend.html", {"form": form_Log,
                                                             "usuario": userTEF,
                                                             }
                      )
    elif request.method == "POST":
        form_Sel = forms.RegLogPendForm(request.POST)
        data = request.POST
        opcao = data.get("opcao")
        if opcao == "confirma":
            reg_Log.statusTRN = "Efetuada"
            reg_Log.save()
            return render(request, "servtef/msg.generica.html", {"msg": "Transação confirmada",
                                                                 }
                          )
        elif opcao == "desfaz":
            reg_Log.statusTRN = "Desfeita"
            reg_Log.save()
            return render(request, "servtef/msg.generica.html", {"msg": "Transação desfeita"}
                          )
        return render(request, "servtef/dashboard.html", {"userTEF": userTEF})


''' View da tela para seleção dos registros do Log a listar.
    O filtro dos registros será através da loja, data inicial/final, status, adquirente, bandeira
    
    - Template - servtef/seleciona.Pend.html'''


def SelecionaRegLog(request):
    global parametros

    lojaSel = 0
    LISTA = []
    aux = []

    userTEF = UsuarioTEF.objects.get(user=request.user)  # dados do usuario que está fazendo a inclusão
    form_Sel = forms.SelecaoLogForm()

    """ Exibe as lojas a selecionar, se o usuário for admin/corporativo """

    if userTEF.perfil_user == 1 or userTEF.perfil_user == 2:  # usuário admin ou corporativo
        form_Sel = forms.SelecaoLogForm()
        lojas = Loja.objects.filter(empresa=userTEF.empresa)
        aux.append('9999')
        aux.append('Todas')
        LISTA.append(aux[:])
        aux.clear()
        for loja in lojas:  # inicializa a lista de todas as lojas da empresa
            if loja.codLoja != 9999:  # não inclui a loja Dummy
                aux.append(str(loja.codLoja))
                aux.append(loja.nomeLoja)
                LISTA.append(aux[:])
                aux.clear()
        form_Sel.fields['codLoja'].choices = LISTA
        codloja = 0
    else:  # usuário loja só pode listar registros da propria loja
        loja = Loja.objects.get(empresa=userTEF.empresa, codLoja=userTEF.loja.codLoja)
        aux.append(str(loja.codLoja))
        aux.append(loja.nomeLoja)
        LISTA.append(aux[:])
        form_Sel.fields['codLoja'].choices = LISTA
        codloja = userTEF.loja

    """ Exibe as adquirentes a selecionar """

    aux.clear()
    LISTA.clear()
    aux.append('9999')
    aux.append('Todas')
    LISTA.append(aux[:])
    aux.clear()
    adquirentes = Adquirente.objects.all()
    for adiq in adquirentes:
        aux.append(adiq.nomeAdiq)
        aux.append(adiq.nomeAdiq)
        LISTA.append(aux[:])
        aux.clear()
    form_Sel.fields['nomeAdiq'].choices = LISTA

    """ Exibe as bandeiras a selecionar """

    aux.clear()
    LISTA.clear()
    aux.append('9999')
    aux.append('Todas')
    LISTA.append(aux[:])
    aux.clear()
    bandeiras = Bandeira.objects.all()
    for band in bandeiras:
        aux.append(str(band.codBan))
        aux.append(band.nomeBan)
        LISTA.append(aux[:])
        aux.clear()
    form_Sel.fields['nomeBan'].choices = LISTA

    if request.method == "GET":
        return render(request, "servtef/seleciona.Pend.html", {"form": form_Sel,
                                                               "usuario": userTEF,
                                                               }
                      )
    elif request.method == "POST":
        form_Sel = forms.SelecaoLogForm(request.POST)
        data = request.POST
        opcao = data.get("opcao")
        if opcao == "confirma":
            lojaSel = int(data.get('codLoja'))
            data_aux = form_Sel["dataFinal"].value()
            data_final = datetime.datetime(int(data_aux[-4:]), int(data_aux[3:5]), int(data_aux[0:2]))
            data_aux = form_Sel["dataInicial"].value()
            data_inicial = datetime.datetime(int(data_aux[-4:]), int(data_aux[3:5]), int(data_aux[0:2]))
            # print(f'dt inicial {data_inicial.date()}')
            # print(f'dt final {data_final.date()}')
            if data_inicial.date() > data_final.date() or data_inicial.date() > datetime.date.today():
                return render(request, "servtef/msg.generica.html", {"msg": "Data inicial inválida"})
            elif data_final.date() > datetime.date.today():
                return render(request, "servtef/msg.generica.html", {"msg": "Data final inválida"})
            else:
                statusTRN = data.get('statusTRN')
                nomeAdiq = data.get('nomeAdiq')
                nomeBan = data.get('nomeBan')
                parametros = {"codLoja": lojaSel,
                              "dt_inicial": data_inicial.date(),
                              "dt_final": data_final.date(),
                              "statusTRN": statusTRN,
                              "nomeAdiq": nomeAdiq,
                              "nomeBan": nomeBan
                              }
                return redirect("servtef:listaregistroslog", 1)
        else:
            return render(request, "servtef/dashboard.html", {"userTEF": userTEF})


''' View da tela para exibição dos registros do Log, de acordo com o filtro
    feito na tela SelecionaRegLog
    - Template - servtef/lista.Log.html'''


def ListaRegistrosLog(request, page):
    global parametros

    dt_inicial = parametros["dt_inicial"]
    dt_final = parametros["dt_final"]
    loja = parametros["codLoja"]
    statusTRN = parametros["statusTRN"]
    nomeAdiq = parametros["nomeAdiq"]
    nomeBan = parametros["nomeBan"]
    # print(statusTRN)

    """ Filtro por loja. 9999 significa todas  """

    if loja != 9999:
        queryset = LogTrans.objects.filter(codLoja=loja,
                                           dataLocal__gte=dt_inicial,
                                           dataLocal__lte=dt_final,
                                           ).order_by("dataHoraHost")
    else:  # seleciona registros de todas as lojas
        queryset = LogTrans.objects.filter(dataLocal__gte=dt_inicial,
                                           dataLocal__lte=dt_final,
                                           ).order_by("dataHoraHost")

    """ Filtro por status da transação. 999 significa todos """

    if statusTRN != '999':
        queryset = queryset.filter(statusTRN=statusTRN)

    """ Filtro por adquirente. 9999 significa todos """

    if nomeAdiq != '9999':
        queryset = queryset.filter(nomeAdiq=nomeAdiq)

    """ Filtro por bandeira. 9999 significa todas """

    if nomeBan != '9999':
        queryset = queryset.filter(nomeBan=nomeBan)

    if not queryset:
        return render(request, "servtef/msg.generica.html", {"msg": "Não existem registros para esta seleção"})

    paginator = Paginator(queryset, per_page=9)
    page_object = paginator.get_page(page)

    context = {"page_obj": page_object}
    parametros["page_number"] = page_object.number

    return render(request, "servtef/lista.Log.html", context)


""" View da tela para exibir um registro do log completo.
    O registro a ser tratado foi selecionada na tela ListaRegistrosLog
    
    - Template - servtef/listaRegLog.html"""


def ExibeRegLog(request, pk):

    global parametros

    # print(parametros["dt_inicial"])

    userTEF = UsuarioTEF.objects.get(user=request.user)  # dados do usuario que está fazendo a inclusão
    reg_Log = LogTrans.objects.get(NSU_TEF=pk)
    loja = Loja.objects.get(empresa=reg_Log.codEmp,
                            codLoja=reg_Log.codLoja
                            )
    num_cartao = reg_Log.numCartao
    num_cartao = f'{num_cartao[-4:]:*>{len(num_cartao)}}'
    nomeTrans = ''

    match reg_Log.codTRN:

        case 'Cancelamento':
            nomeTrans = "CANCELAMENTO"
        case 'CredVista':
            nomeTrans = "CRÉDITO A VISTA"
        case 'CredParc':
            nomeTrans = f"PARCELADO SEM JUROS"
        case 'CredParcComJuros':
            nomeTrans = f"PARCELADO COM JUROS"
        case 'Debito':
            nomeTrans = "DÉBITO"

    valor_inicial = {'NSU_TEF': reg_Log.NSU_TEF,
                     'NSU_HOST': reg_Log.NSU_HOST,
                     'dataHoraHost': reg_Log.dataHoraHost,
                     'nomeLoja': loja.nomeLoja,
                     'codPDV': reg_Log.codPDV,
                     'codTRN': nomeTrans,
                     'numParcelas': reg_Log.numParcelas,
                     'statusTRN': reg_Log.statusTRN,
                     'codResp': reg_Log.codResp,
                     'msgResp': reg_Log.msgResp,
                     'numCartao': num_cartao,
                     'valorTrans': reg_Log.valorTrans,
                     'nomeBan': reg_Log.nomeBan,
                     'nomeAdiq': reg_Log.nomeAdiq
                     }

    form_Log = forms.RegLogForm(initial=valor_inicial)

    if request.method == "GET":
        return render(request, "servtef/listaRegLog.html", {"form": form_Log,
                                                            "usuario": userTEF,
                                                            }
                      )
    elif request.method == "POST":
        form_Sel = forms.RegLogForm(request.POST)
        data = request.POST
        opcao = data.get("opcao")
        if opcao == "voltar":
            return redirect("servtef:listaregistroslog", parametros['page_number'])
        elif opcao == "cancela":
            return render(request, "servtef/dashboard.html", {"userTEF": userTEF})
