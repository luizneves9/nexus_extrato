import streamlit as st
import pandas as pd
from sqlalchemy import text
from sql import conectar_banco
from queries.extrato_liquidacoes import LISTA_EMPRESAS, ESTORNAR_LIQUIDACAO

engine = conectar_banco()

@st.cache_data
def carregar_empresas():

    # carregando as empresas
    df_empresas = pd.read_sql(LISTA_EMPRESAS, engine)

    # transformando em lista
    lista_empresas = ['GRUPO'] + df_empresas['nome_empresa'].to_list()

    return lista_empresas

def estornar_liquidacao(id):
    try:
        with engine.begin() as conn:
            query = text(ESTORNAR_LIQUIDACAO)
            conn.execute(query, {
                "id_selecionado": int(id)
            })
            return True
    except Exception as e:
        st.toast(f'Erro ao salvar no banco: {e}', icon='❌')
        return False
    
