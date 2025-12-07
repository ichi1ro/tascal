
#------------------------------------------------------------------------#
#                                                                        #
# Last update: "mepa_instr_pt.py: 2015-06-22 (Mon)  10:28:17 BRT (tk)"   #
#                                                                        #
#------------------------------------------------------------------------#
# See mepa.py file for description, history and copyright.               #
#------------------------------------------------------------------------#

#------------------------------------------------------------------------#
#                                                                        #
# Instructions and their function mappings -- Portuguese version         #
#                                                                        #
# Upper case codes may be redefined, but only those.                     #
#                                                                        #
#------------------------------------------------------------------------#


# No args instructions

# End instruction
END_INSTR = "FIM"  # end

INSTR_DICT = {
          # 0 args
          "SOMA": "add",
          "SUBT": "subt",
          "MULT": "mult",
          "DIVI": "divi",
          "INVR": "inv",
          "CONJ": "andd",
          "DISJ": "orr",
          "NEGA": "nott",
          "CMME": "less",
          "CMMA": "grt",
          "CMIG": "eql",
          "CMDG": "dif",
          "CMEG": "leq",
          "CMAG": "geq",
          "NADA": "nop",
          "PARA": "halt",
          "LEIT": "read",
          "IMPR": "writ",
          "INPP": "init",
          "CONT": "cont",
          "DUMP": "dump",
          
          # 1 arg
          "CRCT": "ldct",
          "DSVS": "jmp",
          "DSVF": "jmpf",
          "AMEM": "alloc",
          "DMEM": "dealloc",
          "ENPR": "entproc",
          "RTPR": "retproc",
          "INDX": "indx",
          "CRVM": "ldmv",
          "ARVM": "stmv",
          "DBUG": "dbug",
          "STEP": "step",
   
          # 2 args
          "CRVL": "ldvl",
          "CREN": "ldaddr",
          "ARMZ": "stvl",
          "CRVI": "ldvi",
          "ARMI": "stvi",
          "ENRT": "entlabl",
          "CREG": "ldgaddr",
          "CHPR": "call",

          # 3 args
          "CHPP": "callpar",
          }
          
          
INSTR_0 = [
          "add",
          "subt",
          "mult",
          "divi",
          "inv",
          "andd",
          "orr",
          "nott",
          "less",
          "grt",
          "eql",
          "dif",
          "leq",
          "geq",
          "nop",
          "halt",
          "read",
          "writ",
          "init",
          "cont",
          "dump",
          ]

# One arg instructions
INSTR_1 = [
          "ldct",
          "jmp",
          "jmpf",
          "alloc",
          "dealloc",
          "entproc",
          "retproc",
          "indx",
          "ldmv",
          "stmv",
          "dbug",
          "step",
          ]


# Two args instructions
INSTR_2 = [
          "ldvl",
          "ldaddr",
          "stvl",
          "ldvi",
          "stvi",
          "entlabl",
          "ldgaddr",
          "call",
         ]

# Three args instructions
INSTR_3 = [
          "callpar",
          ]


# All instructions
INSTR_CODES = INSTR_DICT.keys()
INSTR_ALL = INSTR_0 + INSTR_1 + INSTR_2 + INSTR_3
