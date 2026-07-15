LISTA_EMPRESAS = 'SELECT DISTINCT nome_empresa FROM public.db_extratos'

ESTORNAR_LIQUIDACAO = 'DELETE FROM public.db_liquidacoes WHERE id = :id_selecionado'

SELECT_LIQUIDACOES = '''
        SELECT *
        FROM public.vw_registro_liquidacoes
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
