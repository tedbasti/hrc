from rply import LexerGenerator, ParserGenerator
import hrast
import argparse


def generateLexer():
    lg = LexerGenerator()
    lg.add('SEMICOLON', r';')
    lg.add('LPAREN', r'\(')
    lg.add('RPAREN', r'\)')
    lg.add('LBRACE', r'\{')
    lg.add('RBRACE', r'\}')
    lg.add('IF', r'if')
    lg.add('ELSE', r'else')
    lg.add('INPUT', r'input')
    lg.add('OUTPUT', r'output')
    lg.add('TRUE', r'true')
    lg.add('WHILE', r'while')
    lg.add('EQUALS', r'=')
    lg.add('PLUS', r'\+')
    lg.add('MINUS', r'\-')
    lg.add('NOT', r'\!')
    lg.add('BIGGER', r'\>')
    lg.add('SMALLER', r'\<')
    lg.add('NULL', r'0')
    lg.add('NUMBER', r'[0-9]+')
    lg.add('VARIABLE', r'[a-zA-Z_][a-zA-Z0-9_]*')
    # Ignore all spaces
    lg.ignore(r'\s+')
    lg.ignore(r'\/\/[^\n]*\n')
    return lg.build()


class Context(object):
    def __init__(self):
        self.code = []
        self.freeSpacePosition = 0
        # A = 0, B = 1, ...
        self.variables = {}
        self.LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.currentLabelPosition = 0

    def getVariablePos(self, varName):
        if varName in self.variables:
            # return the position of the varName, when exists
            return self.variables[varName]
        memory_position = self.freeSpacePosition
        self.variables[varName] = memory_position
        self.freeSpacePosition = self.freeSpacePosition + 1
        return memory_position

    def getNextLabel(self):
        nextLabel = self.LABELS[self.currentLabelPosition]
        self.currentLabelPosition += 1
        return nextLabel


def generateParser():
    pg = ParserGenerator(['SEMICOLON', 'INPUT', 'OUTPUT',
                          'LPAREN', 'RPAREN', 'EQUALS', 'VARIABLE',
                          'PLUS', 'MINUS', 'LBRACE', 'RBRACE', 'IF',
                          'NOT', 'NULL', 'WHILE', 'TRUE', 'NUMBER',
                          'BIGGER', 'SMALLER', 'ELSE'])

    @pg.production('main : statements')
    def main_statement(s):
        return s[0]

    @pg.production('statements : statements statement')
    def statements(s):
        return hrast.Block(s[0].value + [s[1]])

    @pg.production('statements : statement')
    def statements_statement(s):
        return hrast.Block([s[0]])

    @pg.production('statement : expr SEMICOLON')
    def statement(s):
        return s[0]

    @pg.production('expr : INPUT LPAREN RPAREN')
    def expression_input(_):
        return hrast.Input()

    @pg.production('expr : OUTPUT LPAREN expr RPAREN')
    def expression_output(s):
        return hrast.Output(s[2])

    @pg.production('expr : VARIABLE')
    def expression_variable(s):
        return hrast.ReadVariable(s[0])

    @pg.production('expr : VARIABLE PLUS PLUS')
    def expression_add_one(s):
        return hrast.ReadVariablePlusOne(s[0])

    @pg.production('expr : VARIABLE MINUS MINUS')
    def expression_subtract_one(s):
        return hrast.ReadVariableMinusOne(s[0])

    @pg.production('expr : VARIABLE PLUS VARIABLE')
    def expression_addition(s):
        return hrast.Addition(s[0], s[2])

    @pg.production('expr : VARIABLE MINUS VARIABLE')
    def expression_subtraction(s):
        return hrast.Subtraction(s[0], s[2])

    @pg.production('expr : VARIABLE EQUALS NULL')
    @pg.production('expr : VARIABLE EQUALS NUMBER')
    def expression_variable_to_fix_memory_address(s):
        return hrast.AssignmentToFixMemoryAddress(s[0], s[2])

    @pg.production('expr : VARIABLE EQUALS expr')
    def expression_assignment(s):
        return hrast.Assignment(s[0], s[2])

    @pg.production('statement : IF LPAREN comparison RPAREN LBRACE statements RBRACE ELSE LBRACE statements RBRACE')
    def statement_if_with_else(s):
        return hrast.If(s[2], hrast.Block([s[5]]), hrast.Block([s[9]]))

    @pg.production('statement : IF LPAREN comparison RPAREN LBRACE statements RBRACE')
    def statement_if(s):
        return hrast.If(s[2], hrast.Block([s[5]]), hrast.BaseObject())

    @pg.production('statement : WHILE LPAREN comparison RPAREN LBRACE statements RBRACE')
    def statement_while(s):
        return hrast.While(s[2], hrast.Block([s[5]]))

    @pg.production('comparison : VARIABLE SMALLER VARIABLE')
    @pg.production('comparison : VARIABLE SMALLER NULL')
    def comparison_not_equals_null(s):
        return hrast.Comparison(s[1].value, s[0], s[2])

    @pg.production('comparison : VARIABLE BIGGER EQUALS VARIABLE')
    @pg.production('comparison : VARIABLE NOT EQUALS VARIABLE')
    @pg.production('comparison : VARIABLE EQUALS EQUALS VARIABLE')
    @pg.production('comparison : VARIABLE BIGGER EQUALS NULL')
    @pg.production('comparison : VARIABLE NOT EQUALS NULL')
    @pg.production('comparison : VARIABLE EQUALS EQUALS NULL')
    def comparison_not_equals_null(s):
        return hrast.Comparison(s[1].value + s[2].value, s[0], s[3])

    @pg.production('statement : WHILE LPAREN TRUE RPAREN LBRACE statements RBRACE')
    def statement_while_true(s):
        return hrast.WhileTrue(hrast.Block([s[5]]))

    return pg.build()


def compile(code):
    l = generateLexer()
    p = generateParser()
    ctx = Context()
    p.parse(l.lex(code)).compile(ctx)
    return ctx.code


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", help="The input file where the hrc code lays")
    args = parser.parse_args()
    code = open(args.inputfile, 'r').read()
    compiled = compile(code)
    for line in compiled:
        print(line)


if __name__ == '__main__':
    main()
