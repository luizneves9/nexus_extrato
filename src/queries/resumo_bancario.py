QUERY_RESUMO = '''
    WITH ranking_fluxo AS (
        SELECT
            *,
            ROW_NUMBER() OVER(
                PARTITION BY (nome_empresa, banco, agencia_conta)
                ORDER BY data_contabil DESC
            ) AS rn
            FROM mv_fluxo_caixa_diario
            WHERE data_contabil <= :data
    )
    SELECT
        nome_empresa AS "Empresa",
        data_contabil AS "Data",
        banco AS "Banco", 
        agencia_conta AS "Ag. e Cc",
        "Crédito",
        "Débito",
        "Encontro de Contas",
        "Transferência",
        "Resgate",
        "Aplicação",
        "Mov. do dia",
        "Saldo"
    FROM ranking_fluxo
    WHERE rn = 1 AND nome_empresa ILIKE :empresa
'''

QUERY_RESUMO_APLICACAO = '''
    WITH ranking_fluxo AS (
        SELECT
            *,
            ROW_NUMBER() OVER(
                PARTITION BY (nome_empresa, banco, agencia_conta)
                ORDER BY data_contabil DESC
            ) AS rn
            FROM mv_fluxo_aplicacao_diario
            WHERE data_contabil <= :data
    )
    SELECT
        nome_empresa AS "Empresa",
        data_contabil AS "Data",
        banco AS "Banco", 
        agencia_conta AS "Ag. e Cc",
        "Resgate",
        "Aplicação",
        "Rendimento",
        "Mov. do dia",
        "Saldo"
    FROM ranking_fluxo
    WHERE rn = 1 AND nome_empresa ILIKE :empresa
'''
