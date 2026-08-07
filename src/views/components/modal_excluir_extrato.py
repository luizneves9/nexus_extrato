import streamlit as st
from sqlalchemy import text
from database.connection import conectar_banco

engine = conectar_banco()

@st.dialog('Excluir Registro')
def excluir_registro(linha, senha):

    st.markdown('*Atenção: A exclusão deste registro não poderá ser revertida!*')

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1: st.text_input('Id:', value=linha['id'], disabled=True)
    with col2: st.text_input('Empresa:', value=linha['Empresa'], disabled=True)
    with col3: st.text_input('Data', value=linha['Data'], disabled=True)

    col4, col5, col6 = st.columns([1, 3, 3])
    with col4: st.text_input('Banco', value=linha['Banco'], disabled=True)
    with col5: st.text_input('Conta', value=linha['Agência/Conta'], disabled=True)
    with col6: st.text_input('Histórico', value=linha['Desc. do Hist.'], disabled=True)

    col7, col8 = st.columns([1, 1])
    with col7: st.text_input('Tipo', value=linha['Tipo'], disabled=True)
    with col8: st.text_input('Valor', value=linha['Valor'], disabled=True)

    if linha['Valor liq.'] != '0,00':
        st.divider()
        st.error('Erro: O registro possui valor liquidado!')

    else:
        col1, col2, col3 = st.columns([3, 1.5, 1.5], vertical_alignment='bottom')

        with col1: 
            senha_digitada = st.text_input('Senha:', type='password')

        with col2:
            if st.button('Confirmar'):
                
                if senha_digitada == senha:
                    sucesso = False

                    with engine.begin() as conn:
                        try:
                            query = text('DELETE FROM public.db_extratos WHERE id = :id_linha')
                            result = conn.execute(query, {'id_linha': int(linha['id'])})

                            if result.rowcount > 0:
                                sucesso = True
                            else:
                                st.toast('Sistema: Nenhum registro encontrado com esse ID.', icon='⚠️')

                        except Exception as e:
                            st.toast(f'Sistema: Erro ao deletar registro -> {e}', icon='❌')

                    if sucesso:
                        with engine.begin() as conn:    
                            query = text('''
                                BEGIN;
                                REFRESH MATERIALIZED VIEW mv_fluxo_aplicacao_diario;
                                REFRESH MATERIALIZED VIEW mv_fluxo_caixa_diario;
                                COMMIT;
                            ''')
                            conn.execute(query)   
                        st.session_state['mensagem_sucesso'] = f'Registro excluído com sucesso! ID: {linha['id']}'
                        st.rerun()
               
                else:
                    st.toast('Senha inválida!', icon='❌')

        with col3: 
            if st.button('Cancelar'): st.rerun()