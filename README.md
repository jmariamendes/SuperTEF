# SuperTEF


Plataforma completa para a realização de simulação de transações de Transferência Eletrõnica de Fundos (TEF), com cartões de crédito e débito.

## 1.	Objetivo
A plataforma **SuperTEF** foi desenvolvida com o objetivo de fornecer um ambiente simulado para transações de TEF, incluindo servidor de TEF, simulador das adquirentes, simuladores de PDV em Windows e Android, e o simulador de PinPad.

Totalmente desenvolvido em Python, o projeto serviu também para testar a utilização desta ferramenta em um ambiente totalmente transacional, que exige alta performance, segurança e estabilidade.

## 2.	Componentes
A plataforma **SuperTEF** é composta pelos seguintes projetos:
  ###  2.1.	Servidor SuperTEF
Módulo principal da plataforma, é responsável pela administração do sistema, através de um site onde é possível o cadastramento de todas as entidades necessárias para a realização e controle das transações de TEF.
É responsável também por receber as solicitações de transações de TEF dos PDV´s, via API´s, e encaminhá-las para a autorização pela adquirente correspondente.
  ### 2.2.	Simulador de adquirente
Responsável por receber as transações de TEF do servidor **SuperTEF** e simular as respostas de uma adquirente.
  ### 2.3.	Simulador de PDV
Responsável por simular a captura das transações de TEF em um PDV (Ponto de Venda) de uma loja e submetê-las para autorização ao servidor **SuperTEF**. Estão disponíveis as transações com cartões de crédito, à vista e parcelado, e com cartões de débito.
  ### 2.4.	Simulador de PinPad
Responsável por simular a captura da senha, para a realização de uma transação com cartão de débito.

## 3.	Topologia

## 4. Servidor SuperTEF
Está dividido em dois módulos: 
### 4.1 Site administrativo
O site  foi desenvolvido em Python, Django e banco de dados Postgre, e possui administrações (cadastramento, alteração e deleção) para as seguintes principais entidades:
- Empresa
- Loja
- PDV
- Usuário
- Bandeiras
- Adquirentes
- Número lógico
- Roteamento de transações
### 4.2 Servidor API
O servidor de API foi desenvolvido em Python, Django REST/JSON e Postgre e disponibiliza as seguintes API´s para os PDV´s:
- Incialização de PDV
- Abertura de PDV
- Login
- Venda com cartão de crédito, à vista, parcelado com e sem juros
- Venda com cartão de débito
- Cancelamento de transação
- Relatório de transações

Para cada transação financeira recebida do PDV(cartão de crédito e débito, cancelamento) o servidor **SuperTEF** se comunica com o simulador de adquirente, para autorizar a transação.

## 5. Simulador de adquirente
O objetivo do simulador de adquirente é receber uma transação de TEF, com cartão de crédito ou débito, do servidor **SuperTEF** e simular a autorização, ou não, desta transação.
Ele foi desenvolvido em Python, Django, Django REST/JSON e Postgre. 
A comunicação do servidor **SuperTEF** com o simulador é via API REST.
Como um simulador, ele permite que o usuário faça algumas configurações para a simulação das transações, tais como:
- Simular time out
- Simular um determinado erro, como resposta da transação
- Ativar/desativar monitoração de transações
- Ativar/desativar o envio de sonda

## 6. Simulador de PDV
O simulador de PDV permite gerar transações de TEF para autorização pelo servidor **SuperTEF**.
Foram desenvolvidos dois simuladores, um rodando em Windows e outro em Android.
A versão Windows utiliza Python e PyQT (PSide6), com o QT Designer para o desenho das telas. A comunicação com o servidor **SuperTEF** é feita através de API REST/JSON, utilizando o pacote Requests do Python.
A versão Android utiliza Python e KivyMD. A comunicação com o servidor **SuperTEF** é feita através de API REST/JSON, utilizando o pacote URLRequests do Kivy

Em ambas versões, as funções disponibilizadas são:
- Login
- Inicialização e Abertura do PDV
- Venda com cartão de crédito, à vista e parcelado com e sem juros
- Venda com cartão de débito
- Cancelamento
- Relatório de transações (somente para a versão Windows)

Para cada transação aprovada, é exibido o comprovante TEF na tela e opcionalmente enviado via e-mail para o cliente.

## 7. Simulador de Pin Pad
Para tornar o ambiente de simulação do **SuperTEF** mais próximo possível de um ambiente real, foi desenvolvido um simulador de Pin Pad, para capturar a senha e o cartão do "cliente".
O simulador roda em Android e foi desenvolvido em Python e KivyMD. A comunicação do simulador com o PDV, tanto em Windows quanto em Android, é via TCP/IP Socket utilizando a biblioteca Twisted Reactor do Kivy.
As funções disponibilizadas no Pin Pad para o PDV são:
- msg - exibe uma mensagem na linha de status do Pin Pad
- geral - mensagem após a conexão com o PDV. Será usada como mensagem de status
- aviso - exibe uma mensagem na linha de status por um determinado tempo
- senha - exibe uma mensagem, faz a leitura da senha e transmite para o PDV
- card - exibe uma mensagem e faz a leitura do cartão e transmite para o PDV
- sair - encerra o aplicativo no Android
