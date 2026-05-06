import os

## definindo o caminho base do projeto
CAMINHO_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

## diretorios
CAMINHO_EXTRATO_BANCARIO_NOVO = os.path.join(CAMINHO_BASE, 'data/extrato_bancario/novos')
CAMINHO_EXTRATO_BANCARIO_PROCESSADOS = os.path.join(CAMINHO_BASE, 'data/extrato_bancario/processados')

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