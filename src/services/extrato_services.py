import uuid
import streamlit as st
import pandas as pd
from sqlalchemy import text
from database.connection import conectar_banco
from repositories.extratos_repositories import buscar_empresas, buscar_extratos, buscar_liquidacoes_id, registrar_exclusao_extrato, executar_refresh_view, salvar_liquidacao, transformar_valor_decimal_em_str, transformar_valor_decimal_str_em_float
from queries.extrato_queries import QUERY_DELETE_EXTRATO, REFRESH_VIEWS, INSERIR_REGISTRO
from views.components.modal_detalhamento_extrato import detalhar_lancamentos

engine = conectar_banco()

@st.cache_data
def obter_lista_empresas():
    '''Serviço com cache para listagem de empresas.'''
    return buscar_empresas()

def listar_extratos(filtros):
    '''Busca e prepara a tabela para exibição.'''
    return buscar_extratos(filtros)

def listar_liquidacoes(linha):
    '''Buscar liquidações realizadas em um registro do extrato.'''

    # montagem do filtro
    filtro = {'id_selecionado_extrato': str(linha['id'])}

    # buscando registros no banco de dados
    df_liquidacoes = buscar_liquidacoes_id(filtro)

    # regra de negócio
    if df_liquidacoes.empty:
        return st.toast('Sem registros!', icon='⚠️')
    
    else:

        # montagem do dataframe da linha selecionada
        registro_extrato = [{
            'Empresa': linha['Empresa'],
            'Data': linha['Data'],
            'Banco': linha['Banco'],
            'Agência/Conta': linha['Agência/Conta'],
            'Desc. do Hist.': linha['Desc. do Hist.'],
            'Valor': linha['Valor'],
            'Valor liq.': linha['Valor liq.'],
            'Saldo': linha['Saldo']
            }]

        df_extrato = pd.DataFrame(registro_extrato)

        # transformando as colunas de valor em formato brasileiro
        colunas_valor = ['Valor', 'Valor liq.', 'Saldo']
        for col in colunas_valor:
            df_extrato[col] = df_extrato[col].map(transformar_valor_decimal_em_str)

        df_liquidacoes['Valor liq.'] = df_liquidacoes['Valor liq.'].map(transformar_valor_decimal_em_str)

        # transformando as colunas de data
        df_extrato['Data'] = pd.to_datetime(df_extrato['Data'], errors='coerce')
        df_extrato['Data'] = df_extrato['Data'].dt.strftime('%d/%m/%Y')    

        colunas_data = ['Data liq.', 'Data log']
        for col in colunas_data:
            df_liquidacoes[col] = pd.to_datetime(df_liquidacoes[col], errors='coerce')
            df_liquidacoes[col] = df_liquidacoes[col].dt.strftime('%d/%m/%Y')

        detalhar_lancamentos(df_extrato, df_liquidacoes)

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

def processar_liquidacao(registro_extrato, liquidacao_em_lote=False, lista_lote=None,
                         val_input=None, sistema_input=None, dp_input=None, parc_input=None,
                         date_input=None):
    '''
    Organiza o sistem de liquidação:
    1. Validações de regra de negócio.
    2. Inserir o registro via repository.
    '''

    # arredondando os valores decimais
    saldo_disponivel = round(float(transformar_valor_decimal_str_em_float(registro_extrato['Saldo'])), 2)

    # caso o registro de liquidação não seja em lote
    if liquidacao_em_lote == False:

        if saldo_disponivel >= 0 and val_input <= 0:
            raise ValueError('O valor deve ser maior que zero.')

        elif saldo_disponivel < 0 and val_input >= 0:
            raise ValueError('O valor deve ser menor que zero.')

        elif saldo_disponivel >= 0 and val_input > saldo_disponivel:
            raise ValueError(f'Operação negada! O valor digitado ({transformar_valor_decimal_em_str(val_input)}) é maior que o saldo disponível ({transformar_valor_decimal_em_str(saldo_disponivel)}).')

        elif saldo_disponivel < 0 and val_input < saldo_disponivel:
            raise ValueError(f'Operação negada! O valor digitado ({transformar_valor_decimal_em_str(val_input)}) é menor que o saldo disponível ({transformar_valor_decimal_em_str(saldo_disponivel)}).')

        elif (sistema_input == 'Corporativo' and (dp_input.strip() == '' or parc_input.strip() == '')):
            raise ValueError('Operação negada! Favor preencher a DP e Parcela.')
        
        elif (sistema_input == 'SSW' and dp_input.strip() == ''):
            raise ValueError('Operação negada! Favor preencher a DP.')
        
        elif (sistema_input == 'Delsoft' and dp_input.strip() == ''):
            raise ValueError('Operação negada! Favor preencher a DP/Histórico.')
        
        elif (sistema_input == 'Diversos' and dp_input.strip() == ''):
            raise ValueError('Operação negada! Favor preencher a DP/Histórico.')

        else:
            try:
                salvar_liquidacao(
                    id_extrato=registro_extrato['id'],
                    valor=val_input,
                    data_baixa=date_input,
                    sistema=sistema_input,
                    duplicata=dp_input,
                    parcela=parc_input
                )
            except:
                raise ValueError('Erro ao registrar liquidação')

    # caso o registro de liquidação seja em lote
    else:

        baixa_acumulada = round(sum(item['Valor'] for item in lista_lote), 2)

        if saldo_disponivel >= 0 and baixa_acumulada > saldo_disponivel:
            raise ValueError(f'Operação negada! O valor acumulado ({transformar_valor_decimal_em_str(baixa_acumulada)}) é maior que o saldo disponível ({saldo_disponivel}).')
            
        elif saldo_disponivel < 0 and baixa_acumulada < saldo_disponivel:
            raise ValueError(f'Operação negada! O valor acumulado ({transformar_valor_decimal_em_str(baixa_acumulada)}) é maior que o saldo disponível ({transformar_valor_decimal_em_str(saldo_disponivel)}).')

        else:
            for item in lista_lote:
                try:
                    salvar_liquidacao(
                        id_extrato=registro_extrato['id'],
                        valor=item['Valor'],
                        data_baixa=item['Data liq.'],
                        sistema=item['Sistema'],
                        duplicata=item['DP'],
                        parcela=item['Parc.']
                    )
                except:
                    raise ValueError('Erro ao registrar liquidação')

def validar_e_criar_item_baixa(sistema, data_liq, valor, dp, parc, saldo_referencia):
    """
    Aplica as regras de negócio para validar se um item pode ser adicionado.
    Lança ValueError se os dados forem inválidos.
    """

    # validação de campos obrigatórios
    duplicata = dp.strip()
    parcela = parc.strip()

    if not duplicata:
        raise ValueError(f'O campo de DP é obrigatório para o sistema {sistema}')

    if sistema == 'Corporativo' and not parcela:
        raise ValueError(f'O campo de Parcela é obrigatório para o sistema Corporativo.') 

    if saldo_referencia >= 0 and valor <= 0:
        raise ValueError('Para saldos positivos, o valor digitado deve ser maior que zero.')

    if saldo_referencia < 0 and valor >= 0:
        raise ValueError('Para saldos negativos, o valor digitado deve ser menor que zero.')

    return {
        '_id': str(uuid.uuid4()),
        'Sistema': sistema,
        'Data liq.': data_liq,
        'Valor': valor,
        'DP': duplicata,
        'Parc.': parcela
    }
