from database.connection import conectar_banco
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

    pagina_extrato_bancario = st.Page('views/app_extrato.py', title='Extrato Bancário')
    pagina_liquidacoes = st.Page('views/app_liquidacoes.py', title='Liquidações')    
    pagina_resumo = st.Page('views/3_resumo_bancario.py', title='Diário')
    pagina_santo_anjo = st.Page('views/4_resumo_bancario_santo_anjo.py', title='Extrato - Santo Anjo')

    pages = {
        'Conta Corrente:': [
            pagina_extrato_bancario,
            pagina_liquidacoes
        ],
        'Resumo Bancário': [
            pagina_resumo
        ],
        'Personalizado:': [
            pagina_santo_anjo
        ]
    }

    pg = st.navigation(pages)
    pg.run()

if __name__ == "__main__":
    main()