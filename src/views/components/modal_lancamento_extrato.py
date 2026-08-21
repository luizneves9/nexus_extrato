import streamlit as st
from sqlalchemy import text
from database.connection import conectar_banco
from services.extrato_services import listar_contas_bancarias

engine = conectar_banco()

@st.dialog('Lançamento Manual')
def modal_lancamento():

    st.markdown('*Os lançamentos serão apontados como "Manual" na coluna "Complemento".*')
    st.write('')

    df_contas = listar_contas_bancarias()
    lista_contas = [''] + df_contas['agencia_conta'].to_list()

    col2, col3 = st.columns([2.5, 1.2])
    with col2: input_agencia = st.selectbox('Ag./Cc:', lista_contas)
    with col3: input_data = st.date_input('Data:', format='DD/MM/YYYY')

    if input_agencia != '':
        filtro_empresa = df_contas.loc[df_contas['agencia_conta'] == input_agencia, 'nome_empresa']
        filtro_banco = df_contas.loc[df_contas['agencia_conta'] == input_agencia, 'banco']

        st.session_state.input_empresa = filtro_empresa.iloc[0] if not filtro_empresa.empty else ''
        st.session_state.input_banco = filtro_banco.iloc[0] if not filtro_banco.empty else ''

    col1, col4, col5 = st.columns([1, 3, 3])
    with col1: input_banco = st.text_input('Banco', value=st.session_state.input_banco, disabled=True)
    with col4: input_empresa = st.text_input('Empresa:', value=st.session_state.input_empresa, disabled=True)
    with col5: input_historico = st.text_input('Histórico:', value=st.session_state.input_historico, key='input_historico')

    col6, col7, col8 = st.columns([1, 2, 2])
    with col6: input_complemento = st.text_input('Comp.', value='Manual', disabled=True)
    with col7: input_tipo = st.selectbox('Tipo:', ['CREDITO', 'DEBITO', 'ECONTAS', 'TRANSFERENCIA', 'RESGATE', 'APLICACAO', 'RENDIMENTO'])
    with col8: input_valor = st.number_input('Valor', key='input_valor')

    st.write('')

    with st.container(horizontal=True):

        if st.button('Confirmar', type='primary'):
            if input_empresa == '' or input_valor == 0 or input_historico.strip() == '': #type: ignore
                st.toast('Aviso: Preencha todos os campos!', icon='⚠️')
            else:
                sucesso = False

                try:
                    with engine.begin() as conn:
                        query = text('''
                            INSERT INTO db_extratos (banco, agencia_conta, data_contabil, codigo_categoria, descricao_categoria, cod_hist, descricao_historico, documento, complemento, natureza, tipo, valor, status, nome_empresa)
                            VALUES
                                (:banco, :agencia_conta, :data, 0, '', '', :historico, '0', 'Lcto Manual', 'DPV', :tipo_lcto, :valor, 'NC', :empresa)
                        ''')
                        conn.execute(query, {
                            'banco': input_banco,
                            'agencia_conta': input_agencia,
                            'data': input_data,
                            'historico': input_historico,
                            'tipo_lcto': input_tipo,
                            'valor': input_valor,
                            'empresa': input_empresa
                        })
                        sucesso = True

                except ValueError:
                    st.toast('Erro ao salvar o lançamento!', icon='❌')

                if sucesso:

                    with engine.begin() as conn:    
                        query = text('''
                            BEGIN;
                                REFRESH MATERIALIZED VIEW mv_fluxo_aplicacao_diario;
                                REFRESH MATERIALIZED VIEW mv_fluxo_caixa_diario;
                                COMMIT;
                        ''')
                        conn.execute(query)   

                    st.session_state['mensagem_sucesso'] = 'Lançamento realizado com sucesso!'
                    st.rerun()
                    
        if st.button('Cancelar'):
            st.rerun()
