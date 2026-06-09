import os
import pandas as pd
import numpy as np
import hashlib
from config import CAMINHO_EXTRATO_BANCARIO_NOVO, RENOMEAR_EXTRATO
from loader.sql_tools import upsert_extrato
from sql import conectar_banco
from extractor.extractor import importar_csv
import streamlit as st
from sqlalchemy import text
from datetime import date
import warnings
import uuid

## configurações iniciais

# configuração para visualização no terminal
pd.set_option('display.max_columns', None)
warnings.filterwarnings('ignore', category=DeprecationWarning)

# conectando engine
engine = conectar_banco()

# streamlit pagina
st.set_page_config(
    page_title='NEXUS',
    layout='wide',
    initial_sidebar_state='expanded'
    )

@st.cache_data
def carregar_filtro(_engine, trigger_atualizacao):

    # carregando as datas
    query_datas_extrato = 'SELECT DISTINCT data_contabil FROM db_extratos ORDER BY data_contabil'
    query_datas_liquidacao = 'SELECT DISTINCT "Data liq." FROM vw_registro_liquidacoes ORDER BY "Data liq."'

    df_datas_extrato = pd.read_sql(query_datas_extrato, _engine)
    df_datas_extrato['data_contabil'] = pd.to_datetime(df_datas_extrato['data_contabil']).dt.date

    df_datas_liquidacao = pd.read_sql(query_datas_liquidacao, _engine)
    df_datas_liquidacao['Data liq.'] = pd.to_datetime(df_datas_liquidacao['Data liq.']).dt.date

    # carregando as empresas
    query_empresas = 'SELECT DISTINCT nome_empresa FROM db_extratos'
    df_empreas = pd.read_sql(query_empresas, engine)

    # transformando em lista
    lista_datas_extrato = df_datas_extrato['data_contabil'].to_list()
    lista_datas_liquidacao = df_datas_liquidacao['Data liq.'].to_list()
    lista_empresas = ['GRUPO'] + df_empreas['nome_empresa'].to_list()

    return lista_datas_extrato, lista_empresas, lista_datas_liquidacao

def gerar_id_numerico(row):
    # Cria a string base para o hash
    raw_str = f"{row['Banco']}{row['Ag./Conta']}{row['Data Contábil']}{row['Descrição Histórico']}{row['Valor']}"
    
    # Gera o Hash MD5 (retorna uma string hexadecimal)
    hex_hash = hashlib.md5(raw_str.encode('utf-8')).hexdigest()
    
    return hex_hash

def salvar_movimentacao(sistema, id_extrato, valor, data_baixa, duplicata, parcela):

    try:
        with engine.begin() as conn:
            query = text('''
                INSERT INTO db_liquidacoes (id_extrato, valor, data_liquidacao, sistema, duplicata, parcela)
                VALUES (:id, :val, :dt, :sis, :dp, :par)
            ''')
            conn.execute(query, {
                "id": int(id_extrato),
                "val": valor,
                "dt": data_baixa,
                "sis": sistema,
                "dp": duplicata,
                "par": parcela
            })
            return True
    except Exception as e:
        st.error(f'Erro ao salvar no banco: {e}')
        return False
    
def deletar_movimentacao(id):
    try:
        with engine.begin() as conn:
            query = text('''
                DELETE FROM db_liquidacoes WHERE id = :id_selecionado
            ''')
            conn.execute(query, {
                "id_selecionado": int(id)
            })
            return True
    except Exception as e:
        st.error(f'Erro ao salvar no banco: {e}')
        return False

@st.dialog('Liquidação Multipla', width='medium')
def modal_operacao_multipla(linha_selecionada):

    def excluir_registro(id_deletar):
        st.session_state.temp_baixas = [
            x for x in st.session_state.temp_baixas if x['_id'] != id_deletar
        ]

    if 'temp_baixas' not in st.session_state:
        st.session_state.temp_baixas = []

    st.write(f'{linha_selecionada["id"]} - {linha_selecionada["Empresa"]}')
    st.write(f'Saldo: R$ {linha_selecionada["Saldo"]:.2f}')

    with st.container(border=True):
        col1, col2, col3, col4, col5, col6 = st.columns([2.5, 2, 2.9, 1.5, 1, 1])
        with col1:
            sistema_input = st.selectbox('Sistema', ['Corporativo', 'SSW', 'Delsoft', 'Diversos'])
        
        with col2:
            date_input = st.date_input('Data liq.', value=linha_selecionada['Data'], format='YYYY-MM-DD')

        with col3:
            val_input = st.number_input('Valor', step=0.01, value=linha_selecionada['Saldo'])

        with col4:
            dp_input = st.text_input('DP')
            
        with col5:
            parc_input = st.text_input('Parc.', value='')

        with col6:
            st.write('##')
            if st.button('+', key='add_btn'):

                if (sistema_input == 'Corporativo' and dp_input.strip() != '' and parc_input.strip() != '') or (sistema_input == 'SSW' and dp_input.strip() != '') or (sistema_input == 'Delsoft' and dp_input.strip() != '') or (sistema_input == 'Diversos' and dp_input.strip() != ''):

                    if linha_selecionada["Saldo"] > 0:
                        if val_input > 0:
                            st.session_state.temp_baixas.append({'_id': str(uuid.uuid4()), 'Sistema': sistema_input, 'Data liq.': date_input, 'Valor': val_input, 'DP': dp_input, 'Parc.':parc_input})
                    else:
                        if val_input < 0:
                            st.session_state.temp_baixas.append({'_id': str(uuid.uuid4()), 'Sistema': sistema_input, 'Data liq.': date_input, 'Valor': val_input, 'DP': dp_input, 'Parc.':parc_input})

    if st.session_state.temp_baixas:

        with st.container(border=True):

            col_sis, col_date, col_val, col_dp, col_parc, col_btn = st.columns([1, 1, 1, 1, 1, 1])
            col_sis.write('**Sistema**')
            col_date.write('**Data liq.**')
            col_val.write('**Valor**')
            col_dp.write('**DP**')
            col_parc.write('**Parc.**')
            col_btn.write('**Ação**')

            for item in st.session_state.temp_baixas:
                c1, c2, c3, c4, c5, c6 = st.columns([1, 1, 1, 1, 1, 1])
                c1.write(item['Sistema'])
                c2.write(f'{item['Data liq.']}')
                c3.write(f'{item["Valor"]}')
                c4.write(item['DP'])
                c5.write(item['Parc.'])
                c6.button('-', key=f'btn_del_{item["_id"]}', on_click=excluir_registro, args=(item['_id'],))

    baixa_acumulada = sum(item['Valor'] for item in st.session_state.temp_baixas)

    if linha_selecionada['Saldo'] > 0:
        if baixa_acumulada > linha_selecionada['Saldo']:
            st.markdown(f'<span style="color:red">Total acumulado: R$ {baixa_acumulada:.2f}</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'Total acumulado: R$ {baixa_acumulada:.2f}')

    else:
        if baixa_acumulada < linha_selecionada['Saldo']:
            st.markdown(f'<span style="color:red">Total acumulado: R$ {baixa_acumulada:.2f}</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'Total acumulado: R$ {baixa_acumulada:.2f}')

    col_vazia, col_btn = st.columns([1, 1])

    with col_vazia:
        if st.button('Cancelar', width='stretch'):
            st.session_state.temp_baixas = []
            st.rerun()

    with col_btn:
        if st.button('Confirmar', width='stretch'):

            saldo_disponivel = float(linha_selecionada['Saldo'])

            if  saldo_disponivel >= 0 and baixa_acumulada > saldo_disponivel:
                st.error(f'Operação negada! O valor acumulado ({baixa_acumulada:.2f}) é maior que o saldo disponível ({linha_selecionada["Saldo"]:.2f}).')
            
            elif saldo_disponivel < 0 and baixa_acumulada < saldo_disponivel:
                st.error(f'Operação negada! O valor acumulado ({baixa_acumulada:.2f}) é maior que o saldo disponível ({linha_selecionada["Saldo"]:.2f}).')

            else:
                
                if 'temp_baixas' in st.session_state and st.session_state.temp_baixas:
                    
                    for item in st.session_state.temp_baixas:

                        sucesso = salvar_movimentacao(
                            id_extrato=linha_selecionada['id'],
                            valor=item['Valor'],
                            data_baixa=item['Data liq.'],
                            sistema=item['Sistema'],
                            duplicata=item['DP'],
                            parcela=item['Parc.']
                        )

                    st.session_state.last_update += 1
                    st.rerun()

                else:

                    if linha_selecionada['Saldo'] >= 0 and val_input <= 0:
                        st.error('O valor deve ser maior que zero.')

                    elif linha_selecionada['Saldo'] < 0 and val_input >= 0:
                        st.error('O valor deve ser menor que zero.')

                    elif linha_selecionada['Saldo'] >= 0 and val_input > saldo_disponivel:
                        st.error(f'Operação negada! O valor digitado ({val_input:.2f}) é maior que o saldo disponível ({saldo_disponivel:.2f}).')

                    elif linha_selecionada['Saldo'] < 0 and val_input < saldo_disponivel:
                        st.error(f'Operação negada! O valor digitado ({val_input:.2f}) é menor que o saldo disponível ({saldo_disponivel:.2f}).')

                    elif (sistema_input == 'Corporativo' and (dp_input.strip() == '' or parc_input.strip() == '')):
                        st.error(f'Operação negada! Favor preencher a DP e Parcela.')
                    
                    elif (sistema_input == 'SSW' and dp_input.strip() == ''):
                        st.error(f'Operação negada! Favor preencher a DP.')
                    
                    elif (sistema_input == 'Delsoft' and dp_input.strip() == ''):
                        st.error(f'Operação negada! Favor preencher a DP/Histórico.')
                    
                    elif (sistema_input == 'Diversos' and dp_input.strip() == ''):
                        st.error(f'Operação negada! Favor preencher a DP/Histórico.')

                    else:

                        sucesso = salvar_movimentacao(
                            id_extrato=linha_selecionada['id'],
                            valor=val_input,
                            data_baixa=date_input,
                            sistema=sistema_input,
                            duplicata=dp_input,
                            parcela=parc_input
                        )

                        if sucesso:
                            st.success('Liquidação registrada!')
                            st.session_state.last_update += 1
                            st.rerun()

@st.dialog('Estorno de liquidacao')
def modal_estorno_liquidacao(linha_selecionada):
    st.markdown(f'### ID: {linha_selecionada["ID"]}')
    st.markdown(f'Valor: {linha_selecionada["Valor liq."]}')

    st.write('')

    col_vazia, col_btn = st.columns([1, 1])

    with col_btn:
        if st.button('Confirmar estorno', width='stretch', type='primary'):
            sucesso = deletar_movimentacao(
                id=linha_selecionada['ID']
            )

            if sucesso:
                st.success('Liquidação registrada!')
                st.session_state.last_update += 1
                st.rerun()

    with col_vazia:
        if st.button('Cancelar', width='stretch'):
            st.rerun()

def main():

    ## IMPORTANDO OS DADOS DO SISTEMA ATLAS

    # gerando a engine
    engine = conectar_banco()

    # listando os arquivos disponíveis na pasta para importação
    arquivos_atlas = [
        os.path.join(CAMINHO_EXTRATO_BANCARIO_NOVO, f) for f in os.listdir(CAMINHO_EXTRATO_BANCARIO_NOVO)
        if not f.startswith('~') and f.endswith('.csv')
    ]

    # processando cada arquivo dentro da lista
    for arquivo in arquivos_atlas:

        df = None

        # carregando o nome do arquivo
        nome_arquivo = os.path.basename(arquivo)

        # procesando e tratando os dados
        try:
            # processando o arquivo
            df = importar_csv(arquivo)

            # validando se o df está vazio
            if df is None or df.empty:
                continue

            # filtrando os dados
            df = df[df['Unnamed: 18'].notna()]
            df.columns = df.iloc[0]
            df = df.iloc[1:]

            df = df[df['Valor'] != 'Valor']

            colunas_valor = ['Valor']
            for col in colunas_valor:
                df[col] = (df[col].astype(str)
                                    .str.replace(r'[R\$\s\xa0]', '', regex=True)
                                    .str.replace('.', '', regex=False)
                                    .str.replace(',', '.', regex=False)
                                    .astype(float))

            # negativando os valores de débito
            df['Valor'] = np.where(df['Tipo'].str.lower() == 'debito', df['Valor'] * -1, df['Valor'])
            
            # filtrando as colunas essenciais
            df = df[['Banco', 'Ag./Conta', 'Data Contábil', 'Código Categoria', 'Descrição Categoria', 'Cód. Hist.', 'Descrição Histórico', 'Documento', 'Complemento', 'Natureza', 'Tipo', 'Valor', 'Status']]

            df = df[df['Ag./Conta'] != 'Ag.: 4018-0 Cc: 89394-3']

            df.reset_index()

            # criando o hash
            df['hash'] = df.apply(gerar_id_numerico, axis=1)

            # criando o sequencial
            df = df.sort_values(by=['Data Contábil'])
            df['seq'] = (df.groupby(df['hash']).cumcount() + 1).astype(str).str.zfill(5)

            # criando o id
            df['id_transacao'] = df['hash'] + df['seq']

            # excluindo colunas
            df.drop(columns=['hash', 'seq'], inplace=True)

            # renomeando colunas
            df.rename(columns=RENOMEAR_EXTRATO, inplace=True)

            # tratando os dados de data
            df['data_contabil'] = pd.to_datetime(df['data_contabil'], dayfirst=True, errors='coerce')

            # tratando os dados de string
            colunas_string = ['banco', 'agencia_conta', 'codigo_categoria', 'descricao_categoria', 'cod_hist',
                              'descricao_historico', 'documento', 'complemento', 'natureza', 'tipo', 'status',
                              'id_transacao']

            for col in colunas_string:
                df[col] = df[col].astype(str)

            # importando os cadastros bancarios
            query_cadastros_bancarios = '''
                SELECT * FROM cadastro_contas_bancarias
            '''

            # considerando o nome da empresa
            cadastros_bancarios = pd.read_sql(query_cadastros_bancarios, engine)

            df = df.merge(cadastros_bancarios[['agencia_conta', 'nome_empresa']], on='agencia_conta', how='left')
            df['nome_empresa'] = df['nome_empresa'].fillna('Desconhecido')

            # upando o arquivo
            upsert_extrato(df, engine, nome_arquivo, arquivo)

        except Exception as e:
            print(f'[-] Erro ao processar o arquivo - "{nome_arquivo}": {e}')

if __name__ == "__main__":
    main()

    if 'last_update' not in st.session_state:
        st.session_state.last_update = 0
    lista_datas_extrato, lista_empresas, lista_datas_liquidacao = carregar_filtro(engine, st.session_state.last_update)

    with st.sidebar:
        st.title('NEXUS')
        st.header('Menu:')
        pagina = st.radio('Menu', ['Extrato', 'Liquidações'], label_visibility='collapsed')
        st.header('Configurações:')

    if pagina == 'Resumo':

        st.write('< em desenvolvimento ')

        ## RETIRADO PARA ANÁLISE
        #query_resumo = '''
        #    SELECT
        #        data_contabil as "Data",
        #        SUM(CASE WHEN tipo = 'CREDITO' THEN valor ELSE 0 END) AS "Crédito",
        #        SUM(CASE WHEN tipo = 'DEBITO' THEN valor ELSE 0 END) AS "Débito",
        #        SUM(CASE WHEN tipo = 'CREDITO' THEN valor ELSE 0 END) + SUM(CASE WHEN tipo = 'DEBITO' THEN valor ELSE 0 END) as "Saldo do dia"
        #    FROM db_extratos
        #    GROUP BY
        #        data_contabil
        #    ORDER BY
        #        data_contabil
        #'''
        #
        #df_resumo = pd.read_sql(query_resumo, engine)
        #df_resumo['Data'] = pd.to_datetime(df_resumo['Data']).dt.date
        #
        #st.dataframe(df_resumo, hide_index=True)

    elif pagina == 'Extrato':

        st.title('Extrato bancário')

        if 'data_selecionada_1' not in st.session_state: st.session_state.data_selecionada_1 = lista_datas_extrato[-1] if lista_datas_extrato else date.today()
        if 'data_selecionada_2' not in st.session_state: st.session_state.data_selecionada_2 = lista_datas_extrato[-1] if lista_datas_extrato else date.today()
        if 'empresa_selecionada' not in st.session_state: st.session_state.empresa_selecionada = 'GRUPO'
        if 'historico_selecionado' not in st.session_state: st.session_state.historico_selecionado = ''
        if 'complemento_selecionado' not in st.session_state: st.session_state.complemento_selecionado = ''
        if 'banco_selecionado' not in st.session_state: st.session_state.banco_selecionado = ''
        if 'agencia_selecionado' not in st.session_state: st.session_state.agencia_selecionado = ''
        if 'id_selecionado' not in st.session_state: st.session_state.id_selecionado = ''
        if 'valor_selecionado' not in st.session_state: st.session_state.valor_selecionado = 0

        with st.sidebar:

            with st.form(key='filtro_form_extrato'):
                selecao_data_inicio = st.date_input('Data inicio:', value=st.session_state.data_selecionada_1, format='DD/MM/YYYY')
                selecao_data_fim = st.date_input('Data fim:', value=st.session_state.data_selecionada_2, format='DD/MM/YYYY')
                selecao_empresa = st.selectbox('Empresa:', lista_empresas, index=lista_empresas.index(st.session_state.empresa_selecionada))
                selecao_banco = st.text_input('Banco', value=st.session_state.banco_selecionado)
                selecao_agencia = st.text_input('Agencia/conta', value=st.session_state.agencia_selecionado)
                selecao_historico = st.text_input('Histórico', value=st.session_state.historico_selecionado)
                selecao_complemento = st.text_input('Complemento', value=st.session_state.complemento_selecionado)
                selecao_id = st.text_input('ID', value=st.session_state.id_selecionado)
                selecao_valor = st.number_input('Valor', value=float(st.session_state.valor_selecionado))

                submit_button = st.form_submit_button(label='Atualizar')

                if submit_button:
                    st.session_state.data_selecionada_1 = selecao_data_inicio
                    st.session_state.data_selecionada_2 = selecao_data_fim
                    st.session_state.empresa_selecionada = selecao_empresa
                    st.session_state.historico_selecionado = selecao_historico
                    st.session_state.complemento_selecionado = selecao_complemento
                    st.session_state.id_selecionado = selecao_id
                    st.session_state.banco_selecionado = selecao_banco
                    st.session_state.agencia_selecionado = selecao_agencia
                    st.session_state.valor_selecionado = selecao_valor
                    st.rerun()

        busca_historico = f'%{st.session_state.historico_selecionado}%'
        busca_complemento = f'%{st.session_state.complemento_selecionado}%'
        busca_banco = f'%{st.session_state.banco_selecionado}%'
        busca_agencia = f'%{st.session_state.agencia_selecionado}%'
        busca_id = f'%{st.session_state.id_selecionado}%'
        params = {'data_1': st.session_state.data_selecionada_1,
                  'data_2': st.session_state.data_selecionada_2,
                  'historico': busca_historico,
                  'complemento': busca_complemento,
                  'id': busca_id,
                  'banco': busca_banco,
                  'agencia': busca_agencia,
                  'valor': st.session_state.valor_selecionado}
        query = '''
        SELECT 
            ext.id as ID,
            ext.nome_empresa AS "Empresa",
            ext.data_contabil AS "Data", 
            ext.banco AS "Banco", 
            ext.agencia_conta AS "Agência/Conta", 
            ext.descricao_historico AS "Desc. do Hist.",
            ext.documento AS "Doc.",
            ext.complemento AS "Comp.",
            ext.tipo AS "Tipo",
            ext.valor AS "Valor",
            COALESCE(liq.valor, 0) AS "Valor liq.",
            (ext.valor - COALESCE(liq.valor, 0)) AS "Saldo"
        FROM db_extratos ext
        LEFT JOIN (
            SELECT id_extrato, SUM(valor) AS valor
            FROM db_liquidacoes
            GROUP BY id_extrato
        ) AS liq
        ON liq.id_extrato = ext.id
        WHERE ext.data_contabil >= :data_1
            AND ext.data_contabil <= :data_2
            AND COALESCE(ext.descricao_historico, '') ILIKE :historico
            AND COALESCE(ext.banco, '') ILIKE :banco
            AND COALESCE(ext.agencia_conta, '') ILIKE :agencia
            AND COALESCE(ext.complemento, '') ILIKE :complemento
            AND ext.id::TEXT ILIKE :id
            AND (
                CASE
                    WHEN :valor = 0 THEN TRUE
                    ELSE ext.valor = :valor
                END
            )
        '''

        if st.session_state.empresa_selecionada != 'GRUPO':
            query += ' AND nome_empresa = :empresa'
            params['empresa'] = st.session_state.empresa_selecionada

        query += ' ORDER BY ext.data_contabil ASC, ext.id ASC'

        df_resultado = pd.read_sql(text(query), engine, params=params) #type: ignore

        df_com_selecao = df_resultado.copy()
        df_com_selecao.insert(0, 'Sel', False)

        tabela_editavel = st.data_editor(
            df_com_selecao,
            key='editor_extratos',
            hide_index=True,
            width='stretch',
            column_config={
                'Sel': st.column_config.CheckboxColumn('', default=False),
                'ID': st.column_config.NumberColumn('ID', format='%d'),
                'Valor': st.column_config.NumberColumn('Valor', format='%.2f'),
                'Valor liq.': st.column_config.NumberColumn('Valor liq.', format='%.2f'),
                'Saldo': st.column_config.NumberColumn('Saldo atual', format='%.2f'),
                'Data': st.column_config.DateColumn('Data', format='DD/MM/YYYY')
            },
            disabled=[c for c in df_com_selecao.columns if c!= 'Sel']
        )

        selecionados = tabela_editavel[tabela_editavel['Sel'] == True]

        if not selecionados.empty:
            if len(selecionados) > 1:
                st.error('Selecione apenas um item por vez.')
            else:
                linha = selecionados.iloc[0]

                if st.button(f'Liquidar', type='primary'):
                        st.session_state.temp_baixas = []
                        modal_operacao_multipla(linha)

        else:
            st.caption('Selecione um registro acima para habilitar as opções de liquidação.')

    elif pagina == 'Liquidações':

        st.title('Liquidações')

        if 'data_liquidacao_1' not in st.session_state: st.session_state.data_liquidacao_1 = lista_datas_liquidacao[-1] if lista_datas_liquidacao else date.today()
        if 'data_liquidacao_2' not in st.session_state: st.session_state.data_liquidacao_2 = lista_datas_liquidacao[-1] if lista_datas_liquidacao else date.today()
        if 'empresa_liquidacao' not in st.session_state: st.session_state.empresa_liquidacao = 'GRUPO'
        if 'selecao_id_extrato' not in st.session_state: st.session_state.selecao_id_extrato = ''
        if 'selecao_historico' not in st.session_state: st.session_state.selecao_historico = ''
        if 'selecao_valor_banco' not in st.session_state: st.session_state.selecao_valor_banco = 0
        if 'selecao_valor_liq' not in st.session_state: st.session_state.selecao_valor_liq = 0
        if 'selecao_sistema' not in st.session_state: st.session_state.selecao_sistema = ''
        if 'selecao_banco' not in st.session_state: st.session_state.selecao_banco = ''
        if 'selecao_agencia' not in st.session_state: st.session_state.selecao_agencia = ''
        if 'selecao_dp' not in st.session_state: st.session_state.selecao_dp = ''

        with st.sidebar:
            
            with st.form(key='filtro_form_liquidacao'):
                selecao_data_liq_inicio = st.date_input('Data inicio:', value=st.session_state.data_liquidacao_1, format='DD/MM/YYYY')
                selecao_data_liq_fim = st.date_input('Data fim:', value=st.session_state.data_liquidacao_2, format='DD/MM/YYYY')
                selecao_empresa_liq = st.selectbox('Empresa:', lista_empresas, index=lista_empresas.index(st.session_state.empresa_liquidacao) if lista_empresas else 0)
                selecao_banco = st.text_input('Banco:', value=st.session_state.selecao_banco)
                selecao_agencia = st.text_input('Agência/conta:', value=st.session_state.selecao_agencia)
                selecao_id_extrato = st.text_input('ID do extrato:', value=st.session_state.selecao_id_extrato)
                selecao_historico = st.text_input('Histórico:', value=st.session_state.selecao_historico)
                selecao_valor_banco = st.number_input('Valor banco:', value=float(st.session_state.selecao_valor_banco))
                selecao_valor_liq = st.number_input('Valor liq.', value=float(st.session_state.selecao_valor_liq))
                selecao_sistema = st.text_input('Sistema', value=st.session_state.selecao_sistema)
                selecao_dp = st.text_input('DP', value=st.session_state.selecao_dp)

                submit_button_liq = st.form_submit_button(label='Atualizar')

                if submit_button_liq:
                    st.session_state.data_liquidacao_1 = selecao_data_liq_inicio
                    st.session_state.data_liquidacao_2 = selecao_data_liq_fim
                    st.session_state.empresa_liquidacao = selecao_empresa_liq
                    st.session_state.selecao_id_extrato = selecao_id_extrato
                    st.session_state.selecao_historico = selecao_historico
                    st.session_state.selecao_valor_banco = selecao_valor_banco
                    st.session_state.selecao_valor_liq = selecao_valor_liq
                    st.session_state.selecao_sistema = selecao_sistema
                    st.session_state.selecao_banco = selecao_banco
                    st.session_state.selecao_agencia = selecao_agencia
                    st.session_state.selecao_dp = selecao_dp
                    st.rerun()

        busca_historico = f'%{st.session_state.selecao_historico}%'
        busca_sistema = f'%{st.session_state.selecao_sistema}%'
        busca_banco = f'%{st.session_state.selecao_banco}%'
        busca_agencia = f'%{st.session_state.selecao_agencia}%'
        busca_dp = f'%{st.session_state.selecao_dp}%'

        params_liq = {'data_liq_1': st.session_state.data_liquidacao_1,
                      'data_liq_2': st.session_state.data_liquidacao_2,
                      'historico': busca_historico,
                      'valor_banco': st.session_state.selecao_valor_banco,
                      'valor_liq': st.session_state.selecao_valor_liq,
                      'sistema': busca_sistema,
                      'banco': busca_banco,
                      'agencia': busca_agencia,
                      'dp': busca_dp}
        
        query_liquidacoes = '''
            SELECT *
            FROM vw_registro_liquidacoes
            WHERE "Data liq." >= :data_liq_1
                AND "Data liq." <= :data_liq_2
                AND COALESCE("Histórico", '') ILIKE :historico
                AND COALESCE("Sistema", '') ILIKE :sistema
                AND COALESCE("Banco", '') ILIKE :banco
                AND COALESCE("Agência/conta", '') ILIKE :agencia
                AND COALESCE("DP", '') ILIKE :dp
                AND (
                    CASE
                        WHEN :valor_banco = 0 THEN TRUE
                        ELSE "Valor banco" = :valor_banco
                    END
                )
                AND (
                    CASE
                        WHEN :valor_liq = 0 THEN TRUE
                        ELSE "Valor liq." = :valor_liq
                    END
                )
        '''

        if st.session_state.empresa_liquidacao != 'GRUPO':
            query_liquidacoes += ' AND "Empresa" = :empresa'
            params_liq['empresa'] = st.session_state.empresa_liquidacao

        if st.session_state.selecao_id_extrato != '':
            query_liquidacoes += ' AND "ID extrato" = :id_extrato'
            params_liq['id_extrato'] = st.session_state.selecao_id_extrato

        df_liquidacoes = pd.read_sql(text(query_liquidacoes), engine, params=params_liq) #type: ignore
        df_liquidacoes['Data liq.'] = pd.to_datetime(df_liquidacoes['Data liq.']).dt.tz_localize(None)

        if 'Data log' in df_liquidacoes.columns and not df_liquidacoes['Data log'].empty:
            df_liquidacoes['Data log'] = pd.to_datetime(df_liquidacoes['Data log']).dt.tz_convert('America/Sao_Paulo')

        df_com_selecao = df_liquidacoes.copy()
        df_com_selecao.insert(0, 'Sel', False)

        tabela_editavel = st.data_editor(
            df_com_selecao,
            key='editor_liquidacoes',
            hide_index=True,
            width='stretch',
            column_config={
                'Sel': st.column_config.CheckboxColumn('', default=False),
                'ID': st.column_config.NumberColumn('ID', format='%d'),
                'Valor banco': st.column_config.NumberColumn('Valor banco', format='%.2f'),
                'Valor liq.': st.column_config.NumberColumn('Valor liq.', format='%.2f'),
                'Data liq.': st.column_config.DateColumn('Data liq.', format='DD/MM/YYYY'),
                'Data log': st.column_config.DatetimeColumn('Data log', format='DD/MM/YYYY HH:mm:ss')
            },
            disabled=[c for c in df_com_selecao.columns if c!= 'Sel']
        )

        selecionados = tabela_editavel[tabela_editavel['Sel'] == True]

        if not selecionados.empty:
            if len(selecionados) > 1:
                st.error('Selecione apenas um item por vez.')
            else:
                linha = selecionados.iloc[0]

                if st.button(f'Estornar - ID {linha["ID"]}', type='primary', key=f'btn_estorno{linha["ID"]}'):
                    modal_estorno_liquidacao(linha)

        else:
            st.caption('Selecione um registro acima para habilitar as opções de estorno.')

    elif pagina == 'Contas bancarias':

        st.write('< em desenvolvimento >')