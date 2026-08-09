import streamlit as st
import pandas as pd
from repositories.extratos_repositories import transformar_valor_decimal_em_str

@st.dialog('Detalhamento do Registro Bancário', width='medium')
def detalhar_lancamentos(df_extrato, df_liquidacoes):
    '''Modal de montagem do detalhamento referente ao registro bancário.'''
    
    st.markdown(f'### Registro bancário: {df_extrato.iloc[0]['Empresa'].title()}')

    st.dataframe(df_extrato.iloc[:,1:], hide_index=True)

    st.markdown('### Lançamentos realizados:')

    st.dataframe(df_liquidacoes, hide_index=True)
