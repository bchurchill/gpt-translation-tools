
class MockLogger:

    def __init__(self):
        self.outputs = []
        self.logs = []
        self.debugs = []
        self.fatals = []

    # Synchronous methods

    def output(self, message):
        self.outputs.append(message)

    def log(self, message):
        self.logs.append(message)

    def debug(self, message):
        self.debugs.append(message)

    def fatal_error(self, e):
        self.fatals.append(e)

    # Asynchronous methods

    async def output_async(self, message):
        self.output(message)

    async def log_async(self, message):
        self.log(message)

    async def debug_async(self, message):
        self.debug(message)

