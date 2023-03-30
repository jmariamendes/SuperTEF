
""" Rotinas auxiliares e variáveis globais """

import datetime
import re

from django.contrib.auth.models import User
from django.db import transaction

import json
import requests
from requests.exceptions import HTTPError
from requests.exceptions import Timeout

from . import models


class RotinasAuxiliares():

    TAB_MSG = {
        0: "0 - Transação OK",
        1: "1 - Usuario {self.usuario} não existe",
        2: "2 - Loja/empresa {rotAux.cod_loja}/{rotAux.cod_empresa} não existe",
        3: "3 - PDV {rotAux.cod_pdv} não existe para a loja {rotAux.cod_loja}",
        4: "4 - Usuario {rotAux.usuario} não é desta loja",
        5: "5 - Usuario {rotAux.usuario} não tem premissão para inicializar PDV",
        6: "6 - PDV {rotAux.cod_pdv} não está inicializado",
        7: "7 - PDV {rotAux.cod_pdv} já está aberto para usuário {user.id}",
        8: "8 - Cartão inválido - tamanho",
        9: "9 - Cartão inválido - não numérico",
        10: "10 - Cartão inválido - dígito",
        11: "11 - Cartão inválido - BIN",
        12: "12 - Cartão inválido - não existe roteamento",
        13: "13 - Dados inválidos",
        14: "14 - Código transação inválido",
        99: "99 - Erro comunicação com adquirente",
        100: "100 - Timeout na comunicação com adquirente",
        101: "101 - NSU inválido",
        102: "102 - Dado cancelamento inválido - data/hora",
        103: "103 - Dado cancelamento inválido - cartão",
        104: "102 - Dado cancelamento inválido - valor",
        105: "102 - Dado cancelamento inválido - NSU Host",
        106: "106 - Senha inválida",
    }

    BINS = ('3',  # amex
            '4',  # Visa
            '5',  # Mastercard
            '6',  # Elo
            )

    COD_TRANS = ('Login',
                 'AberturaPDV',
                 'InicializaPDV',
                 'Cancelamento',
                 'CredVista',
                 'CredParc',
                 'CredParcComJuros',
                 'Debito',
                 'DadosTrans',
                 'Confirma',
                 'Desfazimento',
                 'PesqLog'
                 )

    buffer_entrada = {}  # JSON de entrada
    buffer_resposta = {}  # JSON de saída
    buffer_envio_host = {} # msg enviada para adquirente/host
    buffer_receb_host = {} # msg recebida da adquirente/host
    headerOut = {}  # header das msgs de saída
    headerIn = {}  # header das msgs de entrada

    def __init__(self, msgIn):
        self.TAB_MSG = {
            0: '0 - Transação OK',
            1: "1 - Usuario {self.usuario} não existe",
            2: "2 - Loja/empresa {rotAux.cod_loja}/{rotAux.cod_empresa} não existe",
            3: "3 - PDV não inicializado",
            4: "4 - Usuario {rotAux.usuario} não é desta loja",
            5: "5 - Usuario {rotAux.usuario} não tem premissão para inicializar PDV",
            6: "6 - PDV {rotAux.cod_pdv} não está inicializado",
            7: "7 - PDV {rotAux.cod_pdv} já está aberto para usuário {user.id}",
            8: "8 - Cartão inválido - tamanho",
            9: "9 - Cartão inválido - não numérico",
            10: "10 - Cartão inválido - dígito",
            11: "11 - Cartão inválido - BIN",
            12: "12 - Cartão inválido - não existe roteamento",
            13: "13 - Dados inválidos",
            14: "14 - Código transação inválido",
            99: "99 - Erro comunicação com adquirente",
            100: "100 - Timeout na comunicação com adquirente",
            101: "101 - NSU inválido",
            102: "102 - Dado cancelamento inválido - data/hora",
            103: "103 - Dado cancelamento inválido - cartão",
            104: "104 - Dado cancelamento inválido - valor",
            105: "105 - Dado cancelamento inválido - NSU Host",
            106: "106 - Senha inválida",
            107: "107 - Dado cancelamento inválido - Transação",
            108: "108 - Não existem registros para esta seleção"
        }
        self.bandeira = ''
        self.userTEFAtual = None
        self.userAtual = None
        self.lojaAtual = None
        self.msg = msgIn
        self.buffer_entrada = msgIn
        self.buffer_resposta = {}
        self.buffer_receb_host = {}
        self.cod_empresa = 0
        self.cod_loja = 0
        self.cod_pdv = 0
        self.usuario = ''
        # self.URL = f"http://localhost:5000/api/"
        self.URL = f"http://simadiq.herokuapp.com/api/"

    def setUp(self, LayOut):
        """ Verifica se a msg de entrada contém todos os campos obrigatórios """

        for campo, valor in LayOut.items():
            if campo not in self.buffer_entrada:
                print(campo)
                self.MontaHeaderOut(13, self.TAB_MSG [13])
                return False
            else:
                if isinstance(valor, dict):
                    for i in valor:
                        if i not in self.buffer_entrada[campo]:
                            print(i)
                            self.MontaHeaderOut(13, self.TAB_MSG [13])
                            return False

        if self.buffer_entrada['headerIn']['transação'] not in self.COD_TRANS:
            self.MontaHeaderOut(14, self.TAB_MSG [14])
            return False

        self.headerIn = self.buffer_entrada["headerIn"]
        self.cod_empresa = int(self.headerIn["empresa"])
        self.cod_loja = int(self.headerIn["loja"])
        self.cod_pdv = int(self.headerIn["pdv"])
        self.usuario = self.buffer_entrada["usuario"]
        return True

    def geraJSON(self, dicionario, msg):

        """ Converte a msg recebida em string para o dicionário JSON.
            Para a conversão serõa utilizados como base os campos do dicionário e os valores correspondentes aos campos,
            serão retirados da msg.
            Não será feita nenhuma consistência, porque acredita-se que a msg de entrada é uma cópia fiel do dicionário,
            mas em formato string """

        for campo, valor in dicionario.items():
            """ Acessa todos as chaves do dicionário. Para cada chave, procura o campo correspondente na msg e atribui o valor 
                deste campo na msg à chave no dicionário"""
            if isinstance(valor, dict):         # campo é um sub-dicionário do dicionário
                self.geraJSON(valor, msg) # chama de novo a geraJSON, passando o sub-dicionario como parametro.
                continue

            result = re.finditer(r"" + campo + "': ", msg) # procura a chave na msg, para atribuir o valor
            for i in result: # não existe chave duplicada no dict, então este for é somente porque não consigo acessar
                             # o resultado de outra forma
                inicio = i.start(0)
                fim = i.end(0)

            if msg[fim] == "'": # valor é alfanumérico, delimitado por '', elimina o '
                fim += 1
                numerico = False
            else:
                numerico = True

            resultVal = re.finditer(r"[A-Za-z0-9]+", msg[fim:len(msg)]) # extrai o valor desta chave na msg
            for j in resultVal: # sempre pega o primeiro valor da pesquisa
                inicio = j.start(0)
                fim = j.end(0)
                valcampo = j.group(0)
                if numerico:
                    dicionario[campo] = int(j.group(0))
                else:
                    dicionario[campo] = j.group(0)
                break

        """ obs.: todo parametro do tipo dicionario é passado como referencia pelo Python, então não precisaria dar
            o return com o valor da variável. Isto foi colocado somente para deixar mais documentado. """
        return dicionario

    def MontaHeaderOut(self, codErro, mensagem):
        self.headerOut['codErro'] = codErro
        self.headerOut['mensagem'] = mensagem
        self.buffer_resposta['headerOut'] = self.headerOut

    def ValidacoesBasicas(self):

        try:
            self.userAtual = User.objects.get(username=self.usuario)
        except User.DoesNotExist:
            self.MontaHeaderOut(1, f'Usuario {self.usuario} não existe')
            return False

        try:
            self.userTEFAtual = models.UsuarioTEF.objects.get(empresa=self.cod_empresa,
                                                              loja=self.cod_loja,
                                                              user=self.userAtual.id)
        except models.UsuarioTEF.DoesNotExist:
            self.MontaHeaderOut(4, f'Usuario {self.usuario} não é desta loja')
            return False

        try:
            self.lojaAtual = models.Loja.objects.get(empresa=self.cod_empresa, codLoja=self.cod_loja)
        except models.Loja.DoesNotExist:
            self.MontaHeaderOut(2, f'Loja/empresa {self.cod_loja}/{self.cod_empresa} não existe')
            return False

        return True

    def ValidaCartao(self):
        import re
        num_cartao = self.buffer_entrada["numCartao"]
        if len(num_cartao) < 12 or len(num_cartao) > 19:
            self.MontaHeaderOut(8, f'Cartão inválido - tamanho')
            return False

        if re.search(r'[^0-9]', num_cartao):
            self.MontaHeaderOut(9, f'Cartão inválido - não numérico')
            return False

        if not self.CalculoDigitoCartao(num_cartao):
            self.MontaHeaderOut(10, f'Cartão inválido - dígito')
            return False

        if num_cartao[0] not in self.BINS:
            self.MontaHeaderOut(11, f'Cartão inválido - BIN')
            return False

        match num_cartao[0]:

            case '3':
                self.bandeira = 'Amex'
            case '4':
                self.bandeira = 'Visa'
            case '5':
                self.bandeira = 'Mastercard'
            case '6':
                self.bandeira = 'Elo'

        return True

    def CalculoDigitoCartao(self, num_cartao):

        """O DV corresponde ao número que falta  para inteirar como múltiplo de 10 a soma da multiplicação de cada
                algarismo da base por 2, 1, 2, 1, 2, 1, 2, 1, 2, 1… a partir da unidade até o penúltimo.
                Em cada multiplicação com valores acima de 9, faremos a “regra dos 9”. Veja um exemplo:
                o número do cartão é 2231 1234 1200 345X;
                fazendo a multiplicação de cada algarismo pelo número apontado acima, temos como resultado:
                4 + 2 + 6 + 1 + 2 + 2 + 6 + 4 + 2 + 2 + 0 + 0 + 6 +4 +1 = 42;
                Para chegar até o múltiplo de 10 mais próximo, que seria 50, faltam 8.
        """

        tot = 0
        x = 2
        for i in range(0, len(num_cartao) - 1):
            y = int(num_cartao[i]) * x
            if y > 9:
                y -= 9
            tot += y
            if x == 2:
                x = 1
            else:
                x = 2
        dig = 10 - int(tot % 10)
        if dig == int(num_cartao[len(num_cartao) - 1]):
            return True
        else:
            return False

    def MontaMsgHost(self, CodTrans, Adquirente):
        """ Monta a mensagem a ser enviada para a adquirente, dependendo do código da transação.
            Os campos das msgs serão baseados na especificação ISO-8583, mas no padrão JSON
         """

        self.buffer_envio_host["numCartao"] = self.buffer_entrada["numCartao"]
        self.buffer_envio_host["valorTrans"] = self.buffer_entrada["valorTrans"]
        self.buffer_envio_host["dataHora"] = f'{datetime.datetime.now():%d-%m-%Y %H:%M:%S}'

        """ Calcula o NSU Tef atual """

        with transaction.atomic():
            empresa = models.Empresa.objects.select_for_update().get(codEmp=self.cod_empresa)
            empresa.ultimoNSU += 1
            self.buffer_envio_host["NSU_TEF"] = empresa.ultimoNSU
            empresa.save()
        self.buffer_envio_host["dataLocal"] = f'{datetime.date.today():%Y-%m-%d}'
        self.buffer_envio_host["horaLocal"] = f'{datetime.datetime.now():%H:%M:%S}'
        self.buffer_envio_host["modoEntrada"] = 1 # cartao digitado
        self.buffer_envio_host["identPDV"] = self.cod_pdv
        if CodTrans != "Cancelamento" and CodTrans != "Debito":
            self.buffer_envio_host["codSeg"] = self.buffer_entrada["codSeg"]
            self.buffer_envio_host["validadeCartao"] = self.buffer_entrada["validadeCartao"]
            self.buffer_envio_host["numParcelas"] = self.buffer_entrada["numParcelas"]
        elif CodTrans == "Cancelamento":
            self.buffer_envio_host["numParcelas"] = 0
            self.buffer_envio_host["NSU_Original"] = self.buffer_entrada["NSU_Original"]
            self.buffer_envio_host["DataOriginal"] = self.buffer_entrada["dataOriginal"]
        elif CodTrans == "Debito":
            self.buffer_envio_host["numParcelas"] = 0
            self.buffer_envio_host["senha"] = self.buffer_entrada["senha"]

        """ Lê o número lógico da empresa/loja, para a adquirente que irá capturar a transação
        """

        numLogico = models.NumLogico.objects.get (empresa=self.cod_empresa,
                                                  loja=self.cod_loja,
                                                  adiq=Adquirente)
        self.buffer_envio_host["numLogico"] = numLogico.numlogico
        self.buffer_envio_host["codLoja"] = self.cod_loja
        self.buffer_envio_host["codTrans"] = CodTrans

        match CodTrans:

            case 'Cancelamento':
                self.buffer_envio_host["codProc"] = '960420'
            case 'CredVista':
                self.buffer_envio_host["codProc"] = '003000'
            case 'CredParc':
                self.buffer_envio_host["codProc"] = '003100'
            case 'CredParcComJuros':
                self.buffer_envio_host["codProc"] = '003800'
            case 'Debito':
                self.buffer_envio_host["codProc"] = '002000'

    def MontaMsgConfDesfHost(self, CodTrans, Log):
        """ Monta a mensagem de confirmação/desfazimento a ser enviada para a adquirente.
            Os campos das msgs serão baseados na especificação ISO-8583, mas no padrão JSON
         """

        dadosTransOrig = {}
        self.buffer_envio_host["valorTrans"] = Log.valorTrans
        self.buffer_envio_host["dataHora"] = f'{datetime.datetime.now():%d-%m-%Y %H:%M:%S}'

        """ Calcula o NSU Tef atual """

        with transaction.atomic():
            empresa = models.Empresa.objects.select_for_update().get(codEmp=self.cod_empresa)
            empresa.ultimoNSU += 1
            self.buffer_envio_host["NSU_TEF"] = empresa.ultimoNSU
            empresa.save()
        self.buffer_envio_host["dataLocal"] = f'{datetime.date.today():%Y-%m-%d}'
        self.buffer_envio_host["horaLocal"] = f'{datetime.datetime.now():%H:%M:%S}'
        self.buffer_envio_host["modoEntrada"] = 1 # cartao digitado
        self.buffer_envio_host["numPDV"] = Log.codPDV
        self.buffer_envio_host["numLogico"] = Log.numLogico

        if CodTrans == "Confirma":
            if Log.codTRN == "Cancelamento":
                self.buffer_envio_host["codProc"] = "000402"
                dadosTransOrig["tipoTrnOriginal"] = "0400"
            else:
                self.buffer_envio_host["codProc"] = "000202"
                dadosTransOrig["tipoTrnOriginal"] = "0200"
        else:
            self.buffer_envio_host["codProc"] = "000420"
            if Log.codTRN == "Cancelamento":
                dadosTransOrig["tipoTrnOriginal"] = "0400"
            else:
                dadosTransOrig["tipoTrnOriginal"] = "0200"

        # dadosTransOrig["NSU_Original"] = Log.NSU_TEF
        # dadosTransOrig["dataHoraTrnOriginal"] = Log.dataHoraHost
        # self.buffer_envio_host["dadosTrnOriginal"] = dadosTransOrig
        self.buffer_envio_host["NSU_Original"] = Log.NSU_TEF
        self.buffer_envio_host["dataHoraTrnOriginal"] = Log.dataHoraHost

    def EnviaRecebeMsgHost(self, Adquirente):

        """ Envia e recebe a mensagem para autorização da transação, para a adquirente configurada no
            roteamento para a loja que está fazendo a transação, de acordo com a bandeira do cartão
         """

        enderecoUrl = f"{self.URL}v1/simuladiq/{Adquirente}"
        dados = self.buffer_envio_host
        try:
            response = requests.put(enderecoUrl, data=self.buffer_envio_host, timeout=30)
        except Timeout:
            self.MontaHeaderOut(100, f'{self.TAB_MSG[100]}')
            return False
        except HTTPError as http_err:
            self.MontaHeaderOut(99, f'{self.TAB_MSG[99]} - {http_err}')
            return False
        except Exception as err:
            self.MontaHeaderOut(99, f'{self.TAB_MSG[99]} - {err}')
            return False

        self.buffer_receb_host = response.json()
        return True

    def CriaLogTrans(self, CodTrans, StatusTrans):

        if StatusTrans != 'TimeOut':

            log_trans = models.LogTrans.objects.create (NSU_TEF=self.buffer_receb_host["NSU_TEF"],
                                                        dataLocal=self.buffer_receb_host["dataLocal"],
                                                        horaLocal=self.buffer_receb_host["horaLocal"],
                                                        NSU_HOST=self.buffer_receb_host["NSU_HOST"],
                                                        dataHoraHost=self.buffer_receb_host["dataHora"],
                                                        codEmp=self.cod_empresa,
                                                        codLoja=self.cod_loja,
                                                        codPDV=self.cod_pdv,
                                                        numLogico=self.buffer_envio_host["numLogico"],
                                                        codTRN=CodTrans,
                                                        statusTRN=StatusTrans,
                                                        codResp=self.buffer_receb_host['codRespAdiq'],
                                                        msgResp=self.buffer_receb_host['msgResp'],
                                                        numCartao=self.buffer_envio_host["numCartao"],
                                                        valorTrans=self.buffer_envio_host["valorTrans"],
                                                        nomeBan=self.bandeira,
                                                        nomeAdiq=self.buffer_resposta['adquirente'],
                                                        numParcelas=self.buffer_envio_host["numParcelas"]
                                                        )
        else:
            log_trans = models.LogTrans.objects.create (NSU_TEF=self.buffer_envio_host['NSU_TEF'],
                                                        dataLocal=self.buffer_envio_host["dataLocal"],
                                                        horaLocal=self.buffer_envio_host["horaLocal"],
                                                        NSU_HOST=0,
                                                        dataHoraHost=self.buffer_resposta['dataHoraTrans'],
                                                        codEmp=self.cod_empresa,
                                                        codLoja=self.cod_loja,
                                                        codPDV=self.cod_pdv,
                                                        numLogico=self.buffer_envio_host["numLogico"],
                                                        codTRN=CodTrans,
                                                        statusTRN=StatusTrans,
                                                        codResp=self.buffer_resposta['codRespAdiq'],
                                                        msgResp=self.buffer_resposta['msgAdiq'],
                                                        numCartao=self.buffer_envio_host["numCartao"],
                                                        valorTrans=self.buffer_envio_host["valorTrans"],
                                                        nomeBan=self.bandeira,
                                                        nomeAdiq=self.buffer_resposta['adquirente'],
                                                        numParcelas=self.buffer_envio_host["numParcelas"]
                                                        )

        log_trans.save()

