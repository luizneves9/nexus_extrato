from sql import conectar_banco
import streamlit as st
import warnings
from security.ip_validator import verificar_acesso_ip

# =========================================================================
# CONFIGURAÇÃO INICIAL
# =========================================================================

st.set_page_config(
    page_title='NEXUS',
    layout='wide',
    initial_sidebar_state='expanded'
    )

# =========================================================================
# VALIDAÇÃO DE ACESSO - IP
# =========================================================================

if not verificar_acesso_ip():
    st.error("**Acesso Não Autorizado**")
    st.stop()

# =========================================================================
# DESENVOLVIMENTO
# =========================================================================

# configuração para visualização no terminal
warnings.filterwarnings('ignore', category=DeprecationWarning)

# conectando engine
engine = conectar_banco()

def main():

    pagina_extrato = st.Page('view/extrato_bancario.py', title='Extrato Bancário', default=True)
    pagina_liquidacoes = st.Page('view/extrato_liquidacoes.py', title='Liquidações')

    pages = {
        'Menu:': [
            pagina_extrato,
            pagina_liquidacoes
        ]
    }

    pg = st.navigation(pages)
    pg.run()

if __name__ == "__main__":
    main()