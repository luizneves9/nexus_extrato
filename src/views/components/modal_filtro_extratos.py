import streamlit as st

@st.dialog('Filtros do Extrato')
def registrar_filtros():
    with st.form(key='filtro_form_extrato_3'):

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

        col1, col2, col3 = st.columns([1, 1, 1])
        col4, col5 = st.columns([1, 1])

        with col1: selecao_agencia = st.text_input('Agencia/conta:', value=st.session_state.agencia_selecionado)
        with col2: selecao_complemento = st.text_input('Complemento:', value=st.session_state.complemento_selecionado)
        with col3: selecao_id = st.text_input('ID', value=st.session_state.id_selecionado)

        with col4: submit_button_refresh = st.form_submit_button(label='Confirmar', use_container_width=True, type='primary')
        with col5: submit_button_cancel = st.form_submit_button(label='Cancelar', use_container_width=True)

        if submit_button_refresh:
            st.session_state.complemento_selecionado = selecao_complemento
            st.session_state.agencia_selecionado = selecao_agencia
            st.session_state.id_selecionado = selecao_id
            st.rerun()

        if submit_button_cancel:
            st.rerun()
