import pandas as pd

def buscar_contas(query, conn):
    return pd.read_sql(query, conn)
