class BaseObject(object):
    def hasReturnValue(self):
        return False

    def compile(self, ctx):
        pass


class Block(BaseObject):
    def __init__(self, value):
        self.value = value

    def compile(self, ctx):
        for obj in self.value:
            obj.compile(ctx)


class Input(BaseObject):
    def compile(self, ctx):
        ctx.code.append("INBOX")

    def hasReturnValue(self):
        return True


class Output(BaseObject):
    def __init__(self, value):
        self.value = value

    def compile(self, ctx):
        if self.value.hasReturnValue():
            self.value.compile(ctx)
            ctx.code.append("OUTBOX")
        else:
            raise Exception("Could not output a value of type without returnValue with object '" + self.value + "'")


class BasicVariable(BaseObject):
    def __init__(self, name, command):
        self.name = name.value
        self.command = command

    def hasReturnValue(self):
        return True

    def compile(self, ctx):
        if self.name in ctx.variables:
            ctx.code.append(self.command + " " + str(ctx.variables[self.name]))
        else:
            raise Exception("Variable '" + self.name + "' is not defined")


class ReadVariable(BasicVariable):
    def __init__(self, name):
        super().__init__(name, "COPYFROM")


class ReadVariablePlusOne(BasicVariable):
    def __init__(self, name):
        super().__init__(name, "BUMPUP")


class ReadVariableMinusOne(BasicVariable):
    def __init__(self, name):
        super().__init__(name, "BUMPDN")


class TwoVariablesExpression(BaseObject):
    def __init__(self, left_object, right_object, command, exception_name):
        self.leftObject = left_object.value
        self.rightObject = right_object.value
        self.command = command
        self.exceptionName = exception_name

    def hasReturnValue(self):
        return True

    def compile(self, ctx):
        if self.leftObject in ctx.variables and self.rightObject in ctx.variables:
            ctx.code.append("COPYFROM " + str(ctx.variables[self.leftObject]))
            ctx.code.append(self.command + " " + str(ctx.variables[self.rightObject]))
        else:
            raise Exception(self.exceptionName + ": Variable '" + self.leftObject +
                            "' or variable '" + self.rightObject + "' is undefined")


class Addition(TwoVariablesExpression):
    def __init__(self, leftObject, rightObject):
        super().__init__(leftObject, rightObject, "ADD", "Addition")


class Subtraction(TwoVariablesExpression):
    def __init__(self, leftObject, rightObject):
        super().__init__(leftObject, rightObject, "SUB", "Subtraction")


class AssignmentToFixMemoryAddress(BaseObject):
    def __init__(self, variable_name, number):
        self.variableName = variable_name.value
        self.number = number.value

    def compile(self, ctx):
        ctx.variables[self.variableName] = int(self.number)


class Assignment(BaseObject):
    def __init__(self, name, value):
        self.name = name.value
        self.value = value

    def hasReturnValue(self):
        return True

    def compile(self, ctx):
        if self.value.hasReturnValue():
            self.value.compile(ctx)
            ctx.code.append("COPYTO " + str(ctx.getVariablePos(self.name)))
        else:
            raise Exception("Could not assign value of type without returnValue with object '" + self.value + "'")


class IfNotEqualsNull(BaseObject):
    def __init__(self, left_position, statements):
        self.leftPosition = left_position.value
        self.statements = statements

    def compile(self, ctx):
        if self.leftPosition in ctx.variables:
            end_label = ctx.getNextLabel()
            ctx.code.append("COPYFROM " + str(ctx.variables[self.leftPosition]))
            ctx.code.append("JUMPZ " + end_label)
            self.statements.compile(ctx)
            ctx.code.append(end_label + ":")
        else:
            raise Exception("If: Variable '" + self.leftPosition + "' is undefined")


class IfEqualsNull(BaseObject):
    def __init__(self, left_position, statements):
        self.leftPosition = left_position.value
        self.statements = statements

    def compile(self, ctx):
        if self.leftPosition in ctx.variables:
            action_label = ctx.getNextLabel()
            end_label = ctx.getNextLabel()
            ctx.code.append("COPYFROM " + str(ctx.variables[self.leftPosition]))
            ctx.code.append("JUMPZ " + action_label)
            ctx.code.append("JUMP " + end_label)
            ctx.code.append(action_label + ":")
            self.statements.compile(ctx)
            ctx.code.append(end_label + ":")
        else:
            raise Exception("If: Variable '" + self.leftPosition + "' is undefined")


class If(BaseObject):
    def __init__(self, comparison, statement_if, statement_else):
        self.comparison = comparison
        self.statement_if = statement_if
        self.statement_else = statement_else
        self.compare_functions = \
            {"!=": "JUMPZ"}

    def compile(self, ctx):
        self.comparison.compile(ctx)
        end_label = ctx.getNextLabel()
        # example for '!=': JUMPZ else_label
        if isinstance(self.statement_else, Block):
            else_label = ctx.getNextLabel()
            ctx.code.append(self.compare_functions[self.comparison.compare_string] + " " + else_label)
        else:
            ctx.code.append(self.compare_functions[self.comparison.compare_string] + " " + end_label)
        # block of statements from the outer side
        self.statement_if.compile(ctx)
        if isinstance(self.statement_else, Block):
            ctx.code.append("JUMP " + end_label)
            #else_label
            ctx.code.append(else_label + ":")
            self.statement_else.compile(ctx)
        ctx.code.append(end_label + ":")


class Comparison(BaseObject):
    def __init__(self, compare_string, left_operand, right_operand):
        self.compare_string = compare_string
        self.left_operand = left_operand.value
        self.right_operand = right_operand.value

    def compile(self, ctx):
        if self.left_operand not in ctx.variables:
            raise Exception("Variable '" + self.left_operand + "' is undefined")
        ctx.code.append("COPYFROM " + str(ctx.variables[self.left_operand]))
        if isinstance(self.right_operand, BasicVariable):
            ctx.code.append(" " + str(ctx.variables[self.right_operand]))
            if self.right_operand not in ctx.variables:
                raise Exception("Variable '" + self.right_operand + "' is undefined")


class WhileTrue(BaseObject):
    def __init__(self, statements):
        self.statements = statements

    def compile(self, ctx):
        label = ctx.getNextLabel()
        ctx.code.append(label + ":")
        self.statements.compile(ctx)
        ctx.code.append("JUMP " + label)
