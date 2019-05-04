from typing import Tuple

from implementation import *


class OptimizableSymbol:

    def __init__(self, name, value=None, optimizable = False):
        self.name = name
        self.value = value
        self.optimizable = optimizable

    def __str__(self) -> str:
        return "OptimizableSymbol<Name: {0}, Value: {1}, Optimizable: {2}>".format(self.name, self.value, self.optimizable)

    def __repr__(self) -> str:
        return "OptimizableSymbol<Name: {0}, Value: {1}, Optimizable: {2}>".format(self.name, self.value, self.optimizable)


class OptStruct:

    def __init__(self, optimizable: bool, value: int, type: int):
        self.optimizable = optimizable
        self.value = value
        self.type = type

    def __str__(self) -> str:
        return "OptStruct<Optimizable: {0}, Value: {1}, Type: {2}>".format(self.optimizable, self.value, "BOOLEAN" if self.type == BOOLEAN else "NATURAL")

    def __repr__(self) -> str:
        return "OptStruct<Optimizable: {0}, Value: {1}, Type: {2}>".format(self.optimizable, self.value, "BOOLEAN" if self.type == BOOLEAN else "NATURAL")


class Optimizer:

    def __init__(self):
        self.opt_table: Dict[str, OptimizableSymbol] = {}

    def simpler_node(self, opt_struct: OptStruct):
        if opt_struct.type == NATURAL:
            return NumberExpression(str(opt_struct.value))
        else:
            return BooleanExpression(bool(opt_struct.value))

    def optimalize_const_merge(self, commands: List[Instruction]):
        for command in commands:
            if isinstance(command, AssignInstruction):
                opt_struct = self.opt_expresstion(command.right)
                #print(opt_struct)
                if opt_struct.optimizable:
                    command.right = self.simpler_node(opt_struct)
                    self.opt_table[command.left] = OptimizableSymbol(command.left, opt_struct.value, True)
                else:
                    self.opt_table[command.left] = OptimizableSymbol(command.left)

            elif isinstance(command, ReadInstruction):
                self.opt_table[command.id] = OptimizableSymbol(command.id)

            elif isinstance(command, WriteInstruction):
                opt_struct = self.opt_expresstion(command.exp)
                if opt_struct.optimizable:
                    command.exp = self.simpler_node(opt_struct)

            elif isinstance(command, IfInstruction):
                opt_struct = self.opt_expresstion(command.condition)
                if opt_struct.optimizable:
                    command.condition = self.simpler_node(opt_struct)
                self.optimalize_const_merge(command.true_branch)
                self.optimalize_const_merge(command.false_branch)

            elif isinstance(command, WhileInstruction):
                opt_struct = self.opt_expresstion(command.condition)
                if opt_struct.optimizable:
                    command.condition = self.simpler_node(opt_struct)
                self.optimalize_const_merge(command.body)

            elif isinstance(command, RepeatInstruction):
                opt_struct = self.opt_expresstion(command.count)
                if opt_struct.optimizable:
                    command.condition = self.simpler_node(opt_struct)
                self.optimalize_const_merge(command.body)

        #print_commands(0, commands)


    def opt_expresstion(self, exp: Expression) -> OptStruct:
        if isinstance(exp, NumberExpression):
            return OptStruct(True, exp.get_value(), NATURAL)

        elif isinstance(exp, BooleanExpression):
            return OptStruct(True, exp.get_value(), BOOLEAN)

        elif isinstance(exp, IdExpression):
            if exp.name in self.opt_table and self.opt_table[exp.name].optimizable:
                return OptStruct(True, self.opt_table[exp.name].value, exp.get_type())
            else:
                return OptStruct(False, -1, -1)

        elif isinstance(exp, NotExpression):
            opt_struct = self.opt_expresstion(exp.operand)
            if opt_struct.optimizable:
                return OptStruct(True, not opt_struct.value, BOOLEAN)
            else:
                return OptStruct(False, -1, -1)

        elif isinstance(exp, BinopExpression):
            opt_struct1 = self.opt_expresstion(exp.left)
            if opt_struct1.optimizable:
                exp.left = self.simpler_node(opt_struct1)

            opt_struct2 = self.opt_expresstion(exp.right)
            if opt_struct2.optimizable:
                exp.right = self.simpler_node(opt_struct2)

            if opt_struct1.optimizable and opt_struct2.optimizable:
                left_value = opt_struct1.value
                right_value = opt_struct2.value
                if exp.op == "+":
                    value =  left_value + right_value
                    type = NATURAL
                elif exp.op == "-":
                    value = left_value - right_value
                    type = NATURAL
                elif exp.op == "*":
                    value = left_value * right_value
                    type = NATURAL
                elif exp.op == "/":
                    value = left_value // right_value
                    type = NATURAL
                elif exp.op == "%":
                    value = left_value % right_value
                    type = NATURAL
                elif exp.op == "<":
                    value = left_value < right_value
                    type = BOOLEAN
                elif exp.op == ">":
                    value = left_value > right_value
                    type = BOOLEAN
                elif exp.op == "<=":
                    value = left_value <= right_value
                    type = BOOLEAN
                elif exp.op == ">=":
                    value = left_value <= right_value
                    type = BOOLEAN
                elif exp.op == "and":
                    value = left_value and right_value
                    type = BOOLEAN
                elif exp.op == "or":
                    value = left_value or right_value
                    type = BOOLEAN
                else:
                    value = left_value == right_value
                    type = BOOLEAN

                return OptStruct(True, value, type)
            else:
                return OptStruct(False, -1, -1)

        elif isinstance(exp, TernaryExpression):
            opt_struct = self.opt_expresstion(exp.condition)

            if opt_struct.optimizable:
                exp.condition = self.simpler_node(opt_struct)
                if opt_struct.value:
                    return self.opt_expresstion(exp.true_expression)
                else:
                    return self.opt_expresstion(exp.false_expression)
            else:
                return OptStruct(False, -1, -1)
