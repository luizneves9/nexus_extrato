## Função de conexão ao banco de dados PostgreSQL

import urllib.parse
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

engine = None

def conectar_banco():
    global engine
    if engine is None:

        ambiente = os.getenv('APP_ENV', 'test')
        load_dotenv(f'.env.{ambiente}')

        url_conexao = os.getenv('DATABASE_URL')

        if not url_conexao:
            raise ValueError(f'A variável DATABASE_URL não foi encontrada no arquivo .env.{ambiente}')

        if url_conexao and url_conexao.startswith('postgresql://'):
            url_conexao = url_conexao.replace('postgresql://', 'postgresql+psycopg2://', 1)

        engine = create_engine(url_conexao, echo=False)

    return engine