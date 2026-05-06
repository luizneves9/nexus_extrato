import pandas as pd
import os

def importar_csv(diretorio, pular_linhas=0):

    nome_arquivo = os.path.basename(diretorio)

    for enc in ['utf-8-sig', 'latin-1']:
        try:
            df = pd.read_csv(diretorio, encoding=enc, sep=';', low_memory=False, skiprows=pular_linhas)
        except Exception as e:
            if enc == 'latin-1':
                print(f'[-] Erro ao processar o arquivo - "{nome_arquivo}": {e}')
                return None
            continue

        return df

