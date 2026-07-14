import streamlit as st
import pandas as pd
from datetime import date
from sqlalchemy import text
from sql import engine
from utils.formatadores import transformar_valor_decimal_em_str
from services.extrato_liquidacoes import carregar_empresas, estornar_liquidacao

# ====================================================================================================
# SESSÃO DE DIALOG DO STREAMLIT
# ====================================================================================================

@st.dialog('Estorno de liquidacao')
def modal_estorno_liquidacao(linha_selecionada):

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.text_input('ID:', value=linha_selecionada['ID'], disabled=True)
    with col2:
        st.text_input('Empresa:', value=linha_selecionada['Empresa'], disabled=True)
    with col3:
        st.text_input('Data liq.', value=pd.to_datetime(linha_selecionada['Data liq.']).strftime('%d/%m/%Y'), disabled=True)

    col4, col5, col6 = st.columns([1, 2, 1])
    with col4:
        st.text_input('Banco:', value=linha_selecionada['Banco'], disabled=True)
    with col5:
        st.text_input('Agência/Conta:', value=linha_selecionada['Agência/conta'], disabled=True)
    with col6:
        st.text_input('Data Extrato', value=pd.to_datetime(linha_selecionada['Data Extrato']).strftime('%d/%m/%Y'), disabled=True)

    col7, col8 = st.columns([1, 1])
    with col7:
        st.text_input('Valor bco:', value=linha_selecionada['Valor banco'], disabled=True)
    with col8:
        st.text_input('Valor liq.', value=linha_selecionada['Valor liq.'], disabled=True)
    
    col9, col10 = st.columns([1, 1])
    with col9:
        st.text_input('DP:', value=linha_selecionada['DP'], disabled=True)
    with col10:
        st.text_input('Parc.', value=linha_selecionada['Parc.'], disabled=True)

    st.write('')

    col01, col02 = st.columns([1, 1])

    with col01:
        if st.button('Confirmar', width='stretch', type='primary'):
            sucesso = estornar_liquidacao(
                id=linha_selecionada['ID']
            )
            st.toast('Sistema: Estorno realizado com sucesso!', icon='✅')

            if sucesso:
                st.rerun()

    with col02:
        if st.button('Cancelar', width='stretch'):
            st.rerun()

def main():

    # ====================================================================================================
    # INICIANDO O SESSION_STATE
    # ====================================================================================================

    if 'input_data_1' not in st.session_state: st.session_state.input_data_1 = date.today()
    if 'input_data_2' not in st.session_state: st.session_state.input_data_2 = date.today()
    if 'input_empresa' not in st.session_state: st.session_state.input_empresa = 'GRUPO'
    if 'input_id_extrato' not in st.session_state: st.session_state.input_id_extrato = ''
    if 'input_historico' not in st.session_state: st.session_state.input_historico = ''
    if 'input_valor_banco' not in st.session_state: st.session_state.input_valor_banco = 0
    if 'input_valor_liq' not in st.session_state: st.session_state.input_valor_liq = 0
    if 'input_sistema' not in st.session_state: st.session_state.input_sistema = ''
    if 'input_banco' not in st.session_state: st.session_state.input_banco = ''
    if 'input_agencia' not in st.session_state: st.session_state.input_agencia = ''
    if 'input_dp' not in st.session_state: st.session_state.input_dp = ''

    # ====================================================================================================
    # VISUALIZAÇÃO FRONT
    # ====================================================================================================

    # carregando a lista das empresas
    lista_empresas = carregar_empresas()

    # processando os filtros
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

        # formulario de filtros
        with st.form(key='filtro_form_liquidacao'):
            input_data_1 = st.date_input('Data inicio:', value=st.session_state.input_data_1, format='DD/MM/YYYY')
            input_data_2 = st.date_input('Data fim:', value=st.session_state.input_data_2, format='DD/MM/YYYY')
            input_empresa = st.selectbox('Empresa:', lista_empresas, index=lista_empresas.index(st.session_state.input_empresa) if lista_empresas else 0)
            input_banco = st.text_input('Banco:', value=st.session_state.input_banco)
            input_agencia = st.text_input('Agência/conta:', value=st.session_state.input_agencia)
            input_id_extrato = st.text_input('ID do extrato:', value=st.session_state.input_id_extrato)
            input_historico = st.text_input('Histórico:', value=st.session_state.input_historico)
            input_valor_banco = st.number_input('Valor banco:', value=float(st.session_state.input_valor_banco))
            input_valor_liq = st.number_input('Valor liq.', value=float(st.session_state.input_valor_liq))
            input_sistema = st.text_input('Sistema', value=st.session_state.input_sistema)
            input_dp = st.text_input('DP', value=st.session_state.input_dp)

            submit_button_liq = st.form_submit_button(label='Atualizar')

            if submit_button_liq:
                st.session_state.input_data_1 = input_data_1
                st.session_state.input_data_2 = input_data_2
                st.session_state.input_empresa = input_empresa
                st.session_state.input_id_extrato = input_id_extrato
                st.session_state.input_historico = input_historico
                st.session_state.input_valor_banco = input_valor_banco
                st.session_state.input_valor_liq = input_valor_liq
                st.session_state.input_sistema = input_sistema
                st.session_state.input_banco = input_banco
                st.session_state.input_agencia = input_agencia
                st.session_state.input_dp = input_dp
                st.rerun()

    busca_historico = f'%{st.session_state.input_historico}%'
    busca_sistema = f'%{st.session_state.input_sistema}%'
    busca_banco = f'%{st.session_state.input_banco}%'
    busca_agencia = f'%{st.session_state.input_agencia}%'
    busca_dp = f'%{st.session_state.input_dp}%'

    params_liq = {'data_liq_1': st.session_state.input_data_1,
                    'data_liq_2': st.session_state.input_data_2,
                    'historico': busca_historico,
                    'valor_banco': st.session_state.input_valor_banco,
                    'valor_liq': st.session_state.input_valor_liq,
                    'sistema': busca_sistema,
                    'banco': busca_banco,
                    'agencia': busca_agencia,
                    'dp': busca_dp}

    query_liquidacoes = '''
        SELECT *
        FROM public.vw_registro_liquidacoes
        WHERE "Data liq." >= :data_liq_1
            AND "Data liq." <= :data_liq_2
            AND COALESCE("Histórico", '') ILIKE :historico
            AND COALESCE("Sistema", '') ILIKE :sistema
            AND COALESCE("Banco", '') ILIKE :banco
            AND COALESCE("Agência/conta", '') ILIKE :agencia
            AND COALESCE("DP", '') ILIKE :dp
            AND (
                CASE
                    WHEN :valor_banco = 0 THEN TRUE
                    ELSE "Valor banco" = :valor_banco
                END
            )
            AND (
                CASE
                    WHEN :valor_liq = 0 THEN TRUE
                    ELSE "Valor liq." = :valor_liq
                END
            )
    '''

    if st.session_state.input_empresa != 'GRUPO':
        query_liquidacoes += ' AND "Empresa" = :empresa'
        params_liq['empresa'] = st.session_state.input_empresa

    if st.session_state.input_id_extrato != '':
        query_liquidacoes += ' AND "ID extrato" = :id_extrato'
        params_liq['id_extrato'] = st.session_state.input_id_extrato

    df_liquidacoes = pd.read_sql(text(query_liquidacoes), engine, params=params_liq) #type: ignore
    df_liquidacoes['Data liq.'] = pd.to_datetime(df_liquidacoes['Data liq.']).dt.tz_localize(None)
    df_liquidacoes['Data Extrato'] = pd.to_datetime(df_liquidacoes['Data Extrato']).dt.tz_localize(None)

    if 'Data log' in df_liquidacoes.columns and not df_liquidacoes['Data log'].empty:
        df_liquidacoes['Data log'] = pd.to_datetime(df_liquidacoes['Data log']).dt.tz_convert('America/Sao_Paulo')

    df_com_selecao = df_liquidacoes.copy()
    df_com_selecao.insert(0, 'Sel', False)

    tabela_editavel = st.data_editor(
        df_com_selecao,
        key='editor_liquidacoes',
        hide_index=True,
        width='stretch',
        column_config={
            'Sel': st.column_config.CheckboxColumn('', default=False),
            'ID': st.column_config.NumberColumn('ID', format='%d'),
            'Valor banco': st.column_config.NumberColumn('Valor banco', format='%.2f'),
            'Valor liq.': st.column_config.NumberColumn('Valor liq.', format='%.2f'),
            'Data liq.': st.column_config.DateColumn('Data liq.', format='DD/MM/YYYY'),
            'Data Extrato': st.column_config.DateColumn('Data Extrato', format='DD/MM/YYYY'),
            'Data log': st.column_config.DatetimeColumn('Data log', format='DD/MM/YYYY HH:mm:ss')
        },
        disabled=[c for c in df_com_selecao.columns if c!= 'Sel']
    )

    selecionados = tabela_editavel[tabela_editavel['Sel'] == True]

    if not selecionados.empty:
        if len(selecionados) > 1:
            st.error('Selecione apenas um item por vez.')
        else:
            linha = selecionados.iloc[0]

            if st.button(f'Estornar - ID {linha["ID"]}', type='primary', key=f'btn_estorno{linha["ID"]}'):
                modal_estorno_liquidacao(linha)

    else:
        st.caption('Selecione um registro acima para habilitar as opções de estorno.')

if __name__ == '__main__':
    main()
