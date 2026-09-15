#!/usr/bin/env python3
"""
Hook pós-ferramenta do Antigravity (Evento 'PostToolUse').
Dispara um alerta no Telegram quando um comando crítico executado pelo agente falha.
"""

import json
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bridge.config import config
from bridge.telegram_client import TelegramClient


def main():
    input_data = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                input_data = json.loads(raw)
    except Exception:
        pass

    tool_error = input_data.get("error")
    # Só notifica se a ferramenta retornou erro
    if tool_error:
        tool_call = input_data.get("toolCall", {})
        tool_name = tool_call.get("name", "ferramenta")
        command_str = tool_call.get("args", {}).get("CommandLine", "")

        try:
            if config.is_configured:
                client = TelegramClient()
                msg = f"Falha na ferramenta <code>{tool_name}</code>\n"
                if command_str:
                    msg += f"<b>Comando:</b> <code>{command_str[:150]}</code>\n"
                msg += f"<b>Erro:</b> <code>{str(tool_error)[:200]}</code>"

                client.send_message(
                    text=msg,
                    level="error",
                    title="ALERTA DE FALHA EM COMANDO",
                )
        except Exception:
            pass

    # PostToolUse exige um objeto JSON vazio no stdout
    sys.stdout.write(json.dumps({}) + "\n")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
