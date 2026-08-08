import pandas as pd
from sqlalchemy import text
from database.connection import conectar_banco
from queries.extrato_queries import LISTA_EMPRESAS, SELECT_EXTRATO, SELECT_LIQUIDACOES_ID, INSERIR_REGISTRO

engine = conectar_banco()

def transformar_valor_decimal_em_str(valor):

    if isinstance(valor, str):
        return str(valor)

    if isinstance(valor, (float, int)):
        return f'{valor:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.')

def transformar_valor_decimal_str_em_float(valor):

    if isinstance(valor, (float, int)):
        return float(valor)

    if isinstance(valor, str):
        return float(valor.replace('.', '').replace(',', '.'))

def buscar_empresas():
    '''Busca no banco de dados e retorna a lista de empresas.'''
    df_empresas = pd.read_sql(LISTA_EMPRESAS, con=engine)
    return ['GRUPO'] + df_empresas['nome_empresa'].to_list()

def buscar_extratos(filtros):
    '''Monta a query com base nos filtros e retorna o dataframe.'''
    query = SELECT_EXTRATO
    params = {
        'data_1': filtros['data_1'],
        'data_2': filtros['data_2'],
        'historico': f'%{filtros['historico']}%',
        'banco': f'%{filtros['banco']}%',
        'agencia': f'%{filtros['agencia']}%',
        'complemento': f'%{filtros['complemento']}%',
        'id': f'%{filtros['id']}%',
        'valor': filtros['valor']
    }

    if filtros['empresa'] != 'GRUPO':
        query += ' AND nome_empresa = :empresa'
        params['empresa'] = filtros['empresa']

    query += ' ORDER BY ext.data_contabil ASC, ext.id ASC'

    df = pd.read_sql(text(query), conectar_banco(), params=params)

    colunas_valor = ['Valor', 'Valor liq.', 'Saldo']

    for col in colunas_valor:
        df[col] = df[col].map(transformar_valor_decimal_em_str)

    return df

def salvar_liquidacao(sistema, id_extrato, valor, data_baixa, duplicata, parcela):
        '''Acessa o banco de dados e inseri um registro de liquidação.'''
        parametros = {
                    "id": int(id_extrato),
                    "val": valor,
                    "dt": data_baixa,
                    "sis": sistema,
                    "dp": duplicata,
                    "par": parcela
                }
        with engine.begin() as conn:
            conn.execute(text(INSERIR_REGISTRO), parametros)

def buscar_liquidacoes_id(filtros):
    '''Monta a query com base nos filtros e retorna o dataframe.'''
    query = SELECT_LIQUIDACOES_ID
    params = {
        'id_selecionado_extrato': filtros['id_selecionado_extrato']
    }

    df = pd.read_sql(text(query), conectar_banco(), params=params)

    return df

def update_tipo(id, tipo):
    with engine.begin() as conn:
        query = text('''
            UPDATE public.db_extratos
            SET tipo = :tipo_novo
            WHERE id = :id_selecionado
        ''')
        conn.execute(query, {
            "id_selecionado": int(id),
            "tipo_novo": str(tipo)
        })
        return True

def registrar_exclusao_extrato(query, id, conn):
    '''Deleta um registro de extrato bancário no banco de dados.'''
    result = conn.execute(query, {'id_linha': int(id)})
    return result

def executar_refresh_view(query):
    with engine.begin() as conn:
        conn.execute(query)
