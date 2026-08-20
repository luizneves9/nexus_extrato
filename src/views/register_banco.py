import streamlit as st
import pandas as pd
from services.register_banco_services import obter_lista_contas_bancarias

def main():

    st.markdown('''
        <h2 style='margin-bottom: 0px;'>Contas Bancárias</h2>
        <p style='margin-top: -15px; color: #666; font-style: italic;'>
            Acompanhe as contas bancárias registradas nas empresas.
        </p>
        ''',
        unsafe_allow_html=True
    )

    # inicializando variáveis
    df = None

    # recebendo dados e visualizando
    df = obter_lista_contas_bancarias()

    if df is not None and not df.empty:
        st.dataframe(df, hide_index=True, width='content')
    else:
        st.markdown('Sem registro!')

    with st.container(horizontal=True):
        if st.button('Incluir*'):
            st.toast('Em desenvolvimento!')
        if st.button('Manutenção*'):
            st.toast('Em desenvolvimento!')
        if st.button('Excluir*'):
            st.toast('Em desenvolvimento!')

if __name__ == '__main__':
    main()
