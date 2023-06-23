
import asyncio

import unittest
from unittest.mock import Mock
from mock.logger import MockLogger
from mock.args import MockArgs

from src.gpt import GPT
from src.input import Input
from src.prompt_all import PromptAll

class TestPromptAll(unittest.IsolatedAsyncioTestCase):

    def test_simple_string(self):
        text = "This is a simple string."
        pa = PromptAll(Mock(), Mock(), Mock(), Mock())
        self.assertEqual(pa._count_words(text), 5)

    def test_empty_string(self):
        text = ""
        pa = PromptAll(Mock(), Mock(), Mock(), Mock())
        self.assertEqual(pa._count_words(text), 0)

    def test_multilingual_string(self):
        text = "مرحبا بالعالم, hello world!"
        pa = PromptAll(Mock(), Mock(), Mock(), Mock())
        self.assertEqual(pa._count_words(text), 4)
        
