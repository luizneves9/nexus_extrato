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

    colunas_valor = ['vlr_anjo', 'vlr_desconhecido', 'vlr_bsr']
    for col in colunas_valor:
        df_extrato_santo_anjo[col] = df_extrato_santo_anjo[col].map(transformar_valor_decimal_em_str)

    st.data_editor(
        df_extrato_santo_anjo,
        hide_index=True,
        width='stretch',
        column_config={
            'id': st.column_config.NumberColumn('ID', format='%d'),
            'data_contabil': st.column_config.DateColumn('Data Extrato', format='DD/MM/YYYY'),
        },
    )

if __name__ == '__main__':
    main()
