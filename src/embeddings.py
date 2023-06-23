import openai
import functools
import asyncio
import os
import json
import numpy as np

from collections import Counter

from src.input import Input
from tenacity import ( retry, stop_after_attempt, wait_random_exponential )

class Embeddings:

    def __init__(self,args,logger):
        self.logger = logger
        self.usage = 0

        # this is used to determine if we should be in test mode
        self.model = args.model

        # check that the API key is valid
        api_key = os.getenv('OPENAI_API_KEY')
        if self.model == "math":
            return

        if not api_key or api_key.strip() == '':
            raise ValueError('Error: OPENAI_API_KEY environment variable is not set or is empty.')

    def get_pricing(self):
        if self.model == "math":
            return 0
        else:
            return 0.0004
           
    def get_cost(self):
        return round(self.usage*self.get_pricing()/1000, 2)

    async def query(self, text):
        if self.model == "math":
            return self._test_math(text)
        else:
            return await self._get_embedding(text)

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    async def _get_embedding(self,text):
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-ada-002"
        )
        embedding = response["data"][0]["embedding"]
        self.usage += response["usage"]["prompt_tokens"]

        cost = self.get_cost()
        self.logger.log(f"[Embeddings] usage: {self.usage}.  Cost: ${cost}.")

        return embedding

    # This function is so that we can test against a "mock" GPT without incurring costs
    def _test_math(self, input_string):
        input_string += "\u241F"  ## add a "Unit Separator" to ensure there's at least one n-gram

        array_length = 5*256
        n = 5

        # Create n-grams from the input string
        input_ngrams = [input_string[i:i+n] for i in range(len(input_string) - n + 1)]
        if len(input_ngrams) == 0:
            input_ngrams = [input_string]

        # Count the occurrences of each n-gram
        ngram_counts = Counter(input_ngrams)

        # Create an array of zeros with the desired length
        float_array = np.zeros(array_length)

        # Calculate the total number of n-grams
        total_ngrams = sum(ngram_counts.values())

        # Assign a float value to each position in the array based on the n-gram counts
        for ngram, count in ngram_counts.items():
            index = sum((i+1)*ord(c) for i, c in enumerate(ngram)) % array_length
            float_array[index] += count / total_ngrams

        # Normalize the array to have a Euclidean length of 1
        float_array /= np.linalg.norm(float_array)

        return float_array.tolist()

    def similarity(self, array1, array2):
        # Compute the cosine similarity between two arrays
        return np.dot(array1,array2)

async def compute_embeddings(args, logger):
    data = Input(args, logger)
    embeddings = Embeddings(args, logger)
    lines = data.get_text_lines()
    for line in lines:
        embedding = await embeddings.query(line)
        logger.output(json.dumps(embedding))
