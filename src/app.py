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

    st.html("""
        <style>
            /* Estiliza os títulos das seções da navegação */
            [data-testid="stSidebarNavItems"] > div:first-child,
            [data-testid="stSidebarNavSeparator"] + div {
                font-weight: bold !important;
                font-size: 1.05rem !important;
                color: #1F2937 !important; /* Ajuste a cor desejada */
            }
        </style>
    """)


    pages = {
        'Conta Corrente': [
            st.Page('views/app_extrato.py', title='⠀⠀⠀Extrato Bancário'),
            st.Page('views/app_liquidacoes.py', title='⠀⠀⠀Liquidações')
        ],
        'Resumo Bancário': [
            st.Page('views/3_resumo_bancario.py', title='⠀⠀⠀Diário')
        ],
        'Personalizado': [
            st.Page('views/4_resumo_bancario_santo_anjo.py', title='⠀⠀⠀Extrato - Santo Anjo')
        ],
        'Cadastros': [
            st.Page('views/register_empresa.py', title='⠀⠀⠀Empresas*'),
            st.Page('views/register_banco.py', title='⠀⠀⠀Contas bancárias'),
            st.Page('views/register_regras.py', title='⠀⠀⠀Regras de extrato*'),
        ]
    }

    pg = st.navigation(pages)
    pg.run()

if __name__ == "__main__":
    main()