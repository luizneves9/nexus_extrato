import streamlit as st
import pandas as pd
from repositories.extratos_repositories import transformar_valor_decimal_em_str

@st.dialog('Lançamentos', width='medium')
def detalhar_lancamentos(dados, linha_selecionada):
    '''Modal de montagem do detalhamento referente ao registro bancário.'''
    
    st.markdown(f'## Registro bancário: {linha_selecionada['Empresa'].title()}')

    # transformando em dataframe
    df = [{
        'ID': linha_selecionada['id'],
        'Data': linha_selecionada['Data'],
        'Banco': linha_selecionada['Banco'],
        'Agência/Conta': linha_selecionada['Agência/Conta'],
        'Desc. do Hist.': linha_selecionada['Desc. do Hist.'],
        'Valor': linha_selecionada['Valor'],
        'Valor liq.': linha_selecionada['Valor liq.'],
        'Saldo': linha_selecionada['Saldo']
    }]

    df_extrato = pd.DataFrame(df)

    # transformando as colunas de valor para a formatação brasileira
    colunas_valor = ['Valor', 'Valor liq.', 'Saldo']
    for col in colunas_valor:
        df_extrato[col] = df_extrato[col].map(transformar_valor_decimal_em_str)

    st.dataframe(df_extrato, hide_index=True)

    st.markdown('## Lançamentos realizados:')

    dados['Valor liq.'] = dados['Valor liq.'].map(transformar_valor_decimal_em_str)

    st.dataframe(dados, hide_index=True)
