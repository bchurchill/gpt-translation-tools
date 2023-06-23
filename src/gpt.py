import openai
import functools
import asyncio
import os

from tenacity import ( retry, stop_after_attempt, wait_random_exponential )

class GPT:

    def __init__(self,args,logger):
        self.model = args.model
        self.top_p = args.top_p
        self.best_of = args.best_of
        self.max_tokens = args.max_tokens
        self.n = args.gpt_n
        self.logger = logger

        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0

        # check that the API key is valid
        api_key = os.getenv('OPENAI_API_KEY')
        if self.model == "math":
            return

        if not api_key or api_key.strip() == '':
            raise ValueError('Error: OPENAI_API_KEY environment variable is not set or is empty.')




    def get_pricing(self):
        if self.model == "gpt-4":
            return {
                    "prompt": 0.03,
                    "completion": 0.06
                }
        elif self.model == "gpt-3.5-turbo":
             return {
                    "prompt": 0.002,
                    "completion": 0.002
                }
        elif self.model == "math":
            return {
                    "prompt": 0,
                    "completion": 0
                }
           
    def get_cost(self):
        usage = self.get_usage()
        prompt_cost = usage["prompt"]*self.get_pricing()["prompt"]/1000
        completion_cost = usage["completion"]*self.get_pricing()["completion"]/1000
        total_cost = round(prompt_cost + completion_cost,2)
        return total_cost

    def get_usage(self):
        return {
            "prompt": self.prompt_tokens,
            "completion": self.completion_tokens,
            "total": self.total_tokens
        }


    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    async def query(self, system, user):
        msgs=[]

        if system is not None:
            msgs.append({"role": "system", "content": system})
        if user is not None:
            msgs.append({"role": "user", "content": user })

        return await self._query(msgs)

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    async def query_history(self, messages):
        return await self._query(messages)

    async def _query(self, messages):
        if self.model == "math":
            return self._test_math(messages[-1]["content"])

        self.logger.debug("Messages=")
        self.logger.debug(messages)
        self.logger.debug(f"model={self.model}, top_p={self.top_p}, best_of={self.best_of}, n={self.n}")

        stub = functools.partial(openai.ChatCompletion.create, model=self.model, top_p=self.top_p, messages=messages, n=self.n)
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, stub)

        self.prompt_tokens = self.prompt_tokens + result.usage["prompt_tokens"]
        self.completion_tokens = self.completion_tokens + result.usage["completion_tokens"]
        self.total_tokens = self.total_tokens + result.usage["total_tokens"]
        usage = self.get_usage()
        cost = self.get_cost()
        self.logger.log(f"[GPT] usage: {self.get_usage()}.  Cost: ${cost}.")

        self.logger.debug(result.choices)
        return result.choices[0].message["content"]


    # This function is so that we can test against a "mock" GPT without incurring costs
    def _test_math(self, problems):
        safe_env = {
            '__builtins__': {},
            'min': min,
            'max': max
        }
        try:
            exprs = [ expr for expr in problems.split("\n") if expr ]
            self.logger.debug(f"exprs={exprs}")
            outputs = map(lambda e : str(eval(e, safe_env)), exprs)
            return "\n".join(outputs)
        except Exception as e:
            self.logger.log(f"Error evaluating expression: {expr}")
            self.logger.log(traceback.format_exc())
            raise e

        

