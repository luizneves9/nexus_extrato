import streamlit as st
from datetime import date
import pandas as pd
from views.components import (registrar_filtros, detalhar_lancamentos, modal_manutencao,
                              modal_lancamento, excluir_registro, operacao_multipla)
from services.extrato_services import obter_lista_empresas, listar_extratos, listar_liquidacoes
from repositories.extratos_repositories import transformar_valor_decimal_str_em_float, transformar_valor_decimal_em_str

def inicializar_state():
    '''Inicialização do session state'''
    defaults = {
        'data_selecionada_1': date.today(),
        'data_selecionada_2': date.today(),
        'empresa_selecionada': 'GRUPO',
        'historico_selecionado': '',
        'complemento_selecionado': '',
        'banco_selecionado': '',
        'agencia_selecionado': '',
        'id_selecionado': '',
        'valor_selecionado': 0
    }
    for key, val in defaults.items():
        if not key in st.session_state:
            st.session_state[key] = val

def render_sidebar(lista_empresas):
    '''Renderizar o sidebar de filtros.'''
    with st.form(key='filtro_form_extrato'):

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

        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 1, 2, 1, 1, 1, 1, 1])
        with col1: selecao_data_inicio = st.date_input('Data inicio:', value=st.session_state.data_selecionada_1, format='DD/MM/YYYY')
        with col2: selecao_data_fim = st.date_input('Data fim:', value=st.session_state.data_selecionada_2, format='DD/MM/YYYY')
        with col3: selecao_empresa = st.selectbox('Empresa:', lista_empresas, index=lista_empresas.index(st.session_state.empresa_selecionada))
        with col4: selecao_banco = st.text_input('Banco', value=st.session_state.banco_selecionado)
        with col5: selecao_historico = st.text_input('Histórico', value=st.session_state.historico_selecionado)
        with col6: selecao_valor = st.number_input('Valor', value=float(st.session_state.valor_selecionado))
        with col7: submit_button_filtros = st.form_submit_button(label='Mais filtros', use_container_width=True)
        with col8: submit_button = st.form_submit_button(label='Atualizar', use_container_width=True)

        if submit_button:
            st.session_state.data_selecionada_1 = selecao_data_inicio
            st.session_state.data_selecionada_2 = selecao_data_fim
            st.session_state.empresa_selecionada = selecao_empresa
            st.session_state.historico_selecionado = selecao_historico
            st.session_state.banco_selecionado = selecao_banco
            st.session_state.valor_selecionado = selecao_valor
            st.rerun()

        if submit_button_filtros:
            registrar_filtros()
    
def main():

    st.markdown('''
            <h2 style='margin-bottom: 0px;'>Extrato Bancário</h2>
            <p style='margin-top: -15px; color: #666; font-style: italic;'>
                Acompanhe o detalhamento dos créditos e débitos do extrato bancário
            </p>
            ''',
            unsafe_allow_html=True
    )

    lista_empresas = obter_lista_empresas()
    inicializar_state()
    render_sidebar(lista_empresas)
    selecionados = pd.DataFrame()

    # definindo filtros para a visualização dos dados
    filtros = {
        'data_1': st.session_state.data_selecionada_1,
        'data_2': st.session_state.data_selecionada_2,
        'historico': st.session_state.historico_selecionado,
        'complemento': st.session_state.complemento_selecionado,
        'id': st.session_state.id_selecionado,
        'banco': st.session_state.banco_selecionado,
        'agencia': st.session_state.agencia_selecionado,
        'valor': st.session_state.valor_selecionado,
        'empresa': st.session_state.empresa_selecionada
    }

    # visualização dos filtros incluidos do botão "mais filtros"
    with st.container(horizontal=True):
        lista = ['agencia_selecionado', 'complemento_selecionado']
        for item in lista:
            if st.session_state[item] != '':
                st.markdown(f':violet-badge[{item.replace('_selecionado', '')}: {st.session_state[item]}]')

    df_resultado = listar_extratos(filtros)

    if not df_resultado.empty:

        colunas_valor = ['Valor', 'Valor liq.', 'Saldo']
        for col in colunas_valor:
            df_resultado[col] = df_resultado[col].map(transformar_valor_decimal_em_str)

        df_com_selecao = df_resultado.copy()
        df_com_selecao.insert(0, 'Sel', False)

        for c in df_com_selecao.columns:
            if c not in ['Sel', 'ID', 'Data']:
                df_com_selecao[c] = df_com_selecao[c].astype(str)

        tabela_editavel = st.data_editor(
            df_com_selecao,
            key='editor_extratos',
            hide_index=True,
            width='stretch',
            column_config={
                'Sel': st.column_config.CheckboxColumn('', default=False),
                'ID': st.column_config.NumberColumn('ID', format='%d'),
                'Data': st.column_config.DateColumn('Data', format='DD/MM/YYYY'),
            },
            disabled=[c for c in df_com_selecao.columns if c!= 'Sel']
        )

        selecionados = tabela_editavel[tabela_editavel['Sel'] == True]

    if not selecionados.empty:
        linha = selecionados.iloc[0].copy()
        
    with st.container(horizontal=True):

        if st.button(f'Liquidar', type='secondary'):
                
            if len(selecionados) != 1:
                st.toast('Selecione um registro.', icon='⚠️')

            else:
                if 'temp_baixas' in st.session_state: del st.session_state['temp_baixas']
                operacao_multipla(linha)

        if st.button(f'Detalhar', type='secondary'):
        
            if len(selecionados) != 1:
                st.toast('Selecione um registro.', icon='⚠️')

            else:
                listar_liquidacoes(linha)

        if st.button('Manutenção', type='secondary'):
            if len(selecionados) != 1:
                st.toast('Selecione um registro.', icon='⚠️')
            else:
                modal_manutencao(linha)

        if st.button('Lançamento', type='secondary'):
            if "input_historico" not in st.session_state:
                st.session_state.input_historico = ""
            if "input_valor" not in st.session_state:
                st.session_state.input_valor = 0.0
            if "input_empresa" not in st.session_state:
                st.session_state.input_empresa = ""
            if "input_banco" not in st.session_state:
                st.session_state.input_banco = ""
            modal_lancamento()

        if st.button('Excluir', type='secondary'):
            if len(selecionados) != 1:
                st.toast('Selecione um registro.', icon='⚠️')
            elif linha['Valor liq.'] != '0,00':
                st.toast('O registro possui liquidações e não pode ser excluido.', icon='⚠️')
            else:
                senha_excluir = 'gbs3299'
                excluir_registro(linha, senha_excluir)

    if 'mensagem_sucesso' in st.session_state:
        st.toast(st.session_state.pop('mensagem_sucesso'), icon='✅')

    if 'mensagem_erro' in st.session_state:
        st.toast(st.session_state.pop('mensagem_sucesso'), icon='❌')

if __name__ == '__main__':
    main()