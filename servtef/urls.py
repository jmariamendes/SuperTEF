from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from . import apis


app_name = "servtef"

urlpatterns = [
    path("login", views.dashboard, name="dashboard"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("register/", views.register, name="register"),
    path("dadosadicionais/<int:pk>", views.dados_adicionais, name="dadosadicionais"),
    path("usuarios/<str:oper>", views.usuarios, name="usuarios"),
    path("excluiuser/<int:pk>", views.exclui_user, name="excluiuser"),
    path("ListaUsuarios", views.ListaUsuarios, name="listausuarios"),
    path("ListaDadosUsuarios/<int:page> <int:loja>", views.ListaDadosUsuarios, name="listadadosusuarios"),
    path("incluiloja/", views.IncluiLoja, name="incluiloja"),
    path("alteraexcluiloja/<str:oper>", views.AlteraExcluiLoja, name="alteraexcluiloja"),
    path("ListaLojas/<int:page> <str:oper>", views.ListaLojas, name="listalojas"),
    path("ListaDadosLoja/<int:pk> <int:page>", views.ListaDadosLoja, name="listadadosloja"),
    path("incluiPDV/", views.IncluiPDV, name="incluipdv"),
    path("listaPDV/<str:oper>", views.ListaPDV, name="listapdv"),
    path("excluiPDV/<int:pk>", views.ExcluiPDV.as_view(), name="excluipdv"),
    path("alteraPDV/<int:pk>", views.AlteraPDV.as_view(), name="alterapdv"),
    path("RelatorioPDV/<int:pk> <int:page>", views.RelatorioPDV, name="relatoriopdv"),
    path("incluiBandeira", views.IncluiBandeira.as_view(), name="incluibandeira"),
    path("incluiAdiq", views.IncluiAdiq, name="incluiadiq"),
    path("listaAdiq", views.ListaAdiq.as_view(), name="listaadiq"),
    path("relatorioAdiq", views.RelatorioAdiq.as_view(), name="relatorioadiq"),
    path("alteraAdiq/<int:pk>", views.AlteraAdiq.as_view(), name="alteraadiq"),
    path("incluiNumLogico", views.IncluiNumLogico, name="incluinumlogico"),
    path("listaNumLogico/<str:oper>", views.ListaNumLogico, name="listanumlogico"),
    path("alterNumLogico/<int:pk>", views.AlteraNumLogico, name="alteranumlogico"),
    path("incluiroteamento/<int:pk>", views.IncluiRoteamento, name="incluiroteamento"),
    path("listaEmpresa/<int:pk>", views.ListaEmpresa.as_view(), name="listaempresa"),
    path("selecionaPendencias", views.SelecionaPendencias, name="selecionapendencias"),
    path("listaPendencias/<int:page>", views.ListaPendencias, name="listapendencias"),
    path("trataPendencia/<int:pk>", views.TrataPendencia, name="tratapendencia"),
    path("selecionaRegistros", views.SelecionaRegLog, name="selecionaregistros"),
    path("listaRegistrosLog/<int:page>", views.ListaRegistrosLog, name="listaregistroslog"),
    path("exibeRegLog/<int:pk>", views.ExibeRegLog, name="exibereglog"),

    # API´s disponíveis no sistema, via Django/REST

    path("api/v1/inicializaPDV", apis.InicializaPDV, name="inicializapdv"),  # inicialização de um PDV na loja
    path("api/v1/login", apis.LoginUsuario, name="login"),  # Login de um usuário no PDV da loja
    path("api/v1/aberturaPDV", apis.AberturaPDV, name="aberturapdv"),  # abertura de um PDV na loja
    path("api/v1/dadostrans", apis.DadosTransacao, name="dadostrans"),  # consulta dados transação
    path("api/v1/vendacredito", apis.VendaCredito, name="vendacredito"),  # venda com cartão de crédito
    path("api/v1/confirmadesfaz", apis.ConfirmaDesfazTrans, name="confirmadesfaz"),  # confirmação/desfazimento de transação
    path("api/v1/cancelamento", apis.Cancelamento, name="cancelamento"),  # cancelamento de transação
    path("api/v1/pesqtranslog", apis.PesqTransLog, name="pesqtranslog"),  # pesquisa transações no Log
    path("api/v1/sonda", apis.TrataSonda, name="sonda"),  # trata mensagem de sonda envidada pelo adquirente
]
