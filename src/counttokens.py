import tiktoken
import math

from src.input import Input
from src.logger import Logger

class CountTokens:

    def __init__(self, args, logger, data):
        self.args = args
        self.logger = logger
        self.data = data

    def count_tokens(self):
        # Load input text
        input_text = self.data.get_text()

        enc = tiktoken.encoding_for_model(self.args.model)

        total_tokens = len(enc.encode(input_text))

        # Print result
        self.logger.output(f"Number of tokens: {total_tokens}")

        # Calculate and print costs
        ktokens=math.ceil(total_tokens/1000)
        if self.args.model == "gpt-4":
            cost = round(ktokens*0.03,2)
            self.logger.output("GPT-4 prompting cost @ $0.03/1K tokens = $" + str(cost))
        if self.args.model == "gpt-3.5-turbo":
            cost = round(ktokens*0.002,2)
            self.logger.output("GPT-3.5 prompting cost @ $0.002/1K tokens = $" + str(cost))

        return total_tokens

async def count_tokens(args, logger):
    data = Input(args, logger)
    ct = CountTokens(args, logger, data)
    ct.count_tokens()
