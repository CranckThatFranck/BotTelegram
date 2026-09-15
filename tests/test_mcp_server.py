import unittest
from bridge.mcp_server import MCP_TOOLS, handle_call_tool


class TestMCPServer(unittest.TestCase):

    def test_tools_list_schema(self):
        tool_names = [t["name"] for t in MCP_TOOLS]
        self.assertIn("telegram_notify", tool_names)
        self.assertIn("telegram_ask", tool_names)

        notify_tool = next(t for t in MCP_TOOLS if t["name"] == "telegram_notify")
        self.assertIn("message", notify_tool["inputSchema"]["required"])

        ask_tool = next(t for t in MCP_TOOLS if t["name"] == "telegram_ask")
        self.assertIn("question", ask_tool["inputSchema"]["required"])

    def test_unknown_tool_call(self):
        res = handle_call_tool("tool_inexistente", {})
        self.assertTrue(res["isError"])
        self.assertIn("Ferramenta desconhecida", res["content"][0]["text"])


if __name__ == "__main__":
    unittest.main()
