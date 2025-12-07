
#------------------------------------------------------------------------#
#                                                                        #
# Last update: "mepa_defs.py: 2015-05-30 (Sat)  09:20:05 BRT (tk)"       #
#                                                                        #
#------------------------------------------------------------------------#
# See mepa.py file for description, history and copyright.               #
#------------------------------------------------------------------------#

#------------------------------------------------------------------------#
#                                                                        #
# General definitions for MEPA interpreter.                              #
#                                                                        #
#------------------------------------------------------------------------#


import sys, traceback, getopt

if sys.argv[0].endswith("mepa_pt.py"):
    from mepa_instr_pt import *
    from mepa_strings_pt import *
else: ## default en
    from mepa_instr_en import *
    from mepa_strings_en import *
    
Usage = """
Usage:

    [python3] mepa.py 
         [-h | --help (False)] [-c | --copyright (False)]
         [--messfile <file name> (stderr)]
         [--programsize <integer> (500)]
         [--stacksize <integer> (500)]
         [--displaysize <integer> (10)]
         [--limit <integer> (10000)]
         [--infile <file name> (stdin)]
         [--outfile <file name> (stdout)]
         [--progfile <file name> (stdin)]
         [--debug (False)]
         [--nocheck (False)]
         [--silent (False)]
         [--step (False)]
"""


OPTIONS_DICT = { 
                 "help":        False,
                 "copyright":   False,
                 "messfile":    sys.stderr,
                 "programsize": 500,
                 "stacksize":   500,
                 "displaysize": 10,
                 "limit":       10000,
                 "infile":      sys.stdin,
                 "outfile":     sys.stdout,
                 "progfile":    sys.stdin,
                 "debug":       False,
                 "nocheck":     False,
                 "silent":      False,
                 "step":        False,
               }
               
BOOL_OPTIONS = [ "help", "copyright", "debug", "nocheck", "silent", "step"]
INT_OPTIONS =  [ "programsize", "stacksize", "displaysize", "limit"]
FILE_OPTIONS = [ "messfile", "infile", "outfile", "progfile"]

def appendColumn(s): 
    """ Help to process options requiring args. """
    return s+"="
    
OPTIONS = BOOL_OPTIONS + list(map(appendColumn,INT_OPTIONS+FILE_OPTIONS))
OPTIONS_ORDER = FILE_OPTIONS + INT_OPTIONS + BOOL_OPTIONS

MESS_FILE = sys.stderr
IN_FILE = sys.stdin
OUT_FILE = sys.stdout
PROG_FILE = sys.stdin

def Msg(msg,quit=False,code=0,silent=False,eol=True):
    """ Error and other messages. """
    if not silent:
        if eol:
            MESS_FILE.write(msg+'\n')
        else:
            MESS_FILE.write(msg)
        MESS_FILE.flush()
    if quit:
        sys.exit(code)

def UndMsg(s,c,k=1):
    Msg(s)
    Msg((len(s)-k)*c)
    
def impossible(k):
    Msg(INTERNAL_ERROR % k,quit=True,code=1)


def inputProgram():
    """ Decodes program instructions """
    
    LABEL_DICT = {}
    P = []
    count = 0
    maxsize = OPTIONS_DICT["programsize"]
    #debug = OPTIONS_DICT["debug"]
    while True:
        try:
            line = inline = PROG_FILE.readline()
        except:
            Msg(UNEXPECTED_PROGRAM_READING_EXCEPTION,quit=True,code=1)
        if not line:
            Msg(UNEXPECTED_EOF_PROGRAM,quit=True,code=1)
        line = line.strip()
        if line=="" or line.startswith(';'):
            continue
        lab, line = getLabel(line)
        if lab==None:
            Msg(ILLEGAL_INSTRUCTION_LABEL % (count,inline),quit=True,code=1)
        instr, line = getInstr(line)
        if instr==None:
            Msg(MISSING_INSTRUCTION_CODE % (count,inline),quit=True,code=1)

        if instr.upper()==END_INSTR:
            break
        if count+1>=maxsize:
            Msg(PROGRAM_TOO_LARGE,quit=True,code=1)
            
        try:
            code = INSTR_DICT[instr.upper()]
        except:
            Msg(ILLEGAL_INSTRUCTION % (count,inline),quit=True,code=1)
            
        if code in INSTR_0:
            numargs = 0
            args = []
        elif code in INSTR_1:
            numargs = 1
        elif code in INSTR_2:
            numargs = 2
        elif code in INSTR_3:
            numargs = 3
        else:
            impossible(7)
            
        args = getArgs(line,numargs)
        if args==None:
            Msg(ILLEGAL_INSTRUCTION_ARGUMENTS % (count,inline),quit=True,code=1)
        p = [lab, instr, args]
        p.append(inline[:-1]) # includes original instr line
        P.append(p)
        if lab!="":
            if lab in LABEL_DICT:
                Msg(REDEFINED_LABEL % (count,inline),quit=True,code=1)
            else:
                LABEL_DICT[lab] = count

        count += 1
        

    return [P, LABEL_DICT]

def getLabel(s):
    """ Determines instruction label, if any. """
    p = s.split()
    lab = p[0]
    if lab.endswith(':'):
        lab = lab[:-1]
        if lab.isalnum() and lab[0].isalpha():
            return [p[0][:-1]," ".join(p[1:])]
        else:
            return [None,""]
    else:
        return ["",s]

def getInstr(s):
    """Determines instruction code. """
    p = s.split()
    if len(p)==0:
        return [None,""]
    else:
        return [p[0]," ".join(p[1:])]
        
def getArgs(s,n):
    """ Determine n arguments. """
    if n==0:
        return []
    p = s.split()
    if len(p)==0:
        return None
    p = p[0].split(',')
    if len(p)<n:
        return None
    return p[:n]


def dumpProgram(P):
    for p in P:
        lab = p[0]
        instr = p[1]
        args = p[2]
        if len(args)==0:
            ar = ""
        elif len(args)==1:
            ar = "%r" % args[0]
        elif len(args)==2:
            ar = "%r,%r" % (args[0],args[1])
        elif len(args)==3:
            ar = "%r,%r,%r" % (args[0],args[1],args[2])
        else:
            Msg(INTERNAL_ERROR % 2,quit=True,code=1)
        if lab!="":
            lab += ':'
        Msg("%-5s  %s  %s" % (lab,instr,ar))
        
def dumpLabels(L):
    for l in L:
        print("%-5s:  %d" % (l,L[l]))

def fixArgs(P,L):
    """ Replace symbolic labels by Mepa addresses and transform other
        arguments into numbers.
    """
    count = 0
    for p in P:
        args = p[2]
        for k in range(len(args)):
            a = args[k]
            if (a[0] in ('+','-') and a[1:].isdigit()) or\
               (a.isdigit()):
                pass
            elif a in L:
                args[k] = str(L[a])
            else:
                Msg(ILLEGAL_ARGUMENT % count,quit=True,code=1)
            count += 1
            
def makeMepa(P):
    """ Transforms program into execution strings. """
    MP = []
    for p in P:
        name = INSTR_DICT[p[1].upper()]
        args = ",".join(p[2])
        m = "%s(%s)" % (name,args)
        MP.append(m)
    return MP

def dumpMepaP(MP):
    for m in MP:
        print(m)
        
