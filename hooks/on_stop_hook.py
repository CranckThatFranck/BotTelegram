#!/usr/bin/env python3
"""
Hook de término de execução do Antigravity (Evento 'Stop').
Intercepta a finalização do loop do agente e avisa o usuário no Telegram:
- Se concluiu com sucesso
- Se parou por erro ou estouro de passos
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
    # Lê payload enviado pelo Antigravity na stdin
    input_data = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                input_data = json.loads(raw)
    except Exception:
        pass

    term_reason = input_data.get("terminationReason", "model_stop")
    error_msg = input_data.get("error", "")
    workspace_list = input_data.get("workspacePaths", [])
    workspace_name = Path(workspace_list[0]).name if workspace_list else "Workspace"

    try:
        if config.is_configured:
            client = TelegramClient()
            if error_msg or term_reason in ["error", "max_steps_exceeded"]:
                motivo = f"Erro: {error_msg}" if error_msg else f"Motivo: {term_reason}"
                client.send_message(
                    text=f"O agente parou no projeto <b>{workspace_name}</b>.\n{motivo}",
                    level="warning",
                    title="AGENTE PAUSADO / ERRO",
                )
            else:
                client.send_message(
                    text=f"O agente concluiu sua execução no projeto <b>{workspace_name}</b>.",
                    level="success",
                    title="TAREFA CONCLUÍDA",
                )
    except Exception:
        pass

    # Resposta exigida pelo contrato do Antigravity (Stop: JSON válido)
    sys.stdout.write(json.dumps({}) + "\n")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
