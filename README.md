# Dados Públicos CNPJ - Conversão para CSV ou SQLITE
Utilitário em Python para carregar a base completa de CNPJ [disponibilizada pela Receita Federal](http://idg.receita.fazenda.gov.br/orientacao/tributaria/cadastros/cadastro-nacional-de-pessoas-juridicas-cnpj/dados-publicos-cnpj) (aprox. 85 GB!) e transformá-la em arquivos csv ou sqlite para fácil consumo. Processa dados de empresas, sócios e CNAEs.


# Configurações prévias
Para executar o script, é necessário que seu sistema contenha essas instalações:

## Python
Versão mais atual, caso não consiga executar usando somente o comando `python`. Para isso, execute no terminal (se estiver usando sistemas GNU/Linux derivados do Debian):

` $ sudo apt upgrade python3`

## Gerenciador de Pacotes do Python (Pip)
A versão mais atual. Se estiver usando Python3:

`$ python3 -m pip install --upgrade pip`

## Biblioteca de Data Science "Pandas"
A versão mais atual da biblioteca [Pandas](https://pandas.pydata.org) para Python. Para instalar via Pip:

`$ python3 -m pip install pandas`

## Pacote NumPy
A princípio, não é necessário. O script neste repositório usa funções da biblioteca [Pandas](https://pandas.pydata.org), que utiliza uma extensão de NumPy chamada [NumExpr](#numexpr). Então, **caso** seu terminal retorne erros por ausência do pacote [NumPy](https://pypi.org/project/numpy/), esse é o motivo. Para instalá-lo (se precisar):

`$ python3 -m pip install numpy`

## NumExpr
A [Pandas](https://pandas.pydata.org) usa. É uma extensão que melhora a velocidade de análise no pacote [NumPy](#pacote-numpy). Para instalar a versão mais atual da [NumExpr](https://pypi.org/project/numexpr):

`$ python3 -m pip install numexpr`


# Antes de executar
Tenha em mente que essa base de dados da RF é imensa!
Para executar esse script, é bastante provável que sua máquina (a não ser que seja um supercomputador) dedique bastante tempo a essa execução, podendo variar de 1 a 4 horas.

O script informa no terminal o parcial do processamento, mostrando o "bloco" (conjunto parcial) de linhas que está sendo convertido. Cada bloco contempla 100.000 linhas (registros) da base de dados.
Ao todo, são 724 blocos processados, o que quer dizer que a base de dados da RF, na versão publicada em 23/11/2018, tem entre 72.400.000 e 72.500.000 linhas!

Esse não é o total de CNPJs cadastrado, pois além dos CNPJs o arquivo também contempla os CNAES secundários de cada CNPJ (cada CNPJ pode ter mais de um CNAE secundário), bem como os sócios.

Em suma, prepare seu computador (e seu tempo) para esperar o script ser executado.
Se possível, feche tudo que estiver fazendo e deixe-o processando apenas esse script.
Se estiver no GNU/Linux, é interessante realizar logout na interface gráfica e utilizar algumas das telas do tty (acesso usando `control` + `alt` + `F1 ou outro até F6`).

## Tamanho das tabelas geradas
Tabela | Tamanho do arquivo | Quantidade de linhas
------ | ------------------ | --------------------
Empresas | Aprox. 12gb | 49.238.928
CNAES secundárias | 1,18gb | 43.680.906
Sócios | 1,71gb | 18.398.543


# Como executar
`python cnpj.py <arquivo original> <tipo de saída:csv ou sqlite> <pasta saída>`

ou, no python3:

`python3 cnpj.py <arquivo original> <tipo de saída:csv ou sqlite> <pasta saída>`

## Exemplo
`python cnpj.py "data\F.K032001K.D81106D" sqlite "data"`

ou, no python3:

`python3 cnpj.py "data\F.K032001K.D81106D" sqlite "data"`


## Separando arquivos CSV por estado ou municipio

Após ter gerado o arquivo empresas.csv, é possível dividir por estado, ou por cidade

###Requisitos

`$ python3 -m pip install python-dotenv`

Para ambos os scripts é necessário informar a localização do arquivo `empresas.csv` no arquivo `.env`

`FILES_LOCATION=/media/Arquivos`

Após isso basta executar os scripts:

####Para separar por UF:

`python3 separar_csv_por_uf.py`

####Para separar por cidade:

`python3 separar_csv_por_cidade.py`
