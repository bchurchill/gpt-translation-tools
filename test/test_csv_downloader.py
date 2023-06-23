import unittest
from unittest.mock import Mock
from src.csv_downloader import CsvDownloader

class TestCsvDownloader(unittest.TestCase):
    def test_substring_insertion(self):
        csvd = CsvDownloader(Mock(), Mock(), Mock())
        success, _, diff, alignment = csvd.validate_match("abcd", "abbcd", 1)
        self.assertTrue(success)
        self.assertEqual(1, diff)
        self.assertIn(alignment, [0,1])


    def test_validation_exact(self):
        csvd = CsvDownloader(Mock(), Mock(), Mock())
        success, _, diff, alignment = csvd.validate_match("Hello, world!", "Hello, world!", 2)
        self.assertTrue(success)
        self.assertEqual(0, diff)
        self.assertEqual(0, alignment)

    def test_validation_prefix(self):
        csvd = CsvDownloader(Mock(), Mock(), Mock())
        success, _, diff, alignment = csvd.validate_match("Hello, world!", "Hello, world!  Habibi I'm here.", 5)
        self.assertTrue(success)
        self.assertEqual(0, diff)
        self.assertEqual(0, alignment)

    def test_validation_offbyone(self):
        csvd = CsvDownloader(Mock(), Mock(), Mock())
        success, _, diff, alignment = csvd.validate_match("Hello, world!", "1Hello, world!  Habibi I'm here.", 5)
        self.assertTrue(success)
        self.assertEqual(0, diff)
        self.assertEqual(1, alignment)

    def test_validation_insertion(self):
        csvd = CsvDownloader(Mock(), Mock(), Mock())
        success, _, diff, alignment = csvd.validate_match("aabcddcba", "aabcdxyzdcba", 1)
        self.assertTrue(success)
        self.assertEqual(3, diff)
        self.assertIn(alignment, [0, 3])

    def test_validation_deletion(self):
        csvd = CsvDownloader(Mock(), Mock(), Mock())
        success, _, diff, alignment = csvd.validate_match("Hello, world!", "Hello world!  Habibi I'm here.", 5)
        self.assertTrue(success)

        self.assertEqual(1, diff)
        self.assertEqual(0, alignment)

    def test_validation_altered(self):
        csvd = CsvDownloader(Mock(), Mock(), Mock())
        success, _, diff, alignment = csvd.validate_match("Hello, world!", "Hello. world!  Habibi I'm here.", 5)
        self.assertTrue(success)
        self.assertEqual(1, diff)
        self.assertEqual(0, alignment)

    def test_validation_too_short(self):
        csvd = CsvDownloader(Mock(), Mock(), Mock())
        success, _, diff, alignment = csvd.validate_match("Hello, world!", "Hello world!", 2)
        self.assertFalse(success)

    def test_validation_elipses(self):
        csvd = CsvDownloader(Mock(), Mock(), Mock())
        success, _, diff, alignment = csvd.validate_match("Hello, ...", "Hello, world!  Habibi I'm here.", 5)
        self.assertTrue(success)
        self.assertEqual(0, diff)
        self.assertEqual(0, alignment)

    def test_validation_elipses_unicode(self):
        csvd = CsvDownloader(Mock(), Mock(), Mock())
        success, _, diff, alignment = csvd.validate_match("Hello, … goodnight I'm gone", "Hello, world!  Habibi I'm here.", 5)
        self.assertTrue(success)
        self.assertEqual(0, diff)
        self.assertEqual(0, alignment)

    def test_validation_elipses_offset(self):
        csvd = CsvDownloader(Mock(), Mock(), Mock())
        success, _, diff, alignment = csvd.validate_match("Hello, ...", "There's a lot going on, Hello, world!", 7)
        self.assertTrue(success)
        self.assertEqual(0, diff)
        self.assertEqual(24, alignment)

    def test_validate_strip_diacriticals(self):
        csvd = CsvDownloader(Mock(), Mock(), Mock())
        string = "جَعْدِي حَبْلِي من تمسّك به لن يضلّ في أزل الآزال لأنّ فيه هدايةً إلى نور الجمال"
        substring = "جعدی حبلی من تمسک به لن یضل فی ازل الازال لان فیه هدایه الی انوار الجما"
        success, _, diff, alignment = csvd.validate_match(substring, string, 20)
        self.assertTrue(success)
        self.assertEqual(2, diff) #one string has extra "al" in it
        self.assertEqual(0, alignment)

