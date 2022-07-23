class BaseObject(object):
    def hasReturnValue(self):
        return False


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


class AssignmentToFixMemoryAddress(BaseObject):
    def __init__(self, variable_name, number):
        self.variableName = variable_name.value
        self.number = number.value

    def compile(self, ctx):
        ctx.variables[self.variableName] = int(self.number)


class IfConditionNotNull(BaseObject):
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


class WhileTrue(BaseObject):
    def __init__(self, statements):
        self.statements = statements

    def compile(self, ctx):
        label = ctx.getNextLabel()
        ctx.code.append(label + ":")
        self.statements.compile(ctx)
        ctx.code.append("JUMP " + label)
