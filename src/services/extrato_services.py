import streamlit as st
from database.connection import conectar_banco
from repositories.extratos_repositories import buscar_empresas, buscar_extratos, buscar_liquidacoes_id

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