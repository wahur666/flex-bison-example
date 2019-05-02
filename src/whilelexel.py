from sly import Lexer

class WhileLexer(Lexer):
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
    LSE = r'<='
    GRE = r'>='
    LS  = r'<'
    GR  = r'>'
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