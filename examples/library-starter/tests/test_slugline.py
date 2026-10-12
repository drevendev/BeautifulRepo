"""Exercise the exact public API promised by the starter README."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from slugline import slugline


class SluglineTests(unittest.TestCase):
    def test_documented_first_success(self):
        self.assertEqual(slugline("Hello, Library 101!"), "hello-library-101")

    def test_normalization(self):
        self.assertEqual(slugline("  One---Two__3  "), "one-two-3")

    def test_invalid_input(self):
        for invalid in ("", "!!!", "café"):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                slugline(invalid)
        with self.assertRaises(TypeError):
            slugline(None)


if __name__ == "__main__":
    unittest.main()
