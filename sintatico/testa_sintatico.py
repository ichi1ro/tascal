import sys
from pathlib import Path
import ply.yacc as yacc

# Importa o analisador sintático (o arquivo onde está sua gramática)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sintatico  # <- nome do arquivo com suas regras PLY (ajuste se necessário)

# Cria o parser
parser = sintatico.parser

# ------------------------------------------------------
# Programa de teste (você pode alterar livremente)
# ------------------------------------------------------
codigo_teste = """
program P8;
var x: integer;
var b: boolean;
begin
  x := 3;
  b := x = 3;
  write(b)
end.
"""

print("========== TESTE DO ANALISADOR SINTÁTICO ==========\n")
print(codigo_teste)
print("---------------------------------------------------")

# Executa o parser
resultado = parser.parse(codigo_teste)

if resultado is None:
    print("\n✅ Análise sintática concluída sem erros!")
else:
    print("\n⚠️ O parser retornou:", resultado)
