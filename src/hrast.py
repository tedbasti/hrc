class BaseObject(object):
    def has_return_value(self):
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

    def has_return_value(self):
        return True


class Output(BaseObject):
    def __init__(self, value):
        self.value = value

    def compile(self, ctx):
        if self.value.has_return_value():
            self.value.compile(ctx)
            ctx.code.append("OUTBOX")
        else:
            raise Exception("Could not output a value of type without returnValue with object '" + self.value + "'")


class BasicVariable(BaseObject):
    def __init__(self, name, command, is_pointer=False):
        self.name = name.value
        self.command = command
        self.is_pointer = is_pointer

    def has_return_value(self):
        return True

    def compile(self, ctx):
        if self.name in ctx.variables:
            if self.is_pointer:
                ctx.code.append(self.command + " [" + str(ctx.variables[self.name]) + "]")
            else:
                ctx.code.append(self.command + " " + str(ctx.variables[self.name]))
        else:
            raise Exception("Variable '" + self.name + "' is not defined")


class ReadVariable(BasicVariable):
    def __init__(self, name, is_pointer=False):
        super().__init__(name, "COPYFROM", is_pointer)


class ReadVariablePlusOne(BasicVariable):
    def __init__(self, name, is_pointer=False):
        super().__init__(name, "BUMPUP", is_pointer)


class ReadVariableMinusOne(BasicVariable):
    def __init__(self, name, is_pointer=False):
        super().__init__(name, "BUMPDN", is_pointer)


class TwoVariablesExpression(BaseObject):
    def __init__(self, left_object, right_object, command, exception_name):
        self.leftObject = left_object.value
        self.rightObject = right_object.value
        self.command = command
        self.exceptionName = exception_name

    def has_return_value(self):
        return True

    def compile(self, ctx):
        if self.leftObject in ctx.variables and self.rightObject in ctx.variables:
            ctx.code.append("COPYFROM " + str(ctx.variables[self.leftObject]))
            ctx.code.append(self.command + " " + str(ctx.variables[self.rightObject]))
        else:
            raise Exception(self.exceptionName + ": Variable '" + self.leftObject +
                            "' or variable '" + self.rightObject + "' is undefined")


class Addition(TwoVariablesExpression):
    def __init__(self, left_object, right_object):
        super().__init__(left_object, right_object, "ADD", "Addition")


class Subtraction(TwoVariablesExpression):
    def __init__(self, left_object, right_object):
        super().__init__(left_object, right_object, "SUB", "Subtraction")


class AssignmentToFixMemoryAddress(BaseObject):
    def __init__(self, variable_name, number):
        self.variableName = variable_name.value
        self.number = number.value

    def compile(self, ctx):
        ctx.variables[self.variableName] = int(self.number)


class Assignment(BaseObject):
    def __init__(self, name, value, is_pointer=False):
        self.name = name.value
        self.value = value
        self.is_pointer = is_pointer

    def has_return_value(self):
        return True

    def compile(self, ctx):
        if self.value.has_return_value():
            self.value.compile(ctx)
            if self.is_pointer:
                ctx.code.append("COPYTO [" + str(ctx.getVariablePos(self.name)) + "]")
            else:
                ctx.code.append("COPYTO " + str(ctx.getVariablePos(self.name)))
        else:
            raise Exception("Could not assign value of type without returnValue with object '" + self.value + "'")


def compile_if_logic(compare_string, if_statements, else_statements, ctx):
    if compare_string == "!=" or compare_string == ">=":
        command = "JUMPZ"
        if compare_string == ">=":
            command = "JUMPN"
        end_label = ctx.getNextLabel()
        if isinstance(else_statements, Block):
            else_label = ctx.getNextLabel()
            ctx.code.append(command + " " + else_label)
        else:
            ctx.code.append(command + " " + end_label)
        if_statements.compile(ctx)
        if isinstance(else_statements, Block):
            ctx.code.append("JUMP " + end_label)
            # else_label
            ctx.code.append(else_label + ":")
            else_statements.compile(ctx)
        ctx.code.append(end_label + ":")


class If(BaseObject):
    def __init__(self, comparison, statement_if, statement_else):
        self.comparison = comparison
        self.statement_if = statement_if
        self.statement_else = statement_else

    def compile(self, ctx):
        # Ensure that the right thing is within the register
        self.comparison.compile(ctx)
        if self.comparison.compare_string == "!=" or self.comparison.compare_string == ">=":
            compile_if_logic(self.comparison.compare_string, self.statement_if, self.statement_else, ctx)
        elif self.comparison.compare_string == "==":
            compile_if_logic("!=", self.statement_else, self.statement_if, ctx)
        elif self.comparison.compare_string == "<":
            compile_if_logic(">=", self.statement_else, self.statement_if, ctx)


class Goto(BaseObject):
    def __init__(self, label):
        self.label = label

    def compile(self, ctx):
        ctx.code.append("JUMP " + self.label)


class While(BaseObject):
    def __init__(self, comparison, statement):
        self.comparison = comparison
        self.statement = statement

    def compile(self, ctx):
        # Ensure that the right thing is within the register
        begin_label = ctx.getNextLabel()
        ctx.code.append(begin_label + ":")
        self.comparison.compile(ctx)
        # Append the JUMP begin_label at the end of the statements
        self.statement.value.append(Goto(begin_label))
        else_statement = BaseObject()
        if self.comparison.compare_string == "!=" or self.comparison.compare_string == ">=":
            compile_if_logic(self.comparison.compare_string, self.statement, else_statement, ctx)
        elif self.comparison.compare_string == "==":
            compile_if_logic("!=", else_statement, self.statement, ctx)
        elif self.comparison.compare_string == "<":
            compile_if_logic(">=", else_statement, self.statement, ctx)


class Comparison(BaseObject):
    def __init__(self, compare_string, left_operand, right_operand, is_pointer=False):
        self.compare_string = compare_string
        self.left_operand = left_operand.value
        self.right_operand = right_operand.value
        self.is_pointer = is_pointer

    def compile(self, ctx):
        if self.left_operand not in ctx.variables:
            raise Exception("Variable '" + self.left_operand + "' is undefined")
        if self.is_pointer:
            ctx.code.append("COPYFROM [" + str(ctx.variables[self.left_operand]) + "]")
        else:
            ctx.code.append("COPYFROM " + str(ctx.variables[self.left_operand]))
        if self.right_operand != '0':
            if self.right_operand not in ctx.variables:
                raise Exception("Variable '" + self.right_operand + "' is undefined")
            ctx.code.append("SUB " + str(ctx.variables[self.right_operand]))


class WhileTrue(BaseObject):
    def __init__(self, statements):
        self.statements = statements

    def compile(self, ctx):
        label = ctx.getNextLabel()
        ctx.code.append(label + ":")
        self.statements.compile(ctx)
        ctx.code.append("JUMP " + label)
