from sqlalchemy import text
import shutil
from config import CAMINHO_EXTRATO_BANCARIO_PROCESSADOS
from datetime import datetime
import os

def upsert_extrato(df, engine, nome_arquivo, diretorio_arquivo):

    try:
        with engine.begin() as conn:

            # criando tabela temporário
            conn.execute(text("CREATE TEMPORARY TABLE temp_extrato (LIKE public.db_extratos INCLUDING ALL) ON COMMIT DROP;"))

            # incluindo os dados na tabela temporária
            df.to_sql(name='temp_extrato', con=conn, if_exists='append', index=False) #type: ignore

            # criando a query de sincronização
            query = text("""
                        INSERT INTO db_extratos (
                            nome_empresa, banco, agencia_conta, data_contabil, codigo_categoria, descricao_categoria,
                            cod_hist, descricao_historico, documento, complemento, natureza, tipo,
                            valor, status, id_transacao
                        )
                        SELECT 
                            nome_empresa, banco, agencia_conta, data_contabil, codigo_categoria, descricao_categoria,
                            cod_hist, descricao_historico, documento, complemento, natureza, tipo,
                            valor, status, id_transacao 
                        FROM temp_extrato
                        ON CONFLICT (id_transacao)
                        DO NOTHING;
            """)

            conn.execute(query)
            print(f'[+] Arquivo "{nome_arquivo}" processado com sucesso!')

            # movendo o arquivo processado
            nome, extensao = os.path.splitext(nome_arquivo)
            hora = datetime.now().strftime('%Y%m%d_%H%M%S')
            novo_nome = f'{nome}_{hora}{extensao}'
            destino_final = os.path.join(CAMINHO_EXTRATO_BANCARIO_PROCESSADOS, novo_nome)

            shutil.move(diretorio_arquivo, destino_final)

    except Exception as e:
        print(f'[-] Erro ao tentar incluir o dataframe no banco de dados: {e}')
