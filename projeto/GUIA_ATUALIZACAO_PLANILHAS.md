#  Guia de Atualização das Planilhas

Este documento explica as diferentes formas de atualizar as planilhas de referência de forma mais fácil.

##  **Problema Atual**
Atualmente, para adicionar um funcionário, alguém precisa:
1. Abrir a planilha FUNC.xlsx no Excel
2. Adicionar uma nova linha com os dados
3. Salvar o arquivo
4. Fazer commit no Git (se usar controle de versão)

##  **Soluções Disponíveis**

### 1.  **Editor Web (Mais Fácil)**
Interface web no próprio sistema Streamlit para editar planilhas.

**Como usar:**
1. No sistema principal, vá em " Editor de Planilhas"
2. Selecione a planilha que quer editar
3. Use a aba " Adicionar" para novos registros
4. Ou edite diretamente na tabela (aba " Editar")
5. Clique em " Salvar Alterações"

**Vantagens:**
-  Interface amigável (não precisa Excel)
-  Validação automática
-  Backup automático
-  Funciona em qualquer dispositivo

### 2.  **API REST**
API para integração com outros sistemas.

**Iniciar API:**
```bash
cd projeto
python api_planilhas.py
```

**Exemplo de uso:**
```bash
curl -X POST http://localhost:5000/api/planilhas/FUNC.xlsx/adicionar \
  -H "Content-Type: application/json" \
  -d '{"matricula": 12345, "nome": "João Silva", "cargo": "Analista"}'
```

### 3.  **Linha de Comando**
Script simples para operações rápidas via terminal.

**Como usar:**
```bash
cd projeto
python cli_planilhas.py add-func 12345 "João Silva" "joao@empresa.com" "Analista"
```

##  **Recomendação**

**Para a maioria dos usuários: Editor Web**
- Interface mais amigável
- Não precisa conhecimento técnico
- Validação automática
- Acesso via navegador

**Escolha a opção que melhor se adapta ao seu workflow!**
