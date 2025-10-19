from sys import argv
from lexico.lexico import lexico, calcula_coluna

if len(argv) == 2:
    with open(argv[1], 'r') as entrada:
        data = entrada.read()

        # lexico.line_start = 0
        lexico.input(data)

        while True:
            tok = lexico.token()
            if not tok:
                break
            col = calcula_coluna(tok, lexico)
            print(f"<{tok.type}, {tok.value!r}> na linha: {tok.lineno}, coluna:{col}") # !r -> imprima a representação repr() do valor, em vez da conversão str()
            # print(f"<{tok.type}, {tok.value!r}> na linha {tok.lineno}, posição {tok.lexpos}")
else:
    print('Faltou o nome do arquivo a ser escaneado!')
