class BaseObject(object):
    def hasReturnValue(self):
        return False

class Input(BaseObject):
    def compile(self, ctx):
        ctx.code.append("INPUT")
    def hasReturnValue(self):
        return True

class Output(BaseObject):
    def __init__(self, value):
        self.value = value
    def compile(self, ctx):
        if self.value.hasReturnValue():
            self.value.compile(ctx)
            ctx.code.append("OUTPUT")
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

class Addition(BaseObject):
    def __init__(self, leftObject, rightObject):
        self.leftObject = leftObject.value
        self.rightObject = rightObject.value

    def hasReturnValue(self):
        return True

    def compile(self, ctx):
        if self.leftObject in ctx.variables and self.rightObject in ctx.variables:
            ctx.code.append("COPYFROM " + str(ctx.variables[self.leftObject]))
            ctx.code.append("ADD " + str(ctx.variables[self.rightObject]))
        else:
            raise Exception("Addition: Variable '" + self.leftObject + "' or variable '" + self.rightObject + "' is undefined")


class Subtraction(BaseObject):
    def __init__(self, leftObject, rightObject):
        self.leftObject = leftObject.value
        self.rightObject = rightObject.value

    def hasReturnValue(self):
        return True

    def compile(self, ctx):
        if self.leftObject in ctx.variables and self.rightObject in ctx.variables:
            ctx.code.append("COPYFROM " + str(ctx.variables[self.leftObject]))
            ctx.code.append("SUB " + str(ctx.variables[self.rightObject]))
        else:
            raise Exception("Subtraction: Variable '" + self.leftObject + "' or variable '" + self.rightObject + "' is undefined")

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

class ifConditionNotNull(BaseObject):
    def __init__(self, leftPosition, statements):
        self.leftPosition = leftPosition.value
        self.statements = statements

    def compile(self, ctx):
        if self.leftPosition in ctx.variables:
            actionLabel = ctx.getNextLabel()
            endLabel = ctx.getNextLabel()
            ctx.code.append("POP " + str(ctx.variables[self.leftPosition]))
            ctx.code.append("JNZ " + actionLabel)
            ctx.code.append("JMP " + endLabel)
            ctx.code.append(actionLabel + ":")
            self.statements.compile(ctx)
            ctx.code.append(endLabel + ":")
        else:
            raise Exception("If: Variable '" + self.leftObject + "' is undefined")


class Block(BaseObject):
    def __init__(self, value):
        self.value = value
    def compile(self, ctx):
        for obj in self.value:
            obj.compile(ctx)

class WhileTrue(BaseObject):
    def __init__(self, statements):
        self.statements = statements
    def compile(self, ctx):
        label = ctx.getNextLabel()
        ctx.code.append(label + ":")
        self.statements.compile(ctx)
        ctx.code.append("JMP " + label)