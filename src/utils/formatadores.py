def transformar_valor_decimal_em_str(valor):
    return f'{valor:,.2f}'.replace(',', 'v').replace('.', ',').replace('v', '.')
