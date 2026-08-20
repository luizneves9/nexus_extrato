import streamlit as st
from sqlalchemy import text
from database.connection import conectar_banco
from services.extrato_services import manutencao_extrato

@st.dialog('Manutenção de Registro')
def modal_manutencao(linha_selecionada):

    st.write('')

    # definindo a lista dos tipos permitidos
    lista_tipos = ['CREDITO', 'DEBITO', 'ECONTAS', 'TRANSFERENCIA', 'RESGATE', 'APLICACAO', 'RENDIMENTO']

    try:
        indice = lista_tipos.index(linha_selecionada['Tipo'])
    except:
        indice = 0

    # caixa de interação para definição do tipo
    selecao_tipo = st.selectbox('Tipo:', options=lista_tipos, index=indice)

    col_confirmar, col_cancelar = st.columns([1, 1])

    with col_confirmar:
        if st.button('Confirmar', width='stretch', type='primary'):
            try:
                msg = manutencao_extrato(
                    id=linha_selecionada['id'],
                    tipo_selecionado=selecao_tipo
                )
                st.session_state['mensagem_sucesso'] = msg
                st.rerun()

            except Exception as e:
                st.session_state['mensagem_erro'] = f'Erro ao salvar o registro!'
                st.rerun()

    with col_cancelar:
        if st.button('Cancelar', width='stretch'):
            st.rerun()