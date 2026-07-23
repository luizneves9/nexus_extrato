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


    df_extrato_santo_anjo = pd.read_sql(SELECT_EXTRATO_SANTO_ANJO, engine)

    st.data_editor(
        df_extrato_santo_anjo,
        hide_index=True,
        width='stretch',
        column_config={
            'id': st.column_config.NumberColumn('ID', format='%d'),
            'vlr_anjo': st.column_config.NumberColumn('Vlr Anjo', format='%.2f'),
            'vlr_desconhecido': st.column_config.NumberColumn('Vlr Desc.', format='%.2f'),
            'vlr_bsr': st.column_config.NumberColumn('Vlr Bsr', format='%.2f'),
            'data_contabil': st.column_config.DateColumn('Data Extrato', format='DD/MM/YYYY'),
        },
    )

if __name__ == '__main__':
    main()
