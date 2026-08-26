import uuid
import streamlit as st
import pandas as pd
from sqlalchemy import text
from database.connection import conectar_banco
from repositories.extratos_repositories import buscar_empresas, buscar_extratos, buscar_liquidacoes_id, registrar_exclusao_extrato, executar_refresh_view, salvar_liquidacao, transformar_valor_decimal_em_str, transformar_valor_decimal_str_em_float, update_tipo, buscar_contas_bancarias, salvar_divisao, salvar_liquidacao_divisao
from queries.extrato_queries import QUERY_DELETE_EXTRATO, REFRESH_VIEWS, MANUTENCAO_REGISTRO_BANCARIO, CONTAS_BANCARIAS, INSERIR_DIVISAO, INSERIR_LIQUIDACAO_DIVISAO
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

def manutencao_extrato(id, tipo_selecionado):
    '''Realiza um ajuste no registro bancário'''

    # query de atualização bancária
    query = text(MANUTENCAO_REGISTRO_BANCARIO)

    # montagem de filtros
    filtros = {
        'id_selecionado': int(id),
        'tipo_novo': str(tipo_selecionado) 
    }

    # salvando no banco de dados
    try:
        with engine.begin() as conn:
            update_tipo(query, filtros, conn)
    except:
        raise ValueError('Erro ao salvar registro.')

    # atualizando resumos bancários
    query = text(REFRESH_VIEWS)
    executar_refresh_view(query)
    return 'Registro atualizado com sucesso!'

def listar_contas_bancarias():
    '''Listagem das contas bancárias cadastradas na empresa.'''

    query = CONTAS_BANCARIAS
    try:
        with engine.begin() as conn:
            df = buscar_contas_bancarias(query, conn)
            if df is not None and not df.empty:
                return df
            else:
                return pd.DataFrame()
    except:
        raise ValueError('Erro ao processar dados.')

def validar_e_criar_item_divisao(tipo_divisao, valor_divisao, linha_selecionada):
    """
    Aplica as regras de negócio para validar se um item pode ser adicionado.
    Lança ValueError se os dados forem inválidos.
    """

    # validação
    if transformar_valor_decimal_str_em_float(linha_selecionada['Valor liq.']) != 0:
        raise ValueError('O registro possui valor liquidado.')

    if linha_selecionada['Tipo'] == 'SUBSTITUIDO':
        raise ValueError('O registro já foi substituido.')

    if valor_divisao <= 0:
        raise ValueError('O valor informado deve ser maior que zero.')

    return {
        '_id': str(uuid.uuid4()),
        'Tipo': tipo_divisao,
        'Valor': valor_divisao
    }

def registrar_divisao(valor_original, soma_tabela, linha_selecionada, tabela_divisao):
    '''
    Registra uma divisão de valores.
    '''

    # validações
    if len(tabela_divisao) == 1:
        raise ValueError('A quantidade de registros deve ser maior que um.')

    if abs(valor_original) != abs(soma_tabela):
        raise ValueError('Valor total da divisão está diferente do valor original.')

    # montando a query
    query = INSERIR_DIVISAO

    for c in tabela_divisao:
        query += f" ,(:banco, :agencia, :data, :historico, '{c['Tipo']}', {-c['Valor'] if transformar_valor_decimal_str_em_float(linha_selecionada['Valor']) < 0 else c['Valor']}, :empresa)"

    # incluindo return
    query += ' RETURNING id'

    # formatando query
    query_final = text(query)

    parametro = {
        'banco': linha_selecionada['Banco'],
        'agencia': linha_selecionada['Agência/Conta'],
        'data': linha_selecionada['Data'],
        'historico': linha_selecionada['Desc. do Hist.'],
        'valor': transformar_valor_decimal_str_em_float(linha_selecionada['Valor']),
        'empresa': linha_selecionada['Empresa']
    }

    try:
        with engine.begin() as conn:

            # salvando registros de divisão
            lista_ids_novos = salvar_divisao(query_final, parametro, conn)

            lista_ids = []
            lista_ids.append(linha_selecionada['id'])
            for id in lista_ids_novos:
                lista_ids.append(id)

            # registrando liquidação
            query_liquidacao = text(INSERIR_LIQUIDACAO_DIVISAO)
            parametro_liquidacao = {
                'id_extrato_1': linha_selecionada['id'],
                'id_extrato_2': lista_ids_novos[0],
                'valor_1': transformar_valor_decimal_str_em_float(linha_selecionada['Valor']),
                'valor_2': transformar_valor_decimal_str_em_float(linha_selecionada['Valor']),
                'data': linha_selecionada['Data'],
                'lista_ids': list(lista_ids)
            }
            salvar_liquidacao_divisao(query_liquidacao, parametro_liquidacao, conn)

            # atualizando registro anterior
            manutencao_extrato(linha_selecionada['id'], 'SUBSTITUIDO')

            # refresh de views
            query_refresh = text(REFRESH_VIEWS)
            executar_refresh_view(query_refresh)

        return lista_ids_novos
    
    except Exception as e:
        raise ValueError(f'Erro ao processar dados. ({e})')

