import streamlit as st
from datetime import date
from services.resumo_bancario import obter_dados_resumo

# =========================================================================
# INICIALIZANDO O SESSION_STATE
# =========================================================================

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
# VISUALIZAÇÃO DOS DADOS
# =========================================================================

df = obter_dados_resumo(st.session_state.input_data, st.session_state.input_empresa)

st.dataframe(
    df,
    hide_index=True,
    column_config={
        'Crédito': st.column_config.NumberColumn('Crédito', format='%.2f'),
        'Saldo': st.column_config.NumberColumn('Saldo', format='%.2f'),
        'Débito': st.column_config.NumberColumn('Débito', format='%.2f'),
        'Encontro de Contas': st.column_config.NumberColumn('Encontro de Contas', format='%.2f'),
        'Transferência': st.column_config.NumberColumn('Transferência', format='%.2f'),
        'Resgate': st.column_config.NumberColumn('Resgate', format='%.2f'),
        'Aplicação': st.column_config.NumberColumn('Aplicação', format='%.2f'),
        'Mov. do dia': st.column_config.NumberColumn('Mov. do dia', format='%.2f'),
    }
)