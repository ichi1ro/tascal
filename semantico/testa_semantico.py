#!/usr/bin/env python3
import sys
from pathlib import Path
import ply.lex as plex


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: python testa_semantico.py <arquivo_codigo>")
        sys.exit(1)

    arquivo = Path(sys.argv[1])
    if not arquivo.exists():
        print(f"Erro: arquivo '{arquivo}' não encontrado.")
        sys.exit(1)

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import semantico

    codigo = arquivo.read_text(encoding="utf-8")

    print("========== TESTE DO ANALISADOR SEMÂNTICO ==========\n")
    print(codigo)
    print("---------------------------------------------------")

    lexer = plex.lex(module=semantico.lexico)
    resultado = semantico.parse_source(codigo, lexer=lexer)
    if resultado is None:
        print("\n✅ Análise semântica concluída (sem erros adicionais reportados).")
    else:
        print("\n⚠️ O analisador retornou:", resultado)


if __name__ == "__main__":
    main()
