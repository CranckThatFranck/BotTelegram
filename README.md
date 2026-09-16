# TeleAgent Bridge 🤖📡
> **Ponte de Notificação e Interação Telegram para Agentes de IA e CLI**  
> *Gemini CLI | Antigravity | GitHub Copilot (VS Code) | Codex | Shell Scripts*

---

## 🎯 Objetivo
O **TeleAgent Bridge** é uma infraestrutura de comunicação leve, minimalista e de alta performance criada para permitir que agentes autônomos e assistentes de desenvolvimento mantenham você informado pelo Telegram sobre:
1. **Dúvidas & Human-in-the-Loop**: Quando a IA precisa de orientação, confirmação ou escolha de rumo (com botões interativos ou resposta em texto no Telegram).
2. **Marcos Críticos (Milestones)**: Início de suítes de testes, refatorações pesadas, compilações longas.
3. **Conclusão de Tarefas**: Notificação imediata de conclusão com sumário de alterações e status.
4. **Erros e Bloqueios**: Alerta de falha em comandos ou gargalos operacionais.

> [!IMPORTANT]
> ⚠️ **DIRETRIZ DE COMUNICAÇÃO VIA TELEGRAM**  
> É recomendado que **TODOS** os agentes de inteligência artificial (incluindo Gemini CLI, Antigravity, VS Code GitHub Copilot e Codex) utilizem esta ferramenta para notificar o usuário e interagir com ele pelo Telegram. O não cumprimento desta diretriz quebra o fluxo de supervisão em tempo real e monitoramento.

---

## ⚙️ Diretrizes de Engenharia & Compatibilidade
Desenvolvido para ser leve, rápido e compatível com sistemas Unix-like (como Linux e macOS):
- **Baixo Consumo de CPU**: O agente não consome ciclos ociosos; usa chamadas síncronas/assíncronas ultrarrápidas em Python puro (stdlib) ou Node.js leve.
- **Terminal First & Sem Fricção**: Operável 100% via linha de comando, sem dependência de interfaces gráficas.
- **Multimodalidade de Agentes**: Funciona tanto via protocolo **MCP (Model Context Protocol)** quanto via **Hooks nativos** e **CLI Wrappers**.

---

## 🏛️ Estrutura de Documentação do Projeto
A documentação completa do plano e arquitetura está detalhada em:
- 📑 [docs/ARQUITETURA.md](docs/ARQUITETURA.md): Desenho do sistema, fluxo de mensagens e barramento IPC.
- 📑 [docs/TELEGRAM_SETUP.md](docs/TELEGRAM_SETUP.md): Guia de criação do bot (BotFather vs. Telegram MTProto/Telefone).
- 📑 [docs/INTEGRACOES.md](docs/INTEGRACOES.md): Configuração detalhada para Antigravity, Gemini CLI, VS Code Copilot e Codex.
- 📑 [docs/PLANO_DE_EXECUCAO.md](docs/PLANO_DE_EXECUCAO.md): Roteiro fase a fase para a execução agêntica completa.

---

## 🚀 Componentes Principais
```
                     +---------------------------------------+
                     |         Agentes & Ferramentas         |
                     |  (Antigravity, Gemini, Copilot, etc.) |
                     +-------------------+-------------------+
                                         |
               +-------------------------+-------------------------+
               | (MCP Protocol)          | (CLI / Scripts)         | (Lifecycle Hooks)
               v                         v                         v
        +--------------+          +--------------+          +--------------+
        |  tele-mcp    |          | agent-notify |          | hooks.json   |
        |  (Stdio/JSON)|          |  / agent-ask |          |  integrator  |
        +-------+------+          +-------+------+          +-------+------+
                |                         |                         |
                +-------------------------+-------------------------+
                                         |
                                         v
                         +-------------------------------+
                         |   TeleAgent Daemon / Core     |
                         |   (Python Stdlib HTTP Client) |
                         +---------------+---------------+
                                         |  Telegram Bot API (HTTPS)
                                         v
                         +-------------------------------+
                         |       Telegram Messenger      |
                         |   (Seu Celular / Desktop)     |
                         +-------------------------------+
```

---

## 📄 Licença e Manutenção
Projeto de código aberto para a comunidade de IA autônoma.
