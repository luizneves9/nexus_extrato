import streamlit as st
import pandas as pd
from sqlalchemy import text
from queries.register_banco_queries import CONTAS_BANCARIAS
from database.connection import conectar_banco
from repositories.register_banco_repositories import buscar_contas

engine = conectar_banco()

@st.cache_data
def obter_lista_contas_bancarias():
    '''Serviço com cache para listagem das contas bancarias.'''

    query = text(CONTAS_BANCARIAS)

    try:
        with engine.begin() as conn:
            df = buscar_contas(query, conn)
            return df
    except Exception as e:
        st.write(e)

        
