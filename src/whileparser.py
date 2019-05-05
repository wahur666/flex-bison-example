from sly import Parser

from implementation import *
from optimizer import Optimizer
from whilelexel import WhileLexer


class WhileParser(Parser):
    tokens = WhileLexer.tokens
    start = 'sstart'

    precedence = (
        ('left', OR),
        ('left', AND),
        ('left', EQ),
        ('left', LS, GR, LSE, GRE),
        ('left', ADD, SUB),
        ('left', MUL, DIV, MOD),
        ('right', BNOT),
    )

    def __init__(self):
        self.names = {}

    @_('')
    def empty(self, p):
        pass

    @_('PRG ID declarations BEG commands END')
    def sstart(self, p):
        type_check_commands(p.commands)

        commands = p.commands

        Optimizer().optimalize_const_merge(commands)
        print_program(p.ID, p.commands)
        print("-"*20)
        generate_code(commands)
        # print(symbol_table)
        # print(value_table)
        # print(commands)

    @_('empty')
    def declarations(self, p):
        pass

    @_('declarations declaration')
    def declarations(self, p):
        pass

    @_('BOO ID')
    def declaration(self, p):
        Symbol(p.lineno, p.ID, BOOLEAN).declare()

    @_('NAT ID')
    def declaration(self, p):
        Symbol(p.lineno, p.ID, NATURAL).declare()

    @_('empty')
    def commands(self, p):
        return []

    @_('commands command')
    def commands(self, p):
        p.commands.append(p.command)
        return p.commands

    @_('REA OP ID CL')
    def command(self, p):
        return ReadInstruction(p.lineno, p.ID)

    @_('WRI OP expression CL')
    def command(self, p):
        return WriteInstruction(p.lineno, p.expression)

    @_('ID ASN expression')
    def command(self, p):
        return AssignInstruction(p.lineno, p.ID, p.expression)

    @_('IF expression THE commands EIF')
    def command(self, p):
        return IfInstruction(p.lineno, p.expression, p.commands, [])

    @_('IF expression THE commands ELS commands EIF')
    def command(self, p):
        return IfInstruction(p.lineno, p.expression, p.commands0, p.commands1)

    @_('WHI expression DO commands DON')
    def command(self, p):
        return WhileInstruction(p.lineno, p.expression, p.commands)

    @_('REP expression DO commands DON')
    def command(self, p):
        return RepeatInstruction(p.lineno, p.expression, p.commands)

    @_('NUM')
    def expression(self, p):
        return NumberExpression(p.NUM)

    @_('TRU')
    def expression(self, p):
        return BooleanExpression(True)

    @_('FAL')
    def expression(self, p):
        return BooleanExpression(False)

    @_('ID')
    def expression(self, p):
        return IdExpression(p.lineno, p.ID)

    @_('expression ADD expression')
    def expression(self, p):
        return BinopExpression(p.lineno, "+", p.expression0, p.expression1)

    @_('expression SUB expression')
    def expression(self, p):
        return BinopExpression(p.lineno, "-", p.expression0, p.expression1)

    @_('expression MUL expression')
    def expression(self, p):
        return BinopExpression(p.lineno, "*", p.expression0, p.expression1)

    @_('expression DIV expression')
    def expression(self, p):
        return BinopExpression(p.lineno, "/", p.expression0, p.expression1)

    @_('expression MOD expression')
    def expression(self, p):
        return BinopExpression(p.lineno, "%", p.expression0, p.expression1)

    @_('expression LS expression')
    def expression(self, p):
        return BinopExpression(p.lineno, "<", p.expression0, p.expression1)

    @_('expression GR expression')
    def expression(self, p):
        return BinopExpression(p.lineno, ">", p.expression0, p.expression1)

    @_('expression LSE expression')
    def expression(self, p):
        return BinopExpression(p.lineno, "<=", p.expression0, p.expression1)

    @_('expression GRE expression')
    def expression(self, p):
        return BinopExpression(p.lineno, ">=", p.expression0, p.expression1)

    @_('expression AND expression')
    def expression(self, p):
        return BinopExpression(p.lineno, "and", p.expression0, p.expression1)

    @_('expression OR expression')
    def expression(self, p):
        return BinopExpression(p.lineno, "or", p.expression0, p.expression1)

    @_('expression EQ expression')
    def expression(self, p):
        return BinopExpression(p.lineno, "=", p.expression0, p.expression1)

    @_('NOT expression %prec BNOT')
    def expression(self, p):
        return NotExpression(p.lineno, "not", p.expression)

    @_('OP expression CL')
    def expression(self, p):
        return p.expression

    @_('OP expression QM expression COL expression CL')
    def expression(self, p):
        return TernaryExpression(p.lineno, p.expression0, p.expression1, p.expression2)
