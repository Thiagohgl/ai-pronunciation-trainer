import string
import unittest
from utilsFileIO import generateRandomString


class TestUtilsFileIO(unittest.TestCase):
    def test_generate_random_string_default_length(self):
        random_string = generateRandomString()
        self.assertEqual(len(random_string), 20)
        self.assertTrue(all(c in string.ascii_lowercase for c in random_string))

    def test_generate_random_string_custom_length(self):
        random_string = generateRandomString(10)
        self.assertEqual(len(random_string), 10)
        self.assertTrue(all(c in string.ascii_lowercase for c in random_string))

    def test_generate_random_string_zero_length(self):
        random_string = generateRandomString(0)
        self.assertEqual(len(random_string), 0)

    def test_generate_random_string_negative_length(self):
        random_string = generateRandomString(-5)
        self.assertEqual(len(random_string), 0)


if __name__ == '__main__':
    unittest.main()