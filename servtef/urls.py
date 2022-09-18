from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = "servtef"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("register/", views.register, name="register"),
    path("dadosadicionais/<int:pk>", views.dados_adicionais, name="dadosadicionais"),
    path("usuarios/<str:oper>", views.usuarios, name="usuarios"),
    path("excluiuser/<int:pk>", views.exclui_user, name="excluiuser"),
    path("incluiloja/", views.IncluiLoja, name="incluiloja"),
    path("alteraexcluiloja/<str:oper>", views.AlteraExcluiLoja, name="alteraexcluiloja"),
    path("incluiPDV/", views.IncluiPDV, name="incluipdv"),
    path("listaPDV/<str:oper>", views.ListaPDV, name="listapdv"),
    path("excluiPDV/<int:pk>", views.ExcluiPDV.as_view(), name="excluipdv"),
    path("alteraPDV/<int:pk>", views.AlteraPDV.as_view(), name="alterapdv"),
    path("incluiBandeira", views.IncluiBandeira.as_view(), name="incluibandeira"),
    path("incluiAdiq", views.IncluiAdiq, name="incluiadiq"),
    path("listaAdiq", views.ListaAdiq.as_view(), name="listaadiq"),
    path("alteraAdiq/<int:pk>", views.AlteraAdiq.as_view(), name="alteraadiq"),
    path("incluiNumLogico", views.IncluiNumLogico, name="incluinumlogico"),
    path("listaNumLogico/<str:oper>", views.ListaNumLogico, name="listanumlogico"),
    path("alterNumLogico/<int:pk>", views.AlteraNumLogico, name="alteranumlogico"),
    path("incluiroteamento/<int:pk>", views.IncluiRoteamento, name="incluiroteamento"),

    # API´s disponíveis no sistema, via Django/REST

    #path("api/v2/inicializaPDV", apis.InicializaPDV, name="inicializapdv"),  # inicialização de um PDV na loja
]
