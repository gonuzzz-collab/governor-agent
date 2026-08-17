import unittest

from governor_agent import __version__


class SmokeTest(unittest.TestCase):
    def test_package_is_importable(self) -> None:
        self.assertEqual(__version__, "0.1.0")


if __name__ == "__main__":
    unittest.main()
