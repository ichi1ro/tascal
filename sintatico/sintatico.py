import sys
from pathlib import Path
from enum import Enum

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lexico"))

import ply.yacc as yacc
import lexico as lexico

tokens = lexico.tokens
var_list = []

# -----------------------------------------------------
# Rastreamento de blocos BEGIN ... END
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
    ('nonassoc', '=', 'DIFERENTE', '<', 'MENOR_IGUAL', '>', 'MAIOR_IGUAL'),
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

# lógicos para expr (AND, OR, NOT)
def p_expr(p):
    '''expr : expr AND expr
            | expr OR expr
            | NOT expr %prec NOT
            | simple_expr
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
                   | simple_expr '-' term'''

def p_term(p):
    '''term : factor
            | term '*' factor
            | term DIV factor'''

def p_factor(p):
    '''factor : ID
              | NUM
              | TRUE
              | FALSE
              | '(' expr ')'
              | '-' factor %prec NEG'''

# -----------------------------------------------------
# Erros
# -----------------------------------------------------

def p_error(p):
    # garante que o lexer atual está sendo rastreado
    if p and hasattr(p, 'lexer') and not hasattr(p.lexer, '_wrapped_for_blocks'):
        p.lexer._wrapped_for_blocks = True
        track_blocks(p.lexer)

    if p:
        print(f"ERRO SINTÁTICO: próximo a '{p.value}' (linha {p.lineno}). Verifique se não está sendo usado uma palavra reservada onde não devia.")
    else:
        if begin_stack:
            while begin_stack:
                linha = begin_stack.pop()
                print(f"ERRO SINTÁTICO: bloco 'BEGIN' iniciado na linha {linha} não foi fechado com 'END'.")
        else:
            print("ERRO SINTÁTICO: fim inesperado do arquivo.")
            
# Falta de ';' após declaração
def p_var_declaration_list_error(p):
    '''var_declaration_list : var_declaration error'''
    print(f"ERRO SINTÁTICO: esperado ';' após declaração de variável (linha {p.lineno(1)}).")
    parser.errok()

def p_var_declaration_error(p):
    '''var_declaration : id_list ':' error'''
    print(f"ERRO SINTÁTICO: tipo inválido na declaração de variável (linha {p.lineno(1)}).")
    parser.errok()
               
def p_id_list_error(p):
    '''id_list : id_list ',' error'''
    print(f"ERRO SINTÁTICO: identificador inválido após ',' (linha {p.lineno(1)}).")
    parser.errok()

# Recuperação em bloco BEGIN ... END
def p_compound_cmd_error(p):
    '''compound_cmd : BEGIN error END'''
    print(f"ERRO SINTÁTICO: comandos inválidos dentro de 'begin ... end' (linha {p.lineno(1)}).")
    parser.errok()

# Recupera comando único inválido
def p_cmd_list_error_single(p):
    '''cmd_list : error'''
    print(F"ERRO SINTÁTICO: comando inválido (linha {p.lineno(1)}).")
    parser.errok()
    
def p_attr_error(p):
    '''attr : ID ATRIBUICAO error'''
    print(f"ERRO SINTÁTICO: expressão inválida em atribuição (linha {p.lineno(1)}).")
    parser.errok()
    
def p_conditional_missing_expr(p):
    '''conditional : IF error THEN cmd else_part'''
    print(f"ERRO SINTÁTICO: expressão booleana inválida após 'if' (linha {p.lineno(1)}).")
    parser.errok()

def p_conditional_missing_then_cmd(p):
    '''conditional : IF expr THEN error'''
    print(f"ERRO SINTÁTICO: comando inválido após 'then' (linha {p.lineno(1)}).")
    parser.errok()

def p_conditional_missing_then(p):
    '''conditional : IF expr error'''
    print(f"ERRO SINTÁTICO: diretiva 'if' sem um 'then' (linha {p.lineno(1)}).")
    parser.errok()

def p_else_part_error(p):
    '''else_part : ELSE error'''
    print(f"ERRO SINTÁTICO: comando inválido após 'else' (linha {p.lineno(1)}).")
    parser.errok()

def p_repetition_error_expr(p):
    '''repetition : WHILE error DO cmd'''
    print(f"ERRO SINTÁTICO: expressão booleana inválida após 'while' (linha {p.lineno(1)}).")
    parser.errok()
    
def p_repetition_error_cmd(p):
    '''repetition : WHILE expr DO error'''
    print(f"ERRO SINTÁTICO: comando inválido após 'do' (linha {p.lineno(1)}).")
    parser.errok()
    
def p_read_error_list(p):
    '''read : READ '(' error ')' '''
    print(f"ERRO SINTÁTICO: lista de identificadores inválida em 'read(...)' (linha {p.lineno(1)}).")
    parser.errok()

def p_read_error_paren(p):
    '''read : READ error '''
    print(f"ERRO SINTÁTICO: sintaxe de 'read' inválida. Esperado '(...)' (linha {p.lineno(1)}).")
    parser.errok()
    
def p_write_error_list(p):
    '''write : WRITE '(' error ')' '''
    print(f"ERRO SINTÁTICO: lista de expressões inválida em 'write(...)' (linha {p.lineno(1)}).")
    parser.errok()
    
def p_write_error_paren(p):
    '''write : WRITE error'''
    print(f"ERRO SINTÁTICO: sintaxe de 'write' inválida. Esperado '(...)' (linha {p.lineno(1)}).")
    parser.errok()
    
def p_expr_list_error(p):
    '''expr_list : expr_list ',' error'''
    print(f"ERRO SINTÁTICO: expressão inválida após ',' (linha {p.lineno(1)}).")
    parser.errok()

def p_expr_logic_error_and(p):
    'expr : expr AND error'
    print(f"ERRO SINTÁTICO: expressão inválida após 'and' (linha {p.lineno(3)}).")
    parser.errok()

def p_expr_logic_error_or(p):
    'expr : expr OR error'
    print(f"ERRO SINTÁTICO: expressão inválida após 'or' (linha {p.lineno(3)}).")
    parser.errok()

def p_expr_logic_error_not(p):
    'expr : NOT error'
    print(f"ERRO SINTÁTICO: expressão inválida após 'not' (linha {p.lineno(1)}).")
    parser.errok()

def p_expr_error_relation_right(p):
    '''expr : simple_expr relation error'''
    print(f"ERRO SINTÁTICO: expressão inválida à direita do operador relacional (linha {p.lineno(1)}).")
    parser.errok()

def p_simple_expr_error_right(p):
    '''simple_expr : simple_expr '+' error
                   | simple_expr '-' error'''
    print(f"ERRO SINTÁTICO: termo inválido após operador aditivo (linha {p.lineno(1)}).")
    parser.errok()
    
def p_term_error_right(p):
    '''term : term '*' error
            | term DIV error'''
    print(f"ERRO SINTÁTICO: fator inválido após operador multiplicativo/divisão (linha {p.lineno(1)}).")
    parser.errok()

def p_factor_paren_error(p):
    '''factor : '(' error ')' '''
    print(f"ERRO SINTÁTICO: expressão inválida entre parênteses (linha {p.lineno(1)}).")
    parser.errok()
    
def p_write_trailing_comma(p):
    '''write : WRITE '(' expr_list ',' ')' '''
    print(f"ERRO SINTÁTICO: falta expressão após ',' em 'write(...)' (linha {p.lineno(4)}).")
    parser.errok()


# -----------------------------------------------------
# Parser
# -----------------------------------------------------

parser = yacc.yacc(start='program')
