# Arquitetura do Sistema - TeleAgent Bridge 🏛️

## 1. Visão Geral
O **TeleAgent Bridge** foi projetado para resolver a assincronia entre o trabalho dos agentes de IA (que operam de forma autônoma no terminal ou na IDE) e o usuário (Francisco), sem sobrecarregar os recursos da máquina host (i7-640M 2 cores / 4 threads, Gaia OS).

O sistema provê **duas vias de comunicação**:
1. **Unidirecional (Push / Alertas)**: Notificações de marcos, início de suítes de testes, conclusão e relatórios de erro.
2. **Bidirecional (Interactive / Ask-Response)**: O agente pausa o fluxo e envia uma pergunta ou opções de escolha para o Telegram. O usuário responde pelo celular, e o agente recebe a resposta diretamente no terminal/sessão e retoma o trabalho.

---

## 2. Camadas do Sistema

### A. Camada de Agentes & Clientes
- **Antigravity IDE & CLI**:
  - Integração via **Hooks (`hooks.json`)**: Intercepta eventos de ciclo de vida (`Stop`, `PostToolUse` em erros).
  - Integração via **MCP (`mcp_config.json`)**: Expõe ferramentas `telegram_notify` e `telegram_ask` para uso consciente pelo modelo.
- **GitHub Copilot & VS Code**:
  - Suporte a servidores MCP configurados no `.vscode/mcp.json` ou extensões de tarefas.
  - Scripts de terminal executáveis por tarefas do VS Code.
- **Gemini CLI / Codex / Terminal Genérico**:
  - Binários de conveniência em `~/.local/bin/`: `agent-notify` e `agent-ask`.
  - Podem ser chamados em Makefiles, shell scripts, pipelines de CI local ou scripts Python.

### B. Camada de Barramento e Comunicação (Core Bridge)
Para manter o consumo de memória abaixo de 20MB e uso de CPU praticamente nulo:
- **Implementação em Python 3 stdlib puro** (sem bibliotecas externas pesadas).
- Usa `urllib.request` e `json` nativos para comunicação HTTPS com a API do Telegram.
- **Mecanismo de Resposta Interativa (Long Polling sob demanda)**:
  - Quando o agente usa `agent-ask` ou a ferramenta MCP `telegram_ask`, um identificador de pergunta único (`poll_id` ou `message_id`) é criado com botões inline (`InlineKeyboardMarkup`) ou aguarda a próxima mensagem de resposta do chat ID autorizado.
  - O script faz requisições rápidas de `getUpdates` com `offset` até receber a resposta ou até estourar o timeout configurado, retornando o texto para o agente.

### C. Camada de Segurança e Autorização
- **Filtro de Chat ID**: O bot rejeita silenciosamente qualquer mensagem que não venha do `TELEGRAM_CHAT_ID` autorizado de Francisco.
- **Armazenamento de Segredos**: Arquivo local `.env` protegido com permissão `600` contendo `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`.

---

## 3. Diagrama de Sequência: Notificação de Dúvida (Human-in-the-Loop)

```
[Agente IA / Antigravity]         [TeleAgent Bridge]             [Telegram / Celular]
          |                               |                                |
          | 1. telegram_ask("Qual banco?") |                                |
          |------------------------------>|                                |
          |                               | 2. POST /sendMessage           |
          |                               |    (Mensagem + Botões inline)  |
          |                               |------------------------------->|
          |                               |                                |
          |                               |                       [Usuário lê e clica]
          |                               | 3. Callback / Mensagem         |
          |                               |    "PostgreSQL"                |
          |                               |<-------------------------------|
          | 4. Retorna "PostgreSQL"       |                                |
          |<------------------------------|                                |
          |                               |                                |
[Continua a codificação]                  |                                |
```

---

## 4. Estrutura de Diretórios Proposta

```
BotTelegram/
├── README.md                  # Apresentação do projeto
├── docs/                      # Documentação detalhada
│   ├── ARQUITETURA.md         # Este documento
│   ├── TELEGRAM_SETUP.md      # Guia do Telegram (BotFather & Credenciais)
│   ├── INTEGRACOES.md         # Como plugar em Antigravity, Copilot, Gemini CLI
│   └── PLANO_DE_EXECUCAO.md   # Passo a passo da implementação
├── bin/                       # Executáveis CLI universais
│   ├── agent-notify           # CLI para envio de alertas/marcos
│   └── agent-ask              # CLI interativo para perguntas com resposta
├── bridge/                    # Núcleo de comunicação
│   ├── __init__.py
│   ├── config.py              # Leitor de variáveis e .env
│   ├── telegram_client.py     # Cliente HTTP leve da Telegram Bot API
│   ├── interactive.py         # Gerenciador de perguntas e polling de respostas
│   └── mcp_server.py          # Servidor MCP stdio (Model Context Protocol)
├── hooks/                     # Modelos e scripts de Hooks para Antigravity
│   └── on_stop_hook.py        # Notifica conclusão ou necessidade de atenção
├── tests/                     # Testes de envio, recebimento e validação
│   ├── test_client.py
│   └── test_interactive.py
├── .env.example               # Exemplo de variáveis de ambiente
└── Makefile                   # Instalação rápida de symlinks em ~/.local/bin
```
