PREFIX ?= $(HOME)/.local/bin
PROJECT_DIR := $(shell pwd)

.PHONY: all help install uninstall test smoke-test clean

help:
	@echo "TeleAgent Bridge - Comandos disponíveis:"
	@echo "  make install     - Instala os comandos 'agent-notify' e 'agent-ask' em $(PREFIX)"
	@echo "  make uninstall   - Remove os symlinks de $(PREFIX)"
	@echo "  make test        - Executa os testes unitários automatizados"
	@echo "  make smoke-test  - Envia uma mensagem real de teste para o Telegram"
	@echo "  make clean       - Limpa arquivos temporários de compilação Python"

install:
	@mkdir -p $(PREFIX)
	@ln -sf $(PROJECT_DIR)/bin/agent-notify $(PREFIX)/agent-notify
	@ln -sf $(PROJECT_DIR)/bin/agent-ask $(PREFIX)/agent-ask
	@chmod +x $(PREFIX)/agent-notify $(PREFIX)/agent-ask
	@echo "✅ Comandos instalados com sucesso em $(PREFIX)!"
	@echo "Certifique-se de que $(PREFIX) está no seu PATH (~/.bashrc ou ~/.profile)."

uninstall:
	@rm -f $(PREFIX)/agent-notify $(PREFIX)/agent-ask
	@echo "🗑️ Symlinks removidos de $(PREFIX)."

test:
	@python3 -m unittest discover -s tests -p "test_*.py" -v

smoke-test:
	@./bin/agent-notify "🚀 Smoke test executado pelo Makefile no Gaia OS!" --level success --title "MAKE SMOKE TEST"

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
