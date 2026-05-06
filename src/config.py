from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

## caminhos
DIR_DATA = BASE_DIR / 'data'
DIR_EXTRATOS = DIR_DATA / 'extrato_bancario'

## pastas de processamento

## diretorios
CAMINHO_EXTRATO_BANCARIO_NOVO = DIR_EXTRATOS / 'novos'
CAMINHO_EXTRATO_BANCARIO_PROCESSADOS = DIR_EXTRATOS / 'processados'

## colunas principais

## renomear colunas
RENOMEAR_EXTRATO = {
    'Banco': 'banco',
    'Ag./Conta': 'agencia_conta',
    'Data Contábil': 'data_contabil',
    'Código Categoria': 'codigo_categoria',
    'Descrição Categoria': 'descricao_categoria',
    'Cód. Hist.': 'cod_hist',
    'Descrição Histórico': 'descricao_historico',
    'Documento': 'documento',
    'Complemento': 'complemento',
    'Natureza': 'natureza',
    'Tipo': 'tipo',
    'Valor': 'valor',
    'Status': 'status',
    'id_transacao': 'id_transacao'
}