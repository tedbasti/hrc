from rply import LexerGenerator, ParserGenerator
import ast

def generateLexer():
    lg = LexerGenerator()
    lg.ignore('\s+') #all spaces could be ignored
    lg.add('SEMICOLON', r';')
    lg.add('LPAREN', r'\(')
    lg.add('RPAREN', r'\)')
    lg.add('LBRACE', r'\{')
    lg.add('RBRACE', r'\}')
    lg.add('if', r'if')
    lg.add('INPUT', r'input')
    lg.add('OUTPUT', r'output')
    lg.add('EQUALS', r'=')
    lg.add('PLUS', r'\+')
    lg.add('MINUS', r'\-')
    lg.add('NOT', r'\!')
    lg.add('NULL', r'0')
    lg.add('VARIABLE', r'[a-zA-Z_][a-zA-Z0-9_]*')
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
                          'PLUS', 'MINUS', 'LBRACE', 'RBRACE', 'if',
                          'NOT', 'NULL'])

    @pg.production('main : statements')
    def main(s):
        return s[0]

    @pg.production('statements : statements statement')
    def statements(s):
        return ast.Block(s[0].value + [s[1]])

    @pg.production('statements : statement')
    def statements_statement(s):
        return ast.Block([s[0]])

    @pg.production('statement : expr SEMICOLON')
    def statement(s):
        return s[0]

    @pg.production('expr : INPUT LPAREN RPAREN')
    def expression_input(s):
        return ast.Input()

    @pg.production('expr : OUTPUT LPAREN expr RPAREN')
    def expression_output(s):
        return ast.Output(s[2])

    @pg.production('expr : VARIABLE')
    def expression_variable(s):
        return ast.ReadVariable(s[0])

    @pg.production('expr : VARIABLE EQUALS expr')
    def expression_assignment(s):
        return ast.Assignment(s[0], s[2])

    @pg.production('expr : VARIABLE PLUS PLUS')
    def expression_addOne(s):
        return ast.ReadVariablePlusOne(s[0])

    @pg.production('expr : VARIABLE MINUS MINUS')
    def expression_addOne(s):
        return ast.ReadVariableMinusOne(s[0])

    @pg.production('expr : VARIABLE PLUS VARIABLE')
    def expression_add(s):
        return ast.Addition(s[0], s[2])

    @pg.production('expr : VARIABLE MINUS VARIABLE')
    def expression_add(s):
        return ast.Subtraction(s[0], s[2])

    @pg.production('statement : if LPAREN VARIABLE NOT EQUALS NULL RPAREN LBRACE statements RBRACE')
    def statement_if(s):
        return ast.ifConditionNotNull(s[2], ast.Block([s[8]]))

    return pg.build()


if __name__ == '__main__':
    lexer = generateLexer()
    parser = generateParser()
    code = 'x=input(); if (x != 0) { output(x); }'
    p = parser.parse(lexer.lex(code))
    ctx = Context()
    p.compile(ctx)
    print(code)
    print(ctx.code)