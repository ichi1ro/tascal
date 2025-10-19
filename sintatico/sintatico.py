import sys
from pathlib import Path
from enum import Enum

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lexico"))

import ply.yacc as yacc
import lexico as lexico

tokens = lexico.tokens
var_list = []

# -----------------------------------------------------
# Tipos
# -----------------------------------------------------
class Tipo(Enum):
    INT  = 1
    BOOL = 2
    
def nomeTipo(t: Tipo) -> str:
    if t is Tipo.INT:  return 'int'
    if t is Tipo.BOOL: return 'bool'
    return "erro"

def erro_semantico(op, le: Tipo, ld: Tipo, esperado: str):
    sys.stderr.write(
        f"ERRO SEMÂNTICO: operador '{op}' incompatível com operandos ({nomeTipo(le)}, {nomeTipo(ld)}). "
        f"Esperado: {esperado}\n"
    )

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', '+', '-'),
    ('left', '*', 'DIV'),
    ('right', 'NOT', 'NEG'),
)

# -----------------------------------------------------
# Regras Sintáticas
# -----------------------------------------------------

def p_empty(p):
    'empty :'
    pass

def p_program(p):
    '''program : PROGRAM ID ';' block '.' '''


def p_block(p):
    '''block : declaration_section compound_cmd
             | compound_cmd'''

def p_declaration_section(p):
    '''declaration_section : VAR var_declaration_list
                           | declaration_section VAR var_declaration_list'''

def p_var_declaration_list(p):
    '''var_declaration_list : var_declaration_list var_declaration ';'
                            | var_declaration ';' '''

def p_var_declaration(p):
    '''var_declaration : id_list ':' type'''

def p_id_list(p):
    '''id_list : ID
               | id_list ',' ID'''

def p_type(p):
    '''type : INTEGER
            | BOOLEAN'''

def p_compound_cmd(p):
    '''compound_cmd : BEGIN cmd_list END'''

def p_cmd_list(p):
    '''cmd_list : cmd
                | cmd_list ';' cmd'''

def p_cmd(p):
    '''cmd : attr
           | conditional
           | repetition
           | read
           | write
           | compound_cmd'''

def p_attr(p):
    '''attr : ID ATRIBUICAO expr'''

def p_conditional(p):
    '''conditional : IF expr THEN cmd else_part'''

def p_else_part(p):
    '''else_part : ELSE cmd
                 | empty'''

def p_repetition(p):
    '''repetition : WHILE expr DO cmd'''

def p_read(p):
    '''read : READ '(' id_list ')' '''

def p_write(p):
    '''write : WRITE '(' expr_list ')' '''

def p_expr_list(p):
    '''expr_list : expr
                 | expr_list ',' expr'''

# -----------------------------------------------------
# Expressões
# -----------------------------------------------------

def p_expr(p):
    '''expr : simple_expr
            | simple_expr relation simple_expr'''

def p_relation(p):
    '''relation : '=' 
                | DIFERENTE
                | '<'
                | MENOR_IGUAL
                | '>'
                | MAIOR_IGUAL'''

def p_simple_expr(p):
    '''simple_expr : term
                   | simple_expr '+' term
                   | simple_expr '-' term
                   | simple_expr OR term'''

def p_term(p):
    '''term : factor
            | term '*' factor
            | term DIV factor
            | term AND factor'''

def p_factor(p):
    '''factor : ID
              | NUM
              | TRUE
              | FALSE
              | '(' expr ')'
              | NOT factor
              | '-' factor %prec NEG'''

# -----------------------------------------------------
# Erros
# -----------------------------------------------------

def p_error(p):
    if p:
        print(f"Erro sintático próximo a '{p.value}' (linha {p.lineno})")
    else:
        print("Erro sintático no final do arquivo")

# -----------------------------------------------------
# Parser
# -----------------------------------------------------

parser = yacc.yacc(start='program')
