import sys
from pathlib import Path
from enum import Enum

import ply.lex as lex
import ply.yacc as yacc

# -----------------------------------------------------
# Importa o léxico do projeto
# -----------------------------------------------------
import lexico.lexico as lexico

tokens = lexico.tokens

# -----------------------------------------------------
# Rastreamento de blocos BEGIN ... END (para EOF)
# -----------------------------------------------------
begin_stack = []

def track_blocks(lexer):
    """Envolve o lexer para empilhar BEGIN e desempilhar END automaticamente."""
    original_token = lexer.token

    def wrapped():
        tok = original_token()
        if tok:
            if tok.type == 'BEGIN':
                begin_stack.append(tok.lineno)
            elif tok.type == 'END':
                if begin_stack:
                    begin_stack.pop()
        return tok

    lexer.token = wrapped
    return lexer

# -----------------------------------------------------
# Tipos e utilidades semânticas
# -----------------------------------------------------
class Tipo(Enum):
    INT = 1
    BOOL = 2

def nome_tipo(tipo: Tipo | None) -> str:
    if tipo is Tipo.INT:
        return "integer"
    if tipo is Tipo.BOOL:
        return "boolean"
    return "indefinido"

def erro_semantico(mensagem: str, lineno: int) -> None:
    print(f"ERRO SEMÂNTICO (linha {lineno}): {mensagem}")

class SymbolTable:
    def __init__(self) -> None:
        self._symbols: dict[str, dict[str, object]] = {}

    def reset(self) -> None:
        self._symbols.clear()

    def declare_program(self, name: str, lineno: int) -> None:
        if name in self._symbols:
            erro_semantico(f"identificador '{name}' já declarado anteriormente.", lineno)
        else:
            self._symbols[name] = {"categoria": "programa", "tipo": None, "lineno": lineno}

    def declare_variable(self, name: str, tipo: Tipo, lineno: int) -> None:
        if name in self._symbols:
            erro_semantico(f"identificador '{name}' já declarado anteriormente.", lineno)
        else:
            self._symbols[name] = {
                "categoria": "variavel",
                "tipo": tipo,
                "lineno": lineno,
            }

    def lookup(self, name: str) -> dict[str, object] | None:
        return self._symbols.get(name)

symbol_table = SymbolTable()

# -----------------------------------------------------
# Precedência
# -----------------------------------------------------
precedence = (
    ("left", "OR"),
    ("left", "AND"),
    ("nonassoc", "=", "DIFERENTE", "<", "MENOR_IGUAL", ">", "MAIOR_IGUAL"),
    ("left", "+", "-"),
    ("left", "*", "DIV"),
    ("right", "NOT", "NEG"),
)

# -----------------------------------------------------
# Regras Sintáticas + Ações Semânticas
# -----------------------------------------------------
def p_empty(p):
    "empty :"
    p[0] = None

def p_program(p):
    "program : PROGRAM ID ';' block '.'"
    symbol_table.declare_program(p[2], p.lineno(2))

def p_block(p):
    """block : declaration_section compound_cmd
             | compound_cmd"""

def p_declaration_section_single(p):
    "declaration_section : VAR var_declaration_list"

def p_declaration_section_multiple(p):
    "declaration_section : declaration_section VAR var_declaration_list"

def p_var_declaration_list_recursive(p):
    "var_declaration_list : var_declaration_list var_declaration ';'"

def p_var_declaration_list_single(p):
    "var_declaration_list : var_declaration ';'"

def p_var_declaration(p):
    "var_declaration : id_list ':' type"
    tipo = p[3]
    for nome, lineno in p[1]:
        symbol_table.declare_variable(nome, tipo, lineno)

def p_id_list_single(p):
    "id_list : ID"
    p[0] = [(p[1], p.lineno(1))]

def p_id_list_recursive(p):
    "id_list : id_list ',' ID"
    p[0] = p[1] + [(p[3], p.lineno(3))]

def p_type_integer(p):
    "type : INTEGER"
    p[0] = Tipo.INT

def p_type_boolean(p):
    "type : BOOLEAN"
    p[0] = Tipo.BOOL

def p_compound_cmd(p):
    "compound_cmd : BEGIN cmd_list END"

def p_cmd_list_single(p):
    "cmd_list : cmd"

def p_cmd_list_recursive(p):
    "cmd_list : cmd_list ';' cmd"

def p_cmd(p):
    """cmd : attr
           | conditional
           | repetition
           | read
           | write
           | compound_cmd"""

def p_attr(p):
    "attr : ID ATRIBUICAO expr"
    info = symbol_table.lookup(p[1])
    lineno = p.lineno(1)
    if info is None:
        erro_semantico(f"variável '{p[1]}' não declarada.", lineno)
        return
    if info.get("categoria") != "variavel":
        erro_semantico(f"identificador '{p[1]}' não é uma variável.", lineno)
        return
    var_tipo = info.get("tipo")
    expr_tipo = p[3]
    if var_tipo is not None and expr_tipo is not None and var_tipo != expr_tipo:
        erro_semantico(
            f"atribuição incompatível. Variável '{p[1]}' é {nome_tipo(var_tipo)} mas expressão é {nome_tipo(expr_tipo)}.",
            lineno,
        )

def p_conditional(p):
    "conditional : IF expr THEN cmd else_part"
    cond_tipo = p[2]
    lineno = p.lineno(1)
    if cond_tipo is not None and cond_tipo is not Tipo.BOOL:
        erro_semantico(
            f"condição do 'if' deve ser boolean, mas é {nome_tipo(cond_tipo)}.",
            lineno,
        )

def p_else_part(p):
    """else_part : ELSE cmd
                 | empty"""

def p_repetition(p):
    "repetition : WHILE expr DO cmd"
    cond_tipo = p[2]
    lineno = p.lineno(1)
    if cond_tipo is not None and cond_tipo is not Tipo.BOOL:
        erro_semantico(
            f"condição do 'while' deve ser boolean, mas é {nome_tipo(cond_tipo)}.",
            lineno,
        )

def p_read(p):
    "read : READ '(' id_list ')'"
    for nome, lineno in p[3]:
        info = symbol_table.lookup(nome)
        if info is None:
            erro_semantico(f"variável '{nome}' não declarada.", lineno)
        elif info.get("categoria") != "variavel":
            erro_semantico(f"identificador '{nome}' não é uma variável.", lineno)

def p_write(p):
    "write : WRITE '(' expr_list ')'"
    # Cada expressão já foi validada individualmente.

def p_expr_list_single(p):
    "expr_list : expr"
    p[0] = [p[1]]

def p_expr_list_recursive(p):
    "expr_list : expr_list ',' expr"
    p[0] = p[1] + [p[3]]

# ----------------- Expressões -----------------
def p_expr_logical_binary(p):
    """expr : expr AND expr
            | expr OR expr"""
    left, right = p[1], p[3]
    lineno = p.lineno(2)
    op = p[2]
    if left is not None and left is not Tipo.BOOL:
        erro_semantico(
            f"operador '{op}' exige operandos boolean, mas operando esquerdo é {nome_tipo(left)}.",
            lineno,
        )
    if right is not None and right is not Tipo.BOOL:
        erro_semantico(
            f"operador '{op}' exige operandos boolean, mas operando direito é {nome_tipo(right)}.",
            lineno,
        )
    p[0] = Tipo.BOOL

def p_expr_logical_not(p):
    "expr : NOT expr %prec NOT"
    expr_tipo = p[2]
    lineno = p.lineno(1)
    if expr_tipo is not None and expr_tipo is not Tipo.BOOL:
        erro_semantico(
            f"operador 'not' exige operando boolean, mas recebeu {nome_tipo(expr_tipo)}.",
            lineno,
        )
    p[0] = Tipo.BOOL

def p_expr_relational(p):
    "expr : simple_expr relation simple_expr"
    left, op, right = p[1], p[2], p[3]
    lineno = p.lineno(2)
    if op in ("<", "<=", ">", ">="):
        for lado, tipo in (("esquerdo", left), ("direito", right)):
            if tipo is not None and tipo is not Tipo.INT:
                erro_semantico(
                    f"operador '{op}' exige inteiros, mas operando {lado} é {nome_tipo(tipo)}.",
                    lineno,
                )
    else:  # '=' ou '<>'
        if left is not None and right is not None and left != right:
            erro_semantico(
                f"operador '{op}' exige operandos do mesmo tipo, mas encontrou {nome_tipo(left)} e {nome_tipo(right)}.",
                lineno,
            )
    p[0] = Tipo.BOOL

def p_expr_simple(p):
    "expr : simple_expr"
    p[0] = p[1]

def p_relation(p):
    """relation : '='
                | DIFERENTE
                | '<'
                | MENOR_IGUAL
                | '>'
                | MAIOR_IGUAL"""
    p[0] = p[1]

def p_simple_expr_term(p):
    "simple_expr : term"
    p[0] = p[1]

def p_simple_expr_add(p):
    """simple_expr : simple_expr '+' term
                   | simple_expr '-' term"""
    left, right = p[1], p[3]
    lineno = p.lineno(2)
    op = p[2]
    for lado, tipo in (("esquerdo", left), ("direito", right)):
        if tipo is not None and tipo is not Tipo.INT:
            erro_semantico(
                f"operador '{op}' exige inteiros, mas operando {lado} é {nome_tipo(tipo)}.",
                lineno,
            )
    p[0] = Tipo.INT

def p_term_factor(p):
    "term : factor"
    p[0] = p[1]

def p_term_mul(p):
    """term : term '*' factor
            | term DIV factor"""
    left, right = p[1], p[3]
    lineno = p.lineno(2)
    op_text = str(p[2])  # '*' ou 'div'
    for lado, tipo in (("esquerdo", left), ("direito", right)):
        if tipo is not None and tipo is not Tipo.INT:
            erro_semantico(
                f"operador '{op_text}' exige inteiros, mas operando {lado} é {nome_tipo(tipo)}.",
                lineno,
            )
    p[0] = Tipo.INT

def p_factor_id(p):
    "factor : ID"
    nome = p[1]
    lineno = p.lineno(1)
    info = symbol_table.lookup(nome)
    if info is None:
        erro_semantico(f"identificador '{nome}' não declarado.", lineno)
        p[0] = None
        return
    if info.get("categoria") != "variavel":
        erro_semantico(f"identificador '{nome}' não é uma variável.", lineno)
        p[0] = info.get("tipo")
        return
    p[0] = info.get("tipo")

def p_factor_num(p):
    "factor : NUM"
    p[0] = Tipo.INT

def p_factor_true(p):
    "factor : TRUE"
    p[0] = Tipo.BOOL

def p_factor_false(p):
    "factor : FALSE"
    p[0] = Tipo.BOOL

def p_factor_parentheses(p):
    "factor : '(' expr ')'"
    p[0] = p[2]

def p_factor_neg(p):
    "factor : '-' factor %prec NEG"
    fator_tipo = p[2]
    lineno = p.lineno(1)
    if fator_tipo is not None and fator_tipo is not Tipo.INT:
        erro_semantico(
            f"operador unário '-' exige inteiro, mas recebeu {nome_tipo(fator_tipo)}.",
            lineno,
        )
    p[0] = Tipo.INT

# -----------------------------------------------------
# Erros Sintáticos (padronizados)
# -----------------------------------------------------
def p_error(p):
    # Garante o rastreador BEGIN/END (para detectar EOF com BEGIN aberto)
    if p and hasattr(p, 'lexer') and not hasattr(p.lexer, '_wrapped_for_blocks'):
        p.lexer._wrapped_for_blocks = True
        track_blocks(p.lexer)

    if p:
        print(f"ERRO SINTÁTICO (linha {p.lineno}): próximo a '{p.value}'.")
    else:
        if begin_stack:
            # Relata todos os 'begin' não fechados com a linha onde começaram
            while begin_stack:
                linha = begin_stack.pop()
                print(f"ERRO SINTÁTICO (linha {linha}): bloco 'begin' iniciado não foi fechado com 'end'.")
        else:
            print("ERRO SINTÁTICO (linha 0): fim inesperado do arquivo.")

# ---- Declarações ----
def p_var_declaration_list_error(p):
    "var_declaration_list : var_declaration error"
    print(f"ERRO SINTÁTICO (linha {p.lineno(1)}): esperado ';' após declaração de variável, próximo a '{getattr(p[2],'value','?')}'.")
    parser.errok()

def p_var_declaration_error(p):
    "var_declaration : id_list ':' error"
    print(f"ERRO SINTÁTICO (linha {p.lineno(1)}): tipo inválido na declaração de variável, próximo a '{getattr(p[3],'value','?')}'.")
    parser.errok()

def p_id_list_error(p):
    "id_list : id_list ',' error"
    print(f"ERRO SINTÁTICO (linha {p.lineno(1)}): identificador inválido após ',' próximo a '{getattr(p[3],'value','?')}'.")
    parser.errok()

# ---- Bloco BEGIN...END ----
def p_compound_cmd_error_inner(p):
    "compound_cmd : BEGIN error END"
    print(f"ERRO SINTÁTICO (linha {p.lineno(1)}): comandos inválidos dentro de 'begin ... end', próximo a '{getattr(p[2],'value','?')}'.")
    parser.errok()

# ---- Atribuição ----
def p_attr_error_rhs(p):
    "attr : ID ATRIBUICAO error"
    print(f"ERRO SINTÁTICO (linha {p.lineno(1)}): expressão inválida em atribuição após '{p[1]}' próximo a '{getattr(p[3],'value','?')}'.")
    parser.errok()

# ---- IF / THEN / ELSE ----
def p_conditional_missing_expr(p):
    "conditional : IF error THEN cmd else_part"
    print(f"ERRO SINTÁTICO (linha {p.lineno(1)}): expressão booleana inválida após 'if' próximo a '{getattr(p[2],'value','?')}'.")
    parser.errok()

def p_conditional_missing_then_and_recover(p):
    "conditional : IF expr error cmd else_part"
    found = getattr(p[3], 'value', 'token')
    after = getattr(p[4], 'value', 'comando')
    print(f"ERRO SINTÁTICO (linha {p.lineno(1)}): esperado 'then' após condição do 'if' (encontrado '{found}') antes de '{after}'.")
    parser.errok()

def p_conditional_then_cmd_error(p):
    "conditional : IF expr THEN error"
    print(f"ERRO SINTÁTICO (linha {p.lineno(1)}): comando inválido após 'then' próximo a '{getattr(p[4],'value','?')}'.")
    parser.errok()

def p_else_part_error(p):
    "else_part : ELSE error"
    print(f"ERRO SINTÁTICO (linha {p.lineno(1)}): comando inválido após 'else' próximo a '{getattr(p[2],'value','?')}'.")
    parser.errok()

# ---- WHILE / DO ----
def p_repetition_error_expr(p):
    "repetition : WHILE error DO cmd"
    print(f"ERRO SINTÁTICO (linha {p.lineno(1)}): expressão booleana inválida após 'while' próximo a '{getattr(p[2],'value','?')}'.")
    parser.errok()

def p_repetition_error_cmd(p):
    "repetition : WHILE expr DO error"
    print(f"ERRO SINTÁTICO (linha {p.lineno(1)}): comando inválido após 'do' próximo a '{getattr(p[4],'value','?')}'.")
    parser.errok()

# ---- READ / WRITE ----
def p_read_error_list(p):
    "read : READ '(' error ')'"
    print(f"ERRO SINTÁTICO (linha {p.lineno(1)}): lista de identificadores inválida em 'read(...)' próximo a '{getattr(p[3],'value','?')}'.")
    parser.errok()

def p_read_error_paren(p):
    "read : READ error"
    print(f"ERRO SINTÁTICO (linha {p.lineno(1)}): sintaxe de 'read' inválida próximo a '{getattr(p[2],'value','?')}'. Esperado '(...)'.")
    parser.errok()

def p_write_error_list(p):
    "write : WRITE '(' error ')'"
    print(f"ERRO SINTÁTICO (linha {p.lineno(1)}): lista de expressões inválida em 'write(...)' próximo a '{getattr(p[3],'value','?')}'.")
    parser.errok()

def p_write_error_paren(p):
    "write : WRITE error"
    print(f"ERRO SINTÁTICO (linha {p.lineno(1)}): sintaxe de 'write' inválida próximo a '{getattr(p[2],'value','?')}'. Esperado '(...)'.")
    parser.errok()

def p_write_trailing_comma(p):
    "write : WRITE '(' expr_list ',' ')'"
    print(f"ERRO SINTÁTICO (linha {p.lineno(4)}): falta expressão após ',' em 'write(...)' próximo a ','.")
    parser.errok()

# ---- Listas de expressões ----
def p_expr_list_error_after_comma(p):
    "expr_list : expr_list ',' error"
    print(f"ERRO SINTÁTICO (linha {p.lineno(1)}): expressão inválida após ',' próximo a '{getattr(p[3],'value','?')}'.")
    parser.errok()

# ---- Expressões: lógicos / relacionais / aritméticos ----
def p_expr_logic_error_and(p):
    "expr : expr AND error"
    print(f"ERRO SINTÁTICO (linha {p.lineno(3)}): expressão inválida após 'and' próximo a '{getattr(p[3],'value','?')}'.")
    parser.errok()

def p_expr_logic_error_or(p):
    "expr : expr OR error"
    print(f"ERRO SINTÁTICO (linha {p.lineno(3)}): expressão inválida após 'or' próximo a '{getattr(p[3],'value','?')}'.")
    parser.errok()

def p_expr_logic_error_not(p):
    "expr : NOT error"
    print(f"ERRO SINTÁTICO (linha {p.lineno(1)}): expressão inválida após 'not' próximo a '{getattr(p[2],'value','?')}'.")
    parser.errok()

def p_expr_error_relation_right(p):
    "expr : simple_expr relation error"
    print(f"ERRO SINTÁTICO (linha {p.lineno(2)}): expressão inválida à direita do operador relacional próximo a '{getattr(p[3],'value','?')}'.")
    parser.errok()

def p_simple_expr_error_right(p):
    """simple_expr : simple_expr '+' error
                   | simple_expr '-' error"""
    print(f"ERRO SINTÁTICO (linha {p.lineno(2)}): termo inválido após operador '{p[2]}' próximo a '{getattr(p[3],'value','?')}'.")
    parser.errok()

def p_term_error_right(p):
    """term : term '*' error
            | term DIV error"""
    op_text = str(p[2])  # '*' ou 'div'
    print(f"ERRO SINTÁTICO (linha {p.lineno(2)}): fator inválido após operador '{op_text}' próximo a '{getattr(p[3],'value','?')}'.")
    parser.errok()

def p_factor_paren_error(p):
    "factor : '(' error ')'"
    print(f"ERRO SINTÁTICO (linha {p.lineno(1)}): expressão inválida entre parênteses próximo a '{getattr(p[2],'value','?')}'.")
    parser.errok()

# -----------------------------------------------------
# Parser + utilidades
# -----------------------------------------------------
parser = yacc.yacc(start="program")

def parse_source(data: str, lexer=None):
    symbol_table.reset()
    if lexer is None:
        lexer = lex.lex(module=lexico)
    # Ativa rastreamento de blocos ANTES do parse para detectar EOF com BEGIN aberto
    track_blocks(lexer)
    return parser.parse(data, lexer=lexer)

def main() -> None:
    data = sys.stdin.read()
    parse_source(data)

if __name__ == "__main__":
    main()
