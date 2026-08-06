import streamlit as st
from datetime import date
from services.liquidacoes_services import obter_lista_empresas, listar_liquidacoes
from views.components.modal_estorno import render_modal_estorno
from views.components.modal_filtro_liquidacoes import registrar_filtros

def inicializar_state():
    '''Inicialização do session_state.'''
    defaults = {
        'input_data_1': date.today(),
        'input_data_2': date.today(),
        'input_empresa': 'GRUPO',
        'input_id_extrato': '',
        'input_historico': '',
        'input_valor_banco': 0,
        'input_valor_liq': 0,
        'input_sistema': '',
        'input_banco': '',
        'input_agencia': '',
        'input_dp': ''
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

def render_sidebar(lista_empresas):
    '''Renderiza a barra lateral de filtros.'''

    # identificando o index da empresa na lista
    try:
        idx_empresa = lista_empresas.index(st.session_state.input_empresa)
    except (ValueError, KeyError, AttributeError):
        idx_empresa = 0

    # formulario de filtros
    with st.form(key='filtro_form_liquidacao'):

        st.markdown(
            """
            <style>
            /* Remove a borda cinza e o padding interno do st.form */
            div[data-testid="stForm"] {
                border: none !important;
                padding: 0px !important;
            }
            
            /* Corrige a margem do botão de submit para alinhar perfeitamente aos campos */
            div[data-testid="stFormSubmitButton"] {
                margin-top: 28px;
            }
            </style>
        """,
            unsafe_allow_html=True,
        )

        col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([1, 1, 1, 1, 1, 1, 1, 1, 1])
        with col1: input_data_1 = st.date_input('Data inicio:', value=st.session_state.input_data_1, format='DD/MM/YYYY')
        with col2: input_data_2 = st.date_input('Data fim:', value=st.session_state.input_data_2, format='DD/MM/YYYY')
        with col3: input_empresa = st.selectbox('Empresa:', lista_empresas, index=idx_empresa)
        with col4: input_id_extrato = st.text_input('ID do extrato:', value=st.session_state.input_id_extrato)
        with col5: input_historico = st.text_input('Histórico:', value=st.session_state.input_historico)
        with col6: input_valor_banco = st.number_input('Valor banco:', value=float(st.session_state.input_valor_banco))
        with col7: input_valor_liq = st.number_input('Valor liq.', value=float(st.session_state.input_valor_liq))
        with col8:
            submit_button_filtro = st.form_submit_button(label='Mais filtros', use_container_width=True)
        with col9:
            submit_button_liq = st.form_submit_button(label='Atualizar', use_container_width=True)

        if submit_button_liq:
            st.session_state.input_data_1 = input_data_1
            st.session_state.input_data_2 = input_data_2
            st.session_state.input_empresa = input_empresa
            st.session_state.input_id_extrato = input_id_extrato
            st.session_state.input_historico = input_historico
            st.session_state.input_valor_banco = input_valor_banco
            st.session_state.input_valor_liq = input_valor_liq
            st.rerun()

    if submit_button_filtro:
        registrar_filtros()

def main():

    st.markdown('''
        <h2 style='margin-bottom: 0px;'>Registros de Liquidações</h2>
        <p style='margin-top: -15px; color: #666; font-style: italic;'>
            Acompanhe o detalhamento das liquidações realizadas no extrato bancário
        </p>
        ''',
        unsafe_allow_html=True)

    inicializar_state()
    lista_empresas = obter_lista_empresas()
    render_sidebar(lista_empresas)

    filtros = {
        'data_1': st.session_state.input_data_1,
        'data_2': st.session_state.input_data_2,
        'empresa': st.session_state.input_empresa,
        'banco': st.session_state.input_banco,
        'agencia': st.session_state.input_agencia,
        'id_extrato': st.session_state.input_id_extrato,
        'historico': st.session_state.input_historico,
        'valor_banco': st.session_state.input_valor_banco,
        'valor_liq': st.session_state.input_valor_liq,
        'sistema': st.session_state.input_sistema,
        'dp': st.session_state.input_dp
    }

    lista = ['input_sistema', 'input_banco', 'input_agencia', 'input_dp']

    with st.container(horizontal=True):
        for item in lista:
            if st.session_state[item] != '':
                st.markdown(f':violet-badge[{item.replace('input_', '')}: {st.session_state[item]}]')
    
    df_liquidacoes = listar_liquidacoes(filtros)

    if not df_liquidacoes.empty:

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

        if st.button(f'Estornar', type='secondary'):

            # capturando registros selecionados
            selecionados = tabela_editavel[tabela_editavel['Sel'] == True]

            # validando o registro para sequenciar o estorno
            if not selecionados.empty and len(selecionados) == 1:
                render_modal_estorno(selecionados.iloc[0])
            else:
                st.toast('Selecione um registro para estornar.', icon='⚠️')

        if 'mensagem_sucesso' in st.session_state:
            st.toast(st.session_state.pop('mensagem_sucesso'), icon='✅')

if __name__ == '__main__':
    main()
