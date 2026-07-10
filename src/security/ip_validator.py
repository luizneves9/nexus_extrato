from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()

def verificar_acesso_ip():
    """
    Valida se o IP de quem está acessando o servidor está na lista
    de IPs permitidos.
    """
    ips_configurados = os.getenv("IPS_PERMITIDOS", "")
    
    if not ips_configurados:
        st.error("Nenhuma rede homologada configurada em 'IPS_PERMITIDOS'.")
        return False
        
    lista_ips_autorizados = [ip.strip() for ip in ips_configurados.split(",")]
    headers = st.context.headers
    ip_usuario = headers.get("x-forwarded-for")

    if not ip_usuario or ip_usuario in ['127.0.0.1', 'localhost']:
        return True

    return ip_usuario in lista_ips_autorizados
