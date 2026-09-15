#!/usr/bin/env python3
"""
Servidor MCP (Model Context Protocol) para o TeleAgent Bridge.
Permite que o Antigravity, GitHub Copilot (VS Code) e outros agentes de IA
acessem nativamente as ferramentas de notificação e perguntas no Telegram via stdio JSON-RPC.

Compatível com a especificação oficial do MCP (Model Context Protocol).
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Adiciona a raiz do projeto ao sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bridge.config import config
from bridge.interactive import ask_user_telegram, TelegramTimeoutError
from bridge.telegram_client import TelegramClient, TelegramAPIError


MCP_TOOLS = [
    {
        "name": "telegram_notify",
        "description": (
            "Envia uma notificação formatada para o Telegram do usuário (Francisco). "
            "Use para comunicar marcos do projeto, início/fim de testes, avisos de build "
            "ou conclusão de tarefas importantes."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Texto da notificação a ser enviada.",
                },
                "level": {
                    "type": "string",
                    "enum": ["info", "success", "warning", "error", "milestone"],
                    "default": "info",
                    "description": "Nível de prioridade e ícone visual da mensagem.",
                },
                "title": {
                    "type": "string",
                    "description": "Título opcional no cabeçalho do alerta.",
                },
            },
            "required": ["message"],
        },
    },
    {
        "name": "telegram_ask",
        "description": (
            "Faz uma pergunta interativa para o usuário no Telegram e aguarda sua resposta. "
            "Use quando surgir uma dúvida arquitetural, necessidade de aprovação ou orientação "
            "do usuário para prosseguir com o trabalho (Human-in-the-Loop)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "A dúvida ou questão para o usuário responder.",
                },
                "options": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Lista opcional de opções que serão exibidas como botões de clique rápido no Telegram.",
                },
                "timeout_seconds": {
                    "type": "integer",
                    "default": 300,
                    "description": "Tempo limite em segundos para esperar a resposta no Telegram.",
                },
                "title": {
                    "type": "string",
                    "default": "DÚVIDA DO AGENTE",
                    "description": "Título exibido no Telegram.",
                },
            },
            "required": ["question"],
        },
    },
]


def send_response(response: Dict[str, Any]):
    """Escreve a resposta JSON-RPC formatada no stdout."""
    payload = json.dumps(response, ensure_ascii=False)
    sys.stdout.write(f"{payload}\n")
    sys.stdout.flush()


def handle_call_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Executa a ferramenta solicitada e retorna o resultado formatado."""
    if tool_name == "telegram_notify":
        msg = args.get("message", "")
        lvl = args.get("level", "info")
        title = args.get("title")

        client = TelegramClient()
        client.send_message(text=msg, level=lvl, title=title)
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Notificação Telegram ({lvl}) enviada com sucesso ao usuário.",
                }
            ],
            "isError": False,
        }

    elif tool_name == "telegram_ask":
        question = args.get("question", "")
        options = args.get("options")
        timeout = args.get("timeout_seconds", 300)
        title = args.get("title", "DÚVIDA DO AGENTE")

        answer = ask_user_telegram(
            question=question,
            options=options,
            timeout=timeout,
            title=title,
        )
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Resposta recebida do usuário no Telegram: {answer}",
                }
            ],
            "isError": False,
        }

    else:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Ferramenta desconhecida: {tool_name}",
                }
            ],
            "isError": True,
        }


def run_mcp_server():
    """Loop principal de leitura e tratamento de requisições JSON-RPC via stdio."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except Exception as e:
            send_response(
                {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {str(e)}"},
                }
            )
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        # 1. Handshake de inicialização
        if method == "initialize":
            send_response(
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": False},
                        },
                        "serverInfo": {
                            "name": "teleagent-bridge",
                            "version": "1.0.0",
                        },
                    },
                }
            )
        elif method == "notifications/initialized":
            # Apenas acknowledge assíncrono do cliente, sem resposta
            pass
        elif method == "ping":
            send_response({"jsonrpc": "2.0", "id": req_id, "result": {}})

        # 2. Listagem de ferramentas
        elif method == "tools/list":
            send_response(
                {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": MCP_TOOLS},
                }
            )

        # 3. Invocação de ferramentas
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})

            try:
                result = handle_call_tool(tool_name, tool_args)
                send_response(
                    {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": result,
                    }
                )
            except TelegramTimeoutError as e:
                send_response(
                    {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [{"type": "text", "text": str(e)}],
                            "isError": True,
                        },
                    }
                )
            except Exception as e:
                send_response(
                    {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Erro na execução da ferramenta: {str(e)}",
                                }
                            ],
                            "isError": True,
                        },
                    }
                )

        else:
            if req_id is not None:
                send_response(
                    {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {
                            "code": -32601,
                            "message": f"Método não encontrado: {method}",
                        },
                    }
                )


if __name__ == "__main__":
    run_mcp_server()
