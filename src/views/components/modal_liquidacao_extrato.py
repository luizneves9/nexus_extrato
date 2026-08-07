import streamlit as st
import uuid
from repositories.extratos_repositories import transformar_valor_decimal_em_str, transformar_valor_decimal_str_em_float
from repositories.extratos_repositories import salvar_movimentacao

@st.dialog('Liquidação Multipla', width='large')
def operacao_multipla(linha_selecionada):


    # função para excluir um registro na tabela temporária
    def excluir_registro(id_deletar):
        st.session_state.temp_baixas = [
            x for x in st.session_state.temp_baixas if x['_id'] != id_deletar
        ]

    # criando tabela temporária de baixa
    if 'temp_baixas' not in st.session_state:
        st.session_state.temp_baixas = []

    # informações do registro
    st.write(f'Saldo: R$ {transformar_valor_decimal_em_str(linha_selecionada["Saldo"])}')

    # transformando o da coluna de saldo
    linha_selecionada['Saldo'] = transformar_valor_decimal_str_em_float(linha_selecionada['Saldo'])

    with st.container(border=True):
        col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1.2, 2, 2, 1])
        with col1:
            sistema_input = st.selectbox('Sistema', ['Corporativo', 'SSW', 'Delsoft', 'Diversos'])
        
        with col2:
            date_input = st.date_input('Data liq.', value=linha_selecionada['Data'], format='DD/MM/YYYY')

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

    col_confirmar, col_cancelar = st.columns([1, 1])

    with col_confirmar:
        if st.button('Confirmar', width='stretch', type='primary'):

            saldo_disponivel = round(float(linha_selecionada['Saldo']), 2)

            if  saldo_disponivel >= 0 and baixa_acumulada > saldo_disponivel:
                st.toast(f'Operação negada! O valor acumulado ({transformar_valor_decimal_em_str(baixa_acumulada)}) é maior que o saldo disponível ({transformar_valor_decimal_em_str(linha_selecionada["Saldo"])}).', icon='⚠️')
            
            elif saldo_disponivel < 0 and baixa_acumulada < saldo_disponivel:
                st.toast(f'Operação negada! O valor acumulado ({transformar_valor_decimal_em_str(baixa_acumulada)}) é maior que o saldo disponível ({transformar_valor_decimal_em_str(linha_selecionada["Saldo"])}).', icon='⚠️')

            else:
                
                if 'temp_baixas' in st.session_state and st.session_state.temp_baixas:
                    
                    for item in st.session_state.temp_baixas:

                        try:
                            salvar_movimentacao(
                                id_extrato=linha_selecionada['id'],
                                valor=item['Valor'],
                                data_baixa=item['Data liq.'],
                                sistema=item['Sistema'],
                                duplicata=item['DP'],
                                parcela=item['Parc.']
                            )

                        except Exception as e:
                            st.toast(f'Erro ao registrar liquidação! ({e})', icon='⚠️')

                    st.session_state['mensagem_sucesso'] = 'Liquidação realizada com sucesso!'
                    st.session_state.temp_baixas = []
                    st.rerun()

                else:

                    if linha_selecionada['Saldo'] >= 0 and val_input <= 0:
                        st.toast('O valor deve ser maior que zero.', icon='⚠️')

                    elif linha_selecionada['Saldo'] < 0 and val_input >= 0:
                        st.toast('O valor deve ser menor que zero.', icon='⚠️')

                    elif linha_selecionada['Saldo'] >= 0 and val_input > saldo_disponivel:
                        st.toast(f'Operação negada! O valor digitado ({transformar_valor_decimal_em_str(val_input)}) é maior que o saldo disponível ({transformar_valor_decimal_em_str(saldo_disponivel)}).', icon='⚠️')

                    elif linha_selecionada['Saldo'] < 0 and val_input < saldo_disponivel:
                        st.toast(f'Operação negada! O valor digitado ({transformar_valor_decimal_em_str(val_input)}) é menor que o saldo disponível ({transformar_valor_decimal_em_str(saldo_disponivel)}).', icon='⚠️')

                    elif (sistema_input == 'Corporativo' and (dp_input.strip() == '' or parc_input.strip() == '')):
                        st.toast(f'Operação negada! Favor preencher a DP e Parcela.', icon='⚠️')
                    
                    elif (sistema_input == 'SSW' and dp_input.strip() == ''):
                        st.toast(f'Operação negada! Favor preencher a DP.', icon='⚠️')
                    
                    elif (sistema_input == 'Delsoft' and dp_input.strip() == ''):
                        st.toast(f'Operação negada! Favor preencher a DP/Histórico.', icon='⚠️')
                    
                    elif (sistema_input == 'Diversos' and dp_input.strip() == ''):
                        st.toast(f'Operação negada! Favor preencher a DP/Histórico.', icon='⚠️')

                    else:

                        try:
                            salvar_movimentacao(
                                id_extrato=linha_selecionada['id'],
                                valor=val_input,
                                data_baixa=date_input,
                                sistema=sistema_input,
                                duplicata=dp_input,
                                parcela=parc_input
                            )

                            st.session_state['mensagem_sucesso'] = 'Liquidação realizada com sucesso!'
                            st.session_state.temp_baixas = []
                            st.rerun()

                        except Exception as e:
                            st.toast('Erro ao registrar liquidação!', icon='⚠️')

    with col_cancelar:
        if st.button('Cancelar', width='stretch'):
            st.session_state.temp_baixas = []
            st.rerun()