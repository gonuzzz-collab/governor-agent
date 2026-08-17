import unittest

from src.config.service import normalize_key


class ConfigurationServiceTest(unittest.TestCase):
    def test_normalize_key(self) -> None:
        self.assertEqual(normalize_key("  User Theme "), "user-theme")


if __name__ == "__main__":
    unittest.main()
