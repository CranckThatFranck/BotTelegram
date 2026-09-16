# Guia de Integração Multi-Agente 🔌

> [!IMPORTANT]
> ⚠️ **DIRETRIZ DE INTEGRAÇÃO**  
> Todos os modelos e agentes ativos no sistema (Gemini CLI, Antigravity, VS Code, Codex) podem ser configurados para utilizar esta infraestrutura. A comunicação via Telegram é o canal de supervisão e decisão human-in-the-loop neste ecossistema.

Este documento detalha como conectar o **TeleAgent Bridge** a cada uma das ferramentas do seu ecossistema de desenvolvimento.

---

## 1. Integração com Antigravity (IDE e CLI)

O Antigravity possui suporte nativo a **Model Context Protocol (MCP)** e **Lifecycle Hooks**. Podemos usar ambos para uma cobertura de 100%.

### A. Ferramentas MCP Conscientes (Tools)
Permite que a IA chame proativamente as funções no meio de uma tarefa.

Adicione ao seu `~/.gemini/config/mcp_config.json` ou no `.agents/mcp_config.json` do workspace:
```json
{
  "mcpServers": {
    "teleagent": {
      "command": "/caminho/para/BotTelegram/bridge/mcp_server.py",
      "args": []
    }
  }
}
```

**Ferramentas disponíveis para o modelo:**
- `telegram_notify(message, level)`: Envia atualizações de marcos (ex: `"Iniciando bateria de testes"` ou `"Build concluída com sucesso"`).
- `telegram_ask(question, options, timeout_seconds)`: Pausa a execução do agente, envia a dúvida ao usuário no Telegram e aguarda a resposta selecionada ou digitada.

### B. Lifecycle Hooks (`hooks.json`)
Mesmo que o modelo não chame a ferramenta manualmente, os hooks interceptam eventos automaticamente.

Crie ou edite `.agents/hooks.json` ou `~/.gemini/config/hooks.json`:
```json
{
  "telegram-supervisor": {
    "Stop": [
      {
        "type": "command",
        "command": "/caminho/para/BotTelegram/hooks/on_stop_hook.py"
      }
    ],
    "PostToolUse": [
      {
        "matcher": "run_command",
        "hooks": [
          {
            "type": "command",
            "command": "/caminho/para/BotTelegram/hooks/on_error_hook.py"
          }
        ]
      }
    ]
  }
}
```
- Quando a sessão parar por erro ou finalização (`Stop`), você recebe o aviso no Telegram.
- Quando um `run_command` crítico falhar em `PostToolUse`, um alerta imediato é enviado.

---

## 2. Integração com GitHub Copilot no VS Code

O VS Code suporta servidores MCP para agentes do Copilot Chat.

Adicione no arquivo de configuração de MCP do VS Code (geralmente em `.vscode/mcp.json` ou configurações globais do VS Code):
```json
{
  "servers": {
    "teleagent": {
      "command": "/caminho/para/BotTelegram/bridge/mcp_server.py"
    }
  }
}
```

Além disso, em tarefas automáticas do VS Code (`.vscode/tasks.json`):
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Build & Notify",
      "type": "shell",
      "command": "npm run build && agent-notify '✅ Build concluída no VS Code' || agent-notify '❌ Falha na build'",
      "problemMatcher": []
    }
  ]
}
```

---

## 3. Integração com Gemini CLI

O Gemini CLI pode interagir através dos comandos globais instalados em `~/.local/bin/`:

### Exemplos no Terminal:
```bash
# Notificação simples de marco
gemini "Refatore o módulo de autenticação" && agent-notify "🎉 Refatoração de autenticação finalizada pelo Gemini CLI"

# Pergunta interativa para o usuário via Telegram
RESPOSTA=$(agent-ask "Qual ambiente devemos fazer deploy?" --options "Homologacao,Producao,Cancelar")
echo "Você escolheu: $RESPOSTA"
```

---

## 4. Integração com Codex, Makefiles e Scripts Bash

Para qualquer pipeline automatizado ou Makefile:

```makefile
test:
	@agent-notify "🧪 Iniciando suíte de testes finais..."
	@pytest tests/ && agent-notify "🏆 Todos os testes passaram com sucesso!" || agent-notify "⚠️ Falha nos testes, verifique o terminal!"
```

Em scripts longos de compilação ou execução noturna:
```bash
#!/usr/bin/env bash
agent-notify "🚀 Job de migração iniciado..."
if ./run_migrations.sh; then
    agent-notify "✅ Migração finalizada com êxito!"
else
    # Pergunta o que fazer
    DECISAO=$(agent-ask "A migração falhou! Deseja executar rollback?" --options "Sim,Nao")
    if [ "$DECISAO" = "Sim" ]; then
        ./rollback.sh && agent-notify "🔄 Rollback efetuado."
    fi
fi
```
