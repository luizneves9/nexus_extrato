import streamlit as st
from database.connection import conectar_banco
from repositories.liquidacoes_repositories import buscar_empresas, executar_estorno, buscar_liquidacoes

engine = conectar_banco()

@st.cache_data
def obter_lista_empresas():
    '''Serviço com cache para listagem de empresas.'''
    return buscar_empresas()

def processar_estorno(id):
    '''
    Regra de negócio para estornar liquidação.
    Retorna uma tupla: (Sucesso: boll, Mensagem: str)
    '''
    try:
        executar_estorno(id)
        return True, 'Estorno realizado com sucesso!'
    except Exception as e:
        return False, 'Erro ao salvar no banco: {e}'

def listar_liquidacoes(filtros):
    '''Busca e prepara a tabela para exibição.'''
    return buscar_liquidacoes(filtros)
