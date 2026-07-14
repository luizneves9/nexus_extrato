import pandas as pd
from sqlalchemy import text
from sql import conectar_banco
from queries.resumo_bancario import QUERY_RESUMO

engine = conectar_banco()

def obter_dados_resumo(input_data, input_empresa) -> pd.DataFrame:
    
    busca_empresa = f'%{input_empresa}%'

    parametro = {
        'data': input_data,
        'empresa': busca_empresa
    }

    return pd.read_sql(text(QUERY_RESUMO), engine, params=parametro)
