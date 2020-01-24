# -*- encoding: utf-8 -*-
import os
import glob
import sys
import csv
import datetime

import pandas as pd

from cfwf import read_cfwf

# CONSTANTES PARA DEFINICAO CENTRALIZADA DA NOMENCLATURA A SER UTILIZADA
# Nomes das tabelas/arquivos
EMPRESAS = 'empresas'
SOCIOS = 'socios'
CNAES_SECUNDARIOS = 'cnaes_secundarios'

# Nome das colunas de empresas
EMP_CNPJ = 'cnpj'
EMP_MATRIZ_FILIAL = 'matriz_filial'
EMP_RAZAO_SOCIAL = 'razao_social'
EMP_NOME_FANTASIA = 'nome_fantasia'
EMP_SITUACAO = 'situacao'
EMP_DATA_SITUACAO = 'data_situacao'
EMP_MOTIVO_SITUACAO = 'motivo_situacao'
EMP_NM_CIDADE_EXTERIOR = 'nm_cidade_exterior'
EMP_COD_PAIS = 'cod_pais'
EMP_NOME_PAIS = 'nome_pais'
EMP_COD_NAT_JURIDICA = 'cod_nat_juridica'
EMP_DATA_INICIO_ATIV = 'data_inicio_ativ'
EMP_CNAE_FISCAL = 'cnae_fiscal'
EMP_TIPO_LOGRADOURO = 'tipo_logradouro'
EMP_LOGRADOURO = 'logradouro'
EMP_NUMERO = 'numero'
EMP_COMPLEMENTO = 'complemento'
EMP_BAIRRO = 'bairro'
EMP_CEP = 'cep'
EMP_UF = 'uf'
EMP_COD_MUNICIPIO = 'cod_municipio'
EMP_MUNICIPIO = 'municipio'
EMP_DDD_1 = 'ddd_1'
EMP_TELEFONE_1 = 'telefone_1'
EMP_DDD_2 = 'ddd_2'
EMP_TELEFONE_2 = 'telefone_2'
EMP_DDD_FAX = 'ddd_fax'
EMP_NUM_FAX = 'num_fax'
EMP_EMAIL = 'email'
EMP_QUALIF_RESP = 'qualif_resp'
EMP_CAPITAL_SOCIAL = 'capital_social'
EMP_PORTE = 'porte'
EMP_OPC_SIMPLES = 'opc_simples'
EMP_DATA_OPC_SIMPLES = 'data_opc_simples'
EMP_DATA_EXC_SIMPLES = 'data_exc_simples'
EMP_OPC_MEI = 'opc_mei'
EMP_SIT_ESPECIAL = 'sit_especial'
EMP_DATA_SIT_ESPECIAL = 'data_sit_especial'

# Nome das colunas de socios
SOC_CNPJ = 'cnpj'
SOC_TIPO_SOCIO = 'tipo_socio'
SOC_NOME_SOCIO = 'nome_socio'
SOC_CNPJ_CPF_SOCIO = 'cnpj_cpf_socio'
SOC_COD_QUALIFICACAO = 'cod_qualificacao'
SOC_PERC_CAPITAL = 'perc_capital'
SOC_DATA_ENTRADA = 'data_entrada'
SOC_COD_PAIS_EXT = 'cod_pais_ext'
SOC_NOME_PAIS_EXT = 'nome_pais_ext'
SOC_CPF_REPRES = 'cpf_repres'
SOC_NOME_REPRES = 'nome_repres'
SOC_COD_QUALIF_REPRES = 'cod_qualif_repres'

# Nome das colunas de cnaes secundarios
CNA_CNPJ = 'cnpj'
CNA_CNAE = 'cnae'
CNA_ORDEM = 'cnae_ordem'
# FIM DAS CONSTANTES PARA DEFINICAO DE NOMENCLATURA

REGISTROS_TIPOS = {
    '1':EMPRESAS,
    '2':SOCIOS,
    '6':CNAES_SECUNDARIOS
}

EMPRESAS_COLUNAS = [
    (EMP_CNPJ,(3, 17)), 
    (EMP_MATRIZ_FILIAL,(17,18)),
    (EMP_RAZAO_SOCIAL,(18,168)),
    (EMP_NOME_FANTASIA,(168,223)),
    (EMP_SITUACAO,(223,225)),
    (EMP_DATA_SITUACAO,(225,233)),
    (EMP_MOTIVO_SITUACAO,(233,235)),
    (EMP_NM_CIDADE_EXTERIOR,(235,290)),
    (EMP_COD_PAIS,(290,293)),
    (EMP_NOME_PAIS,(293,363)),
    (EMP_COD_NAT_JURIDICA,(363,367)),
    (EMP_DATA_INICIO_ATIV,(367,375)),
    (EMP_CNAE_FISCAL,(375,382)),
    (EMP_TIPO_LOGRADOURO,(382,402)),
    (EMP_LOGRADOURO,(402,462)),
    (EMP_NUMERO,(462,468)),
    (EMP_COMPLEMENTO,(468,624)),
    (EMP_BAIRRO,(624,674)),
    (EMP_CEP,(674,682)),
    (EMP_UF,(682,684)),
    (EMP_COD_MUNICIPIO,(684,688)),
    (EMP_MUNICIPIO,(688,738)),
    (EMP_DDD_1,(738,742)),
    (EMP_TELEFONE_1,(742,750)),
    (EMP_DDD_2,(750,754)),
    (EMP_TELEFONE_2,(754,762)),
    (EMP_DDD_FAX,(762,766)),
    (EMP_NUM_FAX,(766,774)),
    (EMP_EMAIL,(774,889)),
    (EMP_QUALIF_RESP,(889,891)),
    (EMP_CAPITAL_SOCIAL,(891,905)),
    (EMP_PORTE,(905,907)),
    (EMP_OPC_SIMPLES,(907,908)),
    (EMP_DATA_OPC_SIMPLES,(908,916)),
    (EMP_DATA_EXC_SIMPLES,(916,924)),
    (EMP_OPC_MEI,(924,925)),
    (EMP_SIT_ESPECIAL,(925,948)),
    (EMP_DATA_SIT_ESPECIAL,(948,956))
]

EMPRESAS_DTYPE = {EMP_CAPITAL_SOCIAL:float}

SOCIOS_COLUNAS = [
    (SOC_CNPJ,(3, 17)), 
    (SOC_TIPO_SOCIO,(17,18)),
    (SOC_NOME_SOCIO,(18,168)),
    (SOC_CNPJ_CPF_SOCIO,(168,182)),
    (SOC_COD_QUALIFICACAO,(182,184)),
    (SOC_PERC_CAPITAL,(184,189)),
    (SOC_DATA_ENTRADA,(189,197)),
    (SOC_COD_PAIS_EXT,(197,200)),
    (SOC_NOME_PAIS_EXT,(200,270)),
    (SOC_CPF_REPRES,(270,281)),
    (SOC_NOME_REPRES,(281,341)),
    (SOC_COD_QUALIF_REPRES,(341,343))
]

SOCIOS_DTYPE = {SOC_PERC_CAPITAL:float}

CNAES_COLNOMES = [CNA_CNPJ] + [num for num in range(99)]
CNAES_COLSPECS = [(3,17)] + [(num*7+17,num*7+24) for num in range(99)]

HEADER_COLUNAS = [
    ('Nome do arquivo',(17,28)),
    ('Data de gravacao',(28,36)),
    ('Numero da remessa',(36,44))
]

TRAILLER_COLUNAS = [
    ('Total de registros de empresas',(17,26)),
    ('Total de registros de socios',(26,35)),
    ('Total de registros de CNAEs secundarios',(35,44)),
    ('Total de registros incluindo header e trailler',(44,55))
]

# (<nome_do_indice>,<tabela>,<coluna>)
INDICES = [
    ('empresas_cnpj', EMPRESAS, EMP_CNPJ),
    ('empresas_raiz', EMPRESAS, 'substr({},0,9)'.format(EMP_CNPJ)),
    ('socios_cnpj', SOCIOS, SOC_CNPJ),
    ('socios_cpf_cnpj', SOCIOS, SOC_CNPJ_CPF_SOCIO),
    ('socios_nome', SOCIOS, SOC_NOME_SOCIO),
    ('cnaes_cnpj', CNAES_SECUNDARIOS, CNA_CNPJ)
]

PREFIXO_INDICE = 'ix_'

CHUNKSIZE=200000

NOME_ARQUIVO_SQLITE = 'CNPJ_full.db'

def cnpj_full(input_list, tipo_output, output_path):
    total_empresas = 0
    controle_empresas = 0
    total_socios = 0
    controle_socios = 0
    total_cnaes = 0
    controle_cnaes = 0

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    if tipo_output == 'sqlite':
        import sqlite3
        conBD = sqlite3.connect(os.path.join(output_path,NOME_ARQUIVO_SQLITE))

    header_colnomes = list(list(zip(*HEADER_COLUNAS))[0])
    empresas_colnomes = list(list(zip(*EMPRESAS_COLUNAS))[0])
    socios_colnomes = list(list(zip(*SOCIOS_COLUNAS))[0])
    trailler_colnomes = list(list(zip(*TRAILLER_COLUNAS))[0])

    header_colspecs = list(list(zip(*HEADER_COLUNAS))[1])
    empresas_colspecs = list(list(zip(*EMPRESAS_COLUNAS))[1])
    socios_colspecs = list(list(zip(*SOCIOS_COLUNAS))[1])
    trailler_colspecs = list(list(zip(*TRAILLER_COLUNAS))[1])

    # Itera sobre sequencia de arquivos (p/ suportar arquivo dividido pela RF)
    for i_arq, arquivo in enumerate(input_list):
        print('Processando arquivo: {}'.format(arquivo))

        dados = read_cfwf(arquivo, 
                          type_width=1, 
                          colspecs= {'0':header_colspecs,
                                     '1':empresas_colspecs,
                                     '2':socios_colspecs,
                                     '6':CNAES_COLSPECS,
                                     '9':trailler_colspecs},
                          names={'0':header_colnomes,
                                 '1':empresas_colnomes, 
                                 '2':socios_colnomes,
                                 '6':CNAES_COLNOMES,
                                 '9':trailler_colnomes},
                          dtype={'1': EMPRESAS_DTYPE,
                                 '2': SOCIOS_DTYPE},
                          chunksize=CHUNKSIZE,
                          encoding='ISO-8859-15')

        # Itera sobre blocos (chunks) do arquivo
        for i_bloco, bloco in enumerate(dados):
            print('Bloco {}: até linha {}. [Emps:{}|Socios:{}|CNAEs:{}]'.format(i_bloco+1,
                                                               (i_bloco+1)*CHUNKSIZE,
                                                               total_empresas, 
                                                               total_socios, 
                                                               total_cnaes), 
                  end='\r')

            for tipo_registro, df in bloco.items():

                if tipo_registro == '1': # empresas
                    total_empresas += len(df)

                    # Troca datas zeradas por vazio
                    df[EMP_DATA_OPC_SIMPLES] = (df[EMP_DATA_OPC_SIMPLES]
                            .where(df[EMP_DATA_OPC_SIMPLES] != '00000000',''))
                    df[EMP_DATA_EXC_SIMPLES] = (df[EMP_DATA_EXC_SIMPLES]
                            .where(df[EMP_DATA_EXC_SIMPLES] != '00000000',''))
                    df[EMP_DATA_SIT_ESPECIAL] = (df[EMP_DATA_SIT_ESPECIAL]
                            .where(df[EMP_DATA_SIT_ESPECIAL] != '00000000',''))

                elif tipo_registro == '2': # socios
                    total_socios += len(df)

                    # Troca cpf invalido por vazio
                    df[SOC_CPF_REPRES] = (df[SOC_CPF_REPRES]
                            .where(df[SOC_CPF_REPRES] != '***000000**',''))
                    df[SOC_NOME_REPRES] = (df[SOC_NOME_REPRES]
                            .where(df[SOC_NOME_REPRES] != 'CPF INVALIDO',''))  

                    # Se socio for tipo 1 (cnpj), deixa campo intacto, do contrario, 
                    # fica apenas com os ultimos 11 digitos
                    df[SOC_CNPJ_CPF_SOCIO] = (df[SOC_CNPJ_CPF_SOCIO]
                            .where(df[SOC_TIPO_SOCIO] == '1',
                                   df[SOC_CNPJ_CPF_SOCIO].str[-11:]))

                elif tipo_registro == '6': # cnaes_secundarios       
                    total_cnaes += len(df)

                    # Verticaliza tabela de associacao de cnaes secundarios,
                    # mantendo apenas os validos (diferentes de 0000000)
                    df = pd.melt(df, 
                                 id_vars=[CNA_CNPJ], 
                                 value_vars=range(99),
                                 var_name=CNA_ORDEM, 
                                 value_name=CNA_CNAE)

                    df = df[df[CNA_CNAE] != '0000000']

                elif tipo_registro == '0': # header
                    print('\nINFORMACOES DO HEADER:')

                    header = df.iloc[0,:]

                    for k, v in header.items():
                        print('{}: {}'.format(k, v))

                    # Para evitar que tente armazenar dados de header
                    continue

                elif tipo_registro == '9': # trailler
                    print('\nINFORMACOES DE CONTROLE:')

                    trailler = df.iloc[0,:]

                    controle_empresas = int(trailler['Total de registros de empresas'])
                    controle_socios = int(trailler['Total de registros de socios'])
                    controle_cnaes = int(trailler['Total de registros de CNAEs secundarios'])

                    print('Total de registros de empresas: {}'.format(controle_empresas))
                    print('Total de registros de socios: {}'.format(controle_socios))
                    print('Total de registros de CNAEs secundarios: {}'.format(controle_cnaes))
                    print('Total de registros incluindo header e trailler: {}'.format(
                            int(trailler['Total de registros incluindo header e trailler'])))

                    # Para evitar que tente armazenar dados de trailler
                    continue

                if tipo_output == 'csv':
                    if (i_arq + i_bloco) > 0:
                        replace_append = 'a'
                        header=False
                    else:
                        replace_append = 'w'
                        header=True

                    nome_arquivo_csv = REGISTROS_TIPOS[tipo_registro] + '.csv'
                    df.to_csv(os.path.join(output_path,nome_arquivo_csv), 
                              header=header,
                              mode=replace_append,
                              index=False,
                              quoting=csv.QUOTE_NONNUMERIC)

                elif tipo_output == 'sqlite':
                    replace_append = 'append' if (i_arq + i_bloco) > 0 else 'replace' 
                        
                    df.to_sql(REGISTROS_TIPOS[tipo_registro], 
                              con=conBD, 
                              if_exists=replace_append, 
                              index=False)


    if tipo_output == 'sqlite':
        conBD.close()

    # Imprime totais
    print('\nConversao concluida. Validando quantidades:')

    inconsistente = False

    print('Total de registros de empresas: {}'.format(total_empresas), end=' ')
    if total_empresas == controle_empresas:
        print('ok')
    else:
        print('!INCONSISTENTE!')
        inconsistente = True

    print('Total de registros de socios: {}'.format(total_socios), end=' ')
    if total_socios == controle_socios:
        print('ok')
    else:
        print('!INCONSISTENTE!')
        inconsistente = True

    print('Total de registros de CNAEs: {}'.format(total_cnaes), end=' ')
    if total_cnaes == controle_cnaes:
        print('ok')
    else:
        print('!INCONSISTENTE!')
        inconsistente = True


    if inconsistente:
        print(u'Atencao! Foi detectada inconsistencia entre as quantidades lidas e as informacoes de controle do arquivo.')

    if tipo_output == 'csv':
        print(u'Arquivos CSV gerados na pasta {}.'.format(output_path))

    elif tipo_output == 'sqlite':
        print(u'''
Arquivo SQLITE gerado: {}
OBS: Uso de índices altamente recomendado!
              '''.format(os.path.join(output_path,NOME_ARQUIVO_SQLITE)))


def cnpj_index(output_path):
    import sqlite3    

    conBD = sqlite3.connect(os.path.join(output_path,NOME_ARQUIVO_SQLITE))

    print(u'''
Criando índices...
Essa operaçao pode levar vários minutos.
    ''')

    cursorBD = conBD.cursor()

    for indice in INDICES:
        nome_indice = PREFIXO_INDICE + indice[0]

        sql_stmt = 'CREATE INDEX {} ON {} ({});'.format(nome_indice, indice[1], indice[2])
        cursorBD.execute(sql_stmt)

        print(u'Index {} criado.'.format(nome_indice))

    print(u'Indices criados com sucesso.')

    conBD.close()


def help():
    print('''
Uso: python cnpj.py <path_input> <output:csv|sqlite> <path_output> [--dir] [--noindex]
Argumentos opcionais:
 [--dir]: Indica que o <path_input> e uma pasta e pode conter varios ZIPs.
 [--noindex]: NAO gera indices automaticamente no sqlite ao final da carga.

Exemplos: python cnpj.py "data/F.K032001K.D81106D" sqlite "output"
          python cnpj.py "data" sqlite "output" --dir
          python cnpj.py "data" sqlite "output" --dir --noindex
          python cnpj.py "data" csv "output" --dir
    ''')


def main():

    num_argv = len(sys.argv)
    if num_argv < 4:
        help()
        sys.exit(-1)
    else:
        input_path = sys.argv[1]
        tipo_output = sys.argv[2]
        output_path = sys.argv[3]

        gera_index = True
        input_list = [input_path]

        if num_argv > 4:
            for opcional in sys.argv[4:num_argv]:
                if (opcional == '--noindex'):
                    gera_index = False

                elif (opcional == '--dir'):
                    input_list = glob.glob(os.path.join(input_path,'*.zip'))

                    if not input_list:
                        # caso nao ache zip, procura arquivos descompactados.
                        input_list = glob.glob(os.path.join(input_path,'*.L*'))

                    if not input_list:
                        # caso nem assim ache, indica erro.
                        print(u'ERRO: Nenhum arquivo válido encontrado no diretório!')
                        sys.exit(-1)

                    input_list.sort()

                else:
                    print(u'ERRO: Argumento opcional inválido.')
                    help()
                    sys.exit(-1)

        if tipo_output not in ['csv','sqlite']:
            print('''
ERRO: tipo de output inválido. 
Escolha um dos seguintes tipos de output: csv ou sqlite.
            ''')
            help()

        else:
            print('Iniciando processamento em {}'.format(datetime.datetime.now()))

            cnpj_full(input_list, tipo_output, output_path)

            if (gera_index) and (tipo_output == 'sqlite'):
                cnpj_index(output_path)

            print('Processamento concluido em {}'.format(datetime.datetime.now()))

if __name__ == "__main__":
    main()
