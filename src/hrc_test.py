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

    def test_compile_input_output_decrease(self):
        result = hrc.compile("x=input();output(x--);")
        self.assertEqual(["INPUT", "COPYTO 0", "BUMPDN 0", "OUTPUT"], result)

    def test_compile_output_addition_of_two_variables(self):
        result = hrc.compile("x=input();y=input();output(x+y);")
        self.assertEqual(["INPUT", "COPYTO 0", "INPUT", "COPYTO 1", "COPYFROM 0", "ADD 1", "OUTPUT"], result)

    def test_compile_add_two_input_variables(self):
        result = hrc.compile("x=input();y=input();z=x+y;")
        self.assertEqual(["INPUT", "COPYTO 0", "INPUT", "COPYTO 1", "COPYFROM 0", "ADD 1", "COPYTO 2"], result)


if __name__ == '__main__':
    unittest.main()
