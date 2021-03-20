# Dados Públicos CNPJ - Conversão para CSV/SQLITE e Consultas
Utilitário em Python para carregar a base completa de CNPJ [disponibilizada pela Receita Federal](http://idg.receita.fazenda.gov.br/orientacao/tributaria/cadastros/cadastro-nacional-de-pessoas-juridicas-cnpj/dados-publicos-cnpj) (aprox. 85 GB) e transformá-la em arquivos csv ou sqlite para fácil consumo. Processa dados de empresas, sócios e CNAEs.
Possibilita também fazer consultas de empresas ou sócios e gravar resultados em CSV ou em grafo de relacionamentos.

![Grafo](img/grafo.png?raw=true "Grafo")

**ATENÇÃO!**

A partir de março de 2021, a Receita Federal mudou completamente a forma de disponibilizar os dados públicos do CNPJ. O script de carga deste repositório ainda não foi atualizado para refletir estas alterações, e portanto não funcionará para os novos arquivos disponibilizados a partir desta data.

A **boa notícia** é que agora os arquivos já estão sendo disponibilizados pela RF em formato CSV, o que, dependendo do seu caso, pode até dispensar o uso deste script.

Os scripts deste repositório no entanto ainda assim serão atualizados para manter funcional a conversão dos dados para formato SQLite, assim como os scripts de consulta.

# Conversão para CSV ou SQLITE

A forma recomendada de fazer a carga atualmente é: salvar os múltiplos arquivos zip em uma pasta dedicada e executar:

`python3 cnpj.py PASTA_COM_ZIPS sqlite PASTA_DE_SAIDA --dir`

ou

`python3 cnpj.py PASTA_COM_ZIPS csv PASTA_DE_SAIDA --dir`

## Configurações prévias
Para executar o script, é necessário que seu sistema contenha essas instalações:

## Python
Versão mais atual, caso não consiga executar usando somente o comando `python`. Para isso, execute no terminal (se estiver usando sistemas GNU/Linux derivados do Debian):

` $ sudo apt upgrade python3`

## Gerenciador de Pacotes do Python (Pip)
A versão mais atual. Se estiver usando Python3:

`$ python3 -m pip install --upgrade pip`

## Instalar Pré-Requisitos:

`$ pip install -r requirements.txt`

Esse comando instalará as seguintes bibliotecas:

#### Pandas
A versão mais atual da biblioteca [Pandas](https://pandas.pydata.org) para Python. 

#### NumPy
A princípio, não é necessário. O script neste repositório usa funções da biblioteca [Pandas](https://pandas.pydata.org), que utiliza uma extensão de NumPy chamada [NumExpr](#numexpr). Então, **caso** seu terminal retorne erros por ausência do pacote [NumPy](https://pypi.org/project/numpy/), esse é o motivo. 

#### NumExpr
O [Pandas](https://pandas.pydata.org) usa. É uma extensão que melhora a velocidade de análise no pacote [NumPy](#pacote-numpy).


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
`python3 cnpj.py <caminho entrada> <tipo de saída:csv ou sqlite> <pasta saída> [--dir] [--noindex]`

Caso a base seja disponibilizada em múltiplos arquivos zip, salvar em uma pasta, usá-la como `<caminho entrada>` e especificar o argumento `--dir`.

O argumento opcional `--noindex`, aplicável somente para saída sqlite, indica que **não** devem ser gerados índices automaticamente.
A criação de índices é muito recomendada e essencial para a funcionalidade de consultas.

## Exemplos
`python3 cnpj.py "data\F.K032001K.D90308" sqlite "data"`

`python3 cnpj.py "data" sqlite "output" --dir`

`python3 cnpj.py "data\DADOS_ABERTOS_CNPJ.zip" sqlite "data" --noindex`

## Separando arquivos CSV por estado ou municipio

Após ter gerado o arquivo empresas.csv, é possível dividir por estado, ou por cidade

### Requisitos

`$ python3 -m pip install python-dotenv`

Para ambos os scripts é necessário informar a localização do arquivo `empresas.csv` no arquivo `.env`

`FILES_LOCATION=/media/Arquivos`

Após isso basta executar os scripts:

#### Para separar por UF:

`python3 separar_csv_por_uf.py`

#### Para separar por cidade:

`python3 separar_csv_por_cidade.py`

# Consultas

**Novidade!** Agora é possível fazer consultas que além de trazer empresas e sócios específicos, traz a rede de relacionamentos na profundidade desejada. Os resultados podem ser salvos em formato tabular e/ou em formatos variados de grafos de relacionamento, que podem ser visualizados de forma interativa no navegador ou abertos em softwares que suportem os formatos especificados, como o [Gephi](https://gephi.org/).

Essa funcionalidade é exclusiva para a base sqlite gerada usando o `cnpj.py`. No entanto, pode ser relativamente simples adaptar o código para funcionar com outros SGBDs ou arquivos sqlite gerados usando outra nomenclatura.

## Configurações prévias
Para executar o script de consulta, é necessário que seu sistema contenha as instalações especificadas acima e, além disso, é necessário:

#### Networkx 2.x (pacote de criação, manipulação e análise de grafos/redes)

É **IMPRESCINDÍVEL** que índices sejam criados nos campos `cnpj` das tabelas `empresas` e `socios`, e nos campos `nome_socio` e `cnpj_cpf_socio` da tabela `socios`. Do contrário, as consultas se tornam insuportavelmente lentas ou até mesmo inviáveis dependendo da profundidade. O script de carga (cnpj.py) foi atualizado para opcionalmente gerar os índices mais importantes automaticamente ao final da carga.

## Instruções Básicas:

Uso: `python consulta.py <tipo consulta> <item|arquivo input> <caminho output> [--base <arquivo sqlite>]`
`[--nivel <int>] [--csv] [--graphml] [--gexf] [--viz]`

#### Argumentos obrigatórios:

`<tipo consulta>`: Especifica o tipo de item a ser procurado. Opções:
* **cnpj:** Busca empresa pelo número do CNPJ.

* **nome_socio:** Busca sócios pelo nome completo.

* **cpf:** Busca sócios pelo número do CPF.
      (Pode trazer vários sócios, uma vez que apenas seis dígitos são fornecidos pela RF)
      
* **cpf_nome:** Busca sócios pelo número do CPF seguido (sem espaço) do nome completo.

* **file:** Arquivo que contem mais de um item a ser buscado.
        Caso o arquivo tenha apenas um dado por linha, será tratado como número de CNPJ.
        Caso o arquivo tenha mais de um dado separado por `;`, o primeiro
        indica um dos tipos acima, e o segundo o item a ser buscado.
        (outro separador pode ser definido em `SEP_CSV` no `config.py`) 

`<item|arquivo input>`: Item a ser procurado, de acordo com `<tipo consulta>`.
  
`<caminho output>`: Pasta onde serão salvos os arquivos gerados.

#### Argumentos opcionais:

`--base`: Especifica o arquivo do banco de dados de CNPJ em formato sqlite.
           Caso não seja especificado, usa o `PATH_BD` definido no `config.py`

`--nivel`: Especifica a profundidade da consulta em número de "pulos".
            Exemplo: Caso seja especificado `--nivel 1`, busca o item e as empresas ou pessoas diretamente relacionadas.
            Caso não seja especificado, usa o `NIVEL_MAX_DEFAULT` no `config.py`

`--csv`: Para gerar o resultado em arquivos csv.
          São gerados dois arquivos, `pessoas.csv` e `vinculos.csv`.

`--graphml`: Para gerar o resultado em grafo no formato GRAPHML.

`--gexf`: Para gerar o resultado em grafo no formato GEXF. 
           Pode ser aberto com o software [Gephi](https://gephi.org/)

 `--viz`: Para gerar um HTML interativo com o resultado em grafo.
          Para abrir automaticamente o navegador, informar o `PATH_NAVEGADOR` 
          no `config.py`. Do contrário, basta abrir o arquivo `grafo.html` gerado 
          em `<caminho output>` com o navegador de preferência.

#### Exemplos:

`python consulta.py cnpj 00000000000191 folder --nivel 1 --viz`

`python consulta.py file data/input.csv pasta --csv --gexf`

`python consulta.py nome_socio "FULANO SICRANO" output --graphml --viz`

#### Atenção:

Especifique o nível de profundidade da rede com moderação, uma vez que, dependendo das empresas ou pessoas buscadas, a quantidade de relacionados pode crescer exponencialmente, atingindo facilmente centenas ou milhares de registros, o que resulta na execução intensiva de queries no BD. Nível 3 é um bom parâmetro.

#### Configuração

No `config.py`, as seguintes configurações são definidas:

`PATH_BD`: Caminho para o arquivo de banco de dados da Receita Federal convertido em sqlite. 
Pode ser sobrescrito em tempo de execução usando o argumento `--base`.

`NIVEL_MAX_DEFAULT`: Nível máximo default para a profundidade das buscas.
Pode ser sobrescrito em tempo de execução usando o argumento `--nivel <num>`

`PATH_NAVEGADOR`: Caminho completo para o executável do navegador preferido se desejar que a visualização seja automaticamente apresentada ao final da execução da consulta (se argumento `--viz` for utilizado). Caso vazio, apenas gera o html na pasta de saída.

`SEP_CSV`: Especifica o separador a ser considerado tanto para os arquivos csv de saída (caso seja utilizado o argumento `--csv`), quanto para o arquivo de entrada no caso do uso de `file` como `<tipo consulta>`.

`COLUNAS_CSV`: Especifica a lista de colunas a serem incluídas no arquivo `pessoas.csv` quando usado o argumento `--csv`.

`QUALIFICACOES`: Especifica a lista de qualificações de sócios a serem consideradas na busca dos relacionamentos. Caso `TODAS`, qualquer relação de sociedade listada no BD é considerada.

## Trabalhando diretamente com a classe RedeCNPJ

O objetivo do `consulta.py` é disponibilizar uma interface por linha de comando para facilitar a extração/visualização da rede de relacionamentos de empresas e pessoas a partir da base de dados da RF convertida em sqlite. Ele é uma "casca" para a classe `RedeCNPJ` definida em `rede_cnpj.py`, onde fica a inteligência de navegação no BD e criação de rede/grafo usando o pacote `networkx`, além de métodos para conversão em DataFrames pandas e formatos diversos de representação de estruturas em grafo.

Em seu projeto você pode instanciar diretamente a `RedeCNPJ` especificando a conexão ao BD e o nível máximo de navegação nos relacionamentos, usar os métodos de inserção de empresas/pessoas para montar a rede (sem se preocupar com a navegação para as relacionadas), e usar os métodos para conversão da rede em DataFrame ou formatos diversos de representação de grafos.

E dessa forma você pode também usar o grafo gerado (atributo "G" da classe) para incrementá-lo a partir de outras fontes de dados de interesse para seu caso de uso e usar os diversos algoritmos disponibilizados pela biblioteca `networkx`, como por exemplo detecção de ciclos.

## TO DO

* Aprimorar a documentação do código (principalmente da classe RedeCNPJ) e as instruções neste README.
