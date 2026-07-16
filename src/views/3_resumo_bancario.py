import streamlit as st
from datetime import date
from services.resumo_bancario import obter_dados_resumo
from queries.resumo_bancario import QUERY_RESUMO, QUERY_RESUMO_APLICACAO

# =========================================================================
# INICIALIZANDO O SESSION_STATE
# =========================================================================

if 'resumo_bancario_input_empresa' not in st.session_state: st.session_state.resumo_bancario_input_empresa = ''
if 'resumo_bancario_input_data' not in st.session_state: st.session_state.resumo_bancario_input_data = date.today()

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
        resumo_bancario_input_empresa = st.text_input('Empresa:', value=st.session_state.resumo_bancario_input_empresa)
        resumo_bancario_input_data = st.date_input('Data:', value=st.session_state.resumo_bancario_input_data, format='DD/MM/YYYY')

        if st.form_submit_button('Atualizar'):
            st.session_state.resumo_bancario_input_data = resumo_bancario_input_data
            st.session_state.resumo_bancario_input_empresa = resumo_bancario_input_empresa
            st.rerun()

# =========================================================================
# VISUALIZAÇÃO DOS DADOS
# =========================================================================

# tabela de dados da conta corrente
st.title('Conta Corrente')

df = obter_dados_resumo(st.session_state.resumo_bancario_input_data, st.session_state.resumo_bancario_input_empresa, QUERY_RESUMO)

st.markdown(
    """
    <style>
    [data-testid="stMetricValue"] {
        font-size: 20px !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 13px !important;
    }
    div[data-testid="stMetric"] {
        padding: 0px !important;
        margin-top: -10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

soma_credito = df.loc[df['Data'] == st.session_state.resumo_bancario_input_data, 'Crédito'].sum()
soma_debito = df.loc[df['Data'] == st.session_state.resumo_bancario_input_data, 'Débito'].sum()
soma_econtas = df.loc[df['Data'] == st.session_state.resumo_bancario_input_data, 'Encontro de Contas'].sum()
soma_transferencia = df.loc[df['Data'] == st.session_state.resumo_bancario_input_data, 'Transferência'].sum()
soma_resgate = df.loc[df['Data'] == st.session_state.resumo_bancario_input_data, 'Resgate'].sum()
soma_aplicacao = df.loc[df['Data'] == st.session_state.resumo_bancario_input_data, 'Aplicação'].sum()
soma_saldo = df.loc[df['Data'] == st.session_state.resumo_bancario_input_data, 'Saldo'].sum()

with st.container(horizontal=True):
    st.metric('Crédito', f'R$ {soma_credito:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))
    st.metric('Débito', f'R$ {soma_debito:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))
    st.metric('Encontro de Contas', f'R$ {soma_econtas:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))
    st.metric('Transferência', f'R$ {soma_transferencia:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))
    st.metric('Resgate', f'R$ {soma_resgate:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))
    st.metric('Aplicação', f'R$ {soma_aplicacao:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))
    st.metric('Saldo', f'R$ {soma_saldo:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))

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

# tabela de dados da aplicação
st.title('Aplicação')

df_aplicacao = obter_dados_resumo(st.session_state.resumo_bancario_input_data, st.session_state.resumo_bancario_input_empresa, QUERY_RESUMO_APLICACAO)

st.markdown(
    """
    <style>
    [data-testid="stMetricValue"] {
        font-size: 20px !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 13px !important;
    }
    div[data-testid="stMetric"] {
        padding: 0px !important;
        margin-top: -10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

soma_resgate_invest = df_aplicacao.loc[df['Data'] == st.session_state.resumo_bancario_input_data, 'Resgate'].sum()
soma_aplicacao_invest = df_aplicacao.loc[df['Data'] == st.session_state.resumo_bancario_input_data, 'Aplicação'].sum()
soma_rendimento_invest = df_aplicacao.loc[df['Data'] == st.session_state.resumo_bancario_input_data, 'Rendimento'].sum()
soma_saldo_invest = df_aplicacao.loc[df['Data'] == st.session_state.resumo_bancario_input_data, 'Saldo'].sum()

with st.container(horizontal=True):
    st.metric('Resgate', f'R$ {soma_resgate_invest:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))
    st.metric('Aplicação', f'R$ {soma_aplicacao_invest:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))
    st.metric('Rendimento', f'R$ {soma_rendimento_invest:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))
    st.metric('Saldo', f'R$ {soma_saldo_invest:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))

st.dataframe(
    df_aplicacao,
    hide_index=True,
    column_config={
        'Resgate': st.column_config.NumberColumn('Resgate', format='%.2f'),
        'Aplicação': st.column_config.NumberColumn('Aplicação', format='%.2f'),
        'Rendimento': st.column_config.NumberColumn('Rendimento', format='%.2f'),
        'Mov. do dia': st.column_config.NumberColumn('Mov. do dia', format='%.2f'),
    }
)
