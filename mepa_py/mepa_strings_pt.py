
#------------------------------------------------------------------------#
#                                                                        #
# Last update: "mepa_strings_pt.py: 2015-10-07 (Wed)  12:42:59 BRT (tk)" #
#                                                                        #
#------------------------------------------------------------------------#
# See mepa.py file for description, history and copyright.               #
#------------------------------------------------------------------------#

#------------------------------------------------------------------------#
#                                                                        #
# Definitions of language dependant strings: Portuguese (BR)             #
#                                                                        #
#------------------------------------------------------------------------#

# General

INTERNAL_ERROR = "Erro interno %d"

# main.py

BANNER = "\nInterpretador Mepa versão %s"
UNRECOGNIZED_OPTION = "\nOpção(ões) desconhecida(s)"
ILLEGAL_OPTION = "Opção inválida '--%s %s'"
ILLEGAL_OPTIONS = "Opção(ões) inválida(s)"
EXECUTION_ERROR = "Erro de execução %d"
UNEXPECTED_EXCEPTION = "Exceção inesperada"
OPTIONS_TITLE = "Opções:"
STEP_STDIN = "Opção '--step' não pode ser usada sem '--progfile'\n"

# main_defs.py

UNEXPECTED_PROGRAM_READING_EXCEPTION = "\nExceção inesperada no arquivo de programa"
UNEXPECTED_EOF_PROGRAM = "Fim inesperado do arquivo de programa"
ILLEGAL_INSTRUCTION_LABEL = "Rótulo de instrução inválido %d:  %s" 
MISSING_INSTRUCTION_CODE = "Falta código de instrução %d:  %s"
PROGRAM_TOO_LARGE = "Programa muito grande; use a opção '--programsize'"
ILLEGAL_INSTRUCTION  = "Instrução inválida (%3d)  %s" 
ILLEGAL_INSTRUCTION_ARGUMENTS = "Argumentos inválidos para instrução %d:  %s" 
REDEFINED_LABEL = "Rótulo redefinido (%3d)  %s" 
ILLEGAL_ARGUMENT = "Argumento inválido ou rótulo indefinido na linha %3d" 

# mepa_interp.py

ILLEGAL_ARGUMENT_TYPE = "Tipo de argumento inválido para uma instrução ou algum limite excedido"
EXECUTED_INSTRUCTIONS = "\n%d instruções executadas\n"
MAXIMUM_INSTRUCTIONS_EXCEEDED = "Número máximo de instruções executadas excedido (%d)"
UNEXPECTED_EOF_INPUT = "Fim inesperado do arquivo de entrada"
ILLEGAL_INPUT_VALUE = "Valor de entrada inválido"
PROG_END = "Atingido o fim do programa sem a instrução de parada"
STARTING_DEBUGGING = "Liga depuração"
STOPPING_DEBUGGING = "Desliga depuração"
STARTING_STEPEXEC = "\nLiga execução passo a passo"
STOPPING_STEPEXEC = "Desliga execução passo a passo"
DUMP = "\n\nDespejo"
DISPLAY = "\nVetor de base"
MEMORY = "\nMemória"
LABELS = "\nRótulos"
END_DUMP = "\nFim de despejo"
ILLEGAL_DEBUG_VALUE = "Valor inválido para depuração"
OPEN_FILE_ERROR = "Erro na abertura do arquivo '%s'"
ILLEGAL_VALUE = "Valor inválido encontrado durante a interpretação da instrução %d"
