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
    lg.add('INPUT', r'input')
    lg.add('OUTPUT', r'output')
    lg.add('TRUE', r'true')
    lg.add('WHILE', r'while')
    lg.add('EQUALS', r'=')
    lg.add('PLUS', r'\+')
    lg.add('MINUS', r'\-')
    lg.add('NOT', r'\!')
    lg.add('NULL', r'0')
    lg.add('NUMBER', r'[0-9]+')
    lg.add('VARIABLE', r'[a-zA-Z_][a-zA-Z0-9_]*')
    lg.ignore('\s+') #all spaces could be ignored
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
            return self.variables[varName] #return the position of the varName, when exists
        memory_position = self.freeSpacePosition
        self.variables[varName] = memory_position
        self.freeSpacePosition = self.freeSpacePosition + 1
        return memory_position

    def getNextLabel(self):
        nextLabel = self.LABELS[self.currentLabelPosition]
        self.currentLabelPosition+=1
        return nextLabel

def generateParser():
    pg = ParserGenerator(['SEMICOLON', 'INPUT', 'OUTPUT',
                          'LPAREN', 'RPAREN', 'EQUALS', 'VARIABLE',
                          'PLUS', 'MINUS', 'LBRACE', 'RBRACE', 'IF',
                          'NOT', 'NULL', 'WHILE', 'TRUE', 'NUMBER'])

    @pg.production('main : statements')
    def main(s):
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
    def expression_input(s):
        return hrast.Input()

    @pg.production('expr : OUTPUT LPAREN expr RPAREN')
    def expression_output(s):
        return hrast.Output(s[2])

    @pg.production('expr : VARIABLE')
    def expression_variable(s):
        return hrast.ReadVariable(s[0])

    @pg.production('expr : VARIABLE EQUALS expr')
    def expression_assignment(s):
        return hrast.Assignment(s[0], s[2])

    @pg.production('expr : VARIABLE PLUS PLUS')
    def expression_addOne(s):
        return hrast.ReadVariablePlusOne(s[0])

    @pg.production('expr : VARIABLE MINUS MINUS')
    def expression_addOne(s):
        return hrast.ReadVariableMinusOne(s[0])

    @pg.production('expr : VARIABLE PLUS VARIABLE')
    def expression_add(s):
        return hrast.Addition(s[0], s[2])

    @pg.production('expr : VARIABLE MINUS VARIABLE')
    def expression_add(s):
        return hrast.Subtraction(s[0], s[2])

    @pg.production('statement : IF LPAREN VARIABLE NOT EQUALS NULL RPAREN LBRACE statements RBRACE')
    def statement_if(s):
        return hrast.IfConditionNotNull(s[2], hrast.Block([s[8]]))

    @pg.production('statement : WHILE LPAREN TRUE RPAREN LBRACE statements RBRACE')
    def statement_while_true(s):
        return hrast.WhileTrue(hrast.Block([s[5]]))

    @pg.production('expr : VARIABLE EQUALS NULL')
    def expression_variable_gets_number(s):
        return hrast.AssignmentVariableToNumber(s[0], s[2])


    @pg.production('expr : VARIABLE EQUALS NUMBER')
    def expression_variable_gets_number(s):
        return hrast.AssignmentVariableToNumber(s[0], s[2])


    return pg.build()


def compile(input):
    lexer = generateLexer()
    parser = generateParser()
    ctx = Context()
    parser.parse(lexer.lex(input)).compile(ctx)
    return ctx.code

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("inputfile", help="The input file where the hrc code lays")
    args = parser.parse_args()
    code = open(args.inputfile, 'r').read()
    compiled = compile(code)
    for line in compiled:
        print(line)
