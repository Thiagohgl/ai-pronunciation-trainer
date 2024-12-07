import unittest

from aip_trainer import WordMetrics


words_real = 'Ich habe sehr viel glück, am leben und gesund zu sein'
words_transcribed = 'Ic hab zeh viel guck am und gesund tu sein'


class TestWordMetrics(unittest.TestCase):
    def test_edit_distance_python(self):
        output = WordMetrics.edit_distance_python(words_real, words_transcribed)
        self.assertEqual(output, int(14))

    def test_edit_distance_python_same(self):
        output = WordMetrics.edit_distance_python(words_real, words_real)
        self.assertEqual(output, int(0))
    
    def test_edit_distance_python_empty(self):
        output = WordMetrics.edit_distance_python("", "")
        self.assertEqual(output, int(0))
        output = WordMetrics.edit_distance_python(words_real, "")
        self.assertEqual(output, int(53))
        output = WordMetrics.edit_distance_python("", words_real)
        self.assertEqual(output, int(53))

    def test_edit_distance_python_not_printable_characters(self):
        output = WordMetrics.edit_distance_python("Ich bin Alex\t a\0b! Hallo.", "Ich bi\tn Tom a\nc... Hallo")
        self.assertEqual(output, int(12))

    def test_edit_distance_python_survived(self):
        # These tests are added based on the mutation test results to ensure the function is robust

        # Test case where mutation survived for ReplaceBinaryOperator_Add_Mul
        output = WordMetrics.edit_distance_python("Ich habe", "Ich habe sehr")
        self.assertEqual(output, int(5))

        # Test case where mutation survived for ReplaceBinaryOperator_Add_Div
        output = WordMetrics.edit_distance_python("Ich habe", "Ich habe sehr viel")
        self.assertEqual(output, int(10))

        # Test case where mutation survived for ReplaceBinaryOperator_Add_FloorDiv
        output = WordMetrics.edit_distance_python("Ich habe", "Ich habe sehr viel glück")
        self.assertEqual(output, int(16))

        # Test case where mutation survived for ReplaceBinaryOperator_Add_Pow
        output = WordMetrics.edit_distance_python("Ich habe", "Ich habe sehr viel glück, am")
        self.assertEqual(output, int(20))

        # Test case where mutation survived for ReplaceBinaryOperator_Sub_Mod
        output = WordMetrics.edit_distance_python("Ich habe", "Ich habe sehr viel glück, am leben")
        self.assertEqual(output, int(26))

        # Test case where mutation survived for ReplaceBinaryOperator_Sub_RShift
        output = WordMetrics.edit_distance_python("Ich habe", "Ich habe sehr viel glück, am leben und")
        self.assertEqual(output, int(30))

        # Test case where mutation survived for ReplaceBinaryOperator_Sub_LShift
        output = WordMetrics.edit_distance_python("Ich habe", "Ich habe sehr viel glück, am leben und gesund")
        self.assertEqual(output, int(37))

        # Test case where mutation survived for ReplaceBinaryOperator_Sub_BitAnd
        output = WordMetrics.edit_distance_python("Ich habe", "Ich habe sehr viel glück, am leben und gesund zu")
        self.assertEqual(output, int(40))

        # Test case where mutation survived for ReplaceBinaryOperator_Sub_BitXor
        output = WordMetrics.edit_distance_python("Ich habe", "Ich habe sehr viel glück, am leben und gesund zu sein")
        self.assertEqual(output, int(45))

if __name__ == '__main__':
    unittest.main()
