import streamlit as st
from sqlalchemy import text
from database.connection import conectar_banco
from repositories.extratos_repositories import update_tipo

@st.dialog('Manutenção de Registro')
def modal_manutencao(linha_selecionada):

    st.write('')

    lista_tipos = ['CREDITO', 'DEBITO', 'ECONTAS', 'TRANSFERENCIA', 'RESGATE', 'APLICACAO', 'RENDIMENTO']

    try:
        indice = lista_tipos.index(linha_selecionada['Tipo'])
    except:
        indice = 0

    selecao_tipo = st.selectbox('Tipo:', options=lista_tipos, index=indice)

    col_confirmar, col_cancelar = st.columns([1, 1])

    with col_confirmar:
        if st.button('Confirmar', width='stretch', type='primary'):
            sucesso = update_tipo(
                id=linha_selecionada['id'],
                tipo=selecao_tipo
            )

            with conectar_banco().begin() as conn:    
                query = text('''
                    BEGIN;
                    REFRESH MATERIALIZED VIEW mv_fluxo_aplicacao_diario;
                    REFRESH MATERIALIZED VIEW mv_fluxo_caixa_diario;
                    COMMIT;
                ''')
                conn.execute(query)     

            st.session_state['mensagem_sucesso'] = 'Alteração registrada!'
            st.rerun()

    with col_cancelar:
        if st.button('Cancelar', width='stretch'):
            st.rerun()