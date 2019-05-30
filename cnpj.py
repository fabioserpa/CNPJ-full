# -*- encoding: utf-8 -*-
import os
import sys
import csv

import pandas as pd

from cfwf import read_cfwf

REGISTROS_TIPOS = {
    '1':'empresas',
    '2':'socios',
    '6':'cnaes_secundarios'
}

EMPRESAS_COLUNAS = [
    'cnpj',
    'matriz_filial',     
    'razao_social',      
    'nome_fantasia',     
    'situacao',          
    'data_situacao',     
    'motivo_situacao',   
    'nm_cidade_exterior',
    'cod_pais',          
    'nome_pais',         
    'cod_nat_juridica',  
    'data_inicio_ativ',  
    'cnae_fiscal',       
    'tipo_logradouro',   
    'logradouro',        
    'numero',            
    'complemento',       
    'bairro',            
    'cep',               
    'uf',                
    'cod_municipio',     
    'municipio',         
    'ddd_1',             
    'telefone_1',        
    'ddd_2',             
    'telefone_2',        
    'ddd_fax',           
    'num_fax',           
    'email',             
    'qualif_resp',       
    'capital_social',    
    'porte',             
    'opc_simples',       
    'data_opc_simples',  
    'data_exc_simples',  
    'opc_mei',           
    'sit_especial',      
    'data_sit_especial'
]

EMPRESAS_COLSPECS = [
    (3, 17), 
    (17 ,18 ),
    (18 ,168),
    (168,223),
    (223,225),
    (225,233),
    (233,235),
    (235,290),
    (290,293),
    (293,363),
    (363,367),
    (367,375),
    (375,382),
    (382,402),
    (402,462),
    (462,468),
    (468,624),
    (624,674),
    (674,682),
    (682,684),
    (684,688),
    (688,738),
    (738,742),
    (742,750),
    (750,754),
    (754,762),
    (762,766),
    (766,774),
    (774,889),
    (889,891),
    (891,905),
    (905,907),
    (907,908),
    (908,916),
    (916,924),
    (924,925),
    (925,948),
    (948,956)
]

EMPRESAS_DTYPE = {'capital_social':float}

SOCIOS_COLUNAS = [
    'cnpj',
    'tipo_socio',      
    'nome_socio',       
    'cnpj_cpf_socio',   
    'cod_qualificacao', 
    'perc_capital',     
    'data_entrada',     
    'cod_pais_ext',     
    'nome_pais_ext',    
    'cpf_repres',       
    'nome_repres',      
    'cod_qualif_repres'
]

SOCIOS_COLSPECS = [
    (3, 17),      
    (17 ,18 ),
    (18 ,168),
    (168,182),
    (182,184),
    (184,189),
    (189,197),
    (197,200),
    (200,270),
    (270,281),
    (281,341),
    (341,343)
]

SOCIOS_DTYPE = {'perc_capital':float}

CNAES_COLUNAS = ['cnpj'] + [num for num in range(99)]
CNAES_COLSPECS = [(3,17)] + [(num*7+17,num*7+24) for num in range(99)]

# (<nome_do_indice>,<tabela>,<coluna>)
INDICES = [
    ('empresas_cnpj', REGISTROS_TIPOS['1'], EMPRESAS_COLUNAS[0]),
    ('empresas_raiz', REGISTROS_TIPOS['1'], 'substr({},0,9)'.format(EMPRESAS_COLUNAS[0])),
    ('socios_cnpj', REGISTROS_TIPOS['2'], SOCIOS_COLUNAS[0]),
    ('socios_cpf_cnpj', REGISTROS_TIPOS['2'], SOCIOS_COLUNAS[3]),
    ('socios_nome', REGISTROS_TIPOS['2'], SOCIOS_COLUNAS[2]),
    ('cnaes_cnpj', REGISTROS_TIPOS['6'], CNAES_COLUNAS[0])
]

PREFIXO_INDICE = 'ix_'

CHUNKSIZE=100000

NOME_ARQUIVO_SQLITE = 'CNPJ_full.db'

def cnpj_full(input_path, tipo_output, output_path):

    if tipo_output == 'sqlite':
        import sqlite3
        conBD = sqlite3.connect(os.path.join(output_path,NOME_ARQUIVO_SQLITE))

    dados = read_cfwf(input_path, 
                      type_width=1, 
                      colspecs= {'1':EMPRESAS_COLSPECS,
                                 '2':SOCIOS_COLSPECS,
                                 '6':CNAES_COLSPECS},
                      names={'1': EMPRESAS_COLUNAS, 
                             '2': SOCIOS_COLUNAS,
                             '6': CNAES_COLUNAS},
                      dtype={'1': EMPRESAS_DTYPE,
                         '2': SOCIOS_DTYPE},
                      chunksize=CHUNKSIZE)

    for i, dado in enumerate(dados):
        print('Processando bloco {}: até linha {}.'.format(i+1,(i+1)*CHUNKSIZE), end='\r')

        for tipo_registro, df in dado.items():

            if tipo_registro == '1': # empresas
                # Troca datas zeradas por vazio
                df['data_opc_simples'] = (df['data_opc_simples']
                        .where(df['data_opc_simples'] != '00000000',''))
                df['data_exc_simples'] = (df['data_exc_simples']
                        .where(df['data_exc_simples'] != '00000000',''))
                df['data_sit_especial'] = (df['data_sit_especial']
                        .where(df['data_sit_especial'] != '00000000',''))

            elif tipo_registro == '2': # socios
                # Troca cpf invalido por vazio
                df['cpf_repres'] = (df['cpf_repres']
                        .where(df['cpf_repres'] != '***000000**',''))
                df['nome_repres'] = (df['nome_repres']
                        .where(df['nome_repres'] != 'CPF INVALIDO',''))  

                # Se socio for tipo 1 (cnpj), deixa campo intacto, do contrario, 
                # fica apenas com os ultimos 11 digitos
                df['cnpj_cpf_socio'] = (df['cnpj_cpf_socio']
                        .where(df['tipo_socio'] == '1',
                               df['cnpj_cpf_socio'].str[-11:]))

            elif tipo_registro == '6': # cnaes_secundarios       
                # Verticaliza tabela de associacao de cnaes secundarios,
                # mantendo apenas os validos (diferentes de 0000000)
                df = pd.melt(df, 
                             id_vars=[CNAES_COLUNAS[0]], 
                             value_vars=range(99),
                             var_name='cnae_ordem', 
                             value_name='cnae')

                df = df[df['cnae'] != '0000000']

            if tipo_output == 'csv':
                if i > 0:
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
                replace_append = 'append' if i > 0 else 'replace' 
                    
                df.to_sql(REGISTROS_TIPOS[tipo_registro], 
                          con=conBD, 
                          if_exists=replace_append, 
                          index=False)

    if tipo_output == 'csv':
        print(u'''
            Arquivos CSV gerados na pasta {}. 
            '''.format(output_path))

    elif tipo_output == 'sqlite':
        conBD.close()
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

    print(u'''
        Indices criados com sucesso.
    ''')

    conBD.close()

def help():
    print('''
        Uso: python cnpj.py <arquivo_input> <output:csv|sqlite> <path_output> [--index]
        Exemplo: python cnpj.py "data/F.K032001K.D81106D" sqlite "data" --index
    ''')

def main():
    # python cnpj.py <arquivo_input> <output:csv|sqlite> <arquivo_output> [--index]
    num_argv = len(sys.argv)
    if num_argv < 4:
        help()
        sys.exit(-1)
    else:
        input_path = sys.argv[1]
        tipo_output = sys.argv[2]
        output_path = sys.argv[3]

        if tipo_output not in ['csv','sqlite']:
            print('''
                Erro: tipo de output inválido. 
                Escolha um dos seguintes tipos de output: csv ou sqlite.
            ''')

            help()
        else:
            cnpj_full(input_path, tipo_output, output_path)

            # Possui argumento opcional
            if num_argv > 4:
                for opcional in sys.argv[4:num_argv]:
                    if (opcional == '--index') and (tipo_output == 'sqlite'):
                        cnpj_index(output_path)

            print('\nProcessamento concluído!')

if __name__ == "__main__":
    main()