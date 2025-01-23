from __future__ import annotations
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from pyforth.runtime import CallFrame
import logging
from pyforth.primitives import forthprim
from pyforth.exceptions import WordNotFoundError, ExecutionError

#Flags for compilation
BEGINFLAG = "BEGINFLAG"
WHILEFLAG = "WHILEFLAG"
DOFLAG    ="DOFLAG"
LEAVEFLAG = "LEAVEFLAG"

@forthprim("RESET")
def forth_reset(engine, caller):
    engine.reset()


@forthprim(".")
def forth_print(engine, caller):
    """print TOS"""
    sp = engine.stack
    top = sp[-1]
    sp.pop()
    print(top)


@forthprim('(', isImmediate=True)
def paren(engine, caller):
    """ start of a comment. Complete until ')' """
    engine.get_input_till(')')[1:]

@forthprim('."', isImmediate=True)
def dot_quote(engine, caller):
    """fetch the next words up and until then next quote char.
    if compiling then compile this as a string constant and a print , otherwise print it out"""
    s = engine.get_input_till('"')[1:]
    if engine.isCompiling:
        engine.compileConstant(s)
        engine.compileWord(".")
    else:
        print(s)


@forthprim("!")
def store(engine, caller):
    addr = engine.pop()
    n = engine.pop()
    engine.mem[addr] = n


@forthprim("@")
def fetch(engine, caller):
    addr = engine.pop()
    engine.push(engine.mem[addr])

@forthprim("FILL")
def fill(engine, caller):
    """fill memory at add with u elements b
    ( addr u b ->)
    """
    addr, u, b = engine.pop(3)
    engine.fillMem(addr, u, b)


@forthprim("MOVE")
def move(engine, caller):
    """ move u items in memory 
    ( from to u->)
    """
    origin, dest, nrItems = engine.pop(3)
    engine.moveMem(origin, dest, nrItems)


@forthprim("ERASE")
def erase(engine, caller):
    """ erase u items in memory 
    ( addr   u->)
    """
    addr, nrItems = engine.pop(2)
    engine.fillMem(addr, nrItems, None)

@forthprim("BLANKS")
def blanks(engine, caller):
    """ set u blanks in memory 
    ( addr   u->)
    """
    addr, nrItems = engine.pop(2)
    engine.fillMem(addr, nrItems, " ")

@forthprim("TOGGLE")
def toggle(engine, caller):
    """ XOR item  in memory with b
    ( addr  b ->)
    """
    addr, val = engine.pop(2)
    if not isinstance(val, int):
        raise ValueError(f'XOR requires an integer value, found "{val}"')
    target = engine.mem[addr]
    if not isinstance(target, int):
        raise ValueError(f'XOR requires an integer target, found "{target} at {addr}"')    
    engine.mem[addr] = target ^ val


@forthprim("*")
def forthMul(engine, caller):
    sp = engine.stack
    n = sp.pop() * sp.pop()
    sp.append(n)


@forthprim("*/")
def forthMulDiv(engine, caller):
    sp = engine.stack
    n3 = sp.pop()
    n = sp.pop() * sp.pop() / n3
    sp.append(n)


@forthprim("/")
def forthDiv(engine, caller):
    sp = engine.stack
    divisor = sp.pop()
    n = sp.pop() / divisor
    sp.append(n)


@forthprim("+")
def forthAdd(engine, caller):
    sp = engine.stack
    a = sp.pop()
    n = sp.pop() + a
    sp.append(n)


@forthprim("-")
def forthSubtract(engine, caller):
    sp = engine.stack
    n2 = sp.pop()
    n = sp.pop() - n2
    sp.append(n)


@forthprim("OR")
def forthOr(engine, caller):
    """n1 n2 -> n3"""
    engine.push(engine.pop() or engine.pop())


@forthprim("XOR")
def forthXor(engine, caller):
    """n1 n2 -> n3"""
    engine.push(engine.pop() ^ engine.pop())


@forthprim("+!")
def forth_plus_bang(engine, caller):
    sp = engine.stack
    addr = sp.pop()
    engine.mem[addr] += sp.pop()


@forthprim("+-")
def forthchangeSigne(engine, caller):
    """n1 n2 -> n3
    apply sign of n2 on n1"""
    sp = engine.stack
    sign = sp.pop()
    if sign < 0:
        sp[-1] *= -1


@forthprim("-DUP")
def minusDup(engine, caller):
    """n1 -> n1  if n1  == 0
    n1 -> n1 n1 if n1 != 0"""
    sp = engine.stack
    if sp[-1]:
        sp.append(sp[-1])


@forthprim("0<")
def ltzero(engine, caller):
    sp = engine.stack
    sp.append(sp.pop() < 0)


@forthprim("0=")
def eqzero(engine, caller):
    sp = engine.stack
    sp.append(sp.pop() == 0)


@forthprim("1+")
def inc1(engine, caller):
    sp = engine.stack
    sp[-1] += 1


@forthprim("2+")
def inc2(engine, caller):
    sp = engine.stack
    sp[-1] += 2


@forthprim("<")
def lt(engine, caller):
    sp = engine.stack
    n2 = sp.pop()
    n1 = sp.pop()
    sp.append(n1 < n2)


@forthprim("=")
def eq(engine, caller):
    sp = engine.stack
    n2 = sp.pop()
    n1 = sp.pop()
    sp.append(n1 == n2)


@forthprim(">")
def gt(engine, caller):
    """ 2 1 > -> True-"""
    sp = engine.stack
    n2 = sp.pop()
    n1 = sp.pop()
    sp.append(n1 > n2)


@forthprim(">=")
def ge(engine, caller):
    sp = engine.stack
    n2 = sp.pop()
    n1 = sp.pop()
    sp.append(n1 >= n2)


@forthprim("<=")
def le(engine, caller):
    sp = engine.stack
    n2 = sp.pop()
    n1 = sp.pop()
    sp.append(n1 <= n2)


@forthprim("?")
def question_mark(engine, caller):
    sp = engine.stack
    addr = sp.pop()
    print(engine.mem[addr])


@forthprim(":")
def startCompile(engine, caller):
    methodName = engine.nextWord()
    engine.startCompiling(methodName)


@forthprim(";", isImmediate=True, inColonOnly=True)
def endCompile(engine, caller):
    engine.completeCompile()


@forthprim("DUP")
def forthDup(engine, caller):
    engine.stack.append(engine.stack[-1])


@forthprim("DROP")
def forthDrop(engine, caller):
    engine.pop()


@forthprim("ROT")
def forthdrop(engine, caller):
    """n1 n2 n3 -> n2 n3 n1"""
    n3 = engine.pop()
    n2 = engine.pop()
    n1 = engine.pop()
    engine.push(n2)
    engine.push(n3)
    engine.push(n1)


@forthprim("OVER")
def forthover(engine, caller):
    """n1 n2 -> n1 n2 n1"""
    n1 = engine.stack[-2]
    engine.push(n1)


@forthprim("SWAP")
def swap(engine, caller):
    """n1 n2 -> n2 n1"""
    n2 = engine.pop()
    n1 = engine.pop()
    engine.push(n2)
    engine.push(n1)


# Return Stack
@forthprim(">R")
def toR(engine, caller):
    """move TOS to Return stack
    ( n -> )"""
    engine.rp.append(engine.pop())


@forthprim("R>")
def r_to(engine, caller):
    """move top of Return stack to stack
    (  -> n)"""
    engine.push(engine.rp.pop())


@forthprim("R")
def forth_r(engine, caller):
    """copy top of Return stack to stack
    (  -> n)"""
    engine.push(engine.rp[-1])


"""looping"""


@forthprim("I")
def forthI(engine, caller):
    """index of current loop"""
    engine.push(engine.rp[-1])

@forthprim("J")
def forthJ(engine, caller):
    """index if next outer loop"""
    engine.push(engine.rp[-3])


@forthprim("DO", isImmediate=True)
def forthDo(engine, caller):
    """set a marker for the LOOP statement
    ( I Limit -- )

    """
    engine.start_loop()
    engine.compileWord(">R")  # store the Limit
    engine.compileWord(">R")  # store the index (aka I)

    # save on the stack the location of the next step (i.e. the start of the loop)
    engine.stack.append(len(engine.compilingMethod.code))  
    # save a marker that there is a DO active
    engine.stack.append(DOFLAG)
    engine.compileWord("(DO)") # 
    engine.compileWord("0BRANCH")
    engine.compileConstant(0)  # at addr + 2


@forthprim("(DO)")
def forthRunTimeDo(engine, caller):
    """push start index and loop limit onto return stack"""
    index = engine.rp[-1]
    limit = engine.rp[-2]
    if index >= limit:
        engine.push(0)      
    else:
        engine.push(1)


@forthprim("LOOP", isImmediate=True)
def forthLoop(engine, caller):
    """compile a decrement i and jump to marker"""
    engine.end_loop()
    if DOFLAG != engine.pop():
        raise ValueError("LOOP statement did not see a paired DO")
    engine.compileWord("(LOOP)")
    doAddr = engine.pop()
    engine.compileConstant(
        doAddr - len(engine.compilingMethod.code)
    )  # constant for the branch of the (LOOP)

    # fixup the const for the 0Branch after the (DO) word
    branchConst = engine.compilingMethod.code[doAddr + 2]
    branchConst.constantValue = len(engine.compilingMethod.code) - doAddr - 2
    """Remove the loop limit and loop index"""
    engine.compileWord("R>")
    engine.compileWord("R>")
    engine.compileWord("DROP")
    engine.compileWord("DROP")



@forthprim("+LOOP", isImmediate=True)
def forthPlusLoop(engine, caller):
    """compile a decrement i and jump to marker"""
    engine.end_loop()
    if DOFLAG != engine.pop():
        raise ValueError("LOOP statement did not see a paired DO")
    engine.compileWord("(+LOOP)")
    doAddr = engine.pop()
    engine.compileConstant(
        doAddr - len(engine.compilingMethod.code)
    )  # constant for the branch of the (LOOP)

    # fixup the const for the 0Branch after the (DO) word
    branchConst = engine.compilingMethod.code[doAddr + 2]
    branchConst.constantValue = len(engine.compilingMethod.code) - doAddr - 2
    # remove the 2 items on the RP stack
    engine.compileWord("R>")
    engine.compileWord("R>")
    engine.compileWord("DROP")
    engine.compileWord("DROP")


@forthprim("(LOOP)", executeOnly=True)
def forthDoLoop(engine, caller):
    """compile a decrement i and jump to marker
    (  -- )
    """
    engine.rp[-1] += 1
    caller.branch()


@forthprim("(+LOOP)", executeOnly=True)
def forthDoPlusLoop(engine, caller):
    """compile a decrement i and jump to marker
    (inc --  )
    """
    inc = engine.pop()
    engine.rp[-1] += inc
    caller.branch()

@forthprim("LEAVE", isImmediate=True)
def forthLeave(engine, caller):
    """effect the leav of the current LOOP"""
    # caller.leave()
    # check there is an active BEGIN, WHILE or DO
    if not engine.stack:
        raise ValueError(" Syntax error. LEAVE used outside of active loop")
    # check that stack has one of these flags
    foundflags = [flag in engine.stack for flag in [BEGINFLAG, WHILEFLAG, DOFLAG]]
    if not any(foundflags):    
        raise ValueError (" Syntax error. LEAVE used outside of active loop")
    engine.compileWord("(LEAVE)")  
    
    engine.compileConstant(0) # offset to jump
    engine.mark_leave(len(engine.compilingMethod.code)-1) #referene to compiled constant
    

@forthprim("(LEAVE)", executeOnly=True)
def forthDoLeave(engine, caller):  
    # just jump relative to next adddress
    caller.branch()

@forthprim("BEGIN", isImmediate=True)
def ForthBegin(engine, caller):
    engine.start_loop()
    engine.stack.append(len(engine.compilingMethod.code))
    engine.stack.append(BEGINFLAG)


@forthprim("UNTIL", isImmediate=True)
def ForthUntil(engine, caller):
    if BEGINFLAG != engine.pop():
        raise ValueError("UNTIL statement did not see a paired BEGIN")
    addr = engine.pop()
    engine.end_loop()
    engine.compileWord("0BRANCH")
    
    engine.compileConstant(addr - len(engine.compilingMethod.code))
    


@forthprim("WHILE", isImmediate=True)
def ForthWhile(engine, caller):
    flag = engine.pop()
    if flag != BEGINFLAG:
        raise ValueError("WHILE statement did not see a paired BEGIN")
    engine.compileWord("0BRANCH")
    engine.compileConstant(0)
    addr = len(engine.compilingMethod.code) - 1
    engine.push(addr)
    engine.push(WHILEFLAG)


@forthprim("REPEAT", isImmediate=True)
def ForthRepeat(engine, caller):
    engine.end_loop()
    flag = engine.pop()
    if flag != WHILEFLAG:
        raise ValueError("REPEAT statement did not see a paired WHILE")
    whileAddr = engine.pop()
    beginAddr = engine.pop()
    engine.compileWord("BRANCH")
    addr = len(engine.compilingMethod.code)
    engine.compileConstant(beginAddr - addr)
    # update the branch distance at the WHILE
    branchDistance = engine.compilingMethod.code[
        whileAddr
    ]  # get the JUMP constant at the WHILE statement
    branchDistance.constantValue = (
        len(engine.compilingMethod.code) - whileAddr
    )  # update it to point past this code


"""branching"""


@forthprim("BRANCH")
def forthBranch(engine, caller):
    """jump relative to current position"""
    caller.branch()


@forthprim("0BRANCH")
def forthZeroBranch(engine, caller):
    """jump relative to current position if TOS is zero (or False"""
    flag = engine.pop()
    if (flag == 0) or not flag:
        caller.branch()
    else:
        caller.jumpRelative(1)  # jump over branch constant


@forthprim("IF", isImmediate=True)
def compileIf(engine, caller):
    """compile a 0branch and a temporary zero constant. leave location of that constant on stack"""
    engine.compileWord("0BRANCH")
    engine.compileConstant(0)
    engine.push(len(engine.compilingMethod.code) - 1)
    engine.push("DOIF")  # flag


@forthprim("ELSE", isImmediate=True)
def compileElse(engine, caller):
    engine.compileWord("BRANCH")
    engine.compileConstant(0)
    addr = len(engine.compilingMethod.code) - 1
    flag = engine.pop()
    if flag != "DOIF":
        raise ValueError("ELSE statement did not see a paired IF")
    branchValueLocation = engine.pop()
    branchDistance = engine.compilingMethod.code[
        branchValueLocation
    ]  # get the constant with the jump distance
    branchDistance.constantValue = (
        len(engine.compilingMethod.code) - branchValueLocation
    )
    logging.debug(
        "Compiling ELSE: fixing up branch value at {} to {}".format(
            branchValueLocation, branchDistance.constantValue
        )
    )
    engine.push(addr)
    engine.push("DOIF")  # flag


@forthprim("ENDIF", isImmediate=True)
def compileEndif(engine, caller):
    flag = engine.pop()
    if flag != "DOIF":
        raise ValueError("ENDIF statement did not see a paired IF")

    branchValueLocation = engine.pop()
    branchDistance = engine.compilingMethod.code[
        branchValueLocation
    ]  # get the constant with the jump distance
    branchDistance.constantValue = (
        len(engine.compilingMethod.code) - branchValueLocation
    )  # relative jump
    logging.debug(
        "Compiling Endif: fixing up branch value at {} to {}".format(
            branchValueLocation, branchDistance.constantValue
        )
    )

@forthprim("[COMPILE]")
def forthCompile(engine, caller):
    """during comilation force compilation of next word, even if 
    it is marked as immediate"""
    methodName = engine.nextWord()
    engine.compileWord(methodName)

@forthprim("VARIABLE")
def compileVariable(engine, caller):
    """compile a word, that when called will leave an address of a variable, which then can be used with @ and !"""
    varName = engine.nextWord()
    engine.startCompiling(varName)
    addr = engine.mem.append(engine.pop())
    engine.compileConstant(addr)
    engine.completeCompile()


@forthprim("CONSTANT")
def compileConstant(engine, caller):
    """compile a constant, that when called will push the constant value on the stack"""
    varName = engine.nextWord()
    engine.startCompiling(varName)
    engine.compileConstant(engine.pop())
    engine.completeCompile()



@forthprim("VOCABULARY", isImmediate=True)
def mk_vocabulary(engine, caller):
    """create a vocabulary or select it"""
    voc_name = engine.nextWord()
    assert voc_name not in engine.vocabularies
    engine.vocabularies[voc_name] ={}
    engine.startCompiling(voc_name)
    engine.compileConstant(voc_name)
    engine.compileWord("(VOCABULARY)")
    engine.completeCompile()
    engine.definitions = voc_name


@forthprim("(VOCABULARY)")
def invoke_vocabulary(engine, caller):
    """create a vocabulary or select it"""
    voc_name = engine.pop()
    assert voc_name in engine.vocabularies
    engine.context = voc_name
    
@forthprim("DEFINITIONS")
def definitions_vocabulary(engine, caller):
    """create a vocabulary or select it"""
    voc_name = engine.pop()
    assert voc_name in engine.vocabularies
    engine.definitions = voc_name

@forthprim("WORDS")
def showWords(engine, caller):
    global vocabulary
    names = sorted(vocabulary.keys())
    print(" ".join(names))


@forthprim("EXPECT")
def expect(engine, caller):
    txt = str(input(">"))
    engine.push(txt)


@forthprim("SPLIT")
def split(engine, caller):
    """s c ->array ...
    split a string using delimiter c
    """
    delim = engine.pop()
    arr = engine.pop().split(delim)
    engine.push(arr)


@forthprim("LOAD")
def loadForth(engine, caller):
    with open(engine.pop(), "r", encoding="utf-8") as fd:
        engine.readFrom(fd)


@forthprim("FORMAT")
def formatString(engine, caller):
    """format a string , using the python format command.
    ( arg1, arg2 .. argn, formatString -> formattedResult )
    """
    # count all open curlies in the format string
    fmtString = engine.pop()
    nParams = fmtString.count("{")
    args = [engine.stack.pop() for p in range(nParams)]
    logging.debug(args)
    result = fmtString.format(*tuple(reversed(args)))
    engine.push(result)


# execute words


@forthprim("'")
def tick(engine, caller):
    """take the next word and put the associated method on the stack.
    Used for EXECUTE and MAP etc"""
    nextWord = engine.nextWord()
    if nextWord:
        method = engine.vocabulary.get(nextWord, None)
        if method:
            engine.push(method)
        else:
            raise WordNotFoundError(nextWord, "not in Vocabulary")
    else:
        raise ValueError("Empty Input after tick")


@forthprim("EXECUTE")
def forthExecute(engine, caller):
    """execute the method that is on TOS"""
    method = engine.pop()
    engine.execute(method, caller)


# Array stuff


@forthprim("[")
def forthArrayStart(engine, caller):
    """execute the method that is on TOS"""
    engine.push("LABEL[")


@forthprim("]")
def forthArrayEnd(engine, caller):
    """execute the method that is on TOS"""
    # found = False
    result = []
    while len(engine.stack) > 0:
        item = engine.pop()
        if item == "LABEL[":
            break
        result.append(item)
    if item == "LABEL[":
        result.reverse()
        engine.push(result)
    else:
        raise ExecutionError("Array Expression", "Found ']' without matching '['")


@forthprim("MAP")
def forthArrayMap(engine, caller):
    """run a map on an array
    (arr forthWord -- )"""
    method = engine.pop()
    arr = engine.pop()
    for item in arr:
        engine.push(item)
        method.execute(engine, caller)


@forthprim("UNPACK")
def forthArrayUnpack(engine, caller):
    """unpack an array"""
    arr = engine.pop()
    for item in reversed(arr):
        engine.push(item)


@forthprim("PACK")
def forthArray_pack(engine, caller):
    """unpack an array
    (n1 , n2, ..nx depth - arr)
    """
    depth = engine.pop()
    result = [engine.pop() for n in range(depth)]
    engine.push(reversed(result))


@forthprim("LEN")
def forthLen(engine, caller):
    """determine the len attribute of the TOS
    ( n -- n len)
    """
    engine.push(len(engine.stack[-1]))

@forthprim("MOD")
def forthMod(engine, caller):
    """modulo function ( n1, n2 -> rest )"""
    n1 = engine.pop()
    n2 = engine.pop()
    r = n2 % n1
    engine.push(r)


@forthprim("/MOD")
def forthSlashMod(engine, caller):
    """modulo function ( n1, n2 -> rest qu0t)"""
    n2 = engine.pop()
    n1 = engine.pop()
    q, r = divmod(n1, n2)
    
    engine.push(r)
    engine.push(q)



@forthprim("*/MOD")
def forthstarSlashMod(engine, caller):
    """modulo function ( n1, n2 n3 -> rest qu0t)
    multiplication, followed by division  n1 * n2/n3"""
    n3 = engine.pop()
    n2 = engine.pop()
    n1 = engine.pop()
    nn = n1 * n2
    q, r = divmod(nn, n3)
    engine.push(r)
    engine.push(q)    


@forthprim("*/")
def forthstarSlash(engine, caller):
    """( n1, n2 n3 -> qu0t)
    multiplication, followed by division  n1 * n2/n3"""
    n3 = engine.pop()
    n2 = engine.pop()
    n1 = engine.pop()
    nn = n1 * n2
    q, r = divmod(nn, n3)
    engine.push(q)   

@forthprim("MIN")
def forthMin(engine, caller):
    """( n1, n2 -> n)
    smaller of the two values"""
    n2 = engine.pop()
    n1 = engine.pop()
    result = min(n1, n2)
    engine.push(result)       


@forthprim("MAX")
def forthMax(engine, caller):
    """( n1, n2 -> n)
    larger of the two values"""
    n2 = engine.pop()
    n1 = engine.pop()
    result = max(n1, n2)
    engine.push(result)      

@forthprim("ABS")
def forthAbs(engine, caller):
    """( n1  -> un)
    absolute value"""
    n1 = engine.pop()
    result = abs(n1)
    engine.push(result)         


@forthprim("MINUS")
def forthMinus(engine, caller):
    """( n1  -> -n1)
    absolute value"""
    n1 = engine.pop()
    result = - n1
    engine.push(result)             

@forthprim("1+")
def forthOnePlus(engine, caller):
    """( n1  -> n1+1 )
    absolute value"""
    n1 = engine.pop()
    result = n1 + 1
    engine.push(result)             

@forthprim("2+")
def forthTwoPlus(engine, caller):
    """( n1  -> n1 + 2)
    absolute value"""
    n1 = engine.pop()
    result = n1 + 2
    engine.push(result)                 

# LOGICAL    
@forthprim("AND")
def forthAND(engine, caller):
    """( n1 n2  -> n1 & 2)
    bit logical and"""
    n1 = engine.pop()
    n2 = engine.pop()

    result = n1 & n2
    engine.push(result)                 

@forthprim("OR")
def forthor(engine, caller):
    """( n1 n2  -> n1 | 2)
    bit logical and"""
    n1 = engine.pop()
    n2 = engine.pop()

    result = n1 | n2
    engine.push(result)                 

