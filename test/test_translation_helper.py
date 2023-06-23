import unittest
from unittest.mock import MagicMock, patch
from src.translation_helper import TranslationHelper

class TestTranslationHelper(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.logger = MagicMock()
        self.logger.fatal_error.side_effect = Exception("fatal error")
        self.args = MagicMock()
        self.args.model = "math"

    def read_mock_data(self, filename):
        file_data = {
            'examples_in': 'example1\nexample2\nexample3\n',
            'examples_out': 'translation1\ntranslation2\ntranslation3\n',
            'examples_embeddings': '[1.0, 0.0, 0.0]\n[0.0, 1.0, 0.0]\n[0.0, 0.0, 1.0]\n',
            'wordlist': '["word1", ["translation1","translation2"]]\n["word2", ["translation3", "translation4"], "example comment"]\n'
        }
        return file_data[filename]

    def create_open_mock(self, filename, mode):
        file_mock = MagicMock()
        file_mock.readlines.return_value = self.read_mock_data(filename).split("\n")
        file_mock.read.return_value = self.read_mock_data(filename)

        enter_mock = MagicMock()
        enter_mock.__enter__.return_value = file_mock
        return enter_mock


    @patch('builtins.open', new_callable=MagicMock)
    def test_initialize_examples(self, mock_open):
        mock_open.side_effect = self.create_open_mock

        self.args.examples_in = "examples_in"
        self.args.examples_out = "examples_out"
        self.args.examples_embeddings = "examples_embeddings"

        th = TranslationHelper(self.args, self.logger)
        self.assertEqual(len(th.examples_in), 3)
        self.assertEqual(len(th.examples_out), 3)
        self.assertEqual(len(th.examples_embeddings), 3)

    @patch('builtins.open', new_callable=MagicMock)
    def test_initialize_wordlist(self, mock_open):
        mock_open.side_effect = self.create_open_mock

        self.args.wordlist = "wordlist"

        th = TranslationHelper(self.args, self.logger)
        self.assertEqual(len(th.wordlist), 2)

    def test_get_wordcount(self):
        text = "This is an example sentence."

        th = TranslationHelper(self.args, self.logger)
        wordcount = th.get_wordcount(text)

        self.assertEqual(wordcount, 5)

    @patch('builtins.open', new_callable=MagicMock)
    @patch('src.translation_helper.Embeddings.query')
    async def test_get_nearest_example(self, mock_query, mock_open):
        mock_open.side_effect = self.create_open_mock
        mock_query.return_value = [0.9, 0.1, 0.1]

        self.args.examples_in = "examples_in"
        self.args.examples_out = "examples_out"
        self.args.examples_embeddings = "examples_embeddings"

        th = TranslationHelper(self.args, self.logger)
        example_in, example_out = await th.get_nearest_example("dummy text")

        self.assertEqual(example_in, "example1")
        self.assertEqual(example_out, "translation1")

    def test_id_to_author(self):
        th = TranslationHelper(self.args, self.logger)

        self.assertEqual(th.id_to_author("BH123"), "by Bahá’u’lláh")
        self.assertEqual(th.id_to_author("AB123"), "by `Abdu’l-Bahá")
        self.assertEqual(th.id_to_author("UNKNOWN"), "from the Baha’i Writings")

    @patch('builtins.open', new_callable=MagicMock)
    def test_get_wordlist(self, mock_open):
        mock_open.side_effect = self.create_open_mock

        self.args.wordlist = "wordlist"

        th = TranslationHelper(self.args, self.logger)
        wordlist_result = th.get_wordlist("This text contains word1 and word2.")

        expected_result = "Prefer using the following translations.\nword1 => translation1; translation2\nword2 => translation3; translation4  (NOTE: example comment)\n"
        self.assertEqual(wordlist_result, expected_result)

    @patch('src.translation_helper.Embeddings.query')
    @patch('builtins.open', new_callable=MagicMock)
    async def test_get_variables(self, mock_open, mock_query):
        mock_open.side_effect = self.create_open_mock
        mock_query.return_value = [0.1, 0.7, 0.2]

        self.args.examples_in = "examples_in"
        self.args.examples_out = "examples_out"
        self.args.examples_embeddings = "examples_embeddings"
        self.args.wordlist = "wordlist"

        th = TranslationHelper(self.args, self.logger)
        result = await th.get_variables("This text contains word1 and word2.", "BH123")

        expected_result = {
            "LEN": 6,
            "NEAREST_EXAMPLE_IN": "example2",
            "NEAREST_EXAMPLE_OUT": "translation2",
            "WORDLIST": "Prefer using the following translations.\nword1 => translation1; translation2\nword2 => translation3; translation4  (NOTE: example comment)\n",
            "AUTHOR": "by Bahá’u’lláh"
        }
        self.assertEqual(result, expected_result)

