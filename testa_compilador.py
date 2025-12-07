#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
from pathlib import Path
import importlib
import ply.lex as plex


def coletar_arquivos(alvo: Path, recursivo: bool = True) -> list[Path]:
    if alvo.is_file():
        return [alvo]
    padrao = "**/*.tascal" if recursivo else "*.tascal"
    return sorted(alvo.rglob("*.tascal")) if recursivo else sorted(alvo.glob("*.tascal"))


def testar_arquivo(mod, arquivo: Path) -> bool:
    """Executa parse_source do módulo do compilador. Retorna True se não houver exceções inesperadas."""
    try:
        codigo = arquivo.read_text(encoding="utf-8")
        # Cria um lexer a partir do lexico do módulo do compilador (mesmo léxico usado internamente)
        lexer = plex.lex(module=mod.lexico)
        # A função parse_source do compilador aceita 'lexer' e cuida do restante
        resultado = mod.parse_source(codigo, lexer=lexer)
        # Geralmente PLY retorna None no sucesso; mensagens de erro são impressas pelo próprio módulo.
        return resultado is None
    except Exception as exc:
        print(f"EXCEÇÃO ao analisar {arquivo.name}: {exc}")
        return False


def main():
    ap = argparse.ArgumentParser(
        prog="testa_compilador.py",
        description="Roda o compilador (léxico+sintático+semântico) em um arquivo ou diretório com .tascal."
    )
    ap.add_argument("alvo", help="Arquivo .tascal ou diretório contendo .tascal")
    ap.add_argument("--no-recursive", action="store_true", help="Não varrer recursivamente diretórios")
    ap.add_argument("--module", default="compilador",
                    help="Nome do módulo do compilador unificado (default: compilador)")
    args = ap.parse_args()

    alvo = Path(args.alvo).resolve()
    if not alvo.exists():
        print(f"Erro: caminho '{alvo}' não encontrado.")
        sys.exit(1)

    # Importa dinamicamente o módulo do compilador
    try:
        mod = importlib.import_module(args.module)
    except Exception as e:
        print(f"Erro: não foi possível importar o módulo '{args.module}': {e}")
        sys.exit(1)

    # Checagens mínimas de API esperada
    if not hasattr(mod, "parse_source") or not hasattr(mod, "lexico"):
        print(f"Erro: o módulo '{args.module}' não expõe 'parse_source' e/ou 'lexico'.")
        sys.exit(1)

    arquivos = coletar_arquivos(alvo, recursivo=not args.no_recursive)
    if not arquivos:
        print("Nenhum arquivo .tascal encontrado.")
        sys.exit(0)

    total = 0
    ok = 0
    fail = 0

    print("========== TESTE DO COMPILADOR (léxico+sintático+semântico) ==========\n")
    for arq in arquivos:
        total += 1
        print(f"--- [{total}] {arq} ---")
        if testar_arquivo(mod, arq):
            ok += 1
            print("✅ Compilação/Análise concluída (mensagens, se houver, acima).\n")
        else:
            fail += 1
            print("⚠️  Erros encontrados acima.\n")

    print("============== RESUMO ==============")
    print(f"Total: {total} | OK: {ok} | Falhas: {fail}")
    sys.exit(0 if fail == 0 else 2)


if __name__ == "__main__":
    main()
