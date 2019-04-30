# -----------------------------------------------------------------------------
# calc.py
# -----------------------------------------------------------------------------

from sly import Lexer, Parser

class CalcLexer(Lexer):
    tokens = {
        PRG,
        BEG,
        END,
        BOO,
        NAT,
        REA,
        WRI,
        IF,
        THE,
        ELS,
        EIF,
        WHI,
        REP,
        DO,
        DON,
        TRU,
        FAL,
        ASN,
        OP,
        CL,
        QM,
        COL,
        ID,
        NUM,

        OR,
        AND,
        EQ,
        LS, GR, LSE, GRE,
        ADD, SUB,
        MUL, DIV, MOD,
        NOT
    }

    PRG = r'program'
    BEG = r'begin'
    BOO = r'boolean'
    NAT = r'natural'
    REA = r'read'
    WRI = r'write'
    IF  = r'if'
    THE = r'then'
    ELS = r'else'
    EIF = r'endif'
    END = r'end'
    WHI = r'while'
    REP = r'repeat'
    DON = r'done'
    DO  = r'do'
    TRU = r'true'
    FAL = r'false'
    ASN = r':='
    ADD = r'\+'
    SUB = r'-'
    MUL = r'\*'
    DIV = r'/'
    MOD = r'%'
    LS  = r'<'
    GR  = r'>'
    LSE = r'<='
    GRE = r'>='
    EQ  = r'='
    QM  = r'\?'
    COL = r':'
    AND = r'and'
    OR  = r'or'
    NOT = r'not'
    OP = r'\('
    CL = r'\)'
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    NUM = r'\d+'

    ignore = '[ \t]'

    # Ignored pattern
    ignore_newline = r'\n+'


    # Extra action for newlines
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    ignore_comment = r'#.*'

    def ignore_comment(self, t):
        pass

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1

class CalcParser(Parser):
    tokens = CalcLexer.tokens
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
        self.names = { }

    @_('')
    def empty(self, p):
        pass

    @_('PRG ID declarations BEG commands END')
    def sstart(self, p):
        print(p.ID)

    @_('empty')
    def declarations(self, p):
        pass

    @_('declarations declaration')
    def declarations(self, p):
        pass
        #print(p.declaration)

    @_('BOO ID')
    def declaration(self, p):
        print(p.ID)\

    @_('NAT ID')
    def declaration(self, p):
        print(p.ID)

    @_('empty')
    def commands(self, p):
        pass

    @_('commands command')
    def commands(self, p):
        pass

    @_('REA OP ID CL')
    def command(self, p):
        pass

    @_('WRI OP expression CL')
    def command(self, p):
        pass

    @_('ID ASN expression')
    def command(self, p):
        pass

    @_('IF expression THE commands EIF')
    def command(self, p):
        print("")

    @_('IF expression THE commands ELS commands EIF')
    def command(self, p):
        pass

    @_('WHI expression DO commands DON')
    def command(self, p):
        pass

    @_('REP expression DO commands DON')
    def command(self, p):
        pass

    @_('NUM')
    def expression(self, p):
        pass

    @_('TRU')
    def expression(self, p):
        pass

    @_('FAL')
    def expression(self, p):
        pass

    @_('ID')
    def expression(self, p):
        pass

    @_('expression ADD expression')
    def expression(self, p):
        pass

    @_('expression SUB expression')
    def expression(self, p):
        pass

    @_('expression MUL expression')
    def expression(self, p):
        pass

    @_('expression DIV expression')
    def expression(self, p):
        pass

    @_('expression MOD expression')
    def expression(self, p):
        pass

    @_('expression LS expression')
    def expression(self, p):
        pass

    @_('expression GR expression')
    def expression(self, p):
        pass

    @_('expression LSE expression')
    def expression(self, p):
        pass

    @_('expression GRE expression')
    def expression(self, p):
        pass

    @_('expression AND expression')
    def expression(self, p):
        pass

    @_('expression OR expression')
    def expression(self, p):
        pass

    @_('expression EQ expression')
    def expression(self, p):
        pass

    @_('NOT expression %prec BNOT')
    def expression(self, p):
        pass

    @_('OP expression CL')
    def expression(self, p):
        pass

    @_('OP expression QM expression COL expression CL')
    def expression(self, p):
        pass

    # @_('ID ASN expr')
    # def statement(self, p):
    #     self.names[p.ID] = p.expr
    #
    # @_('expr')
    # def statement(self, p):
    #     print(p.expr)
    #
    # @_('expr ADD expr')
    # def expr(self, p):
    #     return p.expr0 + p.expr1
    #
    # @_('expr SUB expr')
    # def expr(self, p):
    #     return p.expr0 - p.expr1
    #
    # @_('expr MUL expr')
    # def expr(self, p):
    #     return p.expr0 * p.expr1
    #
    # @_('expr DIV expr')
    # def expr(self, p):
    #     return p.expr0 / p.expr1
    #
    # @_('SUB expr %prec UMINUS')
    # def expr(self, p):
    #     return -p.expr
    #
    # @_('OP expr CL')
    # def expr(self, p):
    #     return p.expr
    #
    # @_('NUM')
    # def expr(self, p):
    #     return int(p.NUM)
    #
    # @_('ID')
    # def expr(self, p):
    #     try:
    #         return self.names[p.ID]
    #     except LookupError:
    #         print(f'Undefined name {p.ID!r}')
    #         return 0


def readfile(file_name: str) -> str:
    with open(file_name, 'r') as f:
        return f.read()

if __name__ == '__main__':
    lexer = CalcLexer()
    parser = CalcParser()
    # while True:
    #     try:
    #         text = input('calc > ')
    #     except EOFError:
    #         break
    #     if text:
    #         parser.parse(lexer.tokenize(text))

    text = readfile('../test/00.test')
    tokenz = lexer.tokenize(text)
    parser.parse(tokenz)