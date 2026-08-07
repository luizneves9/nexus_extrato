import streamlit as st
from sqlalchemy import text
from database.connection import conectar_banco
from services.extrato_services import excluir_extrato, refresh_views

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

    col9, col10, col11 = st.columns([3, 1.5, 1.5], vertical_alignment='bottom')

    with col9: 
        senha_digitada = st.text_input('Senha:', type='password')

    with col10:
        if st.button('Confirmar', type='primary'):
            
            if senha_digitada == senha:

                sucesso = excluir_extrato(linha['id'])

                if sucesso:
                    refresh_views()  
                    st.session_state['mensagem_sucesso'] = f'Registro excluído com sucesso!'
                    st.rerun()

                else:
                    st.session_state['mensagem_erro'] = f'Erro ao excluir registro!'
                    st.rerun()
            
            else:
                st.toast('Senha inválida!', icon='❌')

    with col11: 
        if st.button('Cancelar'): st.rerun()