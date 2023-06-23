import re
import traceback
import numpy as np
import json

from src.embeddings import Embeddings
from src.arabic_strings import ArabicStrings

class TranslationHelper:
    def __init__(self, args, logger):
        self.logger = logger
        self.args = args

        self.arabic_strings = ArabicStrings(logger)

        self._initialize_examples()
        self._initialize_wordlist()

    def _check_example_arguments(self):
        args = self.args

        # verify arguments make sense
        if hasattr(args, "examples_in") and isinstance(args.examples_in, str):
            if args.examples_out == None:
                self.logger.fatal_error(Exception("When --examples-in is specified, --examples-out is also required."))
            if args.examples_embeddings == None:
                self.logger.fatal_error(Exception("When --examples-in is specified, --examples-embeddings is also required."))
            return True
        else:
            if hasattr(args, "examples_out") and isinstance(args.examples_out, str):
                self.logger.fatal_error(Exception("When --examples-out is specified, --examples-in is also required."))
            if hasattr(args, "examples_embeddings") and isinstance(args.examples_embeddings, str):
                self.logger.fatal_error(Exception("When --examples-embeddings is specified, --examples-in is also required."))
            return False


    def _initialize_examples(self):

        if not self._check_example_arguments():
            self.logger.debug("[translation helper] No examples in given")
            self.embeddings = None
            self.examples_in = None
            self.examples_out = None
            self.examples_embeddings = None
            return
        else:
            self.logger.debug("[translation helper] Parsing example data")

        try:
            with open(self.args.examples_in, 'r') as f:
                examples_in = f.readlines()

            with open(self.args.examples_out, 'r') as f:
                examples_out = f.readlines()

            with open(self.args.examples_embeddings, 'r') as f:
                embeddings = f.readlines()

        except Exception as e:
            self.logger.fatal_error(e)

        # remove empty lines
        examples_in = [ x for x in examples_in if len(x) > 0 ]
        examples_out = [ x for x in examples_out if len(x) > 0 ]
        embeddings = [ x for x in embeddings if len(x) > 0 ]

        self.examples_in = examples_in
        self.examples_out = examples_out
        embedding_arrays = [np.array(json.loads(line)) for line in embeddings]
        self.examples_embeddings = np.vstack(embedding_arrays)

        if len(self.examples_in) != len(self.examples_out):
            self.logger.fatal_error(Exception(f"Wrong number of output examples; expected {len(self.examples_in)} but got {len(self.examples_out)}."))
        
        if len(self.examples_in) != len(self.examples_embeddings):
            self.logger.fatal_error(Exception("Wrong number of example embeddings; expected {len(self.examples_in)} but got {len(self.examples_embeddings)}."))

        self.embeddings = Embeddings(self.args, self.logger)

    def _initialize_wordlist(self):

        self.wordlist = None

        if not hasattr(self.args, "wordlist"):
            return

        if not isinstance(self.args.wordlist, str):
            return

        self.wordlist = []

        try:
            with open(self.args.wordlist, 'r') as f:
                lines = f.readlines()
        except Exception as e:
            self.logger.fatal_error(e)
    
        for line in lines:
            if len(line.strip()) == 0:
                continue

            line = json.loads(line)
            if len(line) == 2:
                obj = {
                    "original": line[0],
                    "translations": line[1]
                }
            elif len(line) == 3:
                obj = {
                    "original": line[0],
                    "translations": line[1],
                    "comment": line[2]
                }
            self.wordlist.append(obj)

    async def get_variables(self, text, fileid=""):
        example_in, example_out = await self.get_nearest_example(text)

        return {
            "LEN": self.get_wordcount(text),
            "NEAREST_EXAMPLE_IN": example_in,
            "NEAREST_EXAMPLE_OUT": example_out,
            "WORDLIST": self.get_wordlist(text),
            "AUTHOR": self.id_to_author(fileid)
        }

    def _word_is_relevant(self, word, text):
        normalized_word = self.arabic_strings.strip_diacritical(word)
        normalized_text = self.arabic_strings.strip_diacritical(text)
        matches = normalized_word in normalized_text
        return matches

    def get_wordlist(self, text):
        if self.wordlist == None:
            return ""

        output = ""
        for line in self.wordlist:
            word = line["original"]

            if self._word_is_relevant(word, text):
                translations = '; '.join(line['translations'])
                if "comment" in line:
                    comment = line['comment']
                    output = output + f"{word} => {translations}  (NOTE: {comment})\n"
                else:
                    output = output + f"{word} => {translations}\n"

        if output != "":
            output = "Prefer using the following translations.\n" + output

        return output

    def get_wordcount(self, text):
        return len(text.split(" "))

    async def get_nearest_example(self, text):
        if self.embeddings == None:
            return None, None

        embedding = await self.embeddings.query(text)
        target_dot_products = np.dot(self.examples_embeddings, np.array(embedding))
        closest_index = np.argmax(target_dot_products)
        example_in = self.examples_in[closest_index]
        example_out = self.examples_out[closest_index]
        return example_in, example_out

    def id_to_author(self, fileid):
        if fileid.startswith("BH"):
            return "by Bahá’u’lláh"
        elif fileid.startswith("AB"):
            return "by `Abdu’l-Bahá"
        else:
            return "from the Baha’i Writings"


