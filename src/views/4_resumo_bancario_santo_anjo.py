import streamlit as st
import pandas as pd
from sqlalchemy import text
from sql import engine
from queries.resumo_bancario_santo_anjo import SELECT_EXTRATO_SANTO_ANJO

# ====================================================================================================
# SESSÃO DE DIALOG DO STREAMLIT
# ====================================================================================================

def main():

    # ====================================================================================================
    # VISUALIZAÇÃO FRONT
    # ====================================================================================================

    def transformar_valor_decimal_em_str(valor):
        return f'{valor:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.')

    df_extrato_santo_anjo = pd.read_sql(SELECT_EXTRATO_SANTO_ANJO, engine)

    colunas_valor = ['valor_banco', 'vlr_anjo', 'vlr_desconhecido', 'vlr_bsr']
    for col in colunas_valor:
        df_extrato_santo_anjo[col] = df_extrato_santo_anjo[col].map(transformar_valor_decimal_em_str)

    st.data_editor(
        df_extrato_santo_anjo,
        hide_index=True,
        width='stretch',
        column_config={
            'id': st.column_config.NumberColumn('Id', format='%d'),
            'nome_empresa': st.column_config.TextColumn('Empresa'),
            'banco': st.column_config.TextColumn('Banco'),
            'agencia_conta': st.column_config.TextColumn('Ag/Cc'),
            'data_contabil': st.column_config.DateColumn('Data', format='DD/MM/YYYY'),
            'descricao_historico': st.column_config.TextColumn('Hist.'),
            'documento': st.column_config.TextColumn('Doc.'),
            'complemento': st.column_config.TextColumn('Comp.'),
            'tipo': st.column_config.TextColumn('Tipo'),
            'valor_banco': st.column_config.TextColumn('Vlr Banco'),
            'vlr_anjo': st.column_config.TextColumn('Vlr Anjo'),
            'vlr_desconhecido': st.column_config.TextColumn('Vlr Desc.'),
            'vlr_bsr': st.column_config.TextColumn('Vlr Bsr'),
        },
    )

if __name__ == '__main__':
    main()
