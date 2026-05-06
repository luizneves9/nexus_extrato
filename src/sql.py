## Função de conexão ao banco de dados PostgreSQL

import urllib.parse
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

engine = None

def conectar_banco():
    global engine
    if engine is None:

        load_dotenv()

        usuario = os.getenv("DB_USER")
        senha = os.getenv("DB_PASS")
        host = os.getenv("DB_HOST")
        porta = os.getenv("DB_PORT")
        database = os.getenv("DB_NAME")

        senha_tratada = urllib.parse.quote_plus(senha) #type: ignore
        url_conexao = f'postgresql://{usuario}:{senha_tratada}@{host}:{porta}/{database}'

        engine = create_engine(url_conexao, echo=False)

    return engine