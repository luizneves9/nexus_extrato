import uuid
import pandas as pd
import streamlit as st
from datetime import date
from sqlalchemy import text
from sql import conectar_banco

engine = conectar_banco()

@st.cache_data
def carregar_filtro(_engine, trigger_atualizacao):

    # carregando as datas
    query_datas_extrato = 'SELECT DISTINCT data_contabil FROM public.db_extratos ORDER BY data_contabil'
    query_datas_liquidacao = 'SELECT DISTINCT "Data liq." FROM public.vw_registro_liquidacoes ORDER BY "Data liq."'

    df_datas_extrato = pd.read_sql(query_datas_extrato, _engine)
    df_datas_extrato['data_contabil'] = pd.to_datetime(df_datas_extrato['data_contabil']).dt.date

    df_datas_liquidacao = pd.read_sql(query_datas_liquidacao, _engine)
    df_datas_liquidacao['Data liq.'] = pd.to_datetime(df_datas_liquidacao['Data liq.']).dt.date

    # carregando as empresas
    query_empresas = 'SELECT DISTINCT nome_empresa FROM public.db_extratos'
    df_empreas = pd.read_sql(query_empresas, engine)

    # transformando em lista
    lista_datas_extrato = df_datas_extrato['data_contabil'].to_list()
    lista_datas_liquidacao = df_datas_liquidacao['Data liq.'].to_list()
    lista_empresas = ['GRUPO'] + df_empreas['nome_empresa'].to_list()

    return lista_datas_extrato, lista_empresas, lista_datas_liquidacao

def transformar_valor_decimal_em_str(valor):
    return f'{valor:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.')

def transformar_valor_decimal_em_str(valor):
    return f'{valor:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.')

def transformar_valor_decimal_str_em_float(valor):
    return float(valor.replace('.', '').replace(',', '.'))

def salvar_movimentacao(sistema, id_extrato, valor, data_baixa, duplicata, parcela):

    try:
        with engine.begin() as conn:
            query = text('''
                INSERT INTO public.db_liquidacoes (id_extrato, valor, data_liquidacao, sistema, duplicata, parcela)
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

@st.dialog('Liquidação Multipla', width='large')
def modal_operacao_multipla(linha_selecionada):

    def excluir_registro(id_deletar):
        st.session_state.temp_baixas = [
            x for x in st.session_state.temp_baixas if x['_id'] != id_deletar
        ]

    if 'temp_baixas' not in st.session_state:
        st.session_state.temp_baixas = []

    st.write(f'{linha_selecionada["id"]} - {linha_selecionada["Empresa"]}')
    st.write(f'Saldo: R$ {transformar_valor_decimal_em_str(linha_selecionada["Saldo"])}')

    with st.container(border=True):
        col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1.2, 2, 2, 1])
        with col1:
            sistema_input = st.selectbox('Sistema', ['Corporativo', 'SSW', 'Delsoft', 'Diversos'])
        
        with col2:
            date_input = st.date_input('Data liq.', value=linha_selecionada['Data'], format='YYYY-MM-DD')

        with col3:
            val_input = st.number_input('Valor', step=0.01, value=linha_selecionada['Saldo'])

        with col4:
            dp_input = st.text_input('DP/Histórico')
            
        with col5:
            parc_input = st.text_input('Parc./Complemento', value='')

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
                c3.write(f'{transformar_valor_decimal_em_str(item["Valor"])}')
                c4.write(item['DP'])
                c5.write(item['Parc.'])
                c6.button('-', key=f'btn_del_{item["_id"]}', on_click=excluir_registro, args=(item['_id'],))

    baixa_acumulada = sum(item['Valor'] for item in st.session_state.temp_baixas)

    if linha_selecionada['Saldo'] > 0:
        if baixa_acumulada > linha_selecionada['Saldo']:
            st.markdown(f'<span style="color:red">Total acumulado: R$ {transformar_valor_decimal_em_str(baixa_acumulada)}</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'Total acumulado: R$ {transformar_valor_decimal_em_str(baixa_acumulada)}')

    else:
        if baixa_acumulada < linha_selecionada['Saldo']:
            st.markdown(f'<span style="color:red">Total acumulado: R$ {transformar_valor_decimal_em_str(baixa_acumulada)}</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'Total acumulado: R$ {transformar_valor_decimal_em_str(baixa_acumulada)}')

    col_vazia, col_btn = st.columns([1, 1])

    with col_vazia:
        if st.button('Cancelar', width='stretch'):
            st.session_state.temp_baixas = []
            st.rerun()

    with col_btn:
        if st.button('Confirmar', width='stretch'):

            saldo_disponivel = float(linha_selecionada['Saldo'])

            if  saldo_disponivel >= 0 and baixa_acumulada > saldo_disponivel:
                st.error(f'Operação negada! O valor acumulado ({transformar_valor_decimal_em_str(baixa_acumulada)}) é maior que o saldo disponível ({transformar_valor_decimal_em_str(linha_selecionada["Saldo"])}).')
            
            elif saldo_disponivel < 0 and baixa_acumulada < saldo_disponivel:
                st.error(f'Operação negada! O valor acumulado ({transformar_valor_decimal_em_str(baixa_acumulada)}) é maior que o saldo disponível ({transformar_valor_decimal_em_str(linha_selecionada["Saldo"])}).')

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
                        st.error(f'Operação negada! O valor digitado ({transformar_valor_decimal_em_str(val_input)}) é maior que o saldo disponível ({transformar_valor_decimal_em_str(saldo_disponivel)}).')

                    elif linha_selecionada['Saldo'] < 0 and val_input < saldo_disponivel:
                        st.error(f'Operação negada! O valor digitado ({transformar_valor_decimal_em_str(val_input)}) é menor que o saldo disponível ({transformar_valor_decimal_em_str(saldo_disponivel)}).')

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

@st.dialog('Lançamentos', width='medium')
def detalhar_lancamentos(dados, linha_selecionada):
    
    st.markdown(f'## Registro bancário: {linha_selecionada['Empresa'].title()}')
    
    ## exibindo o crédito bancário

    # transformando em dataframe
    df = [{
        'ID': linha_selecionada['id'],
        'Data': linha_selecionada['Data'],
        'Banco': linha_selecionada['Banco'],
        'Agência/Conta': linha_selecionada['Agência/Conta'],
        'Desc. do Hist.': linha_selecionada['Desc. do Hist.'],
        'Valor': linha_selecionada['Valor'],
        'Valor liq.': linha_selecionada['Valor liq.'],
        'Saldo': linha_selecionada['Saldo']
    }]

    df_extrato = pd.DataFrame(df)

    # transformando as colunas de valor para a formatação brasileira
    colunas_valor = ['Valor', 'Valor liq.', 'Saldo']
    for col in colunas_valor:
        df_extrato[col] = df_extrato[col].map(transformar_valor_decimal_em_str)

    st.dataframe(df_extrato, hide_index=True)

    st.markdown('## Lançamentos realizados:')

    dados['Valor liq.'] = dados['Valor liq.'].map(transformar_valor_decimal_em_str)

    st.dataframe(dados, hide_index=True)

def main():

    if 'last_update' not in st.session_state:
        st.session_state.last_update = 0

    lista_datas_extrato, lista_empresas, lista_datas_liquidacao = carregar_filtro(engine, st.session_state.last_update)

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

        st.html(
            """
            <style>
            [data-testid="stSidebar"] [data-testid="stForm"] {
                border: none;
                padding: 0;
                background-color: transparent;
            }
            </style>
            """
        )

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
    FROM public.db_extratos ext
    LEFT JOIN (
        SELECT id_extrato, SUM(valor) AS valor
        FROM public.db_liquidacoes
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

    colunas_valor = ['Valor', 'Valor liq.', 'Saldo']

    for col in colunas_valor:
        df_com_selecao[col] = df_com_selecao[col].map(transformar_valor_decimal_em_str)

    tabela_editavel = st.data_editor(
        df_com_selecao,
        key='editor_extratos',
        hide_index=True,
        width='stretch',
        column_config={
            'Sel': st.column_config.CheckboxColumn('', default=False),
            'ID': st.column_config.NumberColumn('ID', format='%d'),
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

            with st.container(horizontal=True):

                if st.button(f'Liquidar', type='primary'):
                        
                        for col in colunas_valor:
                            linha[col] = transformar_valor_decimal_str_em_float(linha[col])

                        st.session_state.temp_baixas = []
                        modal_operacao_multipla(linha)

                detalhar = st.button(f'Detalhar Lançamentos', type='primary')

            if detalhar:

                for col in colunas_valor:
                            linha[col] = transformar_valor_decimal_str_em_float(linha[col])

                id_selecionado = str(linha['id'])

                params_lanc = {'id_selecionado_extrato': id_selecionado}

                query_liquidacoes = '''
                    SELECT 
                        "ID",
                        "Data liq.",
                        "Sistema",
                        "DP",
                        "Parc.",
                        "Valor liq.",
                        "Data log"::date
                    FROM public.vw_registro_liquidacoes
                    WHERE "ID extrato" = :id_selecionado_extrato
                '''

                df_lancamentos = pd.read_sql(text(query_liquidacoes), engine, params=params_lanc)
                
                #st.title('Lançamentos:')
                if df_lancamentos.empty:
                    st.markdown('<span style="color:red">Sem registros!</span>', unsafe_allow_html=True)
                else:
                    detalhar_lancamentos(df_lancamentos, linha)

    else:
        st.caption('Selecione um registro acima para habilitar as opções de liquidação.')

if __name__ == '__main__':
    main()