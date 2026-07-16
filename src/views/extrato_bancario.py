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

    baixa_acumulada = round(sum(item['Valor'] for item in st.session_state.temp_baixas), 2)

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

            saldo_disponivel = round(float(linha_selecionada['Saldo']), 2)

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

def update_tipo(id, tipo):
    try:
        with engine.begin() as conn:
            query = text('''
                UPDATE public.db_extratos
                SET tipo = :tipo_novo
                WHERE id = :id_selecionado
            ''')
            conn.execute(query, {
                "id_selecionado": int(id),
                "tipo_novo": str(tipo)
            })
            return True
    except Exception as e:
        st.error(f'Erro ao salvar no banco: {e}')
        return False

@st.dialog('Manutenção de Registro')
def modal_manutencao(linha_selecionada):

    st.write('')

    lista_tipos = ['CREDITO', 'DEBITO', 'ECONTAS', 'TRANSFERENCIA', 'RESGATE', 'APLICACAO', 'RENDIMENTO']

    try:
        indice = lista_tipos.index(linha_selecionada['Tipo'])
    except:
        indice = 0

    selecao_tipo = st.selectbox('Tipo:', options=lista_tipos, index=indice)

    col_vazia, col_btn = st.columns([1, 1])

    with col_btn:
        if st.button('Confirmar', width='stretch', type='primary'):
            sucesso = update_tipo(
                id=linha_selecionada['id'],
                tipo=selecao_tipo
            )

            if sucesso:
                st.toast('Sistema: Alteração registrada!', icon='✅')
                st.session_state.last_update += 1

                with engine.begin() as conn:    
                    query = text('''
                        BEGIN;
                        REFRESH MATERIALIZED VIEW mv_fluxo_aplicacao_diario;
                        REFRESH MATERIALIZED VIEW mv_fluxo_caixa_diario;
                        COMMIT;
                    ''')
                    conn.execute(query)     

                st.rerun()

    with col_vazia:
        if st.button('Cancelar', width='stretch'):
            st.rerun()

@st.dialog('Excluir Registro')
def excluir_registro(linha, senha):

    st.markdown('*Atenção: A exclusão deste registro não poderá ser revertida!*')

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1: st.text_input('Id:', value=linha['id'], disabled=True)
    with col2: st.text_input('Empresa:', value=linha['Empresa'], disabled=True)
    with col3: st.text_input('Data', value=linha['Data'], disabled=True)

    col4, col5, col6 = st.columns([1, 3, 3])
    with col4: st.text_input('Banco', value=linha['Banco'], disabled=True)
    with col5: st.text_input('Conta', value=linha['Agência/Conta'], disabled=True)
    with col6: st.text_input('Histórico', value=linha['Desc. do Hist.'], disabled=True)

    col7, col8 = st.columns([1, 1])
    with col7: st.text_input('Tipo', value=linha['Tipo'], disabled=True)
    with col8: st.text_input('Valor', value=linha['Valor'], disabled=True)

    if linha['Valor liq.'] != '0,00':
        st.divider()
        st.error('Erro: O registro possui valor liquidado!')

    else:
        col1, col2, col3 = st.columns([3, 1.5, 1.5], vertical_alignment='bottom')

        with col1: 
            senha_digitada = st.text_input('Senha:', type='password')

        with col2:
            if st.button('Confirmar'):
                
                if senha_digitada == senha:
                    sucesso = False

                    with engine.begin() as conn:
                        try:
                            query = text('DELETE FROM public.db_extratos WHERE id = :id_linha')
                            result = conn.execute(query, {'id_linha': int(linha['id'])})

                            if result.rowcount > 0:
                                sucesso = True
                            else:
                                st.toast('Sistema: Nenhum registro encontrado com esse ID.', icon='⚠️')

                        except Exception as e:
                            st.toast(f'Sistema: Erro ao deletar registro -> {e}', icon='❌')

                    if sucesso:
                        st.toast(f'Registro excluído com sucesso! ID: {linha['id']}', icon='✅')
                        with engine.begin() as conn:    
                            query = text('''
                                BEGIN;
                                REFRESH MATERIALIZED VIEW mv_fluxo_aplicacao_diario;
                                REFRESH MATERIALIZED VIEW mv_fluxo_caixa_diario;
                                COMMIT;
                            ''')
                            conn.execute(query)   
                        st.rerun()
               
                else:
                    st.toast('Senha inválida!', icon='❌')

        with col3: 
            if st.button('Cancelar'): st.rerun()

@st.dialog('Lançamento Manual')
def modal_lancamento():

    st.markdown('*Os lançamentos serão apontados como "Manual" na coluna "Complemento".*')
    st.write('')

    contas_bancarias = {
        '': ['', ''],
        "Ag.: 4018-0 Cc: 99881-7": [341 ,"VIACAO GARCIA LTDA"],
        "Ag.: 3425-0 Cc: 3789-3": [1 ,"EMPR STO ANJO DA GUARDA LTDA"],
        "Ag.: 3407-0 Cc: 8740-8": [1 ,"EMPR PRINCESA DO IVAI LTDA"],
        "Ag.: 4315-0 Cc: 577214883-0": [104 ,"EMPR PRINCESA DO IVAI LTDA"],
        "Ag.: 730-0 Cc: 15801-1": [341 ,"EMPR STO ANJO DA GUARDA LTDA"],
        "Ag.: 4315-0 Cc: 577214251-4": [104 ,"BRASIL SUL LINHAS RODOVIARIAS LTDA"],
        "Ag.: 0001 Cc: 850471-5": [208 ,"BRASIL SUL LINHAS RODOVIARIAS LTDA"],
        "Ag.: 3407-0 Cc: 90239-X": [1 ,"BRASIL SUL GESTORA DE BENS VIAGENS E TURISMO LTDA"],
        "Ag.: 3407-0 Cc: 5685-5": [1 ,"BRASIL SUL ENCOMENDAS RAPIDAS LTDA"],
        "Ag.: 3407-0 Cc: 3761-3": [1 ,"VIACAO GARCIA LTDA"],
        "Ag.: 3407-0 Cc: 5723-1": [1 ,"BRASIL SUL LINHAS RODOVIARIAS LTDA"],
        "Ag.: 0001 Cc: 238108-2": [208 ,"VIACAO GARCIA LTDA"],
        "Ag.: 3552-1 Cc: 30810-2": [237 ,"BRASIL SUL GESTORA DE BENS VIAGENS E TURISMO LTDA"],
        "Ag.: 0001 Cc: 247316-9": [208 ,"BRASIL SUL LINHAS RODOVIARIAS LTDA"],
        "Ag.: 3552-1 Cc: 21500-7": [237 ,"BRASIL SUL LINHAS RODOVIARIAS LTDA"],
        "Ag.: 4315-0 Cc: 577214882-2": [104 ,"LONDRINA SUL TRANSPORTE COLETIVO LTDA"],
        "Ag.: 3552-1 Cc: 30820-P": [237 ,"BRASIL SUL ENCOMENDAS RAPIDAS LTDA"],
        "Ag.: 162-0 Cc: 13050874-5": [33 ,"BRASIL SUL ENCOMENDAS RAPIDAS LTDA"],
        "Ag.: 0041 Cc: 068578670-3": [41 ,"BRASIL SUL LINHAS RODOVIARIAS LTDA"],
        "Ag.: 0718-8 Cc: 83237-5": [748 ,"VIACAO GARCIA LTDA"],
        "Ag.: 162-0 Cc: 13036565-6": [33 ,"BRASIL SUL LINHAS RODOVIARIAS LTDA"],
        "Ag.: 4018-0 Cc: 99889-0": [341 ,"BRASIL SUL LINHAS RODOVIARIAS LTDA"],
        "Ag.: 3552-1 Cc: 4825-9": [237 ,"VIACAO GARCIA LTDA"],
        "Ag.: 0515 Cc: 060027530-0": [41 ,"EMPR STO ANJO DA GUARDA LTDA"],
        "Ag.: 4018-0 Cc: 99871-8": [341 ,"BRASIL SUL LINHAS RODOVIARIAS LTDA"],
        "Ag.: 4018-0 Cc: 89397-6": [341 ,"BRASIL SUL GESTORA DE BENS VIAGENS E TURISMO LTDA"],
        "Ag.: 162-0 Cc: 13004356-9": [33 ,"EMPR PRINCESA DO IVAI LTDA"],
        "Ag.: 4018-8 Cc: 38508-0": [341 ,"EMPR PRINCESA DO IVAI LTDA"],
        "Ag.: 4018-0 Cc: 89394-3": [341 ,"BRASIL SUL LINHAS RODOVIARIAS LTDA"],
        "Ag.: 0718-8 Cc: 87525-2": [748 ,"EMPR PRINCESA DO IVAI LTDA"],
        "Ag.: 4018-0 Cc: 99892-4": [341 ,"BRASIL SUL LINHAS RODOVIARIAS LTDA"],
        "Ag.: 0001 Cc: 849938-3": [208 ,"VIACAO GARCIA LTDA"],
        "Ag.: 4018-0 Cc: 99891-6": [341 ,"BRASIL SUL ENCOMENDAS RAPIDAS LTDA"],
        "Ag.: 162-0 Cc: 13010059-8": [33 ,"BRASIL SUL LINHAS RODOVIARIAS LTDA"],
        "Ag.: 3552-1 Cc: 17501-3": [237 ,"BRASIL SUL LINHAS RODOVIARIAS LTDA"],
        "Ag.: 4315-0 Cc: 577214293-0": [104 ,"VIACAO GARCIA LTDA"],
        "Ag.: 0001 Cc: 244607-4": [208 ,"BRASIL SUL LINHAS RODOVIARIAS LTDA"],
        "Ag.: 3471-0 Cc: 773-0": [237 ,"EMPR STO ANJO DA GUARDA LTDA"],
        "Ag.: 3552-1 Cc: 29412-8": [237 ,"EMPR PRINCESA DO IVAI LTDA"],
        "Ag.: 4018-0 Cc: 89565-8": [341 ,"VIACAO GARCIA LTDA"],
        "Ag.: 4315-0 Cc: 577219567-7": [104 ,"EMPR STO ANJO DA GUARDA LTDA"],
        "Ag.: 4018-8 Cc: 89394-3": [341 ,"BRASIL SUL LINHAS RODOVIARIAS LTDA"],
        "Ag.: 0001 Cc: 1460-7": [563 ,"VIACAO GARCIA LTDA"],
        "Ag.: 0001 Cc: 1461-5": [563 ,"LONDRINA SUL TRANSPORTE COLETIVO LTDA"],
        "Ag.: 0001 Cc: 241516-9": [208 ,"BRASIL SUL GESTORA DE BENS VIAGENS E TURISMO LTDA"],
        "Ag.: 4018-0 Cc: 89564-1": [341 ,"VIACAO GARCIA LTDA"],
        "Ag.: 4018-0 Cc: 37758-2": [341 ,"VIACAO GARCIA LTDA"],
        "Ag.: 162-0 Cc: 13065874-7": [33 ,"BRASIL SUL GESTORA DE BENS VIAGENS E TURISMO LTDA"],
        "Ag.: 0001 Cc: 240329-6": [208 ,"BRASIL SUL ENCOMENDAS RAPIDAS LTDA"],
        "Ag.: 0001 Cc: 259840-3": [208 ,"BRASIL SUL ENCOMENDAS RAPIDAS LTDA"],
        "Ag.: 4018-0 Cc: 89396-8": [341 ,"LONDRINA SUL TRANSPORTE COLETIVO LTDA"],
        "Ag.: 3407-0 Cc: 6789-X": [1 ,"LONDRINA SUL TRANSPORTE COLETIVO LTDA"],
        "Ag.: 3407-0 Cc: 10395-0": [1 ,"BRASIL SUL LINHAS RODOVIARIAS LTDA"],
        "Ag.: 0001 Cc: 268719-3": [208 ,"EMPR PRINCESA DO IVAI LTDA"],
        "Ag.: 4018-0 Cc: 89401-6": [341 ,"BRASIL SUL ENCOMENDAS RAPIDAS LTDA"],
        "Ag.: 162-0 Cc: 13000259-3": [33 ,"VIACAO GARCIA LTDA"],
        "Ag.: 0001 Cc: 221770-2": [208 ,"LONDRINA SUL TRANSPORTE COLETIVO LTDA"],
        "Ag.: 162-0 Cc: 13065654-9": [33 ,"LONDRINA SUL TRANSPORTE COLETIVO LTDA"],
        "Ag.: 3552-1 Cc: 31800-0": [237 ,"LONDRINA SUL TRANSPORTE COLETIVO LTDA"],
        "Ag.: 4018-0 Cc: 99876-7": [341 ,"EMPR STO ANJO DA GUARDA LTDA"],
        "Ag.: 3407-X Cc: 5180-2": [1 ,"VIACAO OURO BRANCO LTDA"],
        "Ag.: 4315 Cc: 5772148814": [104 ,"VIACAO OURO BRANCO LTDA"]
    }

    col2, col3 = st.columns([2.5, 1.2])
    with col2: input_agencia = st.selectbox('Ag./Cc:', list(contas_bancarias.keys()), index=0)
    with col3: input_data = st.date_input('Data:', format='DD/MM/YYYY')

    if input_agencia:
        st.session_state.input_empresa = contas_bancarias[input_agencia][1]
        st.session_state.input_banco = contas_bancarias[input_agencia][0]

    col1, col4, col5 = st.columns([1, 3, 3])
    with col1: input_banco = st.text_input('Banco', value=st.session_state.input_banco, disabled=True)
    with col4: input_empresa = st.text_input('Empresa:', value=st.session_state.input_empresa, disabled=True)
    with col5: input_historico = st.text_input('Histórico:', value=st.session_state.input_historico, key='input_historico')

    col6, col7, col8 = st.columns([1, 2, 2])
    with col6: input_complemento = st.text_input('Comp.', value='Manual', disabled=True)
    with col7: input_tipo = st.selectbox('Tipo:', ['CREDITO', 'DEBITO', 'ECONTAS', 'TRANSFERENCIA', 'RESGATE', 'APLICACAO', 'RENDIMENTO'])
    with col8: input_valor = st.number_input('Valor', value=0.00, key='input_valor')

    st.write('')

    with st.container(horizontal=True):

        if st.button('Confirmar'):
            if input_empresa == '' or input_valor == 0 or input_historico.strip() == '': #type: ignore
                st.toast('Aviso: Preencha todos os campos!', icon='⚠️')
            else:
                sucesso = False

                try:
                    with engine.begin() as conn:
                        query = text('''
                            INSERT INTO db_extratos (banco, agencia_conta, data_contabil, codigo_categoria, descricao_categoria, cod_hist, descricao_historico, documento, complemento, natureza, tipo, valor, status, nome_empresa)
                            VALUES
                                (:banco, :agencia_conta, :data, 0, '', '', :historico, '0', 'Lcto Manual', 'DPV', :tipo_lcto, :valor, 'NC', :empresa)
                        ''')
                        conn.execute(query, {
                            'banco': input_banco,
                            'agencia_conta': input_agencia,
                            'data': input_data,
                            'historico': input_historico,
                            'tipo_lcto': input_tipo,
                            'valor': input_valor,
                            'empresa': input_empresa
                        })
                        sucesso = True
                        st.toast('Sistema: Lançamento realizado com sucesso!', icon='✅')
                except ValueError:
                    st.toast('Sistema: Erro ao salvar o lançamento!', icon='❌')

                if sucesso:

                    with engine.begin() as conn:    
                        query = text('''
                            BEGIN;
                                REFRESH MATERIALIZED VIEW mv_fluxo_aplicacao_diario;
                                REFRESH MATERIALIZED VIEW mv_fluxo_caixa_diario;
                                COMMIT;
                        ''')
                        conn.execute(query)   

                    st.rerun()
                    
        if st.button('Cancelar'):
            st.rerun()

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
                ELSE ABS(ext.valor) = ABS(:valor)
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
        linha = selecionados.iloc[0]

    with st.container(horizontal=True):

        if st.button(f'Liquidar', type='primary'):
                
            if len(selecionados) != 1:
                st.toast('Selecione um registro.', icon='⚠️')

            else:
                for col in colunas_valor:
                    linha[col] = transformar_valor_decimal_str_em_float(linha[col])

                st.session_state.temp_baixas = []
                modal_operacao_multipla(linha)

        if st.button(f'Detalhar', type='primary'):

            if len(selecionados) != 1:
                st.toast('Selecione apenas um registro.', icon='⚠️')

            else:
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

        if st.button('Manutenção', type='primary'):

            if len(selecionados) != 1:
                st.toast('Selecione um registro.', icon='⚠️')

            else:
                modal_manutencao(linha)

        if st.button('Lançamento', type='secondary'):
            if "input_historico" not in st.session_state:
                st.session_state.input_historico = ""
            if "input_valor" not in st.session_state:
                st.session_state.input_valor = 0.0
            if "input_empresa" not in st.session_state:
                st.session_state.input_empresa = ""
            if "input_banco" not in st.session_state:
                st.session_state.input_banco = ""
            modal_lancamento()

        if st.button('Excluir', type='secondary'):

            if len(selecionados) != 1:
                st.toast('Selecione um registro.', icon='⚠️')

            else:
                senha_excluir = 'gbs3299'
                excluir_registro(linha, senha_excluir)

if __name__ == '__main__':
    main()