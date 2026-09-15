# Plano de Execução do Projeto TeleAgent Bridge 🗺️

Este documento define o roteiro fase a fase para a execução agêntica da criação e validação do **TeleAgent Bridge**.

---

## 🎯 Metas do Projeto
1. **Ponte de Notificação Ultraleve**: Notificar marcos históricos, início de testes e conclusão de projetos com zero impacto no hardware do Gateway NV55C.
2. **Interação Bidirecional (Human-in-the-Loop)**: Permitir que agentes suspendam a execução para fazer perguntas críticas ao Francisco no Telegram e recebam sua resposta (texto ou botões) para prosseguir.
3. **Compatibilidade Universal**: Suporte a Antigravity (Hooks + MCP), GitHub Copilot (MCP + Tasks), Gemini CLI e scripts shell/Makefile.
4. **Sem Dependências Pesadas**: Implementado em Python 3 standard library (`urllib.request`, `json`, `sys`, `socket`).

---

## 📋 Fases de Execução

### Fase 1: Fundação do Repositório e Configurações
- [x] Criar estrutura de documentação (`README.md`, `ARQUITETURA.md`, `TELEGRAM_SETUP.md`, `INTEGRACOES.md`, `PLANO_DE_EXECUCAO.md`).
- [ ] Criar `.env.example` e módulo de configuração `bridge/config.py` para carregar tokens e chat IDs com validação estrita.
- [ ] Criar `Makefile` para instalação facilitada dos executáveis no `~/.local/bin/` do Gaia OS.

### Fase 2: Cliente Telegram Leve (Core HTTP)
- [ ] Implementar `bridge/telegram_client.py`:
  - Envio de mensagens com formatação Markdown/HTML.
  - Suporte a alertas com ícones contextuais (`INFO`, `WARN`, `ERROR`, `SUCCESS`, `MILESTONE`).
  - Suporte a `InlineKeyboardMarkup` (botões de ação rápida).
  - Timeout resiliente e tratamento de erros de conexão sem travar o processo chamador.

### Fase 3: Módulo Interativo (Perguntas & Respostas no Telegram)
- [ ] Implementar `bridge/interactive.py`:
  - Função `ask_user_telegram(question, options=[], timeout_seconds=300)`:
    1. Envia a pergunta com botões inline para as opções (se fornecidas) ou aguarda texto livre.
    2. Registra o `message_id` para correlacionar a resposta.
    3. Faz polling leve com `getUpdates` filtrando exclusivamente mensagens do `CHAT_ID` autorizado.
    4. Ao receber a resposta ou clique no botão, edita a mensagem no Telegram marcando como `[Respondido: <Opção>]` e retorna o valor para a IA.

### Fase 4: Utilitários de Linha de Comando (CLI Wrappers)
- [ ] Criar executável `bin/agent-notify`:
  - Sintaxe: `agent-notify "Mensagem"` ou `agent-notify --level milestone "Bateria de testes em andamento"`.
- [ ] Criar executável `bin/agent-ask`:
  - Sintaxe: `agent-ask "Qual o banco de dados?" --options "Postgres,MySQL,SQLite"`.
  - Retorna a resposta na saída padrão (`stdout`), facilitando a captura em scripts (`RESPOSTA=$(agent-ask ...)`).
- [ ] Tornar os arquivos executáveis (`chmod +x bin/*`).

### Fase 5: Servidor MCP Universal (`bridge/mcp_server.py`)
- [ ] Implementar servidor MCP leve usando JSON-RPC 2.0 via `stdio`.
- [ ] Expor as ferramentas:
  - `telegram_notify`: Para Antigravity, Copilot e Codex dispararem marcos.
  - `telegram_ask`: Para agentes solicitarem decisões do usuário.
- [ ] Testar compatibilidade de schemas com a especificação oficial do MCP.

### Fase 6: Hooks de Ciclo de Vida do Antigravity
- [ ] Implementar `hooks/on_stop_hook.py`:
  - Notifica término da execução ou alerta se o agente parou por erro ou limite de passos.
- [ ] Implementar `hooks/on_error_hook.py`:
  - Detecta falhas em ferramentas (`PostToolUse` com erro) e avisa no Telegram se um comando crítico falhar.
- [ ] Fornecer configuração modelo para `.agents/hooks.json`.

### Fase 7: Bateria de Testes e Validação
- [ ] Criar suite de testes unitários simulados (mockando chamadas da API do Telegram):
  - Teste de formatação e sanitização de mensagens.
  - Teste de fluxo de perguntas e respostas (timeout, cancelamento, resposta válida).
  - Teste de protocolo JSON-RPC do MCP Server.
- [ ] Smoke test real com as credenciais do bot do Francisco.
- [ ] Walkthrough final documentando a entrega.
