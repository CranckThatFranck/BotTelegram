"""
Gerenciador de configurações e variáveis de ambiente do TeleAgent Bridge.
Lê arquivos .env de forma nativa (sem bibliotecas de terceiros) para máxima
eficiência e portabilidade no Gaia OS.
"""

import os
import socket
from pathlib import Path
from typing import Optional, Dict


def load_env_file(filepath: Path) -> Dict[str, str]:
    """Carrega pares chave-valor de um arquivo .env se existir."""
    env_vars = {}
    if not filepath.is_file():
        return env_vars

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip()
                    # Remove aspas simples ou duplas envolventes
                    if (val.startswith('"') and val.endswith('"')) or (
                        val.startswith("'") and val.endswith("'")
                    ):
                        val = val[1:-1]
                    env_vars[key] = val
    except Exception:
        pass
    return env_vars


def find_and_load_config() -> Dict[str, str]:
    """
    Busca por arquivos .env nos locais padrões:
    1. Diretório raiz do projeto BotTelegram
    2. Diretório de trabalho atual (CWD)
    3. ~/.config/teleagent/.env
    Variáveis pré-existentes em os.environ têm precedência.
    """
    project_root = Path(__file__).resolve().parent.parent
    candidate_paths = [
        project_root / ".env",
        Path.cwd() / ".env",
        Path.home() / ".config" / "teleagent" / ".env",
    ]

    loaded_vars: Dict[str, str] = {}
    for path in candidate_paths:
        if path.is_file():
            file_vars = load_env_file(path)
            for k, v in file_vars.items():
                if k not in loaded_vars:
                    loaded_vars[k] = v

    # Injeta no os.environ se ainda não estiver definido
    for k, v in loaded_vars.items():
        if k not in os.environ:
            os.environ[k] = v

    return loaded_vars


class Config:
    """Configurações centralizadas do bot."""

    def __init__(self):
        find_and_load_config()

        self.bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        self.chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        self.hostname: str = os.getenv(
            "TELEGRAM_BOT_HOSTNAME", socket.gethostname() or "Gaia-Host"
        ).strip()
        
        try:
            self.ask_timeout: int = int(os.getenv("TELEGRAM_ASK_TIMEOUT", "300"))
        except ValueError:
            self.ask_timeout = 300

    @property
    def is_configured(self) -> bool:
        """Verifica se as credenciais obrigatórias estão presentes."""
        return bool(
            self.bot_token
            and self.chat_id
            and not self.bot_token.startswith("1234567890:")  # placeholder check
        )

    def validate_or_raise(self):
        """Gera exceção caso a configuração esteja incompleta."""
        if not self.bot_token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN não configurado! Configure no arquivo .env ou como variável de ambiente."
            )
        if not self.chat_id:
            raise ValueError(
                "TELEGRAM_CHAT_ID não configurado! Configure no arquivo .env ou como variável de ambiente."
            )
        if self.bot_token.startswith("1234567890:"):
            raise ValueError(
                "TELEGRAM_BOT_TOKEN parece ser o valor de exemplo. Substitua pelo token real do @BotFather no .env."
            )


# Instância global reutilizável
config = Config()
