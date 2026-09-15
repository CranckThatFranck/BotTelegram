# Configuração do Telegram - TeleAgent Bridge 📱

## 1. Escolha da Abordagem: BotFather vs. Conta com Telefone

Você mencionou que possui um **número de telefone sobressalente**. Vamos avaliar os dois caminhos técnicos:

| Critério | Opção A: Bot Oficial (@BotFather) ⭐️ *(Recomendado)* | Opção B: Conta de Usuário (MTProto / Telethon) |
| :--- | :--- | :--- |
| **Consumo de Recursos** | Mínimo (chamadas REST HTTPS via `curl`/`urllib`) | Médio/Alto (daemon MTProto permanente com SQLite) |
| **Risco de Bloqueio** | Zero (API oficial do Telegram para bots) | Risco de flag de automação por spam da conta |
| **Botões Interativos** | Nativo (`InlineKeyboardMarkup` para clicar e responder) | Não suportado para mensagens de usuário |
| **Complexidade** | Simples: apenas `TOKEN` e `CHAT_ID` | Exige API_ID, API_HASH, login SMS e sessão |
| **Uso do Telefone Extra** | Pode ser usado para criar uma conta do Telegram dedicada para receber os alertas, separando da sua conta pessoal | O número é usado diretamente pelo bot |

> [!TIP]
> **Recomendação Técnica**: Use a **Opção A (BotFather)**.  
> Você pode usar o seu número de telefone extra para registrar uma conta no Telegram no seu celular/desktop dedicada exclusivamente ao seu laboratório de agentes, e o bot enviará as mensagens para ela!

---

## 2. Passo a Passo para Criar o Bot Oficial no Telegram

### Passo 1: Falar com o @BotFather
1. No seu aplicativo Telegram, procure por **`@BotFather`** (verifique o selo de verificado).
2. Envie o comando:
   ```text
   /newbot
   ```
3. Escolha um nome de exibição para o bot (exemplo: `Juca Agent Alerter` ou `DevOps Notify`).
4. Escolha um username único que termine em `bot` (exemplo: `francisco_devops_bot` ou `juca_agent_bot`).
5. O BotFather fornecerá um **HTTP API Token**, no formato:
   ```text
   1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ_1234567
   ```
6. **Guarde esse token com segurança.**

---

### Passo 2: Obter o seu `CHAT_ID`
O bot só pode enviar mensagens para você após você iniciar uma conversa com ele.

1. Abra a conversa com o seu bot recém-criado no Telegram e clique em **Começar** (ou envie `/start`).
2. Para descobrir o seu identificador numérico (`CHAT_ID`), use um destes dois métodos rápidos:

#### Método A (Via terminal cURL - Sem sair da linha de comando):
Substitua `<SEU_TOKEN>` pelo token do seu bot e rode:
```bash
curl -s https://api.telegram.org/bot<SEU_TOKEN>/getUpdates | jq .
```
No JSON retornado, localize o campo `"id"` dentro de `"from"` ou `"chat"`:
```json
"chat": {
  "id": 987654321,
  "first_name": "Francisco",
  "type": "private"
}
```

#### Método B (Via Bot auxiliar no Telegram):
Envie uma mensagem para o bot **`@userinfobot`** no Telegram. Ele responderá imediatamente com o seu ID numérico (ex: `987654321`).

---

### Passo 3: Configurar o arquivo `.env` do Projeto
No diretório raiz do projeto:
```bash
cd /home/francisco/Documentos/Projetos/BotTelegram
cp .env.example .env
chmod 600 .env
```

Edite o `.env` com suas credenciais:
```ini
TELEGRAM_BOT_TOKEN="1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ_1234567"
TELEGRAM_CHAT_ID="987654321"
```

---

### Passo 4: Teste Imediato de Conexão (Smoke Test)
Você pode validar o envio com uma única linha no terminal:
```bash
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
     -d "chat_id=${TELEGRAM_CHAT_ID}" \
     -d "text=🚀 Conexão estabelecida com sucesso pelo TeleAgent Bridge!"
```
Se a mensagem chegar no seu celular, a ponte está pronta para ser conectada aos agentes!
