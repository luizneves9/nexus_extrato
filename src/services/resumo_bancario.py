import pandas as pd
from sqlalchemy import text
from sql import conectar_banco

engine = conectar_banco()

def obter_dados_resumo(input_data, input_empresa, query) -> pd.DataFrame:
    
    busca_empresa = f'%{input_empresa}%'

    parametro = {
        'data': input_data,
        'empresa': busca_empresa
    }

    return pd.read_sql(text(query), engine, params=parametro)
