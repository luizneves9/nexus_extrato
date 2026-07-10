import streamlit as st
import pandas as pd
from datetime import date
from sqlalchemy import text
from sql import engine

@st.cache_data
def carregar_filtro(_engine, trigger_atualizacao):

    # carregando as datas
    query_datas_extrato = 'SELECT DISTINCT data_contabil FROM public.db_extratos ORDER BY data_contabil'
    query_datas_liquidacao = 'SELECT DISTINCT "Data liq." FROM public.vw_registro_liquidacoes ORDER BY "Data liq."'

    df_datas_extrato = pd.read_sql(query_datas_extrato, _engine)
    df_datas_extrato['data_contabil'] = pd.to_datetime(df_datas_extrato['data_contabil']).dt.date

    df_datas_liquidacao = pd.read_sql(query_datas_liquidacao, _engine)
    df_datas_liquidacao['Data liq.'] = pd.to_datetime(df_datas_liquidacao['Data liq.']).dt.date

    # carregando as empresas
    query_empresas = 'SELECT DISTINCT nome_empresa FROM public.db_extratos'
    df_empreas = pd.read_sql(query_empresas, engine)

    # transformando em lista
    lista_datas_extrato = df_datas_extrato['data_contabil'].to_list()
    lista_datas_liquidacao = df_datas_liquidacao['Data liq.'].to_list()
    lista_empresas = ['GRUPO'] + df_empreas['nome_empresa'].to_list()

    return lista_datas_extrato, lista_empresas, lista_datas_liquidacao

def transformar_valor_decimal_em_str(valor):
    return f'{valor:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.')

def deletar_movimentacao(id):
    try:
        with engine.begin() as conn:
            query = text('''
                DELETE FROM public.db_liquidacoes WHERE id = :id_selecionado
            ''')
            conn.execute(query, {
                "id_selecionado": int(id)
            })
            return True
    except Exception as e:
        st.error(f'Erro ao salvar no banco: {e}')
        return False

@st.dialog('Estorno de liquidacao')
def modal_estorno_liquidacao(linha_selecionada):
    st.markdown(f'### ID: {linha_selecionada["ID"]}')
    st.markdown(f'Valor: {transformar_valor_decimal_em_str(linha_selecionada["Valor liq."])}')

    st.write('')

    col_vazia, col_btn = st.columns([1, 1])

    with col_btn:
        if st.button('Confirmar estorno', width='stretch', type='primary'):
            sucesso = deletar_movimentacao(
                id=linha_selecionada['ID']
            )

            if sucesso:
                st.success('Liquidação registrada!')
                st.session_state.last_update += 1
                st.rerun()

    with col_vazia:
        if st.button('Cancelar', width='stretch'):
            st.rerun()

def main():
    if 'last_update' not in st.session_state:
        st.session_state.last_update = 0

    lista_datas_extrato, lista_empresas, lista_datas_liquidacao = carregar_filtro(engine, st.session_state.last_update)

    if 'data_liquidacao_1' not in st.session_state: st.session_state.data_liquidacao_1 = lista_datas_liquidacao[-1] if lista_datas_liquidacao else date.today()
    if 'data_liquidacao_2' not in st.session_state: st.session_state.data_liquidacao_2 = lista_datas_liquidacao[-1] if lista_datas_liquidacao else date.today()
    if 'empresa_liquidacao' not in st.session_state: st.session_state.empresa_liquidacao = 'GRUPO'
    if 'selecao_id_extrato' not in st.session_state: st.session_state.selecao_id_extrato = ''
    if 'selecao_historico' not in st.session_state: st.session_state.selecao_historico = ''
    if 'selecao_valor_banco' not in st.session_state: st.session_state.selecao_valor_banco = 0
    if 'selecao_valor_liq' not in st.session_state: st.session_state.selecao_valor_liq = 0
    if 'selecao_sistema' not in st.session_state: st.session_state.selecao_sistema = ''
    if 'selecao_banco' not in st.session_state: st.session_state.selecao_banco = ''
    if 'selecao_agencia' not in st.session_state: st.session_state.selecao_agencia = ''
    if 'selecao_dp' not in st.session_state: st.session_state.selecao_dp = ''

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

        with st.form(key='filtro_form_liquidacao'):
            selecao_data_liq_inicio = st.date_input('Data inicio:', value=st.session_state.data_liquidacao_1, format='DD/MM/YYYY')
            selecao_data_liq_fim = st.date_input('Data fim:', value=st.session_state.data_liquidacao_2, format='DD/MM/YYYY')
            selecao_empresa_liq = st.selectbox('Empresa:', lista_empresas, index=lista_empresas.index(st.session_state.empresa_liquidacao) if lista_empresas else 0)
            selecao_banco = st.text_input('Banco:', value=st.session_state.selecao_banco)
            selecao_agencia = st.text_input('Agência/conta:', value=st.session_state.selecao_agencia)
            selecao_id_extrato = st.text_input('ID do extrato:', value=st.session_state.selecao_id_extrato)
            selecao_historico = st.text_input('Histórico:', value=st.session_state.selecao_historico)
            selecao_valor_banco = st.number_input('Valor banco:', value=float(st.session_state.selecao_valor_banco))
            selecao_valor_liq = st.number_input('Valor liq.', value=float(st.session_state.selecao_valor_liq))
            selecao_sistema = st.text_input('Sistema', value=st.session_state.selecao_sistema)
            selecao_dp = st.text_input('DP', value=st.session_state.selecao_dp)

            submit_button_liq = st.form_submit_button(label='Atualizar')

            if submit_button_liq:
                st.session_state.data_liquidacao_1 = selecao_data_liq_inicio
                st.session_state.data_liquidacao_2 = selecao_data_liq_fim
                st.session_state.empresa_liquidacao = selecao_empresa_liq
                st.session_state.selecao_id_extrato = selecao_id_extrato
                st.session_state.selecao_historico = selecao_historico
                st.session_state.selecao_valor_banco = selecao_valor_banco
                st.session_state.selecao_valor_liq = selecao_valor_liq
                st.session_state.selecao_sistema = selecao_sistema
                st.session_state.selecao_banco = selecao_banco
                st.session_state.selecao_agencia = selecao_agencia
                st.session_state.selecao_dp = selecao_dp
                st.rerun()

    busca_historico = f'%{st.session_state.selecao_historico}%'
    busca_sistema = f'%{st.session_state.selecao_sistema}%'
    busca_banco = f'%{st.session_state.selecao_banco}%'
    busca_agencia = f'%{st.session_state.selecao_agencia}%'
    busca_dp = f'%{st.session_state.selecao_dp}%'

    params_liq = {'data_liq_1': st.session_state.data_liquidacao_1,
                    'data_liq_2': st.session_state.data_liquidacao_2,
                    'historico': busca_historico,
                    'valor_banco': st.session_state.selecao_valor_banco,
                    'valor_liq': st.session_state.selecao_valor_liq,
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

    if st.session_state.empresa_liquidacao != 'GRUPO':
        query_liquidacoes += ' AND "Empresa" = :empresa'
        params_liq['empresa'] = st.session_state.empresa_liquidacao

    if st.session_state.selecao_id_extrato != '':
        query_liquidacoes += ' AND "ID extrato" = :id_extrato'
        params_liq['id_extrato'] = st.session_state.selecao_id_extrato

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
