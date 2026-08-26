import streamlit as st
from sqlalchemy import text
from database.connection import conectar_banco
from services.extrato_services import manutencao_extrato, validar_e_criar_item_divisao, registrar_divisao
from repositories.extratos_repositories import transformar_valor_decimal_em_str, transformar_valor_decimal_str_em_float

@st.dialog('Manutenção de Registro', dismissible=False)
def modal_manutencao(linha_selecionada):

    # inicializando variáveis
    lista_tipos = ['CREDITO', 'DEBITO', 'ECONTAS', 'TRANSFERENCIA', 'RESGATE', 'APLICACAO', 'RENDIMENTO', 'SUBSTITUIDO']

    if 'temp_divisao' not in st.session_state:
            st.session_state.temp_divisao = []

    # função para excluir registros da tabela temporária
    def excluir_registro(id_deletar):
        st.session_state.temp_divisao = [
            x for x in st.session_state.temp_divisao if x['_id'] != id_deletar
        ]

    try:
        indice = lista_tipos.index(linha_selecionada['Tipo'])
    except:
        indice = 0

    # informações do registro
    with st.container(border=True):
        c01, c02 = st.columns([1, 4])
        c03, c04, c05 = st.columns([0.5, 1, 1])
        c06, c07, c08 = st.columns([1, 1, 1])

        c01.text_input('**ID**', value=linha_selecionada['id'], disabled=True)
        c02.text_input('**Empresa**', value=linha_selecionada['Empresa'], disabled=True)

        c03.text_input('**Banco**', value=linha_selecionada['Banco'], disabled=True)
        c04.text_input('**Agência/Cc**', value=linha_selecionada['Agência/Conta'], disabled=True)
        with c05: selecao_tipo = st.selectbox('**Tipo**', options=lista_tipos, index=indice)

        c06.text_input('**Data**', value=linha_selecionada['Data'], disabled=True)
        c07.text_input('**Histórico**', value=linha_selecionada['Desc. do Hist.'], disabled=True)
        c08.text_input('**Valor**', value=linha_selecionada['Valor'], disabled=True)
        
    # caixa de interação para manutenção
    with st.container(border=True):

        c001, c002, c003 = st.columns([1.5, 2, 0.5], vertical_alignment='bottom')

        with c001:
            tipo_input = st.selectbox('**Tipo:**', options=lista_tipos, index=indice)

        with c002:
            val_input = st.number_input('**Valor:**', step=0.01)

        with c003:
            if st.button('+', key='add_btn_div'):
                try:
                    registro = validar_e_criar_item_divisao(tipo_input, val_input, linha_selecionada)
                    st.session_state.temp_divisao.append(registro)
                except Exception as e:
                    st.toast(e, icon='⚠️')

        if st.session_state.temp_divisao:
            with st.container(border=True):

                c0001, c0002, c0003 = st.columns([2.5, 2, 0.5], vertical_alignment='bottom')
                c0001.write('**Tipo**')
                c0002.write('**Valor**')
                c0003.write('')
    
                for item in st.session_state.temp_divisao:
                    c1, c2, c3 = st.columns([2.5, 2, 0.5], vertical_alignment='bottom')
                    c1.write(f'{item['Tipo']}')
                    c2.write(transformar_valor_decimal_em_str(item['Valor']))
                    c3.button('-', key=f'btn_del_{item["_id"]}', on_click=excluir_registro, args=(item['_id'],))
    
    col_confirmar, col_cancelar = st.columns([1, 1])

    with col_confirmar:
        if st.button('Confirmar', width='stretch', type='primary'):
            try:

                # manutenção de tipo do registro
                msg = manutencao_extrato(
                    id=linha_selecionada['id'],
                    tipo_selecionado=selecao_tipo
                )

                # divisao
                if 'temp_divisao' in st.session_state and st.session_state.temp_divisao:
                    valor_original = transformar_valor_decimal_str_em_float(linha_selecionada['Valor'])
                    soma_tabela = round(sum(round(item['Valor'], 2) for item in st.session_state.temp_divisao), 2)
                    sucesso = registrar_divisao(valor_original, soma_tabela, linha_selecionada, st.session_state.temp_divisao)

                # encerramento
                st.session_state['mensagem_sucesso'] = f'{msg}'
                st.session_state.temp_divisao = []
                st.rerun()

            except Exception as e:
                st.toast(e, icon='⚠️')

    with col_cancelar:
        if st.button('Cancelar', width='stretch'):
            st.session_state.temp_divisao = []
            st.rerun()
