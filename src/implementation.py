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
            error(self.line, "Re-declared variable: {0}".format(self.name))
        symbol_table[self.name] = self

    def get_code(self) -> str:
        return "{0}: resb {1} \t; variable: {2}\n".format(self.label, self.get_size(), self.name)

    def get_size(self) -> int:
        if self.symbol_type == BOOLEAN:
            return 1
        else:
            return 4


symbol_table: Dict[str, Symbol] = {}
value_table: Dict[str, int] = {}


class Expression:

    def get_type(self) -> int:
        pass

    def get_code(self) -> str:
        pass

    def get_value(self) -> int:
        pass

    def print(self):
        print(self.to_string())

    def to_string(self) -> str:
        pass


class NumberExpression(Expression):

    def __init__(self, text: str):
        self.value = int(text)

    def get_type(self) -> int:
        return NATURAL

    def get_code(self) -> str:
        return "mov eax,{0}\n".format(self.value)

    def get_value(self) -> int:
        return self.value

    def to_string(self) -> str:
        return str(self.value)


class BooleanExpression(Expression):

    def __init__(self, value: bool):
        self.value = value

    def get_type(self) -> int:
        return BOOLEAN

    def get_code(self) -> str:
        return "mov al,{0}\n".format(1 if self.value else 0)

    def get_value(self) -> int:
        return int(self.value)

    def to_string(self) -> str:
        return "true" if self.value else "false"


class IdExpression(Expression):

    def __init__(self, line: int, name: str):
        self.line = line
        self.name = name

    def get_type(self) -> int:
        if self.name not in symbol_table:
            error(self.line, "Undefined variable: {0}".format(self.name))
        return symbol_table[self.name].symbol_type

    def get_code(self) -> str:
        if self.name not in symbol_table:
            error(self.line, "Undefined variable: {0}".format(self.name))
        return "mov eax,[{0}]\n".format(symbol_table[self.name].label)

    def get_value(self) -> int:
        if self.name not in symbol_table:
            error(self.line, "Variable has not been initialized {0}".format(self.name))
        return value_table[self.name]

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
                error(self.line, "Left operand of '{0}' has unexpected type.".format(self.op))
            if self.right.get_type() != operand_type(self.op):
                error(self.line, "Right operand of '{0}' has unexpected type.".format(self.op))
        return return_type(self.op)

    def get_code(self) -> str:
        s = self.left.get_code()
        s += "push eax\n"
        s += self.right.get_code()
        s += "pop eax\n"
        s += eq_code(self.left.get_type() if self.op == "=" else operator_code(self.op))
        return s

    def get_value(self) -> int:
        left_value: int = self.left.get_value()
        right_value: int = self.right.get_value()
        if self.op == "+":
            return left_value + right_value
        elif self.op == "-":
            return left_value - right_value
        elif self.op == "*":
            return left_value * right_value
        elif self.op == "/":
            return left_value // right_value
        elif self.op == "%":
            return left_value % right_value
        elif self.op == "<":
            return left_value < right_value
        elif self.op == ">":
            return left_value > right_value
        elif self.op == "<=":
            return left_value <= right_value
        elif self.op == ">=":
            return left_value <= right_value
        elif self.op == "and":
            return left_value and right_value
        elif self.op == "or":
            return left_value or right_value
        elif self.op == "=":
            return left_value == right_value
        else:
            error(self.line, "Unkonwn operator: {0}".format(self.op))

    def to_string(self) -> str:
        return "({0}) {1} ({2})".format(self.left.to_string(), self.op, self.right.to_string())


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
        s = self.operand.get_code()
        s += "xor al,1\n"
        return s

    def get_value(self) -> int:
        return int(not self.operand.get_value())

    def to_string(self) -> str:
        return "{0} ({1})".format(self.op, self.operand.to_string())


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
        else_label = next_label()
        end_label = next_label()
        s = self.condition.get_code()
        s += "cmp al,1\n"
        s += "jne near {0}\n".format(else_label)
        s += self.true_expression.get_code()
        s += "jmp {0}\n".format(end_label)
        s += "{0}:\n".format(else_label)
        s += self.false_expression.get_code()
        s += "{0}:\n".format(end_label)
        return s

    def get_value(self) -> int:
        if self.condition.get_value():
            return self.true_expression.get_value()
        else:
            return self.false_expression.get_value()

    def to_string(self) -> str:
        return "({0} ? {1} : {2})".format(self.condition.to_string(), self.true_expression.to_string(),
                                          self.false_expression.to_string())


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
            error(self.line, "Undefined variable: {0}".format(self.left))
        if symbol_table[self.left].symbol_type != self.right.get_type():
            error(self.line, "Left and right hand sides of assignment are of different types.")

    def get_code(self) -> str:
        s = self.right.get_code()
        s += "mov [{0}], {1}\n".format(symbol_table[self.left].label, get_register(symbol_table[self.left].symbol_type))
        return s

    def execute(self):
        value_table[self.left] = self.right.get_value()

    def print(self, indent_level: int):
        indent(indent_level)
        print("{0} := {1}".format(self.left, self.right.to_string()))


class ReadInstruction(Instruction):

    def __init__(self, line: int, id: str):
        super().__init__(line)
        self.id = id

    def type_check(self):
        if self.id not in symbol_table:
            error(self.line, "Undefined variable: {0}".format(self.id))

    def get_code(self) -> str:
        t = symbol_table[self.id].symbol_type
        s = "call read_{0}\n".format(get_type_name(t))
        s += "mov [{0}],{1}\n".format(symbol_table[self.id].label, get_type_name(t))
        return s

    def execute(self):
        input_line = input()
        if symbol_table[self.id].symbol_type == NATURAL:
            value_table[self.id] = int(input_line)
        elif symbol_table[self.id].symbol_type == BOOLEAN:
            if input_line == "true":
                value_table[self.id] = 1
            else:
                value_table[self.id] = 0

    def print(self, indent_level: int):
        indent(indent_level)
        print("read({0})".format(self.id))


class WriteInstruction(Instruction):

    def __init__(self, line: int, exp: Expression):
        super().__init__(line)
        self.exp = exp
        self.exp_type = None

    def type_check(self):
        self.exp_type = self.exp.get_type()

    def get_code(self) -> str:
        s = self.exp.get_code()
        if self.exp_type == BOOLEAN:
            s += "and eax,1\n"
        s += "push eax\n"
        s += "call write_{0}\n".format(get_type_name(self.exp_type))
        return s

    def execute(self):
        if self.exp_type == NATURAL:
            print(self.exp.get_value())
        else:
            print("true" if self.exp.get_value() else "false")

    def print(self, indent_level: int):
        indent(indent_level)
        print("write({0})".format(self.exp.to_string()))


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
        else_label = next_label()
        end_label = next_label()
        s = self.condition.get_code()
        s += "cmp al,1\n"
        s += "jne near {0}\n".format(else_label)
        s += generate_code_of_commands(self.true_branch)
        s += "jmp {0}\n".format(end_label)
        s += "{0}:\n".format(else_label)
        s += generate_code_of_commands(self.false_branch)
        s += "{0}:\n".format(end_label)
        return s

    def execute(self):
        if self.condition.get_value():
            execute_commands(self.true_branch)
        else:
            execute_commands(self.false_branch)

    def print(self, indent_level: int):
        indent(indent_level)
        print("if {0} then".format(self.condition.to_string()))
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
        begin_label = next_label()
        end_label = next_label()
        s = "{0}:\n".format(begin_label)
        s += self.condition.get_code()
        s += "cmp al,1\n"
        s += "jne near {0}\n".format(end_label)
        s += generate_code_of_commands(self.body)
        s += "jmp {0}\n".format(begin_label)
        s += "{0}:\n".format(end_label)
        return s

    def execute(self):
        while self.condition.get_value():
            execute_commands(self.body)

    def print(self, indent_level: int):
        indent(indent_level)
        print("while {0} do".format(self.condition.to_string()))
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
        begin_label = next_label()
        s = self.count.get_code()
        s += "mov ecx,eax\n"
        s += "{0}:\n".format(begin_label)
        s += "push ecx\n"
        s += generate_code_of_commands(self.body)
        s += "pop ecx\n"
        s += "loop {0}\n".format(begin_label)
        return s

    def execute(self):
        for i in range(self.count.get_value(), 0, -1):
            execute_commands(self.body)

    def print(self, indent_level: int):
        indent(indent_level)
        print("repeat {0} do".format(self.count.get_value()))
        print_commands(indent_level + 1, self.body)

        indent(indent_level)
        print("done")


def type_check_commands(commands: List[Instruction]):
    for it in commands:
        it.type_check()


def execute_commands(commands: List[Instruction]):
    for command in commands:
        command.execute()


def print_program(name: str, commands: List[Instruction]):
    print("program {0}".format(name))

    for value in symbol_table.values():
        print("{0}{1} {2}".format(INDENT, "boolean" if value.symbol_type == 0 else "natural", value.name))

    print("begin")
    print_commands(1, commands)
    print("end")


def error(line: int, text: str):
    print("Line {1}: Error: {1}".format(line, text))
    exit(1)


def print_commands(indent_level: int, commands: List[Instruction]):
    for it in commands:
        it.print(indent_level)


def indent(indent_level: int):
    print(INDENT * indent_level, end="")


def next_label() -> str:
    global ID
    ID += 1
    return "label{0}".format(ID)


def generate_code(commands: List[Instruction]):
    s = "global main\n"
    s += "extern write_natural\n"
    s += "extern read_natural\n"
    s += "extern write_boolean\n"
    s += "extern read_boolean\n"
    s += "\n"
    s += "section .bss\n"
    for symbol in symbol_table.values():
        s += symbol.get_code()
    s += "\n"
    s += "section .text\n"
    s += "main:\n"
    s += generate_code_of_commands(commands)
    s += "xor eax,eax\n"
    s += "ret\n"
    print(s)


def generate_code_of_commands(commands: List[Instruction]) -> str:
    s = ""
    for command in commands:
        s += command.get_code()
    return s


def get_type_name(t: int) -> str:
    if t == BOOLEAN:
        return "boolean"
    else:
        return "natural"


def get_register(t: int) -> str:
    if t == BOOLEAN:
        return "al"
    else:
        return "eax"


def eq_code(t: int) -> str:
    if t == NATURAL:
        s = "cmp eax, ecx\n"
    else:
        s = "cmp al, cl\n"
    s += "mov al,0\n"
    s += "mov cx,1\n"
    s += "cmove ax, cx\n"
    return s


def operator_code(op: str) -> str:
    s = ""
    if op == "+":
        s += "add eax,ecx\n"
    elif op == "-":
        s += "sub eax,ecx\n"
    elif op == "*":
        s += "xor edx,edx\n"
        s += "mul ecx\n"
    elif op == "/":
        s += "xor edx,edx\n"
        s += "div ecx\n"
    elif op == "%":
        s += "xor edx,edx\n"
        s += "div ecx\n"
        s += "mov eax,edx\n"
    elif op == "<":
        s += "cmp eax,ecx\n"
        s += "mov al,0\n"
        s += "mov cx,1\n"
        s += "cmovb ax,cx\n"
    elif op == "<=":
        s += "cmp eax,ecx\n"
        s += "mov al,0\n"
        s += "mov cx,1\n"
        s += "cmovbe ax,cx\n"
    elif op == ">":
        s += "cmp eax,ecx\n"
        s += "mov al,0\n"
        s += "mov cx,1\n"
        s += "cmova ax,cx\n"
    elif op == ">=":
        s += "cmp eax,ecx\n"
        s += "mov al,0\n"
        s += "mov cx,1\n"
        s += "cmovae ax,cx\n"
    elif op == "and":
        s += "cmp al,1\n"
        s += "cmove ax,cx\n"
    elif op == "or":
        s += "cmp al,0\n"
        s += "cmove ax,cx\n"
    else:
        error(-1, "Bug: Unsupported binary operator: {0}".format(op))
    return s


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
