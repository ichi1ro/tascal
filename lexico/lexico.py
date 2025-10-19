import ply.lex as lex

p_reservadas = {
    'program': 'PROGRAM',
    'var': 'VAR',
    'begin': 'BEGIN',
    'end': 'END',
    'integer': 'INTEGER',
    'boolean': 'BOOLEAN',
    'false': 'FALSE',
    'true': 'TRUE',
    'read': 'READ',
    'write': 'WRITE',
    'while': 'WHILE',
    'do': 'DO',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'div': 'DIV',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT'
}

tokens = (
    'NUM',
    'ID',
    'DIFERENTE',
    'MENOR_IGUAL',
    'MAIOR_IGUAL',
    'ATRIBUICAO',
) + tuple(p_reservadas.values())

literals = ['+', '-', '*', '(', ')', ';', '=', '<', '>', ':', ',', '.']

t_DIFERENTE   = r'<>'
t_MENOR_IGUAL = r'<='
t_MAIOR_IGUAL = r'>='
t_ATRIBUICAO  = r':='


def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[A-Za-z][A-Za-z0-9_]*'
    t.type = p_reservadas.get(t.value, 'ID')
    return t

def t_AND(t):
    r'and'
    return t

def t_OR(t):
    r'or'
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.lexer.line_start = t.lexpos + len(t.value)

def calcula_coluna(t, lexico):
    line_start = getattr(lexico, "line_start", 0)
    return t.lexpos - line_start + 1

t_ignore = ' \t'

def t_error(t):
    col = calcula_coluna(t, t.lexer)
    print(f"ERRO: Símbolo ilegal {t.value[0]!r} na linha {t.lineno}, coluna {col}")
    t.lexer.skip(1)

lexico = lex.lex()
