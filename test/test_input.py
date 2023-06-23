import unittest
from unittest.mock import MagicMock
from src.input import Input

class TestInput(unittest.TestCase):
    def setUp(self):
        self.mock_args = MagicMock()
        self.mock_file_handler = MagicMock()

    def test_single_line_number(self):
        input_obj = Input(self.mock_args, self.mock_file_handler)
        input_obj._filter_lines = MagicMock(wraps=input_obj._filter_lines)
        self.mock_args.lines = "3"
        result = input_obj._filter_lines(["line 1", "line 2", "line 3", "line 4", "line 5"])
        self.assertEqual(result, ["line 3"])

    def test_single_range(self):
        input_obj = Input(self.mock_args, self.mock_file_handler)
        input_obj._filter_lines = MagicMock(wraps=input_obj._filter_lines)
        self.mock_args.lines = "2-4"
        result = input_obj._filter_lines(["line 1", "line 2", "line 3", "line 4", "line 5"])
        self.assertEqual(result, ["line 2", "line 3", "line 4"])

    def test_multiple_ranges_and_numbers(self):
        input_obj = Input(self.mock_args, self.mock_file_handler)
        input_obj._filter_lines = MagicMock(wraps=input_obj._filter_lines)
        self.mock_args.lines = "1,3-4,6"
        result = input_obj._filter_lines(["line 1", "line 2", "line 3", "line 4", "line 5", "line 6"])
        self.assertEqual(result, ["line 1", "line 3", "line 4", "line 6"])

    def test_line_number_out_of_bounds(self):
        input_obj = Input(self.mock_args, self.mock_file_handler)
        input_obj._filter_lines = MagicMock(wraps=input_obj._filter_lines)
        self.mock_args.lines = "7"
        with self.assertRaises(ValueError):
            input_obj._filter_lines(["line 1", "line 2", "line 3", "line 4", "line 5", "line 6"])

    def test_range_out_of_bounds(self):
        input_obj = Input(self.mock_args, self.mock_file_handler)
        input_obj._filter_lines = MagicMock(wraps=input_obj._filter_lines)
        self.mock_args.lines = "5-8"
        with self.assertRaises(ValueError):
            input_obj._filter_lines(["line 1", "line 2", "line 3", "line 4", "line 5", "line 6"])

    def test_range_start_greater_than_end(self):
        input_obj = Input(self.mock_args, self.mock_file_handler)
        input_obj._filter_lines = MagicMock(wraps=input_obj._filter_lines)
        self.mock_args.lines = "4-2"
        with self.assertRaises(ValueError):
            input_obj._filter_lines(["line 1", "line 2", "line 3", "line 4", "line 5"])

    def test_invalid_line_number(self):
        input_obj = Input(self.mock_args, self.mock_file_handler)
        input_obj._filter_lines = MagicMock(wraps=input_obj._filter_lines)
        self.mock_args.lines = "0"
        with self.assertRaises(ValueError):
            input_obj._filter_lines(["line 1", "line 2", "line 3", "line 4", "line 5"])

