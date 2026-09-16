"""
Módulo de interação bidirecional (Human-in-the-loop).
Permite que agentes autônomos façam perguntas para o usuário no Telegram,
exibam botões de clique rápido (inline keyboard) e recebam a resposta de volta
para orientar a tomada de decisão.
"""

import time
from typing import Dict, List, Optional, Tuple, Union

from bridge.config import config
from bridge.telegram_client import TelegramClient, TelegramAPIError


class TelegramTimeoutError(Exception):
    """Exceção levantada quando o usuário não responde dentro do tempo limite."""
    pass


def build_inline_keyboard(options: List[str]) -> Tuple[Dict, Dict[str, str]]:
    """
    Constrói a estrutura de InlineKeyboardMarkup e um mapa de callback_data para valor real.
    Garante que o callback_data respeite o limite de 64 bytes da Telegram API.
    """
    keyboard = []
    callback_map = {}

    row = []
    for idx, opt in enumerate(options):
        clean_opt = opt.strip()
        cb_key = f"opt_{idx}"
        callback_map[cb_key] = clean_opt

        btn = {"text": clean_opt, "callback_data": cb_key}
        row.append(btn)

        # Quebra em no máximo 2 botões por linha para melhor legibilidade no celular
        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    return {"inline_keyboard": keyboard}, callback_map


def ask_user_telegram(
    question: str,
    options: Optional[List[str]] = None,
    timeout: Optional[int] = None,
    title: str = "DÚVIDA DO AGENTE",
    client: Optional[TelegramClient] = None,
) -> str:
    """
    Envia uma pergunta para o Telegram e aguarda a resposta (via botão inline ou mensagem de texto).
    Retorna o texto da opção selecionada ou da mensagem enviada pelo usuário.
    """
    tg = client or TelegramClient()
    timeout_sec = timeout if timeout is not None else config.ask_timeout

    # 1. Consome e descarta updates anteriores para evitar ler mensagens antigas
    latest_offset = None
    try:
        pending_updates = tg.get_updates(offset=None, limit=100, timeout=0)
        if pending_updates:
            latest_offset = pending_updates[-1]["update_id"] + 1
    except Exception:
        pass

    # 2. Prepara botões se houver opções
    reply_markup = None
    callback_map: Dict[str, str] = {}
    if options:
        reply_markup, callback_map = build_inline_keyboard(options)

    # 3. Envia a mensagem da pergunta
    sent_msg = tg.send_message(
        text=question,
        level="question",
        title=title,
        reply_markup=reply_markup,
    )
    sent_msg_id = sent_msg.get("message_id")
    if not sent_msg_id:
        raise TelegramAPIError("Não foi possível obter o ID da mensagem enviada.")

    start_time = time.time()
    current_offset = latest_offset

    # 4. Loop de polling leve até obter resposta ou estourar timeout
    while time.time() - start_time < timeout_sec:
        try:
            updates = tg.get_updates(offset=current_offset, timeout=3)
        except Exception:
            time.sleep(1)
            continue

        for up in updates:
            current_offset = up["update_id"] + 1

            # Caso A: Usuário clicou em um botão inline (Callback Query)
            if "callback_query" in up:
                cb = up["callback_query"]
                user_id = str(cb.get("from", {}).get("id", ""))
                msg_target_id = cb.get("message", {}).get("message_id")

                # Valida que veio do chat do usuário e refere-se a esta pergunta
                if user_id == str(tg.chat_id) and msg_target_id == sent_msg_id:
                    cb_data = cb.get("data", "")
                    selected_val = callback_map.get(cb_data, cb_data)
                    cb_id = cb.get("id")

                    if cb_id:
                        try:
                            tg.answer_callback_query(
                                cb_id, text=f"Opção registrada: {selected_val}"
                            )
                        except Exception:
                            pass

                    # Atualiza a mensagem no Telegram marcando como respondida e retirando os botões
                    edited_text = (
                        f"{tg.format_html(question, level='question', title=title)}\n\n"
                        f"👉 <b>Respondido:</b> <code>{selected_val}</code>"
                    )
                    try:
                        tg.edit_message_text(sent_msg_id, edited_text, reply_markup=None)
                    except Exception:
                        pass

                    return selected_val

            # Caso B: Usuário respondeu digitando uma mensagem de texto no chat
            if "message" in up:
                msg = up["message"]
                user_id = str(msg.get("from", {}).get("id", ""))
                text_content = msg.get("text", "").strip()

                if user_id == str(tg.chat_id) and text_content:
                    # Atualiza a pergunta original marcando a resposta recebida
                    edited_text = (
                        f"{tg.format_html(question, level='question', title=title)}\n\n"
                        f"👉 <b>Resposta digitada:</b> <code>{text_content}</code>"
                    )
                    try:
                        tg.edit_message_text(sent_msg_id, edited_text, reply_markup=None)
                    except Exception:
                        pass

                    return text_content

        time.sleep(0.5)

    # 5. Se o tempo estourou
    timeout_text = (
        f"{tg.format_html(question, level='question', title=title)}\n\n"
        f"⏰ <i>Tempo limite de resposta esgotado ({timeout_sec}s).</i>"
    )
    try:
        tg.edit_message_text(sent_msg_id, timeout_text, reply_markup=None)
    except Exception:
        pass

    raise TelegramTimeoutError(
        f"Tempo limite ({timeout_sec}s) esgotado aguardando resposta do usuário no Telegram."
    )
