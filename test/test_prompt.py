
import asyncio

import unittest
from unittest.mock import Mock
from mock.logger import MockLogger
from mock.args import MockArgs

from src.gpt import GPT
from src.input import Input
from src.prompt import PromptOne

class TestPrompt(unittest.IsolatedAsyncioTestCase):

    # Verify that the input is read from the module, passed to GPT, and then outputted to log module
    async def test_prompt_works(self):
        test_input = "Hello, "
        test_output = "world!"

        args = MockArgs()
        logger = MockLogger()
        
        # Mock input data
        data = Mock()
        data.get_text.return_value = test_input

        # Mock GPT
        async def gpt_fake():
            return test_output 
        gpt = Mock(spec=GPT)
        gpt.query.return_value = await gpt_fake()

        # Run the prompt
        promptone = PromptOne(args,logger,data,gpt)
        result = await promptone.prompt_one()

        # Verify GPT was passed the input
        gpt.query.assert_called_once_with(None, test_input)

        # Verify that logger received the output
        self.assertIn(test_output, logger.outputs)
        self.assertEqual(0, len(logger.fatals))
        
