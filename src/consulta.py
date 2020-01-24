import os
import sys
import json
import subprocess

import pandas as pd
import sqlite3
import networkx as nx

import config
from rede_cnpj import RedeCNPJ

def consulta(tipo_consulta, objeto_consulta, qualificacoes, path_BD, nivel_max, path_output, 
             csv=False, colunas_csv=None, csv_sep=',', graphml=False, gexf=False, viz=False, 
             path_conexoes=None):

    try:
        conBD = sqlite3.connect(path_BD)

        try:
            rede = RedeCNPJ(conBD, nivel_max=nivel_max, qualificacoes=qualificacoes)

            if tipo_consulta == 'file':
                df_file = pd.read_csv(objeto_consulta, sep=csv_sep, header=None, dtype=str)

                qtd_colunas = len(df_file.columns)

                for _, linha in df_file.iterrows():
                    if qtd_colunas >= 2:
                        try:
                            consulta_item(rede, linha[0].strip(), linha[1].strip())
                        except KeyError as e:
                            print('Item nao encontrado ({}): {}'.format(linha[0].strip(),
                                                                        linha[1].strip()))
                    else:
                        try:
                            consulta_item(rede, 'cnpj', linha[0].strip())
                        except KeyError as e:
                            print('CNPJ nao encontrado: {}'.format(linha[0].strip()))
            else:
                consulta_item(rede, tipo_consulta, objeto_consulta)

            if not os.path.exists(path_output):
                os.mkdir(path_output)

            if csv:
                df_nodes = pd.DataFrame(columns=colunas_csv).append(rede.dataframe_pessoas(), sort=False)

                # Verifica se teve ao menos um registro encontrado
                if len(df_nodes) > 0:
                    df_nodes[colunas_csv].to_csv(os.path.join(path_output, 'pessoas.csv'), index_label='id', sep=csv_sep)

                    df_edges = rede.dataframe_vinculos()
                    if len(df_edges) > 0:
                        df_edges.to_csv(os.path.join(path_output, 'vinculos.csv'), sep=csv_sep)
                else:
                    print('Nenhum registro foi localizado. Arquivos de output nao foram gerados.')

            if graphml:
                rede.gera_graphml(os.path.join(path_output, 'rede.graphml'))

            if gexf:
                rede.gera_gexf(os.path.join(path_output, 'rede.gexf'))

            if viz:
                try:
                    with open('viz/template.html', 'r', encoding='utf-8') as template:
                        str_html = template.read().replace('<!--GRAFO-->', json.dumps(rede.json()))
                        
                    path_html = os.path.join(path_output, 'grafo.html')
                    with open(path_html, 'w', encoding='utf-8') as html:
                        html.write(str_html)

                    if config.PATH_NAVEGADOR:
                        subprocess.Popen([config.PATH_NAVEGADOR, os.path.abspath(path_html)])

                except Exception as e:
                    print('Não foi possível gerar a visualização. [{}]'.format(e))

            if path_conexoes:
                df_conexoes = pd.read_csv(path_conexoes, sep=csv_sep, header=None, dtype=str)

                qtd_colunas = len(df_conexoes.columns)

                if qtd_colunas >= 2:
                    G_undirected = rede.G.to_undirected()
                    lista_conexoes = []

                    for _, linha in df_conexoes.iterrows():
                        pessoa_A = linha[0].strip()
                        pessoa_B = linha[1].strip()

                        conexao = ''
                        try:
                            lst_pessoas_conexao = nx.shortest_path(G_undirected, pessoa_A, pessoa_B)
                            conexao = ' | '.join(lst_pessoas_conexao)
                        except:
                            conexao = 'SEM CONEXAO'

                        lista_conexoes.append((pessoa_A, pessoa_B, conexao))

                    pd.DataFrame(lista_conexoes).to_csv(os.path.join(path_output, 'conexoes.csv'),
                                                        sep=csv_sep,
                                                        header=None,
                                                        index=None)

                else:
                    print('''
Arquivo de vinculos precisa ter pelo menos duas colunas, contendo a identificacao das pessoas (CNPJ ou cpf+nome).
No caso de pessoa fisica, informar cpf seguido imediatamente do nome (ex: "***123456**NOME COMPLETO DA PESSOA").
                    ''')

            print('Consulta finalizada. Verifique o(s) arquivo(s) de saida na pasta "{}".'.format(path_output))

        except Exception as e:
            print('Um erro ocorreu:\n{}'.format(e))
        finally:
            conBD.close()

    except:
        print('Nao foi possivel encontrar ou conectar ao BD {}'.format(path_BD))

def consulta_item(rede, tipo_item, item):
    if tipo_item == 'cnpj':
        #print('Consultando CNPJ: {}'.format(item))
        rede.insere_pessoa(1, item.replace('.','').replace('/','').replace('-','').zfill(14))

    elif tipo_item == 'nome_socio':
        #print('Consultando socios com nome: {}'.format(item))
        rede.insere_com_cpf_ou_nome(nome=item.upper())

    elif tipo_item == 'cpf':
        cpf = mascara_cpf(item.replace('.','').replace('-',''))
        #print('Consultando socios com cpf (mascarado): {}.'.format(cpf))
        rede.insere_com_cpf_ou_nome(cpf=cpf)

    elif tipo_item == 'cpf_nome':
        cpf = mascara_cpf(item[:11])
        nome = item[11:]

        #print('Consultando socio com cpf (mascarado) {} e nome {}'.format(cpf,nome))
        rede.insere_pessoa(2,(cpf,nome))

        # Se nao tem vinculo, nao existe socio com esse par cpf e nome
        if len(rede.dataframe_vinculos()) == 0:
            print('Nenhum socio encontrado com cpf "{}" e nome "{}"'.format(cpf, nome))
            rede.G.remove_node(cpf+nome)
    else:
        print('Tipo de consulta invalido: {}.\nTipos possiveis: cnpj, nome_socio, cpf, cpf_nome'.format(tipo_item))

def mascara_cpf(cpf_original):
    cpf = cpf_original.zfill(11)
    if cpf[0:3] != '***':
        cpf = '***' + cpf[3:9] + '**'

    return cpf

def help():
    print('''
Uso: python consulta.py <tipo consulta> <item|arquivo input> <caminho output> 
     [--base <arquivo sqlite>] [--nivel <int>] 
     [--csv] [--graphml] [--gexf] [--viz]

Argumentos obrigatorios:
  <tipo consulta>: Especifica o tipo de item a ser procurado.
    Opcoes:
    - cnpj: Busca empresa pelo numero do CNPJ
    - nome_socio: Busca socios pelo nome completo
    - cpf: Busca socios pelo numero do CPF 
      Pode trazer varios socios, ja que apenas seis digitos sao armazenados.
    - cpf_nome: Busca socios pelo numero do CPF seguido (sem espaco) do nome
    - file: Arquivo que contem mais de um item a ser buscado.
        Caso o arquivo tenha apenas um dado por linha, dado lido como CNPJ.
        Caso o arquivo tenha mais de um dado separado por ";", o primeiro
        indica um dos tipos acima, e o segundo o item a ser buscado.
        (outro separador pode ser definido em SEP_CSV no config.py) 

  <item|arquivo input>: Item a ser procurado, de acordo com <tipo consulta>. 
  <caminho output>: Pasta onde serao salvos os arquivos gerados.

Argumentos opcionais:
  --base: Especifica o arquivo do banco de dados de CNPJ em formato sqlite.
           Caso nao seja especificado, usa o PATH_BD definido no config.py

  --nivel: Especifica a profundidade da consulta em número de pulos.
            Ex: Caso seja especificado --nivel 1, busca o item e as
            as empresas ou pessoas diretamente relacionadas.
            Csaso nao seja especificado, usa o NIVEL_MAX_DEFAULT no config.py

  --csv: Para gerar o resultado em arquivos csv.
          Sao gerados dois arquivos, pessoas.csv e vinculos.csv.

  --graphml: Para gerar o resultado em grafo no formato GRAPHML.

  --gexf: Para gerar o resultado em grafo no formato GEXF. 
           Pode ser aberto com o software gephi (https://gephi.org/)

  --viz: Para gerar um HTML interativo com o resultado em grafo.
          Para abrir automaticamente o navegador, informar o PATH_NAVEGADOR 
          no config.py. Do contrario, basta abrir o arquivo grafo.html gerado 
          em <caminho output>.

  --conexoes: Especifica arquivo com pares de id de pessoas (cnpj ou cpf+nome),
              um par por linha, para busca de conexoes (diretas ou indiretas) 
              entre cada par. Gera arquivo conexoes.csv, com tres colunas. 
              As duas primeiras com o par de pessoas e a terceira coluna
              com a conexao entre elas, ou a string "SEM CONEXAO".

Exemplos: 
  python consulta.py cnpj 00000000000191 folder --nivel 1 --viz
  python consulta.py file data/input.csv pasta --csv --gexf
  python consulta.py nome_socio "FULANO SICRANO" output --graphml --viz
    ''')

def main():
    NUM_ARGS_OBRIGATORIOS = 4

    # Defaults
    csv = False
    graphml = False
    gexf = False
    viz = False
    nivel = config.NIVEL_MAX_DEFAULT
    path_bd = config.PATH_BD
    path_conexoes = None

    # python consulta.py <tipo consulta> <item|arquivo input> <caminho output> 
    # [--base <arquivo sqlite>] [--nivel <int>] [--csv] [--graphml] [--gexf] [--viz]
    num_argv = len(sys.argv)
    if num_argv < NUM_ARGS_OBRIGATORIOS:
        help()
        sys.exit(-1)
    else:
        tipo_consulta = sys.argv[1]
        objeto_consulta = sys.argv[2]
        output_path = sys.argv[3]

        if num_argv > NUM_ARGS_OBRIGATORIOS:
            i_argv = NUM_ARGS_OBRIGATORIOS
            while i_argv < num_argv:
                opcional = sys.argv[i_argv]

                if opcional == '--base':
                    path_bd = sys.argv[i_argv+1]
                    i_argv += 2
                elif opcional == '--nivel':
                    nivel = int(sys.argv[i_argv+1])
                    i_argv += 2
                elif opcional == '--csv':
                    csv = True
                    i_argv += 1
                elif opcional == '--graphml':
                    graphml = True
                    i_argv += 1
                elif opcional == '--gexf':
                    gexf = True
                    i_argv += 1
                elif opcional == '--viz':
                    viz = True
                    i_argv += 1
                elif opcional == '--conexoes':
                    path_conexoes = sys.argv[i_argv+1]
                    i_argv += 2
                else:
                    print('Parametro opcional invalido: {}'.format(opcional))
                    i_argv += 1

        # Caso nenhum tipo de saida tenha sido selecionado, gera csv como default
        if not (csv+graphml+gexf+viz):
            csv = True

        consulta(tipo_consulta, objeto_consulta, 
                 config.QUALIFICACOES, 
                 path_bd, 
                 nivel, 
                 output_path, 
                 csv=csv, colunas_csv=config.COLUNAS_CSV, csv_sep=config.SEP_CSV,
                 graphml=graphml,
                 gexf=gexf,
                 viz=viz,
                 path_conexoes=path_conexoes)

if __name__ == '__main__':
    main()
