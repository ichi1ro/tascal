#------------------------------------------------------------------------#
#                                                                        #
# Last update: "mepa_interp.py: 2015-08-08 (Sat)  13:35:48 BRT (tk)"     #
#                                                                        #
#------------------------------------------------------------------------#
# See mepa.py file for description, history and copyright.               #
#------------------------------------------------------------------------#

#------------------------------------------------------------------------#
#                                                                        #
# Interpreting functions                                                 #
#                                                                        #
#------------------------------------------------------------------------#

import traceback

from mepa_defs import *

# Jump instructions
JMP_INSTR = [ "jmp", "retproc", "call", "callpar" ]

def execute(MP,P,L,msfile,infile,outfile):
    """Main execution function. """
    global s, i, D, M, labels, debug, nocheck, inf, outf, inputline, check, stepexec
    
    inf = infile
    outf = outfile
    labels = L
    inputline = []
    
    # initial register values and memory sizes
    i = 0
    s = -1
    D = OPTIONS_DICT["displaysize"] * [None]
    
    # memory is [v,t] where v: value, t: type (0: int, 1: level, 
    # 2: mem addr, 3: prog address)
    M = OPTIONS_DICT["stacksize"] * [None,None]
    
    debug = OPTIONS_DICT["debug"]
    nocheck = OPTIONS_DICT["nocheck"]
    check = not nocheck
    limit = OPTIONS_DICT["limit"]
    stepexec = OPTIONS_DICT["step"]
    count = 0
    
    # execution loop
    while True:
        li = i
        try:
            try:
                ins = MP[i]
            except:
                Msg(PROG_END,quit=True,code=1)
            if debug:
                deb(P)
            par = ins.find('(')
            if not ins[:par] in JMP_INSTR:
                i += 1
            eval(ins)
            if debug:
                Msg('')
            if stepexec:
                stepin = input(">>:")
                if stepin:
                    Msg(STOPPING_STEPEXEC)
                    stepexec = False
            count += 1
        except AssertionError as e:
            Msg("\n"+ILLEGAL_ARGUMENT_TYPE)
            sys.exit(1)
        except SystemExit as e:
            sys.exit(1)
        except:
            Msg(ILLEGAL_VALUE % li, quit=True)
        if i<0:      # halt()
            if debug:
                Msg("")
            Msg(EXECUTED_INSTRUCTIONS % count)
            return -1
        if count>=limit:
            Msg(MAXIMUM_INSTRUCTIONS_EXCEEDED % limit,quit=True,code=1)

# Auxiliary instruction functions

def unop(op):
    """ Unary operation. """
    global s, M, check, debug
    if check:
        assert M[s][1]==0
    top(1)
    if op=="inv":
        M[s] = [-M[s][0],0]
    elif op=="nott":
        M[s] = [1-M[s][0],0]
    else:
        impossible(4)

def binop(op):
    """ Binary operation. """
    global s, M, check
    if check:
        assert M[s-1][1]==0 and M[s][1]==0
    top(2)
    v1 = M[s-1][0]
    v2 = M[s][0]
    if op=="add":
        newval = v1+v2
    elif op=="subt":
        newval = v1-v2
    elif op=="mult":
        newval = v1*v2
    elif op=="divi":
        newval = v1//v2
    elif op=="andd":
        newval = v1 and v2
    elif op=="orr":
        newval = v1 or v2
    elif op=="less":
        newval = v1<v2
    elif op=="grt":
        newval = v1>v2
    elif op=="eql":
        newval = v1==v2
    elif op=="dif":
        newval = v1!=v2
    elif op=="leq":
        newval = v1<=v2
    elif op=="geq":
        newval = v1>=v2
    else:
        impossible(5)
    
    s -= 1
    M[s] = [newval,0]

def memop(op,m,n):
    """Memory access binary operation. """
    global s, M, D, check
    assert D[m]!=None
    
    addr = D[m]+n
    
    debnum(addr)
    if op=="ldvl":
        s += 1;  M[s] = M[addr]
    elif op=="ldaddr":
        s += 1;  M[s] = [addr,2]
    elif op=="stvl":
        M[addr] = M[s];  s -= 1
    elif op=="ldvi":
        if check:
            assert M[addr][1]==2
        s += 1;  M[s] = M[M[addr][0]]
    elif op=="stvi":
        if check:
            assert M[addr][1]==2
        M[M[addr][0]] = M[s];  s -= 1
    else:
        impossible(6)
    


# Instructions

def add():
    binop("add")

def subt():
    binop("subt")
    
def mult():
    binop("mult")

def divi():
    binop("divi")

def andd():
    binop("andd")

def orr():
    binop("orr")

def less():
    binop("less")

def grt():
    binop("grt")
    
def eql():
    binop("eql")
    
def dif():
    binop("dif")
    
def leq():
    binop("leq")

def geq():
    binop("geq")

def inv():
    unop("inv")

def nott():
    unop("nott")

def nop():
    pass
    
def halt():
    global i
    i = -1

def read():
    global s, M, inputline, inf
    assert len(M)>s
    while True:
        if len(inputline)>0:
            break
        inputline = inf.readline()
        if not inputline:
            Msg("\n"+UNEXPECTED_EOF_INPUT,quit=True,code=1)
        inputline = inputline[:-1].strip().split()
    try:
        v = int(inputline[0])
        inputline = inputline[1:]
        s += 1; M[s] = [v,0]
        top(1)
    except:
        Msg(ILLEGAL_INPUT_VALUE,quit=True,code=1)
    
def writ():
    global s, M, outf, debug
    if check:
        assert M[s][1]==0
    top(1)
    outf.write("%d\n" % M[s][0])
    s -= 1

def init():
    global s,D
    s = -1;  D[0] = 0

def cont():
    if check:
        assert M[s][1]==2
    top(1)
    M[s] = M[M[s][0]]

def ldct(k):
    global s, M
    s += 1;  
    assert len(M)>s
    M[s] = [k,0]
    top(1)

def jmp(p):
    global i
    debnum(p)
    i = p

def jmpf(p):
    global i, s, M
    if check:
        assert M[s][1]==0
    debnum(p)
    top(1)
    if not M[s][0]:
        i = p
    s -= 1

def alloc(n):
    global s
    s += n

def dealloc(n):
    global s
    s -= n

def entproc(k):
    global s, D, M
    assert len(D)>k
    debnum(D[k-1])
    s += 1
    assert len(M)>s
    M[s] = [D[k-1],2]
    D[k] = s+1
    
def retproc(n):
    global i, s, D, M
    if check:
        assert M[s-1][1]==1 and M[s-2][1]==2 and M[s-3][1]==3
    top(3,1)
    t = M[s-1][0]
    D[t] = M[s-2][0]
    i = M[s-3][0]
    s -= (n+4)
    while t>1:
        if check:
            assert M[D[t]-1][1]==2
        D[t-1] = M[D[t]-1][0]
        t -= 1
        
def indx(k):
    global s, M
    if check:
        assert M[s-1][1]==2 and M[s][1]==0
    top(2)
    M[s-1] = [M[s-1][0]+M[s][0]*k,2]
    s -= 1

def ldmv(k):
    global s, M
    if check:
        assert M[s][1]==2
    assert len(M)>(s+k)
    top(1)
    t = M[s][0]
    M[s:s+k] = M[t:t+k]
    s += (k-1)
    
def stmv(k):
    global s, M
    if check:
        assert M[s-k][1]==2
    top(1,k)
    t = M[s-k][0]
    M[t:t+k] = M[s-k+1:s+1]
    s -= (k+1)


def ldvl(m,n):
    memop("ldvl",m,n)
    
def ldaddr(m,n):
    memop("ldaddr",m,n)
    
def stvl(m,n):
    memop("stvl",m,n)
    
def ldvi(m,n):
    memop("ldvi",m,n)
    
def stvi(m,n):
    memop("stvi",m,n)  
    
def entlabl(j,n):
    global s, D
    debnum(D[j])
    s = D[j]+n-1

def ldgaddr(p,k):
    global s, D, M
    assert len(M)>(s+3)
    M[s+1] = [p,3]
    M[s+2] = [D[k],2]
    M[s+3] = [k,1]
    s += 3
    top(3)

def call(p,k):
    global i, s, D, M
    assert len(M)>(s+3)
    M[s+1] = [i+1,3]
    M[s+2] = [D[k],2]
    M[s+3] = [k,1]
    s += 3
    top(3)
    i = p
    
def callpar(m,n,k):
    global i, s, D, M
    assert D[m]!=None
    addr = D[m]+n
    assert len(M)>(s+3)
    if check:
        assert M[addr][1]==3 and M[addr+1][1]==2 and M[addr+2][1]==1
    debnum(addr)
    M[s+1] = [i+1,3]
    M[s+2] = [D[k],2]
    M[s+3] = [k,1]
    s += 3
    top(3)
    i = M[addr][0]
    t = M[addr+2][0]
    D[t] = M[addr+1][0]
    while t>1:
        if check:
            assert M[D[t]-1][1]==2
        D[t-1] = M[D[t]-1][0]
        t -= 1

def dbug(t):
    """ Set on/off debugging flag."""
    global debug
    if t and not debug:
        Msg(STARTING_DEBUGGING)
    elif debug and not t:
        Msg(STOPPING_DEBUGGING)
    debug = t

def step(t):
    """ Set on/off step execution flag."""
    global stepexec
    if t and not stepexec:
        Msg(STARTING_STEPEXEC)
    elif stepexec and not t:
        Msg(STOPPING_STEPEXEC)
    stepexec = t

def dump():
    """ Dump everything that can be useful. """
    global i, s, M, D, labels
    UndMsg(DUMP,'=',2)
    Msg("i=%3d, s=%3d" % (i,s))
    UndMsg(DISPLAY,'-')
    for k in range(OPTIONS_DICT["displaysize"]):
        if D[k]!=None:
            Msg("%2d: %5d" % (k,D[k]))
    UndMsg(MEMORY,'-')
    for k in range(OPTIONS_DICT["stacksize"]):
        if M[k]!=None and M[k][0]!=None:
            Msg("%2d: %5d (%d)" % (k,M[k][0],M[k][1]))
    UndMsg(LABELS,'-')
    for lab in labels:
        Msg("%-5s:  %d" % (lab,labels[lab]))

    UndMsg(END_DUMP,"=")


def deb(P):
    """Debugging function. """
    global i, s
    Msg("i=%3d, s=%3d:      %-20s      " % (i,s,P[i][3]),eol=False)

def top(k,adj=0):
    """ Prints stack top (adjusted) 'k' values. """
    global s, M, debug
    if debug:
        for i in range(k):
            stack(s-k+i+1-adj)
        #Msg("")
            
        
def stack(n):
    """ Prints M[n]. """
    global M, debug
    if debug:
        try:
            v,t = M[n]
            Msg("%d (%d)    " % (v,t),eol=False)
        except:
            Msg(ILLEGAL_DEBUG_VALUE)

def debnum(addr):
    """ Prints an address. """
    global debug
    if debug:
        Msg("%d        " % addr,eol=False)
        
