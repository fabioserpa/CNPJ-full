import random

import numpy as np
import pandas as pd

import networkx as nx
from networkx.readwrite import json_graph

COL_FLOAT64 = ['capital_social']

class RedeCNPJ:
    __conBD = None  
    __nivel_max = 1
    __qualificacoes = 'TODAS'
    
    G = None

    def __init__(self, conBD, nivel_max=1, qualificacoes='TODAS'):
        self.__conBD = conBD
        self.__nivel_max = nivel_max
        self.__qualificacoes = qualificacoes

        self.G = nx.DiGraph()

    def insere_pessoa(self, tipo_pessoa, id_pessoa):
        self._vinculos(tipo_pessoa=tipo_pessoa, id_pessoa=id_pessoa)

    def dataframe_pessoas_G(self, G):
        return pd.DataFrame.from_dict(dict(G.nodes(data=True)), orient='index')

    def dataframe_pessoas(self, nivel_max=None):
        if nivel_max is None:
            nivel_max = self.__nivel_max

        df = self.dataframe_pessoas_G(self.G)
        return df[df['nivel'] <= nivel_max]

    def dataframe_vinculos_G(self, G):
        edge_data = G.edges(data=True)
        return pd.DataFrame([i[2] for i in edge_data], 
                            index=pd.MultiIndex.from_tuples([(i[0], i[1]) for i in edge_data], 
                            names=['source','target']))

    def dataframe_vinculos(self):
        return self.dataframe_vinculos_G(self.G)

    def json_G(self, G):
        return json_graph.node_link_data(G)

    def json(self):
        return self.json_G(self.G)

    def gera_json(self, path):
        import json

        with open(path, "w") as f:
            f.write(json.dumps(self.json()))

    def gera_graphml_G(self, G, path):
        nx.write_graphml(G, path)

    def gera_graphml(self, path):
        self.gera_graphml_G(self.G, path)

    def gera_gexf_G(self, G, path):
        # Antes de gerar esse formato, necessario adaptar alguns atributos do grafo
        G_adapt = G.copy()

        pos = nx.spring_layout(G_adapt, dim=4, scale=1000)
        
        for node in G_adapt.nodes:
            tipo_pessoa = G_adapt.nodes[node]['tipo_pessoa']

            G_adapt.nodes[node]['label'] = G_adapt.nodes[node]['nome']

            # Configura atributos de visualizacao necessarios para alguns leitores
            G_adapt.nodes[node]['viz'] = {'size':10}

            if tipo_pessoa == 1:
                if G_adapt.nodes[node]['situacao'] == '02':
                    G_adapt.nodes[node]['viz']['color'] = {'a':1,'r':1,'g':57,'b':155}
                else:
                    G_adapt.nodes[node]['viz']['color'] = {'a':1,'r':255,'g':0,'b':0}
            else:
                G_adapt.nodes[node]['viz']['color'] = {'a':1,'r':46,'g':125,'b':32}

            G_adapt.nodes[node]['viz']['position'] = {'x':pos[node][0],
                                                      'y':pos[node][1],
                                                      'z':5}

            # Converte cols para float, por incompatibilidade do nx com o numpy.float64
            for coluna in COL_FLOAT64:
                if coluna in G_adapt.nodes[node]:
                    G_adapt.nodes[node][coluna] = float(G_adapt.nodes[node][coluna])

        nx.write_gexf(G_adapt, path)

    def gera_gexf(self, path):
        self.gera_gexf_G(self.G, path)

    def insere_com_cpf_ou_nome(self, cpf='', nome=''):
        # A partir de um nome ou um cpf, busca socios com esses dados e inclui na rede
        sql = '''
            SELECT distinct 
                tipo_socio, 
                cnpj_cpf_socio, 
                nome_socio 
            FROM 
                socios 
        '''
        if cpf != '':
            sql += '''
                WHERE cnpj_cpf_socio = '{0}'
            '''.format(cpf)
            
        else:
            sql += '''
                WHERE nome_socio = '{0}'
            '''.format(nome)
        
        empresas_socios = pd.read_sql_query(sql, self.__conBD)
        if len(empresas_socios) > 0:
            for _, emp_socio in empresas_socios.iterrows():
                cnpj_cpf_socio = emp_socio['cnpj_cpf_socio']
                nome_socio = emp_socio['nome_socio']
                tipo_socio = int(emp_socio['tipo_socio'])

                if tipo_socio == 1:
                    self._vinculos(tipo_pessoa=tipo_socio, id_pessoa=cnpj_cpf_socio)
                else:
                    self._vinculos(tipo_pessoa=tipo_socio, id_pessoa=(cnpj_cpf_socio,nome_socio))
        else:
            print('Nenhum socio encontrado com o cpf ou nome informado: cpf:{} / nome:{}'.format(cpf, nome))

    def _vinculos(self, tipo_pessoa, id_pessoa, atributos=None, nivel=0, origem=None):
        nome = None

        # Monta o id do node de acordo com o tipo de pessoa
        if tipo_pessoa == 1:
            id_pessoa_str = id_pessoa
        else:
            nome = id_pessoa[1]
            id_pessoa_str = id_pessoa[0] + nome

        # Nova pessoa
        if id_pessoa_str not in self.G:
            nova_pessoa = True

            if atributos:
                self.G.add_node(id_pessoa_str, nome=nome, tipo_pessoa=tipo_pessoa, nivel=nivel, **atributos)
            else:
                self.G.add_node(id_pessoa_str, nome=nome, tipo_pessoa=tipo_pessoa, nivel=nivel)

            #self.G.nodes[id_pessoa_str]['tipo_pessoa'] = tipo_pessoa
            #self.G.nodes[id_pessoa_str]['nivel'] = nivel

            # Se for PJ, pega dados da empresa na tabela de empresas
            if (tipo_pessoa == 1):
                # Atualizacao: pega do banco apenas se dados nao vieram como parametro
                if not atributos:
                    sql = '''
                        SELECT *
                        FROM empresas
                        WHERE cnpj = '{0}'
                    '''.format(id_pessoa)
                    
                    try:
                        empresa = pd.read_sql_query(sql, self.__conBD).iloc[0,:] # pega primeiro registro

                        for k, v in empresa.items():
                            self.G.nodes[id_pessoa_str][k] = v

                    except:
                        print('Empresa nao encontrada: {}'.format(id_pessoa_str))
                        self.G.remove_node(id_pessoa_str)
                        raise KeyError

                if (str(self.G.nodes[id_pessoa_str]['nome_fantasia']).strip() == '') or \
                            (str(self.G.nodes[id_pessoa_str]['nome_fantasia']).strip() == 'NAO POSSUI'):
                    self.G.nodes[id_pessoa_str]['nome'] = self.G.nodes[id_pessoa_str]['razao_social'] 
                else:
                    self.G.nodes[id_pessoa_str]['nome'] = self.G.nodes[id_pessoa_str]['nome_fantasia']

            else:
                # Se no for pessoa fisica
                self.G.nodes[id_pessoa_str]['cpf'] = id_pessoa[0]
        else:
            nova_pessoa = False
            nivel_anterior = self.G.nodes[id_pessoa_str]['nivel']

            if nivel < nivel_anterior:
                self.G.nodes[id_pessoa_str]['nivel'] = nivel
        
        # Condicoes para explorar "relacionados":
        # 1) Nivel atual ser menor do que configuracao max_nivel; e
        # 2) Relacionamentos não terem sido totalmente explorados antes, por
        #       a) ser uma pessoa nova OU
        #       b) nao é uma pessoa nova, mas o nivel atual é menor do que o nivel anterior dessa pessoa 
        if (nivel < self.__nivel_max) and (nova_pessoa or nivel < nivel_anterior):   
            # obtem todas as relacoes de sociedades que envolvam esse PJ ou PF

            # Verifica se relacionados ja estao no grafo ou se precisa buscar no BD
            if (not nova_pessoa) and (nivel_anterior < self.__nivel_max):
                # Relacionados ja estao no grafo, nao precisa buscar no BD

                # navega para os socios
                for id_socio_str in self.G.predecessors(id_pessoa_str):
                    node_socio = self.G.nodes[id_socio_str]
                    tipo_socio = node_socio['tipo_pessoa']

                    if tipo_socio == 1:
                        # socio eh PJ
                        socio = id_socio_str
                    else:
                        # socio eh PF
                        socio = (node_socio['cpf'],node_socio['nome'])

                    self._vinculos(tipo_pessoa=tipo_socio, id_pessoa=socio, nivel=nivel+1, origem=id_pessoa)

                # navega para empresas das quais e socio
                for empresa in self.G.successors(id_pessoa_str):
                    self._vinculos(tipo_pessoa=1, id_pessoa=empresa, nivel=nivel+1, origem=id_pessoa)

            else:
                # Relacionados ainda nao estao no grafo; buscar no BD.
                # (A) busca EMPRESAS das quais esta PJ/PF eh socia
                sql = '''
                    SELECT 
                        s.cnpj as s_cnpj, 
                        s.cod_qualificacao as s_cod_qualificacao, 
                        s.data_entrada as s_data_entrada,
                        e.* 
                    FROM 
                        socios s
                            inner join empresas e
                                on e.cnpj = s.cnpj and e.matriz_filial = 1
                    '''

                if tipo_pessoa == 1:
                    sql += '''
                        WHERE
                            s.cnpj_cpf_socio = '{0}'
                    '''.format(id_pessoa)
                else:
                    sql += '''
                        WHERE s.cnpj_cpf_socio = '{0}' AND 
                              s.nome_socio = '{1}'
                    '''.format(id_pessoa[0],id_pessoa[1])

                empresas = pd.read_sql_query(sql, self.__conBD)

                for _, empresa in empresas.iterrows():
                    cod_qualificacao = empresa['s_cod_qualificacao']

                    # Apenas adiciona relacionamento se for qualificacao de interesse
                    if (self.__qualificacoes == 'TODAS') | (cod_qualificacao in self.__qualificacoes): 
                        cnpj = empresa['s_cnpj']
                        data_entrada = empresa['s_data_entrada']

                        if self.__qualificacoes != 'TODAS':
                            qualificacao = self.__qualificacoes[cod_qualificacao]
                        else:
                            qualificacao = cod_qualificacao     

                        # se a empresa nao for a origem desse pulo
                        if cnpj != origem:
                            atributos = dict(empresa.drop(['s_cnpj','s_cod_qualificacao','s_data_entrada']))

                            # chama recursivamente para tratar a PJ
                            self._vinculos(tipo_pessoa=1, id_pessoa=cnpj, nivel=nivel+1, origem=id_pessoa, atributos=atributos)

                            # adiciona aresta de socio para empresa em questao
                            self.G.add_edge(id_pessoa_str, 
                                            cnpj, 
                                            tipo='socio', 
                                            cod_qualificacao=cod_qualificacao,
                                            qualificacao=qualificacao, 
                                            data_entrada=data_entrada)


                # (B) SOCIOS desta PJ (apenas se matriz)
                if tipo_pessoa == 1 and (self.G.nodes[id_pessoa_str]['matriz_filial'] == '1'):
                    sql = '''
                    SELECT 
                        cnpj, 
                        tipo_socio, 
                        cnpj_cpf_socio, 
                        nome_socio, 
                        cod_qualificacao, 
                        data_entrada 
                    FROM 
                        socios
                    WHERE
                        cnpj = '{0}'
                    '''.format(id_pessoa)
                
                    socios = pd.read_sql_query(sql, self.__conBD)

                    for _, socio in socios.iterrows():
                        cod_qualificacao = socio['cod_qualificacao']

                        # Apenas adiciona relacionamento se for qualificacao de interesse
                        if (self.__qualificacoes == 'TODAS') | (cod_qualificacao in self.__qualificacoes): 
                            cnpj_cpf_socio = socio['cnpj_cpf_socio']
                            nome_socio = socio['nome_socio']
                            tipo_socio = int(socio['tipo_socio'])
                            data_entrada = socio['data_entrada']
                            if self.__qualificacoes != 'TODAS':
                                qualificacao = self.__qualificacoes[cod_qualificacao]
                            else:
                                qualificacao = cod_qualificacao
                    
                            if tipo_socio == 1:
                                # socio eh PJ
                                id_socio = cnpj_cpf_socio
                                socio_str = id_socio
                            else:
                                # socio eh PF
                                id_socio = (cnpj_cpf_socio,nome_socio)
                                socio_str = cnpj_cpf_socio + nome_socio

                            # se o socio nao for a origem desse pulo
                            if id_socio != origem:
                                # chama recursivamente para tratar a nova PJ/PF
                                self._vinculos(tipo_pessoa=tipo_socio, id_pessoa=id_socio, nivel=nivel+1, origem=id_pessoa)

                                # adiciona aresta de socio para empresa em questao
                                self.G.add_edge(socio_str, 
                                                id_pessoa_str, 
                                                tipo='socio', 
                                                cod_qualificacao=cod_qualificacao,
                                                qualificacao=qualificacao, 
                                                data_entrada=data_entrada)

                
                # Se for filial, busca matriz
                if (tipo_pessoa == 1) and (self.G.nodes[id_pessoa_str]['matriz_filial'] == '2'):
                    sql = '''
                        SELECT 
                            cnpj, razao_social 
                        FROM 
                            empresas
                        WHERE 
                            substr(cnpj, 0, 9) = '{0}'
                        and matriz_filial = 1
                    '''.format(id_pessoa[:8])

                    try: 
                        matriz = pd.read_sql_query(sql, self.__conBD).iloc[0,:]
                        cnpj_matriz = matriz['cnpj']

                        self._vinculos(tipo_pessoa=1, id_pessoa=cnpj_matriz, nivel=nivel+1, origem=id_pessoa)

                        self.G.add_edge(id_pessoa_str, cnpj_matriz, tipo='filial')
                    except:
                        print('Matriz nao encontrada associada a filial: {}'.format(id_pessoa_str))
