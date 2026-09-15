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

---

## ⚙️ Diretrizes de Engenharia (Gaia OS & Recursos)
Desenvolvido com foco no **Gaia OS (Debian)** rodando em máquina host Gateway NV55C (Intel Core i7-640M, 6GB RAM, SSD Btrfs):
- **Pegada Zero na CPU**: O agente não consome ciclos ociosos; usa chamadas síncronas/assíncronas ultrarrápidas em Python puro (stdlib) ou Node.js leve.
- **Terminal First & Sem Fricção**: Operável 100% via linha de comando, sem dependência de interfaces gráficas.
- **Multimodalidade de Agentes**: Funciona tanto via protocolo **MCP (Model Context Protocol)** quanto via **Hooks nativos** e **CLI Wrappers**.

---

## 🏛️ Estrutura de Documentação do Projeto
A documentação completa do plano e arquitetura está detalhada em:
- 📑 [docs/ARQUITETURA.md](file:///home/francisco/Documentos/Projetos/BotTelegram/docs/ARQUITETURA.md): Desenho do sistema, fluxo de mensagens e barramento IPC.
- 📑 [docs/TELEGRAM_SETUP.md](file:///home/francisco/Documentos/Projetos/BotTelegram/docs/TELEGRAM_SETUP.md): Guia de criação do bot (BotFather vs. Telegram MTProto/Telefone).
- 📑 [docs/INTEGRACOES.md](file:///home/francisco/Documentos/Projetos/BotTelegram/docs/INTEGRACOES.md): Configuração detalhada para Antigravity, Gemini CLI, VS Code Copilot e Codex.
- 📑 [docs/PLANO_DE_EXECUCAO.md](file:///home/francisco/Documentos/Projetos/BotTelegram/docs/PLANO_DE_EXECUCAO.md): Roteiro fase a fase para a execução agêntica completa.

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
Mantido por Francisco no Gaia OS.
