import sys
from pathlib import Path
import ply.yacc as yacc
import ply.lex as plex            # ✅ importa o construtor de lexer do PLY

# --------------------------------------------
# Verifica se o arquivo de código foi passado
# --------------------------------------------
if len(sys.argv) < 2:
    print("Uso: python teste_parser.py <arquivo_codigo>")
    sys.exit(1)

arquivo_codigo = Path(sys.argv[1])

if not arquivo_codigo.exists():
    print(f"Erro: arquivo '{arquivo_codigo}' não encontrado.")
    sys.exit(1)

# --------------------------------------------
# Importa o analisador sintático (gramática PLY)
# --------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sintatico  # seu arquivo de gramática PLY

parser = sintatico.parser

# --------------------------------------------
# Lê o conteúdo do arquivo de código
# --------------------------------------------
with open(arquivo_codigo, "r", encoding="utf-8") as f:
    codigo_teste = f.read()

print("========== TESTE DO ANALISADOR SINTÁTICO ==========\n")
print(codigo_teste)
print("---------------------------------------------------")

# --------------------------------------------
# Executa o parser (com rastreamento BEGIN/END)
# --------------------------------------------
lexer = plex.lex(module=sintatico.lexico)
sintatico.track_blocks(lexer)                  
resultado = parser.parse(codigo_teste, lexer=lexer)
if resultado is None:
    print("\n✅ Análise sintática concluída sem erros!")
else:
    print("\n⚠️ O parser retornou:", resultado)
