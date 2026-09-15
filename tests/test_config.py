import os
import tempfile
import unittest
from pathlib import Path

from bridge.config import Config, load_env_file


class TestConfig(unittest.TestCase):

    def test_load_env_file(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as tf:
            tf.write("# Comentário\n")
            tf.write("KEY_A=valor_a\n")
            tf.write('KEY_B="valor com aspas"\n')
            tf.write("KEY_C='valor simples'\n")
            tf.flush()
            tmp_path = Path(tf.name)

        try:
            vars_loaded = load_env_file(tmp_path)
            self.assertEqual(vars_loaded["KEY_A"], "valor_a")
            self.assertEqual(vars_loaded["KEY_B"], "valor com aspas")
            self.assertEqual(vars_loaded["KEY_C"], "valor simples")
        finally:
            tmp_path.unlink()

    def test_validation_missing_token(self):
        cfg = Config()
        cfg.bot_token = ""
        with self.assertRaises(ValueError):
            cfg.validate_or_raise()


if __name__ == "__main__":
    unittest.main()
