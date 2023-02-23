"""
      Layout das mensagems de entrada das API´s.

      Estas estruturas serão utilizadas para validar as mensagens recebidas pelas API´s,
      no padrão JSON
"""

DadosTransacaoIn = {
    "headerIn": {
        "transação": "DadosTrans",
        "empresa": 1,
        "loja": 2,
        "pdv": 2
    },
    "usuario": "operCentro",
    "numCartao": "5536360607552502",
    "validadeCartao": "0723",
    "codSeg": "445",
    "valorTrans": 10.50,
    "tipoTrans": "tipo da transação - débito/crédito/cancelamento"
}

DadosLogin = {
    "headerIn": {
        "transação": "Login",
        "empresa": 1,
        "loja": 2,
        "pdv": 2
    },
    "usuario": "operCentro",
    "senha": "**********",
    "inicializaLoja": True
}

DadosAberturaIn = {
    "headerIn": {
        "transação": "AberturaPDV",
        "empresa": 1,
        "loja": 2,
        "pdv": 2
    },
    "usuario": "operCentro"
}

DadosInicializaIn = {
    "headerIn": {
        "transação": "InicializaPDV",
        "empresa": 1,
        "loja": 2,
        "pdv": 2
    },
    "usuario": "janete"
}

DadosVendaCreditoIn = {
    "headerIn": {
        "transação": "CredVista",
        "empresa": 1,
        "loja": 2,
        "pdv": 2
    },
    "usuario": "operCentro",
    "numCartao": "5536360607552502",
    "validadeCartao": "07/23",
    "codSeg": "445",
    "valorTrans": 10.50,
    "numParcelas": 0
}

DadosVendaCreditoOut = {
    "headerOut": {
        "codErro": 99,
        "mensagem": 'string',
    },
    "codRespAdiq": 99,
    "msgAdiq": "string",
    "bandeira": "string",
    "adquirente": "string",
    "codAut": "string",
    "NSU_TEF": "string",
    "NSU_HOST": "string",
    "dataHoraTrans": "data/hora aprovação",
    "cupomTrans": "comprovante",
}

DadosConfirmacao = {
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

DadosConfirmacaOut = {
    "headerOut": {
        "codErro": 99,
        "mensagem": 'string',
    },
    "codRespAdiq": 99,
    "msgAdiq": "string",
    "NSUTef": "string",
    "NSUHost": "string",
    "dataHoraTrans": "data/hora aprovação",
}

DadosCancelamento = {
    "headerIn": {
        "transação": "Cancelamento",
        "empresa": 1,
        "loja": 2,
        "pdv": 2
    },
    "usuario": "operCentro",
    "NSU_Original": "1234567890",
    "dataOriginal": "data trans original",
    "numCartao": "5536360607552502",
    "valorTrans": 10.50,
    "validadeCartao": "07/23",
    "NSU_HOST_Original": "1234567890",
    "supervisor": "janete",
    "senha": "*******"
}

DadosCancelamentoOut = {
    "headerOut": {
        "codErro": 99,
        "mensagem": 'string',
    },
    "codRespAdiq": 99,
    "msgAdiq": "string",
    "codAut": "string",
    "NSU_TEF": "string",
    "NSU_HOST": "string",
    "dataHoraTrans": "data/hora aprovação",
    "cupomTrans": "comprovante",
}

DadosPesqLog = {
    "headerIn": {
        "transação": "PesqLog",
        "empresa": 1,
        "loja": 2,
        "pdv": 2
    },
    "usuario": "operCentro",
    "NSU": 273,
    "dataInicial": "data inicial para pesquisa",
    "dataFinal": "data final para pesquisa",
    "statusTrans": "status da transação"
}

