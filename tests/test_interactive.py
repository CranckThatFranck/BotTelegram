import unittest
from bridge.interactive import build_inline_keyboard


class TestInteractive(unittest.TestCase):

    def test_build_inline_keyboard_rows(self):
        options = ["Opção 1", "Opção 2", "Opção 3"]
        markup, mapping = build_inline_keyboard(options)

        self.assertIn("inline_keyboard", markup)
        kb = markup["inline_keyboard"]

        # Primeira linha deve ter 2 botões, segunda deve ter 1
        self.assertEqual(len(kb), 2)
        self.assertEqual(len(kb[0]), 2)
        self.assertEqual(len(kb[1]), 1)

        # Valida mapeamento de chaves
        self.assertEqual(mapping["opt_0"], "Opção 1")
        self.assertEqual(mapping["opt_1"], "Opção 2")
        self.assertEqual(mapping["opt_2"], "Opção 3")

    def test_build_inline_keyboard_empty(self):
        markup, mapping = build_inline_keyboard([])
        self.assertEqual(markup["inline_keyboard"], [])
        self.assertEqual(mapping, {})


if __name__ == "__main__":
    unittest.main()
