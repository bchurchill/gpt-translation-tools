import unittest
from unittest.mock import Mock
from src.arabic_strings import ArabicStrings

class TestArabicStrings(unittest.TestCase):
    def setUp(self):
        self.arabic = ArabicStrings(Mock())

    def test_strip_diacriticals(self):
        original = "أَشْهَدُ"
        expected = "اشهد"
        actual = self.arabic.strip_diacritical(original)
        self.assertEqual(actual, expected)

    def test_substring_distance_exact(self):
        distance, index = self.arabic.substring_distance("abc", "abc")
        self.assertEqual(0, distance)
        self.assertEqual(0, index)

    def test_substring_distance_insert(self):
        distance, index = self.arabic.substring_distance("abc", "ab.c")
        self.assertEqual(1, distance)
        self.assertEqual(0, index)

    def test_substring_distance_deletion(self):
        distance, index = self.arabic.substring_distance("abc", "ac")
        self.assertEqual(1, distance)
        self.assertEqual(0, index)

    def test_substring_distance_change(self):
        distance, index = self.arabic.substring_distance("abc", "a.c")
        self.assertEqual(1, distance)
        self.assertEqual(0, index)

    def test_substring_distance_shift(self):
        distance, index = self.arabic.substring_distance("abc", ".abc")
        self.assertEqual(0, distance)
        self.assertEqual(1, index)

    def test_substring_distance_gpt1(self):
        distance, _ = self.arabic.substring_distance("abc", "abdecf")
        self.assertEqual(1, distance)

    def test_substring_distance_gpt2(self):
        distance, _ = self.arabic.substring_distance("cde", "abcdefgh")
        self.assertEqual(0, distance)

    def test_substring_distance_gpt3(self):
        distance, _ = self.arabic.substring_distance("a", "b")
        self.assertEqual(1, distance)

    def test_substring_distance_gpt4(self):
        distance, _ = self.arabic.substring_distance("aaab", "baab")
        self.assertEqual(1, distance)

    def test_substring_distance_gpt5(self):
        distance, _ = self.arabic.substring_distance("def", "dddddddefffffff")
        self.assertEqual(0, distance)

    def test_substring_distance_gpt6(self):
        distance, _ = self.arabic.substring_distance("mnop", "qrst")
        self.assertEqual(4, distance)



