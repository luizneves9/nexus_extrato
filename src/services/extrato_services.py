import streamlit as st
from sqlalchemy import text
from database.connection import conectar_banco
from repositories.extratos_repositories import buscar_empresas, buscar_extratos, buscar_liquidacoes_id, registrar_exclusao_extrato, executar_refresh_view
from queries.extrato_queries import QUERY_DELETE_EXTRATO, REFRESH_VIEWS

engine = conectar_banco()

@st.cache_data
def obter_lista_empresas():
    '''Serviço com cache para listagem de empresas.'''
    return buscar_empresas()

def listar_extratos(filtros):
    '''Busca e prepara a tabela para exibição.'''
    return buscar_extratos(filtros)

def listar_liquidacoes_id(filtros):
    '''Busca e prepara a tabela para exibição.'''
    return buscar_liquidacoes_id(filtros)

def excluir_extrato(id):
    '''Excluir registro bancário do banco de dados.'''
    query = text(QUERY_DELETE_EXTRATO)
    with engine.begin() as conn:
        try:
            sucesso = registrar_exclusao_extrato(query, id, conn)
            if sucesso.rowcount > 0:
                return True
            else:
                return False
        except:
            return False

def refresh_views():
    query = text(REFRESH_VIEWS)
    executar_refresh_view(query)
