import unittest
import hrc

class MyTestCase(unittest.TestCase):
    def test_compile_only_input(self):
        result = hrc.compile("input();")
        self.assertEqual(["INPUT"], result)


    def test_compile_input_to_output(self):
        result = hrc.compile("output(input());")
        self.assertEqual(["INPUT", "OUTPUT"], result)


    def test_compile_input_to_variable(self):
        result = hrc.compile("x=input();")
        self.assertEqual(["INPUT", "COPYTO 0"], result)


    def test_compile_input_to_variable_and_output(self):
        result = hrc.compile("x=input();output(x);")
        self.assertEqual(["INPUT", "COPYTO 0", "COPYFROM 0", "OUTPUT"], result)


    def test_compile_input_increase_and_output(self):
        result = hrc.compile("x=input();x++;output(x);")
        self.assertEqual(["INPUT", "COPYTO 0", "BUMPUP 0", "COPYFROM 0", "OUTPUT"], result)


    def test_compile_input_output_increase(self):
        result = hrc.compile("x=input();output(x++);")
        self.assertEqual(["INPUT", "COPYTO 0", "BUMPUP 0", "OUTPUT"], result)


if __name__ == '__main__':
    unittest.main()

