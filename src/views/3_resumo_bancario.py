import streamlit as st
from datetime import date
from services.resumo_bancario import obter_dados_resumo
from queries.resumo_bancario import QUERY_RESUMO, QUERY_RESUMO_APLICACAO

# =========================================================================
# INICIALIZANDO O SESSION_STATE
# =========================================================================

def inicializar_state():
    '''Inicialização do session state'''
    defaults = {
        'resumo_bancario_data': date.today(),
        'resumo_bancario_empresa': '',
        'resumo_bancario_banco': '',
        'resumo_bancario_agencia': ''
    }
    for key, val in defaults.items():
        if not key in st.session_state:
            st.session_state[key] = val

# =========================================================================
# FUNÇÕES
# =========================================================================

def transformar_valor_em_str(valor):
    return f'{valor:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.')

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

# =========================================================================
# FILTROS
# =========================================================================

def render_sidebar():
    '''Renderizar o sidebar de filtros.'''

    with st.form(key='filtro_form_resumo_bancario'):

        st.markdown(
                    """
                    <style>
                    /* Corrige a margem do botão de submit para alinhar perfeitamente aos campos */
                    div[data-testid="stFormSubmitButton"] {
                        margin-top: 28px;
                    }
                    </style>
                """,
                    unsafe_allow_html=True,
                )

        st.markdown('''
            <h6 style='margin-bottom: 0px;'>Filtros Personalizados</h6>
            ''',
            unsafe_allow_html=True
        )

        col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
        with col1: selecao_data = st.date_input('Data:', value=st.session_state.resumo_bancario_data, format='DD/MM/YYYY')
        with col2: selecao_empresa = st.text_input('Empresa:', value=st.session_state.resumo_bancario_empresa)
        with col3: selecao_banco = st.text_input('Banco', value=st.session_state.resumo_bancario_banco, placeholder='<em desenvolvimento>')
        with col4: selecao_agencia = st.text_input('Agencia', value=st.session_state.resumo_bancario_agencia, placeholder='<em desenvolvimento>')
        with col5: submit_button_filtros = st.form_submit_button(label='Mais filtros', use_container_width=True)
        with col6: submit_button = st.form_submit_button(label='Atualizar', use_container_width=True)

        if submit_button:
            st.session_state.resumo_bancario_data = selecao_data
            st.session_state.resumo_bancario_empresa = selecao_empresa
            st.session_state.resumo_bancario_banco = selecao_banco
            st.session_state.resumo_bancario_agencia = selecao_agencia
            st.rerun()

        if submit_button:
            st.toast('<em desenvolvimento>')

# =========================================================================
# VISUALIZAÇÃO DOS DADOS
# =========================================================================

def main():

    st.markdown('''
            <h2 style='margin-bottom: 0px;'>Resumo Bancário</h2>
            <p style='margin-top: -15px; color: #666; font-style: italic;'>
                Acompanhe o resumo dos valores em conta corrente e aplicação.
            </p>
            ''',
            unsafe_allow_html=True)

    inicializar_state()
    render_sidebar()

    # tabela de dados da conta corrente

    with st.container(border=True):

        st.markdown('''
            <h6 style='margin-bottom: 0px;'>Conta Corrente</h6>
            ''',
            unsafe_allow_html=True
        )

        df = obter_dados_resumo(st.session_state.resumo_bancario_data, st.session_state.resumo_bancario_empresa, QUERY_RESUMO)

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

        soma_credito = df.loc[df['Data'] == st.session_state.resumo_bancario_data, 'Crédito'].sum()
        soma_debito = df.loc[df['Data'] == st.session_state.resumo_bancario_data, 'Débito'].sum()
        soma_econtas = df.loc[df['Data'] == st.session_state.resumo_bancario_data, 'Encontro de Contas'].sum()
        soma_transferencia = df.loc[df['Data'] == st.session_state.resumo_bancario_data, 'Transferência'].sum()
        soma_resgate = df.loc[df['Data'] == st.session_state.resumo_bancario_data, 'Resgate'].sum()
        soma_aplicacao = df.loc[df['Data'] == st.session_state.resumo_bancario_data, 'Aplicação'].sum()
        soma_saldo = df['Saldo'].sum()

        with st.container(horizontal=True):
            st.metric('Crédito', f'R$ {soma_credito:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))
            st.metric('Débito', f'R$ {soma_debito:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))
            st.metric('Encontro de Contas', f'R$ {soma_econtas:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))
            st.metric('Transferência', f'R$ {soma_transferencia:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))
            st.metric('Resgate', f'R$ {soma_resgate:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))
            st.metric('Aplicação', f'R$ {soma_aplicacao:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))
            st.metric('Saldo', f'R$ {soma_saldo:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))

        lista_colunas_valores = ['Crédito', 'Débito', 'Encontro de Contas', 'Transferência', 'Resgate', 'Aplicação', 'Mov. do dia', 'Saldo']
        for col in lista_colunas_valores:
            df[col] = df[col].map(transformar_valor_em_str)

        st.dataframe(
            df,
            hide_index=True
        )

    # tabela de dados da aplicação
    with st.container(border=True):
        st.markdown('''
            <h6 style='margin-bottom: 0px;'>Aplicação</h6>
            ''',
            unsafe_allow_html=True
        )

        df_aplicacao = obter_dados_resumo(st.session_state.resumo_bancario_data, st.session_state.resumo_bancario_empresa, QUERY_RESUMO_APLICACAO)

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

        soma_resgate_invest = df_aplicacao.loc[df['Data'] == st.session_state.resumo_bancario_data, 'Resgate'].sum()
        soma_aplicacao_invest = df_aplicacao.loc[df['Data'] == st.session_state.resumo_bancario_data, 'Aplicação'].sum()
        soma_rendimento_invest = df_aplicacao.loc[df['Data'] == st.session_state.resumo_bancario_data, 'Rendimento'].sum()
        soma_saldo_invest = df_aplicacao['Saldo'].sum()

        with st.container(horizontal=True):
            st.metric('Resgate', f'R$ {soma_resgate_invest:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))
            st.metric('Aplicação', f'R$ {soma_aplicacao_invest:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))
            st.metric('Rendimento', f'R$ {soma_rendimento_invest:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))
            st.metric('Saldo', f'R$ {soma_saldo_invest:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.'))

        lista_colunas_valores_aplic = ['Resgate', 'Aplicação', 'Rendimento', 'Mov. do dia', 'Saldo']
        for col in lista_colunas_valores_aplic:
            df_aplicacao[col] = df_aplicacao[col].map(transformar_valor_em_str)

        st.dataframe(
            df_aplicacao,
            hide_index=True
        )

if __name__ == '__main__':
    main()