CONTAS_BANCARIAS = '''
    SELECT
        id,
        nome_empresa,
        banco,
        agencia,
        conta
    FROM cadastro_contas_bancarias
    ORDER BY nome_empresa, banco, agencia, conta, id
'''