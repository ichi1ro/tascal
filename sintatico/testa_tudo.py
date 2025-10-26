#!/usr/bin/env python3
import sys
from pathlib import Path
import ply.yacc as yacc
import ply.lex as plex

# --------------------------------------------
# Carrega o analisador sintático (gramática PLY)
# --------------------------------------------
# Ajuste o sys.path para importar o módulo sintatico.py que está nesta pasta
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sintatico  # seu arquivo de gramática PLY

parser = sintatico.parser

def testar_arquivo(arquivo: Path) -> bool:
    """Retorna True se parse ok, False se houve erro (o parser imprime mensagens por conta própria)."""
    try:
        codigo = arquivo.read_text(encoding="utf-8")

        # cria um lexer NOVO a partir do módulo lexico e aplica o rastreador de blocos
        lexer = plex.lex(module=sintatico.lexico)
        if hasattr(sintatico, "track_blocks"):
            sintatico.track_blocks(lexer)

        # zera a pilha de BEGIN/END entre arquivos (se existir)
        if hasattr(sintatico, "begin_stack"):
            try:
                sintatico.begin_stack.clear()
            except Exception:
                sintatico.begin_stack[:] = []

        # executa o parse
        resultado = parser.parse(codigo, lexer=lexer)

        # se seu parser não retorna AST/valor, o "None" é o caminho feliz
        return resultado is None
    except Exception as e:
        print(f"EXCEÇÃO ao analisar {arquivo.name}: {e}")
        return False

def coletar_arquivos(alvo: Path, recursivo: bool = True):
    if alvo.is_file():
        return [alvo]
    padrao = "**/*.tascal" if recursivo else "*.tascal"
    return sorted(alvo.glob(padrao)) if not recursivo else sorted(alvo.rglob("*.tascal"))

def main():
    if len(sys.argv) < 2:
        print("Uso: python testa_pasta_sintatico.py <arquivo_ou_pasta> [--no-recursive]")
        sys.exit(1)

    alvo = Path(sys.argv[1])
    if not alvo.exists():
        print(f"Erro: caminho '{alvo}' não encontrado.")
        sys.exit(1)

    recursivo = True
    if len(sys.argv) > 2 and sys.argv[2] == "--no-recursive":
        recursivo = False

    arquivos = coletar_arquivos(alvo, recursivo=recursivo)
    if not arquivos:
        print("Nenhum arquivo .tascal encontrado.")
        sys.exit(0)

    total = 0
    ok = 0
    fail = 0

    print("========== TESTE DO ANALISADOR SINTÁTICO ==========\n")
    for arq in arquivos:
        total += 1
        print(f"--- [{total}] {arq} ---")
        passou = testar_arquivo(arq)
        if passou:
            ok += 1
            print("✅ Análise sintática concluída sem erros!\n")
        else:
            fail += 1
            print("⚠️  Erros encontrados acima.\n")

    print("============== RESUMO ==============")
    print(f"Total: {total} | OK: {ok} | Falhas: {fail}")
    sys.exit(0 if fail == 0 else 2)

if __name__ == "__main__":
    main()
