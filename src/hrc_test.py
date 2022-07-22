import unittest
import hrc


class MyTestCase(unittest.TestCase):
    def test_compile_only_input(self):
        result = hrc.compile("input();")
        self.assertEqual(["INBOX"], result)

    def test_compile_input_to_output(self):
        result = hrc.compile("output(input());")
        self.assertEqual(["INBOX", "OUTBOX"], result)

    def test_compile_input_to_variable(self):
        result = hrc.compile("x=input();")
        self.assertEqual(["INBOX", "COPYTO 0"], result)

    def test_compile_input_to_variable_and_output(self):
        result = hrc.compile("x=input();output(x);")
        self.assertEqual(["INBOX", "COPYTO 0", "COPYFROM 0", "OUTBOX"], result)

    def test_compile_input_increase_and_output(self):
        result = hrc.compile("x=input();x++;output(x);")
        self.assertEqual(["INBOX", "COPYTO 0", "BUMPUP 0", "COPYFROM 0", "OUTBOX"], result)

    def test_compile_input_output_increase(self):
        result = hrc.compile("x=input();output(x++);")
        self.assertEqual(["INBOX", "COPYTO 0", "BUMPUP 0", "OUTBOX"], result)

    def test_compile_input_output_decrease(self):
        result = hrc.compile("x=input();output(x--);")
        self.assertEqual(["INBOX", "COPYTO 0", "BUMPDN 0", "OUTBOX"], result)

    def test_compile_output_addition_of_two_variables(self):
        result = hrc.compile("x=input();y=input();output(x+y);")
        self.assertEqual(["INBOX", "COPYTO 0", "INBOX", "COPYTO 1", "COPYFROM 0", "ADD 1", "OUTBOX"], result)

    def test_compile_add_two_input_variables(self):
        result = hrc.compile("x=input();y=input();z=x+y;")
        self.assertEqual(["INBOX", "COPYTO 0", "INBOX", "COPYTO 1", "COPYFROM 0", "ADD 1", "COPYTO 2"], result)

    def test_while_1(self):
        result = hrc.compile("while(true) { output(input()); }")
        self.assertEqual(["A:", "INBOX", "OUTBOX", "JUMP A"], result)


if __name__ == '__main__':
    unittest.main()

