import streamlit as st
from sqlalchemy import text
from database.connection import conectar_banco

engine = conectar_banco()

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
    with col8: input_valor = st.number_input('Valor', key='input_valor')

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

                    st.session_state['mensagem_sucesso'] = 'Sistema: Lançamento realizado com sucesso!'
                    st.rerun()
                    
        if st.button('Cancelar'):
            st.rerun()
