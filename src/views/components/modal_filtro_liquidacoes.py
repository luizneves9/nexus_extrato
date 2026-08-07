import streamlit as st

@st.dialog('Filtros')
def registrar_filtros():
    with st.form(key='filtro_form_liquidacao_2'):

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

        col1, col2 = st.columns([1, 1])
        col3, col4 = st.columns([1, 1])
        col5, col6 = st.columns([1, 1])

        with col1: input_banco = st.text_input('Banco:', value=st.session_state.input_banco)
        with col2: input_agencia = st.text_input('Agência/conta:', value=st.session_state.input_agencia)
        with col3: input_sistema = st.text_input('Sistema', value=st.session_state.input_sistema)
        with col4: input_dp = st.text_input('DP', value=st.session_state.input_dp)

        with col5: submit_button_refresh = st.form_submit_button(label='Confirmar', use_container_width=True, type='primary')
        with col6: submit_button_cancel = st.form_submit_button(label='Cancelar', use_container_width=True)

        if submit_button_refresh:
            st.session_state.input_sistema = input_sistema
            st.session_state.input_banco = input_banco
            st.session_state.input_agencia = input_agencia
            st.session_state.input_dp = input_dp
            st.rerun()

        if submit_button_cancel:
            st.rerun()
