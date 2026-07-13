from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()

def verificar_acesso_ip():
    """
    Valida se o IP de quem está acessando o servidor está na lista
    de IPs permitidos.
    """

    # importando as variáveis de ambiente para verificar IPS permitidos
    ips_configurados = os.getenv("IPS_PERMITIDOS", "")
    
    # validando se há registro de IP nas variáveis
    if not ips_configurados:
        st.error("Nenhuma rede homologada configurada em 'IPS_PERMITIDOS'.")
        return False
        
    # transformando os IPS em lista
    lista_ips_autorizados = [ip.strip() for ip in ips_configurados.split(",")]

    # capturando o IP conectado
    headers = st.context.headers
    ip_usuario = headers.get("x-forwarded-for")

    # verificando se é uma conexão local : desenvolvedor
    if not ip_usuario or ip_usuario in ['127.0.0.1', 'localhost']:
        return True
    
    # separando, caso haja mais de um registro na captura
    if "," in ip_usuario:
        ip_usuario = ip_usuario.split(",")[0].strip()

    return ip_usuario in lista_ips_autorizados
