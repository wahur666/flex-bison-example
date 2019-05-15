# -*- coding: utf-8 -*-
from typing import Tuple

from implementation import *

FLIPPABLE_OPERANDS = ["+", "*", "and", "or"]

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
                opt_struct = self.opt_expresstion(command, command.right)
                #print(opt_struct)
                if opt_struct and opt_struct.optimizable:
                    command.right = self.simpler_node(opt_struct)
                    self.opt_table[command.left] = OptimizableSymbol(command.left, opt_struct.value, True)
                else:
                    self.opt_table[command.left] = OptimizableSymbol(command.left)

            elif isinstance(command, ReadInstruction):
                self.opt_table[command.id] = OptimizableSymbol(command.id)

            elif isinstance(command, WriteInstruction):
                opt_struct = self.opt_expresstion(command, command.exp)
                if opt_struct.optimizable:
                    command.exp = self.simpler_node(opt_struct)

            elif isinstance(command, IfInstruction):
                opt_struct = self.opt_expresstion(command, command.condition)
                if opt_struct.optimizable:
                    command.condition = self.simpler_node(opt_struct)
                self.optimalize_const_merge(command.true_branch)
                self.optimalize_const_merge(command.false_branch)

            elif isinstance(command, WhileInstruction):
                opt_struct = self.opt_expresstion(command, command.condition)
                if opt_struct.optimizable:
                    command.condition = self.simpler_node(opt_struct)
                self.optimalize_const_merge(command.body)

            elif isinstance(command, RepeatInstruction):
                opt_struct = self.opt_expresstion(command, command.count)
                if opt_struct.optimizable:
                    command.count = self.simpler_node(opt_struct)
                self.optimalize_const_merge(command.body)

        #print_commands(0, commands)


    def opt_expresstion(self, root: Instruction, exp: Expression) -> OptStruct:
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
            opt_struct = self.opt_expresstion(root, exp.operand)
            if opt_struct.optimizable:
                return OptStruct(True, not opt_struct.value, BOOLEAN)
            else:
                return OptStruct(False, -1, -1)

        elif isinstance(exp, BinopExpression):
            main_expression_left = self.opt_expresstion(root, exp.left)
            if main_expression_left.optimizable:
                exp.left = self.simpler_node(main_expression_left)

            main_expression_right = self.opt_expresstion(root, exp.right)
            if main_expression_right.optimizable:
                exp.right = self.simpler_node(main_expression_right)

            if main_expression_left.optimizable and main_expression_right.optimizable:
                left_value = main_expression_left.value
                right_value = main_expression_right.value
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
            elif not main_expression_left.optimizable and main_expression_right.optimizable:
                ''' a jobb oldal optimalizalhato
                    megézzük hogy a bal oldal miért nem optimalizálható
                    nézzük meg összetett kifelyezés van-e a bal oldalon '''

                if isinstance(exp.left, BinopExpression):
                    not_optimalizable_expression: BinopExpression = exp.left
                    ''' nézzük meg hogy megegyeznek-e az operátorok, a nem kiértékelhető
                        és a rákövetkező műveletnél, és az asszociativ-e '''

                    if not_optimalizable_expression.op == exp.op and exp.op in FLIPPABLE_OPERANDS:
                        'bal oldalon ki kell derinteni miert nem optimalizalhato'
                        not_optimalizable_left_expression = self.opt_expresstion(root, not_optimalizable_expression.left)
                        not_optimalizable_right_expression = self.opt_expresstion(root, not_optimalizable_expression.right)

                        if not_optimalizable_left_expression.optimizable:
                            'ha bal oldal optimalizalhato akkor a jobb a gond'
                            new_optimlaizable_expression = BinopExpression(exp.line, exp.op, exp.right, not_optimalizable_expression.left)
                            optimalized_expression = self.simpler_node(self.opt_expresstion(root, new_optimlaizable_expression))
                            new_expression = BinopExpression(exp.line, exp.op, not_optimalizable_expression.right, optimalized_expression)
                            # exp = new_expression
                            self.replace_expression(root, exp, new_expression)
                            return self.opt_expresstion(root, new_expression)

                        elif not_optimalizable_right_expression.optimizable:
                            'ha jobb oldal optimalizalhato akkor a bal a gond'
                            new_optimlaizable_expression = BinopExpression(exp.line, exp.op, exp.right, not_optimalizable_expression.right)
                            optimalized_expression = self.simpler_node(self.opt_expresstion(root, new_optimlaizable_expression))
                            new_expression = BinopExpression(exp.line, exp.op, not_optimalizable_expression.left, optimalized_expression)
                            # exp = new_expression
                            self.replace_expression(root, exp, new_expression)
                            return self.opt_expresstion(root, new_expression)
                        else:
                            return OptStruct(False, -1, -1)
                else:
                    'semleges elem vizsgalat, jobb oldal optimalizalhato'
                    if exp.op == "+":
                        if self.opt_expresstion(root, exp.right).value == 0:
                            self.replace_expression(root, exp, exp.left)
                    elif exp.op == "-":
                        if self.opt_expresstion(root, exp.right).value == 0:
                            self.replace_expression(root, exp, exp.left)
                    elif exp.op == "*":
                        if self.opt_expresstion(root, exp.right).value == 1:
                            self.replace_expression(root, exp, exp.left)
                    elif exp.op == "/":
                        if self.opt_expresstion(root, exp.right).value == 1:
                            self.replace_expression(root, exp, exp.left)
                    elif exp.op == "and":
                        if self.opt_expresstion(root, exp.right).value == 1:
                            self.replace_expression(root, exp, exp.left)
                        else:
                            self.replace_expression(root, exp, BooleanExpression(False))
                            return OptStruct(True, False, BOOLEAN)
                    elif exp.op == "or":
                        if self.opt_expresstion(root, exp.right).value == 1:
                            self.replace_expression(root, exp, BooleanExpression(True))
                            return OptStruct(True, True, BOOLEAN)
                        else:
                            self.replace_expression(root, exp, exp.left)

                    return OptStruct(False, -1, -1)

            elif main_expression_left.optimizable and not main_expression_right.optimizable:
                'semleges elem vizsgalat, bal oldal optimalizalhato'
                if exp.op == "+":
                    if self.opt_expresstion(root, exp.left).value == 0:
                        self.replace_expression(root, exp, exp.right)
                elif exp.op == "*":
                    if self.opt_expresstion(root, exp.left).value == 1:
                        self.replace_expression(root, exp, exp.right)
                elif exp.op == "and":
                    if self.opt_expresstion(root, exp.left).value == 1:
                        self.replace_expression(root, exp, exp.right)
                    else:
                        self.replace_expression(root, exp, BooleanExpression(False))
                        return OptStruct(True, False, BOOLEAN)
                elif exp.op == "or":
                    if self.opt_expresstion(root, exp.left).value == 1:
                        self.replace_expression(root, exp, BooleanExpression(True))
                        return OptStruct(True, True, BOOLEAN)
                    else:
                        self.replace_expression(root, exp, exp.right)
                return OptStruct(False, -1, -1)
            else:
                'ez csak akkor lehet ha egyszerre tobb nem kotott valtozo van'
                if isinstance(exp.left, BinopExpression):
                    not_optimalizable_expression: BinopExpression = exp.left
                    'megkeressuk van e legalabb 1 dolog amit ki lehet hozni'

                    if not_optimalizable_expression.op == exp.op and exp.op in FLIPPABLE_OPERANDS:
                        not_optimalizable_left_expression = self.opt_expresstion(root, not_optimalizable_expression.left)
                        not_optimalizable_right_expression = self.opt_expresstion(root, not_optimalizable_expression.right)

                        if not_optimalizable_left_expression.optimizable:
                            'bal oldalon van egy optimalizalhato'
                            'csoportositjuk a ket nem optimalizalhatot'
                            new_not_optimalizable_expression = BinopExpression(exp.line, exp.op, not_optimalizable_expression.right, exp.right)

                            'azaonos valtozo egysegesites'
                            if new_not_optimalizable_expression.op == "-":
                                if new_not_optimalizable_expression.left == new_not_optimalizable_expression.right:
                                    new_not_optimalizable_expression = NumberExpression("0")
                            elif new_not_optimalizable_expression.op == "/":
                                if new_not_optimalizable_expression.left == new_not_optimalizable_expression.right:
                                    new_not_optimalizable_expression = NumberExpression("1")
                            elif new_not_optimalizable_expression.op == "%":
                                if new_not_optimalizable_expression.left == new_not_optimalizable_expression.right:
                                    new_not_optimalizable_expression = NumberExpression("0")
                            elif new_not_optimalizable_expression.op == "and":
                                if new_not_optimalizable_expression.left == new_not_optimalizable_expression.right:
                                    new_not_optimalizable_expression = new_not_optimalizable_expression.left
                            elif new_not_optimalizable_expression.op == "or":
                                if new_not_optimalizable_expression.left == new_not_optimalizable_expression.right:
                                    new_not_optimalizable_expression = new_not_optimalizable_expression.left

                            new_expression = BinopExpression(exp.line, exp.op, new_not_optimalizable_expression, not_optimalizable_expression.left)
                            # exp = new_expression
                            self.replace_expression(root, exp, new_expression)
                            return self.opt_expresstion(root, new_expression)
                        elif not_optimalizable_right_expression.optimizable:
                            'jobb oldalon van egy optimalizalhato'
                            'csoportositjuk a ket nem optimalizalhatot'
                            new_not_optimalizable_expression = BinopExpression(exp.line, exp.op, not_optimalizable_expression.left, exp.right)

                            'azaonos valtozo egysegesites'
                            if new_not_optimalizable_expression.op == "-":
                                if new_not_optimalizable_expression.left == new_not_optimalizable_expression.right:
                                    new_not_optimalizable_expression = NumberExpression("0")
                            elif new_not_optimalizable_expression.op == "/":
                                if new_not_optimalizable_expression.left == new_not_optimalizable_expression.right:
                                    new_not_optimalizable_expression = NumberExpression("1")
                            elif new_not_optimalizable_expression.op == "%":
                                if new_not_optimalizable_expression.left == new_not_optimalizable_expression.right:
                                    new_not_optimalizable_expression = NumberExpression("0")
                            elif new_not_optimalizable_expression.op == "and":
                                if new_not_optimalizable_expression.left == new_not_optimalizable_expression.right:
                                    new_not_optimalizable_expression = new_not_optimalizable_expression.left
                            elif new_not_optimalizable_expression.op == "or":
                                if new_not_optimalizable_expression.left == new_not_optimalizable_expression.right:
                                    new_not_optimalizable_expression = new_not_optimalizable_expression.left

                            new_expression = BinopExpression(exp.line, exp.op, new_not_optimalizable_expression,
                                                             not_optimalizable_expression.right)
                            #exp = new_expression
                            self.replace_expression(root, exp, new_expression)
                            return self.opt_expresstion(root, new_expression)
                        else:
                            return OptStruct(False, -1, -1)
                else:
                    'azaonos valtozo egysegesites'
                    if exp.op == "-":
                        if isinstance(exp.left, IdExpression) and isinstance(exp.right, IdExpression) and exp.left.name == exp.right.name:
                            self.replace_expression(root, exp, NumberExpression("0"))
                    elif exp.op == "/":
                        if isinstance(exp.left, IdExpression) and isinstance(exp.right, IdExpression) and exp.left.name == exp.right.name:
                            self.replace_expression(root, exp, NumberExpression("1"))
                    elif exp.op == "%":
                        if isinstance(exp.left, IdExpression) and isinstance(exp.right, IdExpression) and exp.left.name == exp.right.name:
                            self.replace_expression(root, exp, NumberExpression("0"))
                    elif exp.op == "and":
                        if isinstance(exp.left, IdExpression) and isinstance(exp.right, IdExpression) and exp.left.name == exp.right.name:
                            self.replace_expression(root, exp, exp.left)
                    elif exp.op == "or":
                        if isinstance(exp.left, IdExpression) and isinstance(exp.right, IdExpression) and exp.left.name == exp.right.name:
                            self.replace_expression(root, exp, exp.left)
                return OptStruct(False, -1, -1)

        elif isinstance(exp, TernaryExpression):
            opt_struct = self.opt_expresstion(root, exp.condition)

            if opt_struct.optimizable:
                exp.condition = self.simpler_node(opt_struct)
                if opt_struct.value:
                    return self.opt_expresstion(root, exp.true_expression)
                else:
                    return self.opt_expresstion(root, exp.false_expression)
            else:
                return OptStruct(False, -1, -1)
        return OptStruct(False, -1, -1)

    def replace_expression(self, instrcution: Instruction, old_expression: Expression, new_expression: Expression):
        if isinstance(instrcution, AssignInstruction):
            if instrcution.right == old_expression:
                instrcution.right = new_expression
            else:
                self.search_and_replace_expression(instrcution.right, old_expression, new_expression)
        elif isinstance(instrcution, WriteInstruction):
            if instrcution.exp == old_expression:
                instrcution.exp = new_expression
            else:
                self.search_and_replace_expression(instrcution.exp, old_expression, new_expression)
        elif isinstance(instrcution, IfInstruction):
            if instrcution.condition == old_expression:
                instrcution.condition = new_expression
            else:
                self.search_and_replace_expression(instrcution.condition, old_expression, new_expression)
        elif isinstance(instrcution, WhileInstruction):
            if instrcution.condition == old_expression:
                instrcution.condition = new_expression
            else:
                self.search_and_replace_expression(instrcution.condition, old_expression, new_expression)
        elif isinstance(instrcution, RepeatInstruction):
            if instrcution.count == old_expression:
                instrcution.count = new_expression
            else:
                self.search_and_replace_expression(instrcution.count, old_expression, new_expression)

        return instrcution

    def search_and_replace_expression(self, root_expression: Expression, old_expression: Expression, new_expression: Expression):
        if isinstance(root_expression, BinopExpression):
            if root_expression.right == old_expression:
                root_expression.right = new_expression
            elif root_expression.left == old_expression:
                root_expression.left = new_expression
            else:
                self.search_and_replace_expression(root_expression.right, old_expression, new_expression)
                self.search_and_replace_expression(root_expression.left, old_expression, new_expression)

