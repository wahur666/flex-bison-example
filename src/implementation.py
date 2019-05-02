from typing import List, Dict

BOOLEAN = 0
NATURAL = 1
INDENT = " " * 4

types = {BOOLEAN, NATURAL}
ID: int = 0


class Symbol:

    def __init__(self, line: int = None, name: str = None, type: int = None):
        self.line = line
        self.name = name
        self.symbol_type = type
        self.label = next_label()

    def declare(self):
        if self.name in symbol_table:
            error(self.line, "Re-declared variable: " + self.name)
        symbol_table[self.name] = self

    def get_code(self) -> str:
        pass

    def get_size(self) -> int:
        if self.symbol_type  == BOOLEAN:
            return 1
        else:
            return 4


symbol_table: Dict[str, Symbol] = {}
value_table: List[int] = []


class Expression:

    def get_type(self) -> int:
        pass

    def get_code(self) -> str:
        pass

    def get_value(self) -> int:
        pass

    def print(self):
        pass

    def to_string(self) -> str:
        pass

class NumberExpression(Expression):

    def __init__(self, text: str):
        self.value = int(text)

    def get_type(self) -> int:
        return NATURAL

    def get_code(self) -> str:
        pass

    def get_value(self) -> int:
        pass

    def print(self):
        print(self.value)

    def to_string(self) -> str:
        return str(self.value)

class BooleanExpression(Expression):

    def __init__(self, value: bool):
        self.value = value

    def get_type(self) -> int:
        return BOOLEAN

    def get_code(self) -> str:
        pass

    def get_value(self) -> int:
        pass

    def print(self):
        print("true" if self.value else "false")

    def to_string(self) -> str:
        return "true" if self.value else "false"



class IdExpression(Expression):

    def __init__(self, line: int, name: str):
        self.line = line
        self.name = name

    def get_type(self) -> int:
        if self.name not in symbol_table:
            error(self.line, "Undefined variable: " + self.name)
        return symbol_table[self.name].symbol_type

    def get_code(self) -> str:
        pass

    def get_value(self) -> int:
        pass

    def print(self):
        print(self.name)

    def to_string(self) -> str:
        return self.name


class BinopExpression(Expression):

    def __init__(self, line: int, op: str, left: Expression, right: Expression):
        self.line = line
        self.op = op
        self.left = left
        self.right = right

    def get_type(self) -> int:
        if self.op == "=":
            if self.left.get_type() != self.right.get_type():
                error(self.line, "Left and right operands of '=' have different types.")
        else:
            if self.left.get_type() != operand_type(self.op):
                error(self.line, "Left operand of '" + self.op + "' has unexpected type.")
            if self.right.get_type() != operand_type(self.op):
                error(self.line, "Right operand of '" + self.op + "' has unexpected type.")
        return return_type(self.op)

    def get_code(self) -> str:
        pass

    def get_value(self) -> int:
        pass

    def print(self):
        print("(", self.left.to_string(), ") ", self.op, " (", self.right.to_string(), ")")

    def to_string(self) -> str:
        return "(" + self.left.to_string() + ") " + self.op + " (" + self.right.to_string() + ")"

class NotExpression(Expression):

    def __init__(self, line: int, op: str, operand: Expression):
        self.line = line
        self.op = op
        self.operand = operand

    def get_type(self) -> int:
        if self.operand.get_type() != BOOLEAN:
            error(self.line, "Operand of 'not' is not boolean.")
        return BOOLEAN

    def get_code(self) -> str:
        pass

    def get_value(self) -> int:
        pass

    def print(self):
        print(self.op, " (", self.operand.to_string(), ")")

    def to_string(self) -> str:
        return self.op + " (" + self.operand.to_string() + ")"


class TernaryExpression(Expression):

    def __init__(self, line: int, condition: Expression, true_expression: Expression, false_expression: Expression):
        self.line = line
        self.condition = condition
        self.true_expression = true_expression
        self.false_expression = false_expression

    def get_type(self) -> int:
        if self.condition.get_type() != BOOLEAN:
            error(self.line, "Condition of '?:' expression is not boolean.")
        if self.true_expression.get_type() != self.false_expression.get_type():
            error(self.line, "The sides of '?:' expression are not the same type.")

        return self.true_expression.get_type()

    def get_code(self) -> str:
        pass

    def get_value(self) -> int:
        pass

    def print(self):
        print("(", self.condition.to_string(), " ? ", self.true_expression.to_string(), " : ",
              self.false_expression.to_string(), ")")

    def to_string(self) -> str:
        return "(" + self.condition.to_string() + " ? " + self.true_expression.to_string() + " : " +\
              self.false_expression.to_string() + ")"


class Instruction:

    def __init__(self, line: int):
        self.line = line

    def type_check(self):
        pass

    def get_code(self) -> str:
        pass

    def execute(self):
        pass

    def get_line(self):
        return self.line

    def print(self, indent_level: int):
        pass


class AssignInstruction(Instruction):

    def __init__(self, line: int, left: str, right: Expression):
        super().__init__(line)
        self.left = left
        self.right = right

    def type_check(self):
        if self.left not in symbol_table:
            error(self.line, "Undefined variable: " + self.left)
        if symbol_table[self.left].symbol_type != self.right.get_type():
            error(self.line, "Left and right hand sides of assignment are of different types.")

    def get_code(self) -> str:
        pass

    def execute(self):
        pass

    def print(self, indent_level: int):
        indent(indent_level)
        print(self.left, " := ", self.right.to_string())


class ReadInstruction(Instruction):

    def __init__(self, line: int, id: str):
        super().__init__(line)
        self.id = id

    def type_check(self):
        if self.id not in symbol_table:
            error(self.line, "Undefined variable: " + self.id)

    def get_code(self) -> str:
        pass

    def execute(self):
        pass

    def print(self, indent_level: int):
        indent(indent_level)
        print("read(", self.id, ")")


class WriteInstruction(Instruction):

    def __init__(self, line: int, exp: Expression):
        super().__init__(line)
        self.exp = exp
        self.exp_type = None

    def type_check(self):
        self.exp_type = self.exp.get_type()

    def get_code(self) -> str:
        pass

    def execute(self):
        pass

    def print(self, indent_level: int):
        indent(indent_level)
        print("write(", self.exp.to_string(), ")")


class IfInstruction(Instruction):

    def __init__(self, line: int, condition: Expression, true_branch: List[Instruction],
                 false_branch: List[Instruction]):
        super().__init__(line)
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

    def type_check(self):
        if self.condition.get_type() != BOOLEAN:
            error(self.line, "Condition of 'if' instruction is not boolean.")
        type_check_commands(self.true_branch)
        type_check_commands(self.false_branch)

    def get_code(self) -> str:
        pass

    def execute(self):
        pass

    def print(self, indent_level: int):
        indent(indent_level)
        print("if ", self.condition.to_string(), " then")
        print_commands(indent_level + 1, self.true_branch)

        if self.false_branch:
            indent(indent_level)
            print("else")
            print_commands(indent_level + 1, self.false_branch)

        indent(indent_level)
        print("endif")


class WhileInstruction(Instruction):

    def __init__(self, line: int, condition: Expression, body: List[Instruction]):
        super().__init__(line)
        self.condition = condition
        self.body = body

    def type_check(self):
        if self.condition.get_type() != BOOLEAN:
            error(self.line, "Condition of 'while' instruction is not boolean.")
        type_check_commands(self.body)

    def get_code(self) -> str:
        pass

    def execute(self):
        pass

    def print(self, indent_level: int):
        indent(indent_level)
        print("while ", self.condition.to_string(), " do")
        print_commands(indent_level + 1, self.body)

        indent(indent_level)
        print("done")


class RepeatInstruction(Instruction):

    def __init__(self, line: int, count: Expression, body: List[Instruction]):
        super().__init__(line)
        self.count = count
        self.body = body

    def type_check(self):
        if self.count.get_type() != NATURAL:
            error(self.line, "Count of 'repeat' instruction is not natural.")

        type_check_commands(self.body)

    def get_code(self) -> str:
        pass

    def execute(self):
        pass

    def print(self, indent_level: int):
        indent(indent_level)
        print("repeat ", self.count, " do")
        print_commands(indent_level + 1, self.body)

        indent(indent_level)
        print("done")


def type_check_commands(commands: List[Instruction]):
    if not commands:
        return

    for it in commands:
        it.type_check()


def execute_commands(commands: List[Instruction]):
    pass


def generate_code(commands: List[Instruction]):
    pass


def print_program(name: str, commands: List[Instruction]):
    print("program ", name)

    for key, value in symbol_table.items():
        value: Symbol
        print(INDENT, "boolean" if value.symbol_type == 0 else "natural", " ", value.name)

    print("begin")
    print_commands(1, commands)
    print("end")


def error(line: int, text: str):
    print("Line ", line, ": Error: ", text)
    exit(1)


def delete_commands(commands: List[Instruction]):
    pass


def print_commands(indent_level: int, commands: List[Instruction]):
    for it in commands:
        it.print(indent_level)


def indent(indent_level: int):
    print(INDENT * indent_level, end="")


def next_label() -> str:
    pass


def generate_code_of_commands(out: str, commands: List[Instruction]):
    pass


def get_type_name(t: int) -> str:
    pass


def get_register(t: int) -> str:
    pass


def eq_code(t: int) -> str:
    pass


def operator_code(op: str) -> str:
    pass


def operand_type(op: str) -> int:
    if op in ["+", "-", "*", "/", "%", "<", ">", "<=", ">="]:
        return NATURAL
    else:
        return BOOLEAN


def return_type(op: str) -> int:
    if op in ["+", "-", "*", "/", "%"]:
        return NATURAL
    else:
        return BOOLEAN

