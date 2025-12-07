#! /usr/bin/env python3

#------------------------------------------------------------------------#
#                                                                        #
# Last update: "mepa.py: 2015-10-07 (Wed)  13:02:42 BRT (tk)"            #
#                                                                        #
#------------------------------------------------------------------------#
#  This program implements the Pascal Virtual Machine MEPA as            #
#  described in the book "Implementação de Linguagens de Programação"    #
#  (in Portuguese).                                                      #
#                                                                        #
#  A few additional instructions were added in order to help debugging   #
#  and to implement array operations. A complete description of program's#
#  usage can be found in a companion document "Interpretador de MEPA"    #
#  (in Portuguese).                                                      #
#                                                                        #
# Language dependencies:                                                 #
# ----------------------                                                 #
#                                                                        #
#  (1) File "mepa_instr.py" may be edited in order to change instruction #
#      codes.                                                            #
#  (2) File "mepa_strings.py" may be edited in order to change messages. #
#      Formatting codes like '%s' should be always preserved.            #
#                                                                        #
#------------------------------------------------------------------------#
#                                                                        #
# Author: Tomasz Kowaltowski                                             #
#         Institute of Computing                                         #
#         University of Campinas                                         #
#         Campinas, SP, Brazil                                           #
#                                                                        #
#         www.ic.unicamp.br/~tomasz                                      #
#                                                                        #
#------------------------------------------------------------------------#
#                                                                        #
# HISTORY:                                                               #
#                                                                        #
#  2008-07-09: first version (previous versions were written in          #
#              Modula-3)                                                 #
#  2008-07-12: quick-and-dirty improved debugging                        #
#  2010-01-29: review and change to utf-8 encoding                       #
#  2010-01-30: fixed "silent" and "debug"                                #
#  --------------------------------------------------------------------- #
#  2014-11-29: started adaptation to Python-3 and English codes          #
#  2014-11-30: added --step option and instruction STEP                  #
#  2014-12-22: automatic language detection by program name              #
#              (see mepa_defs.py)                                        #
#  2015-05-30: fixed open file error detection                           #
#  2015-05-30: implemented missing instruction JMPL                      #
#  2015-10-07: detected usage of --step without --progfile               #
#                                                                        #
#------------------------------------------------------------------------#

COPY_RIGHT = """
#------------------------------------------------------------------------#
#                                                                        #
# Copyright (c) 2015, Tomasz Kowaltowski                                 #
#                     Institute of Computing                             #
#                     University of Campinas                             #
#                     Campinas, SP, Brazil                               #
#                                                                        #
#                     www.ic.unicamp.br/~tomasz                          #
#                                                                        #
#------------------------------------------------------------------------#
# All rights reserved.                                                   #
#                                                                        #
# This software may be used only under written permission of the holder  #
# of its copyright.                                                      #
#                                                                        #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER "AS IS" AND ANY      #
# EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE    #
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR     #
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR       #
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,  #
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,    #
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR     #
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF #
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING   #
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS     #
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.           #
#                                                                        #
#------------------------------------------------------------------------#
"""

import sys, traceback, getopt
import mepa_defs
from mepa_defs import *
from mepa_interp import execute

VERSION = "5.0"

#======================================================================
# Main
#======================================================================


if __name__ == "__main__":

    
    try:
        
        # Initialize and process options; open files
        
        try:
            opts, args = getopt.getopt(sys.argv[1:],"hc",OPTIONS)
        except:
            Msg(UNRECOGNIZED_OPTION)
            Msg(Usage,quit=True,code=1)


        for o,a in opts:
            if o=="-h" or o=="--help":
                Msg(Usage,quit=True)
            elif o=="-c" or o=="--copyright":
                Msg(COPY_RIGHT,quit=True)
            o = o[2:]  # remove leading --
            if o in BOOL_OPTIONS:
                OPTIONS_DICT[o] = True
            elif o in INT_OPTIONS:
                try:
                    n = int(a)
                    if n<=0:
                        raise
                    OPTIONS_DICT[o] = n
                except:
                    Msg(ILLEGAL_OPTION % (o,a),code=1,quit=True)
            elif o in FILE_OPTIONS:
                OPTIONS_DICT[o] = a
            else:
                Msg(ILLEGAL_OPTIONS)
                Msg(Usage,quit=True,code=1)
        
        
        first = True
        for k in OPTIONS_ORDER:
            v = OPTIONS_DICT[k]
            if k in FILE_OPTIONS:
                v = str(v)
                if v.startswith("<"):
                    p = v.find("<std")
                    if p<0:
                        Msg(ILLEGAL_OPTION % (k,v))
                    q = v.find(">",p)
                    if q<0:
                        Msg(ILLEGAL_OPTION % (k,v))
                    v = v[p+1:q]
                else:
                    ## These calls of "open" used to have under
                    ## Python2 modifiers 'wb' and 'rb', but it gave
                    ## errors under Python3 -- bytes instead of str?
                    ## Might have problems under Windows?
                    try:
                        if k=="messfile":
                            mepa_defs.MESS_FILE = open(v,"w")
                        elif k=="infile":
                            mepa_defs.IN_FILE = open(v,"r")
                        elif k=="outfile":
                            mepa_defs.OUT_FILE = open(v,"w")
                        elif k=="progfile":  # progfile
                            mepa_defs.PROG_FILE = open(v,"r")
                        else:
                            Msg(INTERNAL_ERROR % 1,code=1,quit=True)
                    except FileNotFoundError:
                        Msg(OPEN_FILE_ERROR % v, code=1,quit=True)

            if not OPTIONS_DICT["silent"]:       
                if first:
                    UndMsg(BANNER % VERSION,'=',1)
                    Msg('\n')
                    UndMsg(OPTIONS_TITLE,'-',0)
                    first = False
                Msg("%12s:  %s" % (k,v))
        if not OPTIONS_DICT["silent"]:  
            Msg("")
        if OPTIONS_DICT["step"] and mepa_defs.PROG_FILE==sys.stdin:
            Msg(STEP_STDIN,quit=True)
        P, L = inputProgram()
        fixArgs(P,L)
        # dumpProgram(P)   ###############
        MP = makeMepa(P)
        # dumpMepaP(MP)    ###############
        res = execute(MP,P,L,mepa_defs.MESS_FILE,mepa_defs.IN_FILE,mepa_defs.OUT_FILE)
        if res!=-1:
            Msg(EXECUTION_ERROR % res,quit=True,code=1)
        Msg("\n")

    except SystemExit as e:
        pass

    except:
        
        if not OPTIONS_DICT["silent"]:
            print("UNEXPECTED_EXCEPTION")
            traceback.print_exc()
        sys.exit(1)
       
