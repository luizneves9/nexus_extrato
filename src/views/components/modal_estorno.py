import streamlit as st
import pandas as pd
from services.liquidacoes_services import processar_estorno

@st.dialog('Estorno de liquidacao')
def render_modal_estorno(linha_selecionada):
    '''
    Descrição: Função desenvolvida para estornar um registro que foi liquidado anteriormente por um usuário.
    
    Parâmetros:
    linha_selecionada: Todos os dados da linha selecionada pelo usuário.

    Resultado:
    O registro informado, após confirmado, é excluido da tabela de liquidações no banco de dados.
    '''

    # apresentação visual dos dados
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

    # botão de confirmação
    with col01:

        # tentativa de exclusão do registro
        if st.button('Confirmar', width='stretch', type='primary'):
            sucesso, mensagem = processar_estorno(id=linha_selecionada['ID'])
            if sucesso:
                st.session_state['mensagem_sucesso'] = mensagem
                st.rerun()
            else:
                st.toast(mensagem, icon='❌')

    # botão de cancelamento da operação
    with col02:
        if st.button('Cancelar', width='stretch'):
            st.rerun()
