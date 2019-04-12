# Dados Públicos CNPJ - Conversão para CSV ou SQLITE
Utilitário em Python para carregar a base completa de CNPJ [disponibilizada pela Receita Federal](http://idg.receita.fazenda.gov.br/orientacao/tributaria/cadastros/cadastro-nacional-de-pessoas-juridicas-cnpj/dados-publicos-cnpj) (aprox. 85 GB) e transformá-la em arquivos csv ou sqlite para fácil consumo. Processa dados de empresas, sócios e CNAEs.


# Configurações prévias
Para executar o script, é necessário que seu sistema contenha essas instalações:

## Python
Versão mais atual, caso não consiga executar usando somente o comando `python`. Para isso, execute no terminal (se estiver usando sistemas GNU/Linux derivados do Debian):

` $ sudo apt upgrade python3`

## Gerenciador de Pacotes do Python (Pip)
A versão mais atual. Se estiver usando Python3:

`$ python3 -m pip install --upgrade pip`

## Pandas (pacote de análise de dados)
A versão mais atual da biblioteca [Pandas](https://pandas.pydata.org) para Python. Para instalar via Pip:

`$ python3 -m pip install pandas`

#### NumPy
A princípio, não é necessário. O script neste repositório usa funções da biblioteca [Pandas](https://pandas.pydata.org), que utiliza uma extensão de NumPy chamada [NumExpr](#numexpr). Então, **caso** seu terminal retorne erros por ausência do pacote [NumPy](https://pypi.org/project/numpy/), esse é o motivo. Para instalá-lo (se precisar):

`$ python3 -m pip install numpy`

#### NumExpr
O [Pandas](https://pandas.pydata.org) usa. É uma extensão que melhora a velocidade de análise no pacote [NumPy](#pacote-numpy). Para instalar a versão mais atual da [NumExpr](https://pypi.org/project/numexpr):

`$ python3 -m pip install numexpr`


# Antes de executar
Atente para o fato de que o arquivo de dados disponibilizado pela RF é muito grande. São aprox. 85 GB de arquivo texto descomprimido.
Portanto, é bastante provável que seu computador dedique tempo considerável a essa execução, algo em torno de 2 ou 3 horas.

O script informa no terminal o parcial do processamento, mostrando o "bloco" (conjunto parcial) de linhas que está sendo convertido. Cada bloco contempla 100.000 linhas (registros) da base de dados.


## Tamanho das tabelas geradas (versão atualizada em 26/03/2019)
Tabela | Tamanho do arquivo | Quantidade de linhas
------ | ------------------ | --------------------
Empresas | Aprox. 12gb | 40.184.161
CNAES secundárias | 1,18gb | 45.321.058 <sup>*</sup>
Sócios | 1,71gb | 18.613.392

<sup>*</sup> Observar que esta quantidade de linhas não corresponde ao número de linhas referentes a CNAEs secundários no arquivo original, uma vez que no original todos os CNAEs secundários de uma determinada empresa estão na mesma linha, enquanto na versão convertida é gerada uma linha para cada CNAE secundário associado à empresa.


# Como executar
`python cnpj.py <arquivo original> <tipo de saída:csv ou sqlite> <pasta saída>`

ou, no python3:

`python3 cnpj.py <arquivo original> <tipo de saída:csv ou sqlite> <pasta saída>`

## Exemplo
`python cnpj.py "data\F.K032001K.D90308" sqlite "data"`

ou, no python3:

`python3 cnpj.py "data\F.K032001K.D90308" sqlite "data"`
