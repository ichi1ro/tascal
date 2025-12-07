import sys
from pathlib import Path
from enum import Enum

import ply.lex as lex
import ply.yacc as yacc

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lexico"))
import lexico as lexico  

tokens = lexico.tokens

# -----------------------------------------------------
# Precedência
# -----------------------------------------------------
begin_stack = []

def track_blocks(lexer):
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

precedence = (
    ('nonassoc', 'IF'),
    ('nonassoc', 'ELSE'),
    ('right', 'NOT', 'NEG'),
)

# -----------------------------------------------------
# Regras Sintáticas (sem ações semânticas)
# -----------------------------------------------------

def p_empty(p):
    "empty :"
    pass

def p_program(p):
    "program : PROGRAM ID ';' block '.'"

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

def p_id_list_single(p):
    "id_list : ID"

def p_id_list_recursive(p):
    "id_list : id_list ',' ID"

def p_type_integer(p):
    "type : INTEGER"

def p_type_boolean(p):
    "type : BOOLEAN"

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

def p_conditional(p):
    "conditional : IF expr THEN cmd else_part"

def p_else_part(p):
    """else_part : ELSE cmd
                 | empty"""

def p_repetition(p):
    "repetition : WHILE expr DO cmd"

def p_read(p):
    "read : READ '(' id_list ')'"

def p_write(p):
    "write : WRITE '(' expr_list ')'"

def p_expr_list_single(p):
    "expr_list : expr"

def p_expr_list_recursive(p):
    "expr_list : expr_list ',' expr"

# ----------------- Expressões -----------------

def p_expr_logic_binary(p):
    """expr : expr AND expr
            | expr OR expr"""

def p_expr_logical_not(p):
    "expr : NOT expr %prec NOT"

def p_expr_relational(p):
    "expr : simple_expr relation simple_expr"

def p_expr_simple(p):
    "expr : simple_expr"

def p_relation(p):
    """relation : '='
                | DIFERENTE
                | '<'
                | MENOR_IGUAL
                | '>'
                | MAIOR_IGUAL"""

def p_simple_expr_term(p):
    "simple_expr : term"

def p_simple_expr_add(p):
    """simple_expr : simple_expr '+' term
                   | simple_expr '-' term"""

def p_term_factor(p):
    "term : factor"

def p_term_mul(p):
    """term : term '*' factor
            | term DIV factor"""

def p_factor_id(p):
    "factor : ID"

def p_factor_num(p):
    "factor : NUM"

def p_factor_true(p):
    "factor : TRUE"

def p_factor_false(p):
    "factor : FALSE"

def p_factor_parentheses(p):
    "factor : '(' expr ')'"

def p_factor_neg(p):
    "factor : '-' factor %prec NEG"

# -----------------------------------------------------
# Erros Sintáticos (com rastreabilidade p.lineno / p[n].value)
# -----------------------------------------------------

def p_error(p):
    # garante que o lexer atual está sendo rastreado
    if p and hasattr(p, 'lexer') and not hasattr(p.lexer, '_wrapped_for_blocks'):
        p.lexer._wrapped_for_blocks = True
        track_blocks(p.lexer)

    if p:
        print(f"ERRO SINTÁTICO: próximo a '{p.value}' (linha {p.lineno}).")
    else:
        if begin_stack:
            while begin_stack:
                linha = begin_stack.pop()
                print(f"ERRO SINTÁTICO: bloco 'begin' iniciado não foi fechado com 'end' (linha {linha}).")
        else:
            print("ERRO SINTÁTICO: fim inesperado do arquivo.")

def p_var_declaration_list_error(p):
    "var_declaration_list : var_declaration error"
    # erro típico: faltou ';' após uma declaração
    print(f"ERRO SINTÁTICO: esperado ';' após declaração de variável, próximo a '{getattr(p[2],'value','?')}' (linha {p.lineno(1)}).")
    parser.errok()

def p_var_declaration_error(p):
    "var_declaration : id_list ':' error"
    print(f"ERRO SINTÁTICO: tipo inválido na declaração de variável, próximo a '{getattr(p[3],'value','?')}' (linha {p.lineno(1)}).")
    parser.errok()

def p_id_list_error(p):
    "id_list : id_list ',' error"
    print(f"ERRO SINTÁTICO: identificador inválido após ',' próximo a '{getattr(p[3],'value','?')}' (linha {p.lineno(1)}).")
    parser.errok()

def p_compound_cmd_error_inner(p):
    "compound_cmd : BEGIN error END"
    print(f"ERRO SINTÁTICO: comandos inválidos dentro de 'begin ... end', próximo a '{getattr(p[2],'value','?')}' (linha {p.lineno(1)}).")
    parser.errok()

def p_attr_error_rhs(p):
    "attr : ID ATRIBUICAO error"
    # p[1] é o identificador à esquerda
    print(f"ERRO SINTÁTICO: expressão inválida em atribuição após '{p[1]}' próximo a '{getattr(p[3],'value','?')}' (linha {p.lineno(1)}).")
    parser.errok()

def p_conditional_missing_expr(p):
    "conditional : IF error THEN cmd else_part"
    print(f"ERRO SINTÁTICO: expressão booleana inválida após 'if' próximo a '{getattr(p[2],'value','?')}' (linha {p.lineno(1)}).")
    parser.errok()

def p_conditional_missing_then_and_recover(p):
    "conditional : IF expr error cmd else_part"
    first_token = getattr(p[3], 'value', 'then')
    print(f"ERRO SINTÁTICO: esperado 'then' após condição do 'if' antes de '{first_token}' (linha {p.lineno(1)}).")
    parser.errok()

def p_conditional_then_cmd_error(p):
    "conditional : IF expr THEN error"
    print(f"ERRO SINTÁTICO: comando inválido após 'then' próximo a '{getattr(p[4],'value','?')}' (linha {p.lineno(1)}).")
    parser.errok()

def p_else_part_error(p):
    "else_part : ELSE error"
    print(f"ERRO SINTÁTICO: comando inválido após 'else' próximo a '{getattr(p[2],'value','?')}' (linha {p.lineno(1)}).")
    parser.errok()

def p_repetition_error_expr(p):
    "repetition : WHILE error DO cmd"
    print(f"ERRO SINTÁTICO: expressão booleana inválida após 'while' próximo a '{getattr(p[2],'value','?')}' (linha {p.lineno(1)}).")
    parser.errok()

def p_repetition_error_cmd(p):
    "repetition : WHILE expr DO error"
    print(f"ERRO SINTÁTICO: comando inválido após 'do' próximo a '{getattr(p[4],'value','?')}' (linha {p.lineno(1)}).")
    parser.errok()

def p_read_error_list(p):
    "read : READ '(' error ')'"
    print(f"ERRO SINTÁTICO: lista de identificadores inválida em 'read(...)' próximo a '{getattr(p[3],'value','?')}' (linha {p.lineno(1)}).")
    parser.errok()

def p_read_error_paren(p):
    "read : READ error"
    print(f"ERRO SINTÁTICO: sintaxe de 'read' inválida próximo a '{getattr(p[2],'value','?')}'. Esperado '(...)' (linha {p.lineno(1)}).")
    parser.errok()

def p_write_error_list(p):
    "write : WRITE '(' error ')'"
    print(f"ERRO SINTÁTICO: lista de expressões inválida em 'write(...)' próximo a '{getattr(p[3],'value','?')}' (linha {p.lineno(1)}).")
    parser.errok()

def p_write_error_paren(p):
    "write : WRITE error"
    print(f"ERRO SINTÁTICO: sintaxe de 'write' inválida próximo a '{getattr(p[2],'value','?')}'. Esperado '(...)' (linha {p.lineno(1)}).")
    parser.errok()

def p_write_trailing_comma(p):
    "write : WRITE '(' expr_list ',' ')'"
    # vírgula final antes de ')'
    print(f"ERRO SINTÁTICO: falta expressão após ',' em 'write(...)' próximo a ',' (linha {p.lineno(4)}).")
    parser.errok()

def p_expr_list_error_after_comma(p):
    "expr_list : expr_list ',' error"
    print(f"ERRO SINTÁTICO: expressão inválida após ',' próximo a '{getattr(p[3],'value','?')}' (linha {p.lineno(1)}).")
    parser.errok()

def p_expr_logic_error_and(p):
    "expr : expr AND error"
    print(f"ERRO SINTÁTICO: expressão inválida após 'and' próximo a '{getattr(p[3],'value','?')}' (linha {p.lineno(3)}).")
    parser.errok()

def p_expr_logic_error_or(p):
    "expr : expr OR error"
    print(f"ERRO SINTÁTICO: expressão inválida após 'or' próximo a '{getattr(p[3],'value','?')}' (linha {p.lineno(3)}).")
    parser.errok()

def p_expr_logic_error_not(p):
    "expr : NOT error"
    print(f"ERRO SINTÁTICO: expressão inválida após 'not' próximo a '{getattr(p[2],'value','?')}' (linha {p.lineno(1)}).")
    parser.errok()

def p_expr_error_relation_right(p):
    "expr : simple_expr relation error"
    print(f"ERRO SINTÁTICO: expressão inválida à direita do operador relacional próximo a '{getattr(p[3],'value','?')}' (linha {p.lineno(2)}).")
    parser.errok()

def p_simple_expr_error_right(p):
    """simple_expr : simple_expr '+' error
                   | simple_expr '-' error"""
    print(f"ERRO SINTÁTICO: termo inválido após operador '{p[2]}' próximo a '{getattr(p[3],'value','?')}' (linha {p.lineno(2)}).")
    parser.errok()

def p_term_error_right(p):
    """term : term '*' error
            | term DIV error"""
    op = p.slice[2].type if hasattr(p.slice[2], "type") else str(p[2])
    print(f"ERRO SINTÁTICO: fator inválido após operador '{op}' próximo a '{getattr(p[3],'value','?')}' (linha {p.lineno(2)}).")
    parser.errok()

def p_factor_paren_error(p):
    "factor : '(' error ')'"
    print(f"ERRO SINTÁTICO: expressão inválida entre parênteses próximo a '{getattr(p[2],'value','?')}' (linha {p.lineno(1)}).")
    parser.errok()

# -----------------------------------------------------
# Parser + utilidades
# -----------------------------------------------------

parser = yacc.yacc(start="program")

def parse_source(data: str, lexer=None):
    if lexer is None:
        lexer = lex.lex(module=lexico)
    return parser.parse(data, lexer=lexer)

def main() -> None:
    data = sys.stdin.read()
    parse_source(data)

if __name__ == "__main__":
    main()
