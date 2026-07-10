import os
import pandas as pd
import hashlib
from sql import conectar_banco
import streamlit as st
from sqlalchemy import text
from datetime import date
import warnings
import uuid
from dotenv import load_dotenv
from security.ip_validator import verificar_acesso_ip

# =========================================================================
# VALIDAÇÃO DE ACESSO - IP
# =========================================================================

if not verificar_acesso_ip():
    st.error("**Acesso Não Autorizado**")
    st.stop()

# =========================================================================
# DESENVOLVIMENTO
# =========================================================================

## configurações iniciais

# configuração para visualização no terminal
pd.set_option('display.max_columns', None)
warnings.filterwarnings('ignore', category=DeprecationWarning)

# conectando engine
engine = conectar_banco()

# streamlit pagina
st.set_page_config(
    page_title='NEXUS',
    layout='wide',
    initial_sidebar_state='expanded'
    )

def main():

    pages = {
        'Menu:': [
            st.Page('pages/extrato_bancario.py', title='Extrato Bancário'),
            st.Page('pages/extrato_liquidacoes.py', title='Liquidações')
        ]
    }

    pg = st.navigation(pages)
    pg.run()

if __name__ == "__main__":
    main()