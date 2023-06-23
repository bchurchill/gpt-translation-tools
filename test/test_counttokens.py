
import asyncio

import unittest
from unittest.mock import Mock
from mock.logger import MockLogger
from mock.args import MockArgs

from src.gpt import GPT
from src.input import Input
from src.prompt import PromptOne
from src.counttokens import CountTokens

class TestCountTokens(unittest.TestCase):

    def test_count_tokens(self):
        test_input = "Hello, 12345"

        args = MockArgs(model="gpt-4")
        logger = MockLogger()
        
        # Mock input data
        data = Mock()
        data.get_text_lines.return_value = [test_input]
        data.get_text.return_value = test_input

        # Run the prompt
        ct = CountTokens(args,logger,data)
        count = ct.count_tokens()

        self.assertEqual(5, count)
        
