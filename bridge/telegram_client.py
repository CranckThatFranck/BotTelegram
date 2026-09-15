"""
Cliente HTTP ultraleve para a Telegram Bot API.
Usa exclusivamente a standard library do Python (urllib.request) para
garantir consumo mínimo de recursos (CPU e RAM) no Gaia OS.
"""

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Union

from bridge.config import config


class TelegramAPIError(Exception):
    """Exceção levantada em falhas de comunicação com a API do Telegram."""
    pass


class TelegramClient:
    """Cliente para envio de mensagens, botões e polling leve de respostas."""

    LEVEL_ICONS = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "🚨",
        "milestone": "🏆",
        "question": "❓",
    }

    def __init__(
        self,
        token: Optional[str] = None,
        chat_id: Optional[Union[str, int]] = None,
        hostname: Optional[str] = None,
    ):
        self.token = (token or config.bot_token).strip()
        self.chat_id = str(chat_id or config.chat_id).strip()
        self.hostname = (hostname or config.hostname).strip()
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def _make_request(
        self,
        method: str,
        payload: Optional[Dict[str, Any]] = None,
        timeout: int = 15,
    ) -> Dict[str, Any]:
        """Executa uma requisição POST HTTPS para a API do Telegram."""
        if not self.token:
            raise TelegramAPIError("TELEGRAM_BOT_TOKEN não foi configurado.")

        url = f"{self.base_url}/{method}"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = json.dumps(payload or {}).encode("utf-8")

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                resp_body = response.read().decode("utf-8")
                result = json.loads(resp_body)
                if not result.get("ok"):
                    desc = result.get("description", "Erro desconhecido")
                    raise TelegramAPIError(f"Telegram API error: {desc}")
                return result.get("result", {})
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="ignore")
            try:
                err_json = json.loads(error_body)
                desc = err_json.get("description", str(e))
            except Exception:
                desc = f"{e} - {error_body}"
            raise TelegramAPIError(f"HTTP {e.code}: {desc}") from e
        except urllib.error.URLError as e:
            raise TelegramAPIError(f"Falha de rede/conexão: {e.reason}") from e

    def format_html(
        self,
        text: str,
        level: str = "info",
        title: Optional[str] = None,
    ) -> str:
        """Formata o texto em HTML com ícone, host e título estilizado."""
        icon = self.LEVEL_ICONS.get(level.lower(), "💬")
        header_title = title or level.upper()
        host_badge = f"<code>[{self.hostname}]</code>" if self.hostname else ""

        # Escapamento básico de HTML para segurança do corpo
        safe_text = (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        return f"{icon} <b>{header_title}</b> {host_badge}\n\n{safe_text}"

    def send_message(
        self,
        text: str,
        level: str = "info",
        title: Optional[str] = None,
        reply_markup: Optional[Dict[str, Any]] = None,
        parse_mode: str = "HTML",
    ) -> Dict[str, Any]:
        """Envia mensagem formatada para o chat autorizado."""
        if not self.chat_id:
            raise TelegramAPIError("TELEGRAM_CHAT_ID não foi configurado.")

        formatted_text = self.format_html(text, level=level, title=title) if parse_mode == "HTML" else text

        payload: Dict[str, Any] = {
            "chat_id": self.chat_id,
            "text": formatted_text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
        }

        if reply_markup:
            payload["reply_markup"] = reply_markup

        return self._make_request("sendMessage", payload)

    def edit_message_text(
        self,
        message_id: int,
        text: str,
        reply_markup: Optional[Dict[str, Any]] = None,
        parse_mode: str = "HTML",
    ) -> Dict[str, Any]:
        """Atualiza uma mensagem existente (útil para marcar perguntas respondidas)."""
        payload: Dict[str, Any] = {
            "chat_id": self.chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        if reply_markup is not None:
            payload["reply_markup"] = reply_markup
        return self._make_request("editMessageText", payload)

    def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Responde a um clique em botão inline para tirar o estado de carregando no Telegram."""
        payload: Dict[str, Any] = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        return self._make_request("answerCallbackQuery", payload)

    def get_updates(
        self,
        offset: Optional[int] = None,
        limit: int = 100,
        timeout: int = 0,
    ) -> List[Dict[str, Any]]:
        """Recupera atualizações via polling."""
        payload: Dict[str, Any] = {"limit": limit, "timeout": timeout}
        if offset is not None:
            payload["offset"] = offset
        result = self._make_request("getUpdates", payload, timeout=timeout + 5)
        return result if isinstance(result, list) else []
