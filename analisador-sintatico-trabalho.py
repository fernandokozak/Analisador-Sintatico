import re
import sys

# Tokens
tokens = [
    ("CONST", r"\bCONST\b"),
    ("VAR", r"\bVAR\b"),
    ("PROCEDURE", r"\bPROCEDURE\b"),
    ("CALL", r"\bCALL\b"),
    ("BEGIN", r"\bBEGIN\b"),
    ("END", r"\bEND\b"),
    ("IF", r"\bIF\b"),
    ("NOT", r"\bNOT\b"),
    ("THEN", r"\bTHEN\b"),
    ("WHILE", r"\bWHILE\b"),
    ("DO", r"\bDO\b"),
    ("ODD", r"\bODD\b"),
    ("EVEN", r"\bEVEN\b"),
    ("PRINT", r"\bPRINT\b"),
    ("IDENT", r"\b[a-zA-Z_][a-zA-Z0-9_]*\b"),
    ("NUMBER", r"\b\d+\b"),
    ("ASSIGN", r"<-"),
    ("RELATION", r"\/\?|<=|>=|=|>|<|#"),
    ("RELATION2", r'/\?'),
    ("OP", r"[+\-*/]"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("SEMICOLON", r";"),
    ("COMMA", r","),
    ("DOT", r"\.")
    # Adicione mais tokens conforme necessário
]

# Função para tokenizar o código-fonte
def tokenize(code):
    tokens_list = []
    pos = 0
    while pos < len(code):
        match = None
        for token_type, pattern in tokens:
            regex = re.compile(pattern)
            match = regex.match(code, pos)
            if match:
                value = match.group(0)
                tokens_list.append((token_type, value))
                pos = match.end()
                break
        if not match:
            if re.match(r'\s', code[pos]):  # Ignora espaços em branco
                pos += 1
            elif code[pos:pos+2] == '{':  # Ignora comentários
                pos = code.find('}', pos) + 1
                if pos == 0:
                    raise SyntaxError("Comment not closed")
            else:
                raise SyntaxError("Unknown symbol: '{}' at position {}".format(code[pos], pos))
    return tokens_list

current_token_index = 0

# Função para obter o próximo token sem consumi-lo
def next_token():
    global tokenized_source, current_token_index
    if current_token_index < len(tokenized_source):
        return tokenized_source[current_token_index]
    return None

# Função para verificar e consumir o próximo token esperado
def expect(token_type):
    global tokenized_source, current_token_index
    if current_token_index < len(tokenized_source) and (tokenized_source[current_token_index][0] == token_type or tokenized_source[current_token_index][1] == token_type):
        print(tokenized_source[current_token_index])
        current_token_index += 1
    else:
        raise SyntaxError(f"Expected token {token_type} but found {tokenized_source[current_token_index][0]}")

# Função para reportar erro
def error(message):
    raise SyntaxError(message)

def parse_program():
    parse_block()
    expect("DOT")

def parse_block():
    if next_token()[0] == "CONST":
        parse_constants()
    if next_token()[0] == "VAR":
        parse_variables()
    if next_token()[0] == "PROCEDURE":
        parse_procedures()
    parse_statement()  # Assumindo que statement é obrigatório

def parse_constants():
    expect("CONST")
    parse_constdecl()
    expect("SEMICOLON")

def parse_constdecl():
    parse_constdef()
    while next_token()[0] == "COMMA":
        expect("COMMA")
        parse_constdef()

def parse_constdef():
    expect("IDENT")
    expect("=")
    expect("NUMBER")

def parse_variables():
    expect("VAR")
    parse_vardecl()
    expect("SEMICOLON")

def parse_vardecl():
    expect("IDENT")
    while next_token()[0] == "COMMA":
        expect("COMMA")
        expect("IDENT")

def parse_procedures():
    while next_token()[0] == "PROCEDURE":
        parse_procdecl()

def parse_procdecl():
    expect("PROCEDURE")
    expect("IDENT")
    expect("SEMICOLON")
    parse_block()
    expect("SEMICOLON")

def parse_expression():
    # <expression> --> <sign>? <term> <terms>?
    if next_token()[1] in ["+", "-"]:
        parse_sign()
    parse_term()
    while next_token()[1] in ["+", "-"]:
        parse_sign()
        parse_term()

def parse_sign():
    # <sign> --> "+" | "-"
    if next_token()[1] == "+":
        expect("+")
    else:
        expect("-")

def parse_term():
    # <term> --> <factor> <factors>?
    parse_factor()
    while next_token()[1] in ["*", "/"]:
        if next_token()[1] == "*":
            expect("*")
        else:
            expect("/")
        parse_factor()

def parse_condition():
    # <condition> --> "ODD" <expression> | "EVEN" <expression> | <expression> <relation> <expression>
    if next_token()[0] == "ODD":
        expect("ODD")
        parse_expression()
    elif next_token()[0] == "EVEN":
        expect("EVEN")
        parse_expression()
    else:
        parse_expression()
        parse_relation()
        parse_expression()

def parse_relation():
    # <relation> --> "=" | "#" | "<" | "<=" | ">" | ">=" | "/?"
    if next_token()[1] == "=":
        expect("=")
    elif next_token()[1] == "#":
        expect("#")
    elif next_token()[1] == "<":
        expect("<")
    elif next_token()[1] == "<=":
        expect("<=")
    elif next_token()[1] == ">":
        expect(">")
    elif next_token()[1] == ">=":
        expect(">=")
    elif next_token()[1] == "/?":
        expect("/?")


def parse_factor():
    # <factor> --> <Ident> | <Number> | "(" <expression> ")"
    if next_token()[0] == "IDENT":
        expect("IDENT")
    elif next_token()[0] == "NUMBER":
        expect("NUMBER")
    else:
        expect("LPAREN")
        parse_expression()
        expect("RPAREN")
    

def parse_assignment_statement():
    # <statement> --> <Ident> "<-" <expression>
    expect("IDENT")
    expect("ASSIGN")
    parse_expression()

def parse_call_statement():
    # <statement> --> "CALL" <Ident>
    expect("CALL")
    expect("IDENT")

def parse_begin_statement():
    # <statement> --> "BEGIN" <compound statement> "END"
    expect("BEGIN")
    parse_statement()
    expect("SEMICOLON")
    while next_token()[0] != "END":
        parse_statement()
        expect("SEMICOLON")
    expect("END")


def parse_if_statement():
    # <statement> --> "IF" "NOT"? <condition> "THEN" <statement>
    expect("IF")
    if next_token()[0] == "NOT":
        expect("NOT")
    parse_condition()
    expect("THEN")
    parse_statement()

def parse_while_statement():
    # <statement> --> "WHILE" "NOT"? <condition> "DO" <statement>
    expect("WHILE")
    if next_token()[0] == "NOT":
        expect("NOT")
    parse_condition()
    expect("DO")
    parse_statement()

def parse_print_statement():
    # <statement> --> "PRINT" <expression>
    expect("PRINT")
    parse_expression()

def parse_statement():
    try:
        if next_token()[0] == "IDENT":
            parse_assignment_statement()
        elif next_token()[0] == "CALL":
            parse_call_statement()
        elif next_token()[0] == "BEGIN":
            parse_begin_statement()
        elif next_token()[0] == "IF":
            parse_if_statement()
        elif next_token()[0] == "WHILE":
            parse_while_statement()
        elif next_token()[0] == "PRINT":
            parse_print_statement()
        else:
            error(f'Unexpected token {next_token()}')
    except SyntaxError as e:
        print(f"SyntaxError: {e}")
        sys.exit(1)  # Encerra a execução do programa com código de saída 1 (indicando um erro)

if __name__ == "__main__":
    file_path = "/Users/fkoza/OneDrive/Documentos/UFT 2023.2/Compiladores/ex3.pl0mod.txt"
    with open(file_path,'r') as file:
        source_code = file.read()
    tokenized_source = tokenize(source_code)
    parse_program()