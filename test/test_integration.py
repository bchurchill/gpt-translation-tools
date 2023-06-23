
import unittest
import os
import subprocess
import tempfile
import shutil
from pathlib import Path

class BaseIntegrationTest(unittest.TestCase):
    # returns the path to one of the test fixture files
    def fixture_file(self, relative_path):
        return os.path.join(self.test_dir, "fixtures/files", relative_path)

    def fixture_dir(self):
        return os.path.join(self.test_dir, "fixtures/directory")

    # returns a path to a file in a temporary directory
    def temp_file(self, relative_path):
        return os.path.join(self.temp_dir, relative_path)

    # runs the tool with a list of arguments
    def run_tool(self, arguments, stdin=None):
        tool_path = os.path.join(self.root_dir, "tool.py")
        command = ["python3", tool_path] + arguments
        print(f"\nRunning: {command}")

        if stdin == None:
            return subprocess.run(command, capture_output=True, text=True)
        else:
            with open(stdin, 'r') as f:
                return subprocess.run(command, capture_output=True, text=True, stdin=f)

    # get the contents of a file
    def get_file_contents(self, output_file):
        with open(output_file, "r") as f:
            content = f.read()
        return content

    # automatically create and delete a temp directory for each test
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.root_dir = os.path.dirname(self.test_dir)
        self.temp_dir = tempfile.mkdtemp(dir = self.root_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def check_log_contents(self, log_contents):
        self.assertIn("Starting at", log_contents)
        self.assertIn("Total duration: 0 seconds", log_contents)
        self.assertNotIn("ERROR", log_contents.upper())
        self.assertNotIn("TRACEBACK", log_contents.upper())



class IntegrationTest(BaseIntegrationTest):

    def test_counttokens(self):
        output = self.run_tool(["counttokens", "-i", self.fixture_file("paragraph.txt"), "-o", self.temp_file("output.txt")])

        # check output is written to stdout
        self.assertIn("Number of tokens: 136", output.stdout)
        self.assertIn("GPT-4 prompting cost @ $0.03/1K tokens = $0.03", output.stdout)
        
        # check output is written to a file
        output_file = self.get_file_contents(self.temp_file("output.txt"))
        log_file = self.get_file_contents(self.temp_file("output.txt.log"))

        self.assertIn("Number of tokens: 136", output_file)
        self.assertIn("GPT-4 prompting cost @ $0.03/1K tokens = $0.03", output_file)
        
        self.assertIn("Number of tokens: 136", log_file)
        self.assertIn("GPT-4 prompting cost @ $0.03/1K tokens = $0.03", log_file)
 
        self.check_log_contents(log_file)     

    def test_prompt(self):
        output = self.run_tool(["prompt", "-m", "math", "-i", self.fixture_file("one-plus-one.txt"), "-o", self.temp_file("output.txt")])

        # check output is written to a file
        output_file = self.get_file_contents(self.temp_file("output.txt"))
        log_file = self.get_file_contents(self.temp_file("output.txt.log"))

        # check output is written to stdout
        self.assertIn("2", output.stdout)
        self.assertIn("2", output_file)
        self.assertIn("2", log_file)
 
        self.check_log_contents(log_file)     

    def test_promptall(self):
        output = self.run_tool(["prompt-all", "-m", "math", "-i", self.fixture_file("0123.txt"), "-p", self.fixture_file("paragraph.txt"), "-o", self.temp_file("output.txt"), "-w", "3"])

        # check output is written to a file
        output_file = self.get_file_contents(self.temp_file("output.txt"))
        log_file = self.get_file_contents(self.temp_file("output.txt.log"))

        # check output is written to stdout
        self.assertIn("0\n1\n2\n3\n", output.stdout)
        self.assertIn("0\n1\n2\n3\n", output_file)
        self.assertIn("0 -> 0\n", log_file)
        self.assertIn("1 -> 1\n", log_file)
        self.assertIn("2 -> 2\n", log_file)
        self.assertIn("3 -> 3\n", log_file)
 
        self.check_log_contents(log_file)     

    def test_chat(self):
        output = self.run_tool(["chat", "-m", "math", "-o", self.temp_file("output.txt")], stdin=self.fixture_file("chat.txt"))

        # check output is written to a file
        output_file = self.get_file_contents(self.temp_file("output.txt"))
        log_file = self.get_file_contents(self.temp_file("output.txt.log"))

        # check output is written to stdout
        self.assertIn("2", output.stdout)
        self.assertIn("2", output_file)
        self.assertIn("2\n", log_file)
 
        self.check_log_contents(log_file)     


    def test_prompt_directory(self):
        output = self.run_tool(["prompt-folder", "-m", "math", "--input-dir", self.fixture_dir(), "-p", self.fixture_file("paragraph.txt"), "-o", self.temp_file("output.txt"), "-w", "2"])

        # check output is written to a file
        output_file = self.get_file_contents(self.temp_file("output.txt"))
        log_file = self.get_file_contents(self.temp_file("output.txt.log"))

        # check output is written to stdout
        for test in ["one: 1", "zero: 0", "two: 2", "three: 3"]:
            self.assertIn(test, output.stdout)
            self.assertIn(test, output_file)
            self.assertIn(test, log_file)
    
        self.check_log_contents(log_file)     

    def test_map_reduce(self):
        output = self.run_tool(["map-reduce", "-m", "math", "--input-dir", self.fixture_dir(), "--map-prompt", self.fixture_file("paragraph.txt"), "--reduce-prompt", self.fixture_file("paragraph.txt"), "-o", self.temp_file("output.txt"), "-w", "2"])

        # check output is written to a file
        output_file = self.get_file_contents(self.temp_file("output.txt"))
        log_file = self.get_file_contents(self.temp_file("output.txt.log"))

        # check output is written to stdout
        for test in ["one: 1", "zero: 0", "two: 2", "three: 3"]:
            self.assertIn(test, output.stdout)
            self.assertIn(test, output_file)
            self.assertIn(test, log_file)
    
        self.check_log_contents(log_file)     

    def test_compute_embeddings(self):
        output = self.run_tool(["compute-embeddings", "-m", "math", "-i", self.fixture_file("paragraph.txt"), "-o", self.temp_file("output.txt")])

        # check output is written to a file
        input_file = self.get_file_contents(self.fixture_file("paragraph.txt"))
        output_file = self.get_file_contents(self.temp_file("output.txt"))
        log_file = self.get_file_contents(self.temp_file("output.txt.log"))

        input_len = len(input_file.split("\n"))
        output_len = len(output_file.split("\n"))

        self.assertEquals(input_len, output_len)
        self.check_log_contents(log_file)     

