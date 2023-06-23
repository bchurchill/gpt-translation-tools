import unittest
from src.template import Template

class TestTemplate(unittest.TestCase):
    def test_basic_arithmetic(self):
        template = Template(None, None, "Sum of {a+5} and {b-3} is {a+5+b-3}")
        variables = {'a': 5, 'b': 10}
        output = template.expand(variables)
        self.assertEqual(output, "Sum of 10 and 7 is 17")

    def test_min_max_function(self):
        template = Template(None, None, "Choose the minimum value {min(a, b)} and maximum value {max(a, b)}")
        variables = {'a': 25, 'b': 40}
        output = template.expand(variables)
        self.assertEqual(output, "Choose the minimum value 25 and maximum value 40")

    def test_expression_error(self):
        template = Template(None, None, "Expression error {a*/2}")
        variables = {'a': 5}
        with self.assertRaises(Exception):
            template.expand(variables)

    def test_no_variables(self):
        template = Template(None, None, "Hello, World!")
        variables = {}
        output = template.expand(variables)
        self.assertEqual(output, "Hello, World!")

    def test_division_non_integer(self):
        template = Template(None, None, "Divide {a} by {b} to get {a/b}")
        variables = {'a': 5, 'b': 2}
        output = template.expand(variables)
        self.assertEqual(output, "Divide 5 by 2 to get 2.5")

    def test_division_integer(self):
        template = Template(None, None, "Divide {a} by {b} to get {a//b}")
        variables = {'a': 5, 'b': 2}
        output = template.expand(variables)
        self.assertEqual(output, "Divide 5 by 2 to get 2")
