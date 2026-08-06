# UC01 - Estornar Liquidação

**Ator Principal:** Operador Financeiro  
**Pré-condição:** O usuário deve estar na tela de liquidações e ter selecionado exatamente 1 registro.  
**Pós-condição:** O registro é removido da tabela de liquidações no banco de dados.  

## Fluxo Principal
1. O usuário seleciona um registro na tabela.
2. O usuário clica no botão "Estornar".
3. O sistema exibe o modal de confirmação com os dados do registro.
4. O usuário clica em "Confirmar".
5. O sistema executa o estorno no banco de dados.
6. O sistema fecha o modal e exibe mensagem de sucesso.

## Fluxos Alternativos
- **4a. Cancelamento:** Se o usuário clicar em "Cancelar" no passo 4, o modal se fecha e nenhuma alteração é feita.

## Fluxos de Exceção
- **2a. Múltipla seleção:** Se o usuário selecionar mais de 1 registro, o sistema bloqueia o envio e exibe um alerta: "Selecione apenas um item por vez."
- **5a. Erro de Conexão com o Banco:** Se o banco falhar no passo 5, o sistema exibe uma mensagem de erro em vermelho e não altera o estado da tela.
