import pandas as pd
from sqlalchemy import text
from database.connection import conectar_banco
from queries.liquidacoes_queries import LISTA_EMPRESAS, ESTORNAR_LIQUIDACAO, SELECT_LIQUIDACOES

def buscar_empresas():
    '''Busca no banco de dados e retorna a lista de empresas.'''
    df_empresas = pd.read_sql(LISTA_EMPRESAS, con=conectar_banco())
    return ['GRUPO'] + df_empresas['nome_empresa'].to_list()

def executar_estorno(id):
    '''Executa a exclusão da liquidação no banco de dados.'''
    with conectar_banco().begin() as conn:
        conn.execute(text(ESTORNAR_LIQUIDACAO), { "id_selecionado": int(id)})
    return True

def buscar_liquidacoes(filtros):
    '''Monta a query com base nos filtros e retorna o dataframe.'''
    query = SELECT_LIQUIDACOES
    params = {
        'data_liq_1': filtros['data_1'],
        'data_liq_2': filtros['data_2'],
        'historico': f'%{filtros["historico"]}%',
        'valor_banco': filtros['valor_banco'],
        'valor_liq': filtros['valor_liq'],
        'sistema': f'%{filtros["sistema"]}%',
        'banco': f'%{filtros["banco"]}%',
        'agencia': f'%{filtros["agencia"]}%',
        'dp': f'%{filtros["dp"]}%'
    }

    if filtros['empresa'] != 'GRUPO':
        query += ' AND "Empresa" = :empresa'
        params['empresa'] = filtros['empresa']

    if filtros['id_extrato']:
        query += ' AND "ID extrato" = :id_extrato'
        params['id_extrato'] = filtros['id_extrato']

    df = pd.read_sql(text(query), conectar_banco(), params=params)

    if not df.empty:
        df['Data liq.'] = pd.to_datetime(df['Data liq.']).dt.tz_localize(None)
        df['Data Extrato'] = pd.to_datetime(df['Data Extrato']).dt.tz_localize(None)

    return df