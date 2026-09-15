import unittest
from unittest.mock import MagicMock, patch

from bridge.telegram_client import TelegramClient, TelegramAPIError


class TestTelegramClient(unittest.TestCase):

    def setUp(self):
        self.client = TelegramClient(token="mock_token", chat_id="12345", hostname="TestHost")

    def test_format_html(self):
        formatted = self.client.format_html("Mensagem com <tag> e & símbolo", level="success", title="SUCESSO")
        self.assertIn("✅", formatted)
        self.assertIn("<b>SUCESSO</b>", formatted)
        self.assertIn("<code>[TestHost]</code>", formatted)
        # Verifica escape de HTML
        self.assertIn("&lt;tag&gt;", formatted)
        self.assertIn("&amp;", formatted)

    @patch("urllib.request.urlopen")
    def test_send_message_success(self, mock_urlopen):
        # Simula resposta bem sucedida da API do Telegram
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"ok": true, "result": {"message_id": 99}}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        res = self.client.send_message("Olá mundo", level="info")
        self.assertEqual(res.get("message_id"), 99)

    @patch("urllib.request.urlopen")
    def test_send_message_api_error(self, mock_urlopen):
        # Simula erro retornado pela API
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"ok": false, "description": "Chat not found"}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        with self.assertRaises(TelegramAPIError) as ctx:
            self.client.send_message("Teste")
        self.assertIn("Chat not found", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
