import pandas as pd
import streamlit as st
from sqlalchemy import text
from sql import conectar_banco
from datetime import date
from queries.rb_select import query_resumo

# =========================================================================
# CONFIGURAÇÕES INICIAIS
# =========================================================================

engine = conectar_banco()

if 'input_empresa' not in st.session_state: st.session_state.input_empresa = ''
if 'input_data' not in st.session_state: st.session_state.input_data = date.today()

# =========================================================================
# INTERAÇÕES COM O USUÁRIO
# =========================================================================

with st.sidebar:

    st.html(
            """
            <style>
            [data-testid="stSidebar"] [data-testid="stForm"] {
                border: none;
                padding: 0;
                background-color: transparent;
            }
            </style>
            """
        )

    with st.form(key='filtro_resumo_bancario'):
        input_empresa = st.text_input('Empresa:', value=st.session_state.input_empresa)
        input_data = st.date_input('Data:', value=st.session_state.input_data, format='DD/MM/YYYY')

        if st.form_submit_button('Atualizar'):
            st.session_state.input_data = input_data
            st.session_state.input_empresa = input_empresa
            st.rerun()

# =========================================================================
# MONTAGEM DE PARÂMETROS
# =========================================================================

busca_empresa = f'%{st.session_state.input_empresa}%'

parametros = {
    'data': st.session_state.input_data,
    'empresa': busca_empresa
}

query_resumo += ' AND nome_empresa ILIKE :empresa'

# =========================================================================
# VISUALIZAÇÃO
# =========================================================================

df = pd.read_sql(text(query_resumo), engine, params=parametros)

st.dataframe(df, hide_index=True)