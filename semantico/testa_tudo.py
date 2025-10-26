#!/usr/bin/env python3
import sys
from pathlib import Path
import ply.lex as plex

sys.path.insert(0, str(Path(__file__).resolve().parent))
import semantico  # noqa: E402


def testar_arquivo(arquivo: Path) -> bool:
    """Retorna True se a análise semântica terminar sem exceções adicionais."""
    try:
        codigo = arquivo.read_text(encoding="utf-8")
        lexer = plex.lex(module=semantico.lexico)
        resultado = semantico.parse_source(codigo, lexer=lexer)
        return resultado is None
    except Exception as exc:  # captura falhas inesperadas
        print(f"EXCEÇÃO ao analisar {arquivo.name}: {exc}")
        return False


def coletar_arquivos(alvo: Path, recursivo: bool = True):
    if alvo.is_file():
        return [alvo]
    padrao = "**/*.tascal" if recursivo else "*.tascal"
    return sorted(alvo.glob(padrao)) if not recursivo else sorted(alvo.rglob("*.tascal"))


def main():
    if len(sys.argv) < 2:
        print("Uso: python testa_semantico.py <arquivo_ou_pasta> [--no-recursive]")
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

    print("========== TESTE DO ANALISADOR SEMÂNTICO ==========\n")
    for arq in arquivos:
        total += 1
        print(f"--- [{total}] {arq} ---")
        if testar_arquivo(arq):
            ok += 1
            print("✅ Análise semântica concluída (veja mensagens acima, se houver).\n")
        else:
            fail += 1
            print("⚠️  Erros encontrados acima.\n")

    print("============== RESUMO ==============")
    print(f"Total: {total} | OK: {ok} | Falhas: {fail}")
    sys.exit(0 if fail == 0 else 2)


if __name__ == "__main__":
    main()
