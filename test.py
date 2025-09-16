# test_setup.py

import unittest

class TestSetup(unittest.TestCase):
    def test_addition(self):
        # A simple test to check if 2 + 2 equals 4
        self.assertEqual(2 + 2, 4)

if __name__ == "__main__":
    unittest.main()