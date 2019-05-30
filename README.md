# Dados Públicos CNPJ - Conversão para CSV/SQLITE e Consultas
Utilitário em Python para carregar a base completa de CNPJ [disponibilizada pela Receita Federal](http://idg.receita.fazenda.gov.br/orientacao/tributaria/cadastros/cadastro-nacional-de-pessoas-juridicas-cnpj/dados-publicos-cnpj) (aprox. 85 GB) e transformá-la em arquivos csv ou sqlite para fácil consumo. Processa dados de empresas, sócios e CNAEs.
Possibilita também fazer consultas de empresas ou sócios e gravar resultados em CSV ou em grafo de relacionamentos.

# Conversão para CSV ou SQLITE

## Configurações prévias
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

## Antes de executar
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

## Como executar
`python cnpj.py <arquivo original> <tipo de saída:csv ou sqlite> <pasta saída> [--index]`

ou, no python3:

`python3 cnpj.py <arquivo original> <tipo de saída:csv ou sqlite> <pasta saída> [--index]`

O argumento opcional `--index`, aplicável somente para saída sqlite, indica que ao final da carga devem ser gerados índices automaticamente.
A criação de índices é muito recomendada e essencial para a funcionalidade de consultas.

## Exemplo
`python cnpj.py "data\F.K032001K.D90308" sqlite "data" --index`

ou, no python3:

`python3 cnpj.py "data\F.K032001K.D90308" sqlite "data" --index`

# Consultas

**Novidade!** Agora é possível fazer consultas que além de trazer empresas e sócios específicos, traz a rede de relacionamentos na profundidade desejada. Os resultados podem ser salvos em formato tabular e/ou em formatos variados de grafos de relacionamento, que podem ser visualizados de forma interativa no navegador ou abertos em softwares que suportem os formatos especificados, como o [Gephi](https://gephi.org/).

## Configurações prévias
Para executar o script de consulta, é necessário que seu sistema contenha as instalações especificadas acima e, além disso, é necessário:

#### Networkx 2.x (pacote de criação, manipulação e análise de grafos/redes)

É **IMPRESCINDÍVEL** que índices sejam criados nos campos `cnpj` das tabelas `empresas` e `socios`, e nos campos `nome_socio` e `cnpj_cpf_socio` da tabela `socios`. Do contrário, as consultas se tornam insuportavelmente lentas ou até mesmo inviáveis dependendo da profundidade.

## Instruções (a serem melhor detalhadas em breve):

Uso: `python consulta.py <tipo consulta> <item|arquivo input> <caminho output> [--base <arquivo sqlite>] [--nivel <int>] [--csv] [--graphml] [--gexf] [--viz]`

#### Argumentos obrigatorios:

`<tipo consulta>`: Especifica o tipo de item a ser procurado. Opções:
* **cnpj:** Busca empresa pelo numero do CNPJ

* **nome_socio:** Busca socios pelo nome completo

* **cpf:** Busca socios pelo numero do CPF 
      Pode trazer varios socios, ja que apenas seis digitos sao armazenados.
      
* **cpf_nome:** Busca socios pelo numero do CPF seguido (sem espaco) do nome

* **file:** Arquivo que contem mais de um item a ser buscado.
        Caso o arquivo tenha apenas um dado por linha, dado lido como CNPJ.
        Caso o arquivo tenha mais de um dado separado por `;`, o primeiro
        indica um dos tipos acima, e o segundo o item a ser buscado.
        (outro separador pode ser definido em `SEP_CSV` no `config.py`) 

`<item|arquivo input>`: Item a ser procurado, de acordo com `<tipo consulta>`.
  
`<caminho output>`: Pasta onde serao salvos os arquivos gerados.

#### Argumentos opcionais:

`--base`: Especifica o arquivo do banco de dados de CNPJ em formato sqlite.
           Caso nao seja especificado, usa o PATH_BD definido no `config.py`

`--nivel`: Especifica a profundidade da consulta em número de pulos.
            Ex: Caso seja especificado --nivel 1, busca o item e as
            as empresas ou pessoas diretamente relacionadas.
            Csaso nao seja especificado, usa o `NIVEL_MAX_DEFAULT` no `config.py`

`--csv`: Para gerar o resultado em arquivos csv.
          Sao gerados dois arquivos, `pessoas.csv` e `vinculos.csv`.

`--graphml`: Para gerar o resultado em grafo no formato GRAPHML.

`--gexf`: Para gerar o resultado em grafo no formato GEXF. 
           Pode ser aberto com o software [Gephi](https://gephi.org/)

 `--viz`: Para gerar um HTML interativo com o resultado em grafo.
          Para abrir automaticamente o navegador, informar o `PATH_NAVEGADOR` 
          no `config.py`. Do contrario, basta abrir o arquivo grafo.html gerado 
          em <caminho output>.

#### Exemplos:

`python consulta.py cnpj 00000000000191 folder --nivel 1 --viz`

`python consulta.py file data/input.csv pasta --csv --gexf`

`python consulta.py nome_socio "FULANO SICRANO" output --graphml --viz`

#### Atenção:

Especifique o nível de profundidade da rede com moderação, uma vez que, dependendo das empresas ou pessoas buscadas, a quantidade de relacionados pode crescer exponencialmente, atingindo facilmente centenas ou milhares de registros, o que resulta na execução intensiva de queries no BD. Nível 3 é um bom parâmetro.
