import datetime

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth.models import User
from django.db.models.functions import Now
from django.contrib.auth.hashers import check_password

from . import models
from .JSON.json import DadosInicializaIn, DadosTransacaoIn, \
    DadosAberturaIn, DadosVendaCreditoIn, \
    DadosConfirmacao, DadosCancelamento, DadosLogin

from cryptography.fernet import Fernet

from .rotauxiliares import RotinasAuxiliares


@api_view(['PUT'])
def InicializaPDV(request):
    """ Inicialização de PDV
        - verifica se a empresa/loja/pdv existem
        - verifica se usuário é do perfil gerente de loja
        - atualiza tabela de PDV
        JSON de entrada:
            {
                "headerIn": {
                            "transação":<string>
                            "empresa": <digit>,
                            "loja": <digit>,
                            "pdv": <digit>,
                            }
                "usuario": <string>
            }
        JSON de saída:
            {
                "headerOut": {
                                "codErro": <digit>,
                                "mensagem": <string>,
                             }
            }
    """
    rotAux = RotinasAuxiliares(request.data)

    if not rotAux.setUp(DadosInicializaIn):
        return Response(rotAux.buffer_resposta, status=status.HTTP_204_NO_CONTENT)

    try:
        user = User.objects.get(username=rotAux.usuario)
    except User.DoesNotExist:
        rotAux.MontaHeaderOut(1, f'Usuario {rotAux.usuario} não existe')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    try:
        loja = models.Loja.objects.get(empresa=rotAux.cod_empresa, codLoja=rotAux.cod_loja)
    except models.Loja.DoesNotExist:
        rotAux.MontaHeaderOut(2, f'Loja/empresa {rotAux.cod_loja}/{rotAux.cod_empresa} não existe')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    try:
        pdv = models.PDV.objects.get(empresa=rotAux.cod_empresa, loja=rotAux.cod_loja, codPDV=rotAux.cod_pdv)
    except models.PDV.DoesNotExist:
        rotAux.MontaHeaderOut(3, f'PDV {rotAux.cod_pdv} não existe para a loja {rotAux.cod_loja}')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    try:
        userTEF = models.UsuarioTEF.objects.get(empresa=rotAux.cod_empresa, loja=rotAux.cod_loja, user=user.id)
    except models.UsuarioTEF.DoesNotExist:
        rotAux.MontaHeaderOut(4, f'Usuario {rotAux.usuario} não é desta loja')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    if userTEF.perfil_user != 3:
        rotAux.MontaHeaderOut(5, f'Usuario {rotAux.usuario} não tem premissão para inicializar PDV')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    pdv.StatusPDV = True
    pdv.save()
    rotAux.MontaHeaderOut(0, f'Pdv {rotAux.cod_pdv} inicializado')
    return Response(rotAux.buffer_resposta, status=status.HTTP_204_NO_CONTENT
                    )


@api_view(['PUT'])
def LoginUsuario(request):

    """ Login de um usuário em um PDV, para início de sessão
        - verifica se o usuária está cadastrado
        - verifica senha
        - verifica se usuário é do perfil operador de loja
        - atualiza tabela de usuário e PDV
        JSON de entrada:
            {
                "headerIn": {
                            "transação":<string>
                            "empresa": <digit>,
                            "loja": <digit>,
                            "pdv": <digit>,
                          }
                "usuario": <string>
                "senha" : <string>
            }
        JSON de saída:
            {
                headerOut": {
                              "codErro": <digit>,
                              "mensagem": <string>,
                             }
                "perfil": <digit>
            }
    """
    rotAux = RotinasAuxiliares(request.data)

    if not rotAux.setUp(DadosLogin):
        return Response(rotAux.buffer_resposta, status=status.HTTP_204_NO_CONTENT)

    try:
        user = User.objects.get(username=rotAux.usuario)
    except User.DoesNotExist:
        rotAux.MontaHeaderOut(1, f'Usuario {rotAux.usuario} não existe')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    if not check_password(rotAux.buffer_entrada['senha'], user.password):
        rotAux.MontaHeaderOut(106, f'{rotAux.TAB_MSG[106]}')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    try:
        userTEF = models.UsuarioTEF.objects.get(empresa=rotAux.cod_empresa,
                                                loja=rotAux.cod_loja,
                                                user=user.id)
    except models.UsuarioTEF.DoesNotExist:
        rotAux.MontaHeaderOut(4, f'Usuario {rotAux.usuario} não é desta loja')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    if userTEF.perfil_user != 4 and userTEF.perfil_user != 3:
        rotAux.MontaHeaderOut(5, f'Usuario {rotAux.usuario} não é operador de PDV')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    try:
        pdv = models.PDV.objects.get(empresa=rotAux.cod_empresa,
                                     loja=rotAux.cod_loja,
                                     codPDV=rotAux.cod_pdv)
    except models.PDV.DoesNotExist:
        rotAux.MontaHeaderOut(3, f'PDV {rotAux.cod_pdv} não existe para a loja {rotAux.cod_loja}')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    pdv.UsuarioAtivo = 0
    pdv.LastLogin = Now()
    pdv.save()

    rotAux.MontaHeaderOut(0, f'Login efetuado')

    return Response(rotAux.buffer_resposta, status=status.HTTP_204_NO_CONTENT
                    )



@api_view(['PUT'])
def AberturaPDV(request):
    """ Abertura de um PDV, para início de sessão
        - verifica se o PDV está inicializado
        - verifica se o usuário fez Login
        - verifica se usuário é do perfil operador de loja
        - atualiza tabela de PDV
        JSON de entrada:
            {
                "headerIn": {
                            "transação":<string>
                            "empresa": <digit>,
                            "loja": <digit>,
                            "pdv": <digit>,
                          }
                "usuario": <string>
            }
        JSON de saída:
            {
                headerOut": {
                              "codErro": <digit>,
                              "mensagem": <string>,
                             }
                "TransHabilitadas": {"TransDigitada": <boolean>
                                     "CreditoVista": <boolean>
                                     "CreditoParc": <boolean>
                                     "CreditoSemJunros": <boolean>
                                     "Debito": <boolean>
                                     "Cancelamento": <boolean>
                                    }
            }
    """
    TransHabilitadas = {}
    rotAux = RotinasAuxiliares(request.data)

    if not rotAux.setUp(DadosAberturaIn):
        return Response(rotAux.buffer_resposta, status=status.HTTP_204_NO_CONTENT)

    try:
        user = User.objects.get(username=rotAux.usuario)
    except User.DoesNotExist:
        rotAux.MontaHeaderOut(1, f'Usuario {rotAux.usuario} não existe')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    try:
        userTEF = models.UsuarioTEF.objects.get(empresa=rotAux.cod_empresa,
                                                loja=rotAux.cod_loja,
                                                user=user.id)
    except models.UsuarioTEF.DoesNotExist:
        rotAux.MontaHeaderOut(4, f'Usuario {rotAux.usuario} não é desta loja')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    if userTEF.perfil_user != 4:
        rotAux.MontaHeaderOut(5, f'Usuario {rotAux.usuario} não é operador de PDV')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    try:
        pdv = models.PDV.objects.get(empresa=rotAux.cod_empresa,
                                     loja=rotAux.cod_loja,
                                     codPDV=rotAux.cod_pdv)
    except models.PDV.DoesNotExist:
        rotAux.MontaHeaderOut(3, f'PDV {rotAux.cod_pdv} não existe para a loja {rotAux.cod_loja}')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    if not pdv.StatusPDV:
        rotAux.MontaHeaderOut(6, f'PDV {rotAux.cod_pdv} não está inicializado')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    if pdv.UsuarioAtivo != 0 and pdv.UsuarioAtivo != user.id:
        rotAux.MontaHeaderOut(7, f'PDV {rotAux.cod_pdv} já está aberto para usuário {user.id}')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    pdv.UsuarioAtivo = user.id
    pdv.LastLogin = Now()
    pdv.save()

    rotAux.MontaHeaderOut(0, f'Pdv {rotAux.cod_pdv} aberto')
    TransHabilitadas['TransDigitado'] = pdv.TransDigitado
    TransHabilitadas['TransVendaCreditoVista'] = pdv.TransVendaCreditoVista
    TransHabilitadas['TransVendaCreditoParc'] = pdv.TransVendaCreditoParc
    TransHabilitadas['TransVendaCreditoSemJuros'] = pdv.TransVendaCreditoSemJuros
    TransHabilitadas['TransVendaDebito'] = pdv.TransVendaDebito
    TransHabilitadas['TransCancelamento'] = pdv.TransCancelamento
    rotAux.buffer_resposta['TransHabilitadas'] = TransHabilitadas

    return Response(rotAux.buffer_resposta, status=status.HTTP_204_NO_CONTENT
                    )


@api_view(['PUT'])
def DadosTransacao(request):
    """ Retorna dados da transação a ser realizada, dependendo do tipo de transação e número do cartão, tais como BIN,
        Bandeira, Adquirente, etc.

        JSON de entrada:
                    {
                        "headerIn": {
                                      "transação": "DadosTrans",
                                      "empresa": 1,
                                      "loja": 2,
                                      "pdv": 2
                        },
                       "numCartao": "string de até 20 dígitod",
                       "validadeCartao": "string MM/AA",
                       "codSeg": "string 3",
                       "valorTrans": "número com 2 casas decimais",
                       "tipoTrans": "tipo da transação - débito/crédito/cancelamento"
                    }

        JSON de saída:
            {
                headerOut": {
                              "codErro": <digit>,
                              "mensagem": <string>,
                             }
                "bandeira": <string>
                "adquirente": <string>
                "adquirente2": <string>
                "BIN": <string>
            }
    """
    rotAux = RotinasAuxiliares(request.data)

    if not rotAux.setUp(DadosTransacaoIn):
        return Response(rotAux.buffer_resposta, status=status.HTTP_204_NO_CONTENT)

    if not rotAux.ValidacoesBasicas():
        return Response(rotAux.buffer_resposta, status=status.HTTP_204_NO_CONTENT)

    if not rotAux.ValidaCartao():
        return Response(rotAux.buffer_resposta, status=status.HTTP_204_NO_CONTENT)

    bandeira = models.Bandeira.objects.get(nomeBan=rotAux.bandeira)

    try:
        roteamento = models.Roteamento.objects.get(empresa=rotAux.cod_empresa,
                                                   loja=rotAux.cod_loja,
                                                   bandeira=bandeira.id)
    except models.Roteamento.DoesNotExist:
        rotAux.MontaHeaderOut(12, f'Cartão inválido - não existe roteamento')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    try:
        pdv = models.PDV.objects.get(empresa=rotAux.cod_empresa,
                                     loja=rotAux.cod_loja,
                                     codPDV=rotAux.cod_pdv)
    except models.PDV.DoesNotExist:
        rotAux.MontaHeaderOut(3, f'PDV {rotAux.cod_pdv} não existe para a loja {rotAux.cod_loja}')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    dataAbertura = f"{pdv.LastLogin:%Y%m%d}"
    dataAtual = f"{datetime.date.today():%Y%m%d}"
    if dataAbertura != dataAtual:
        rotAux.MontaHeaderOut(13, f'Execute a abertura do PDV')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    if pdv.UsuarioAtivo != rotAux.userAtual.id:
        rotAux.MontaHeaderOut(7, f'PDV {rotAux.cod_pdv} já está aberto para usuário {rotAux.userAtual.id}')
        return Response(rotAux.buffer_resposta, status=status.HTTP_404_NOT_FOUND)

    rotAux.MontaHeaderOut(0, f'Transaão OK')
    rotAux.buffer_resposta['bandeira'] = rotAux.bandeira
    rotAux.buffer_resposta['adquirente'] = roteamento.adiq.nomeAdiq
    rotAux.buffer_resposta['adquirente2'] = roteamento.adiq2.nomeAdiq
    num_cartao = rotAux.buffer_entrada["numCartao"]
    Bin = num_cartao[0:4]
    rotAux.buffer_resposta['BIN'] = Bin
    return Response(rotAux.buffer_resposta, status=status.HTTP_204_NO_CONTENT
                    )


@api_view(['PUT'])
def VendaCredito(request):
    """ Venda com cartão de crédito, à vista, parcelado com ou sem juros

        JSON de entrada:
                    {
                        "headerIn": {
                                      "transação": "CredVista ou CredParc ou CredParcJuros",
                                      "empresa": <inteiro>,
                                      "loja": <inteiro>,
                                      "pdv": <inteiro>,
                                      "usuario": "operCentro",
                        },
                       "numCartao": "string de até 20 dígitos",
                       "validadeCartao": "string MM/AA",
                       "codSeg": "string 3",
                       "valorTrans": "número com 2 casas decimais",
                       "numParcelas": "numero de parcelas"
                    }

        JSON de saída:
            {
                headerOut": {
                              "codErro": <digit>,
                              "mensagem": <string>,
                             }
                "codRespAdiq": <inteiro>
                "msgAdiq": "string"
                "bandeira": <string>
                "adquirente": <string>
                "codAut": <string>
                "NSUTef": <inteiro>
                "NSUHost": <inteiro>
                "dataHoraTrans": <timestamp>
                "cupomTrans": <string>
            }
    """
    rotAux = RotinasAuxiliares(request.data)

    if not rotAux.setUp(DadosVendaCreditoIn):
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    if not rotAux.ValidacoesBasicas():
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    if not rotAux.ValidaCartao():
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    bandeira = models.Bandeira.objects.get(nomeBan=rotAux.bandeira)

    try:
        roteamento = models.Roteamento.objects.get(empresa=rotAux.cod_empresa,
                                                   loja=rotAux.cod_loja,
                                                   bandeira=bandeira.id)
    except models.Roteamento.DoesNotExist:
        rotAux.MontaHeaderOut(12, f'Cartão inválido - não existe roteamento')
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    try:
        pdv = models.PDV.objects.get(empresa=rotAux.cod_empresa,
                                     loja=rotAux.cod_loja,
                                     codPDV=rotAux.cod_pdv)
    except models.PDV.DoesNotExist:
        rotAux.MontaHeaderOut(3, f'PDV {rotAux.cod_pdv} não existe para a loja {rotAux.cod_loja}')
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    dataAbertura = f"{pdv.LastLogin:%Y%m%d}"
    dataAtual = f"{datetime.date.today():%Y%m%d}"
    if dataAbertura != dataAtual:
        rotAux.MontaHeaderOut(13, f'Execute a abertura do PDV')
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    if pdv.UsuarioAtivo != rotAux.userAtual.id:
        rotAux.MontaHeaderOut(7, f'PDV {rotAux.cod_pdv} já está aberto para usuário {rotAux.userAtual.id}')
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    rotAux.MontaMsgHost(rotAux.buffer_entrada['headerIn']['transação'], roteamento.adiq)

    if not rotAux.EnviaRecebeMsgHost(roteamento.adiq.nomeAdiq): # erro de comunicação com a adquirente
        # rotAux.MontaHeaderOut(0, f'Transação OK')
        rotAux.buffer_resposta['codRespAdiq'] = 100
        rotAux.buffer_resposta['msgAdiq'] = rotAux.TAB_MSG[100]
        rotAux.buffer_resposta['bandeira'] = rotAux.bandeira
        rotAux.buffer_resposta['adquirente'] = roteamento.adiq.nomeAdiq
        rotAux.buffer_resposta['codAut'] = 0
        rotAux.buffer_resposta['NSU_TEF'] = rotAux.buffer_envio_host["NSU_TEF"]
        rotAux.buffer_resposta['NSU_HOST'] = 0
        rotAux.buffer_resposta['dataHoraTrans'] = f'{datetime.datetime.now():%Y-%m-%d %H:%M:%S}'
        rotAux.CriaLogTrans(rotAux.buffer_entrada['headerIn']['transação'], 'TimeOut')
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    rotAux.MontaHeaderOut(0, f'Transação OK')
    rotAux.buffer_resposta['codRespAdiq'] = rotAux.buffer_receb_host['codRespAdiq']
    rotAux.buffer_resposta['msgAdiq'] = rotAux.buffer_receb_host['msgResp']
    rotAux.buffer_resposta['bandeira'] = rotAux.bandeira
    rotAux.buffer_resposta['adquirente'] = roteamento.adiq.nomeAdiq
    rotAux.buffer_resposta['codAut'] = rotAux.buffer_receb_host["codAutorizacao"]
    rotAux.buffer_resposta['NSU_TEF'] = rotAux.buffer_receb_host["NSU_TEF"]
    rotAux.buffer_resposta['NSU_HOST'] = rotAux.buffer_receb_host["NSU_HOST"]
    rotAux.buffer_resposta['dataHoraTrans'] = rotAux.buffer_receb_host["dataHora"]
    if int(rotAux.buffer_receb_host['codRespAdiq']) == 0:
        rotAux.buffer_resposta['cupomTrans'] = rotAux.buffer_receb_host["comprovante"]
        rotAux.CriaLogTrans(rotAux.buffer_entrada['headerIn']['transação'], 'Pendente')
    else:
        rotAux.CriaLogTrans(rotAux.buffer_entrada['headerIn']['transação'], 'Negada')

    return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK
                    )


@api_view(['PUT'])
def ConfirmaDesfazTrans(request):
    """ Confirmação/desfazimento de uma transação (terceira perna)

        JSON de entrada:
                    {
                       "headerIn": {
                          "transação": "Confirma/Desfazimento",
                          "empresa": 1,
                          "loja": 2,
                          "pdv": 2
                       },
                   "usuario": "operCentro",
                   "NSU_Original": "1234567890",
                   "dataHoraOriginal": "data/hora trans original"
                    }

        JSON de saída:
            {
                headerOut": {
                              "codErro": <digit>,
                              "mensagem": <string>,
                             }
            }
    """
    rotAux = RotinasAuxiliares(request.data)

    if not rotAux.setUp(DadosConfirmacao):
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    if not rotAux.ValidacoesBasicas():
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    try:
        log = models.LogTrans.objects.get(NSU_TEF=rotAux.buffer_entrada['NSU_Original'])
    except models.LogTrans.DoesNotExist:
        rotAux.MontaHeaderOut(101, f'{rotAux.TAB_MSG[101]}')
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    rotAux.MontaMsgConfDesfHost(rotAux.buffer_entrada['headerIn']['transação'], log)

    if not rotAux.EnviaRecebeMsgHost(log.nomeAdiq):
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    rotAux.MontaHeaderOut(0, f'Transação OK')
    rotAux.buffer_resposta['codRespAdiq'] = rotAux.buffer_receb_host['codRespAdiq']
    rotAux.buffer_resposta['msgAdiq'] = rotAux.buffer_receb_host['msgResp']

    if int(rotAux.buffer_receb_host['codRespAdiq']) == 0:
        rotAux.buffer_resposta['NSU_TEF'] = rotAux.buffer_receb_host["NSU_TEF"]
        rotAux.buffer_resposta['NSU_HOST'] = rotAux.buffer_receb_host["NSU_HOST"]
        rotAux.buffer_resposta['dataHoraTrans'] = rotAux.buffer_receb_host["dataHora"]

        if rotAux.buffer_entrada['headerIn']['transação'] == "Confirma":
            log.statusTRN = "Efetuada"
        else:
            log.statusTRN = "Desfeita"
        log.NSU_ConfDesfCanc = rotAux.buffer_resposta['NSU_TEF']
        log.dataHoraConfDesfCanc = rotAux.buffer_receb_host["dataHora"]
        log.save()

    return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK
                    )


@api_view(['PUT'])
def Cancelamento(request):
    """ Cancelamento de uma transação

        JSON de entrada:
                    {
                       "headerIn": {
                          "transação": "Cancelamento",
                          "empresa": 1,
                          "loja": 2,
                          "pdv": 2
                       },
                    "usuario": "operCentro",
                    "NSU_Original": "1234567890",
                    "dataHoraOriginal": "data/hora trans original",
                    "numCartao": "5536360607552502",
                    "valorTrnas": 10.50,
                    "dataValidade": "07/23",
                    "NSU_HOST_Original": "1234567890",
                    }

        JSON de saída:
            {
                headerOut": {
                              "codErro": <digit>,
                              "mensagem": <string>,
                             }
                "codRespAdiq": 99,
                "msgAdiq": "string",
                "codAut": "string",
                "NSUTef": "string",
                "NSUHost": "string",
                "dataHoraTrans": "data/hora aprovação",
                "cupomTrans": "comprovante",
            }
    """
    rotAux = RotinasAuxiliares(request.data)

    if not rotAux.setUp(DadosCancelamento):
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    if not rotAux.ValidacoesBasicas():
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    if not rotAux.ValidaCartao():
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    bandeira = models.Bandeira.objects.get(nomeBan=rotAux.bandeira)

    try:
        log = models.LogTrans.objects.get(NSU_TEF=rotAux.buffer_entrada['NSU_Original'])
    except models.LogTrans.DoesNotExist:
        rotAux.MontaHeaderOut(101, f'{rotAux.TAB_MSG[101]}')
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    dataTransLog = log.dataLocal
    try:
        dataTransMsg = datetime.date.fromisoformat(rotAux.buffer_entrada['dataOriginal'])
    except ValueError:
        rotAux.MontaHeaderOut(102, f'{rotAux.TAB_MSG[102]}')
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    if dataTransMsg != dataTransLog:
        print(dataTransLog)
        print(dataTransMsg)
        rotAux.MontaHeaderOut(102, f'{rotAux.TAB_MSG[102]}')
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    if rotAux.buffer_entrada['numCartao'] != log.numCartao:
        rotAux.MontaHeaderOut(103, f'{rotAux.TAB_MSG[103]}')
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    # print(log.valorTrans)
    # print(rotAux.buffer_entrada['valorTrans'])
    valorTransLog = float(log.valorTrans)
    valorTransMsg = float(rotAux.buffer_entrada['valorTrans'])

    if valorTransMsg != valorTransLog:
        print(valorTransMsg)
        print(valorTransLog)
        rotAux.MontaHeaderOut(104, f'{rotAux.TAB_MSG[104]}')
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    if rotAux.buffer_entrada['NSU_HOST_Original'] != log.NSU_HOST:
        rotAux.MontaHeaderOut(105, f'{rotAux.TAB_MSG[105]}')
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    adiq = models.Adquirente.objects.get(nomeAdiq=log.nomeAdiq)

    rotAux.MontaMsgHost(rotAux.buffer_entrada['headerIn']['transação'], adiq)

    if not rotAux.EnviaRecebeMsgHost(log.nomeAdiq):
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    rotAux.MontaHeaderOut(0, f'Transação OK')
    rotAux.buffer_resposta['codRespAdiq'] = rotAux.buffer_receb_host['codRespAdiq']
    rotAux.buffer_resposta['msgAdiq'] = rotAux.buffer_receb_host['msgResp']
    rotAux.buffer_resposta['NSU_TEF'] = rotAux.buffer_receb_host["NSU_TEF"]
    rotAux.buffer_resposta['NSU_HOST'] = rotAux.buffer_receb_host["NSU_HOST"]
    rotAux.buffer_resposta['dataHoraTrans'] = rotAux.buffer_receb_host["dataHora"]
    rotAux.buffer_resposta['codAut'] = rotAux.buffer_receb_host["codAutorizacao"]
    rotAux.buffer_resposta['adquirente'] = log.nomeAdiq
    if int(rotAux.buffer_receb_host['codRespAdiq']) == 0:
        rotAux.buffer_resposta['cupomTrans'] = rotAux.buffer_receb_host["comprovante"]
        log.statusTRN = "Cancelada"
        log.NSU_Canc = rotAux.buffer_resposta['NSU_TEF']
        log.dataHoraCanc = rotAux.buffer_receb_host["dataHora"]
        log.save()

    rotAux.CriaLogTrans(rotAux.buffer_entrada['headerIn']['transação'], 'Pendente')

    return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK
                    )


@api_view(['PUT'])
def TrataSonda(request):

    """ Trata mensagem de sonda, enviada pela adquirente

        JSON de entrada e saída:
                    {
                        "dataHora": "2022-09-29 19:40:38.694005",
                        "NSU_TEF": "1234567890",
                        "codResp": "0",
                        "statusTRN": "Pendente"
                    }
    """
    rotAux = RotinasAuxiliares(request.data)

    print ('---> Msg Rec. <----\n')
    print(rotAux.buffer_entrada, '\n')

    try:
        log = models.LogTrans.objects.get(NSU_TEF=rotAux.buffer_entrada['NSU_TEF'])
    except models.LogTrans.DoesNotExist:
        rotAux.buffer_resposta['codResp'] = 99
        return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK)

    rotAux.buffer_resposta['NSU_TEF'] = log.NSU_TEF
    rotAux.buffer_resposta['codResp'] = 0
    rotAux.buffer_resposta['statusTRN'] = log.statusTRN

    return Response(rotAux.buffer_resposta, status=status.HTTP_200_OK
                    )
