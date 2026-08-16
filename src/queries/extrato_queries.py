LISTA_EMPRESAS = 'SELECT DISTINCT nome_empresa FROM public.db_extratos'

SELECT_EXTRATO = '''
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

SELECT_LIQUIDACOES_ID = '''
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

QUERY_DELETE_EXTRATO = 'DELETE FROM public.db_extratos WHERE id = :id_linha'

REFRESH_VIEWS = '''
    BEGIN;
    REFRESH MATERIALIZED VIEW mv_fluxo_aplicacao_diario;
    REFRESH MATERIALIZED VIEW mv_fluxo_caixa_diario;
    COMMIT;
'''

INSERIR_REGISTRO = '''
    INSERT INTO public.db_liquidacoes (id_extrato, valor, data_liquidacao, sistema, duplicata, parcela)
    VALUES (:id, :val, :dt, :sis, :dp, :par)
'''
MANUTENCAO_REGISTRO_BANCARIO = '''
    UPDATE public.db_extratos
    SET tipo = :tipo_novo
    WHERE id = :id_selecionado
'''

ATUALIZAÇÃO_SOMA_RESUMOS = '''
    BEGIN;
    REFRESH MATERIALIZED VIEW mv_fluxo_aplicacao_diario;
    REFRESH MATERIALIZED VIEW mv_fluxo_caixa_diario;
    COMMIT;
'''
