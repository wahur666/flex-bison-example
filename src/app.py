from whilelexel import WhileLexer
from whileparser import WhileParser


def readfile(file_name: str) -> str:
    with open(file_name, 'r') as f:
        return f.read()

if __name__ == '__main__':
    lexer = WhileLexer()
    parser = WhileParser()
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