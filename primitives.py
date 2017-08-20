"""
==========
primitives
==========
Implement the primitive words for PyForth

"""
import logging
from calendar import formatstring
from Exceptions import WordNotFoundError, ExecutionError

class CompiledCode(object):
    """
    CompiledCode is an object containing the compiled code of a word.
    """

    def __init__(self, name="AnonCompiled", isImmediate = False, executeOnly=False, inColonOnly=False):
        """
        :type name: str, name of the word definition
        :type isImmediate: bool, if true then the word will be executed even if in compulation mode
        :type executeOnly: bool, if true then the word cannot be used within a word definition
        :type inColonOnly: bool, if true then the word cannot be used outside a word definition
        """
        self.isImmediate = isImmediate
        self.executeOnly = executeOnly
        self.inColonOnly = inColonOnly
        self.code = []
        self.name = name
        self.docstring = []
        self.meta={}

    def __str__(self):
        return "CompiledCode {}".format(self.name)

    def execute(self, engine, caller):
        '''
        execute the code
        '''
        # logging.debug("about to execute CompiledCode '{}'".format(self.name))
        self.xp = 0
        while self.xp < len(self.code):
            nextWord = self.code[self.xp]
            logging.debug("execute::nextWord @{}: {}".format(self.xp, nextWord))
            self.xp = self.xp + 1
            try:
                nextWord.execute(engine, self)
            except Exception as ex:
                logging.error("Execute of word {}, xp= {}".format(self.name, self.xp-1))
                raise

    @property
    def currentWord(self):
        return self.code[self.xp]

    def jump(self, addr):
        """helper - move the xp pointer to this address"""
        self.xp = addr

    def jumpRelative(self, distance):
        """helper - jump relative """
        self.xp += distance

    def branch(self):
        """ take the next primitive, which should be  a constant and do a relative jump based on its value."""
        offset = self.code[self.xp]
        logging.debug("branching by {}".format(offset.constantValue))
        self.jumpRelative(offset.constantValue)

    def appendDocQuote(self, quote):
        """append a doc quote to the words meta information"""
        logging.debug("adding doc string '{}'".format(quote))
        self.docstring.append(quote)

class CompiledPrimitive():
    """
    a compiled primitive will when executed invole the function called func.
    """
    def __init__(self, func, name="AnonPrimitive", isImmediate=False, executeOnly=False, inColonOnly=False):
        self.func = func
        self.name = name
        self.isImmediate = isImmediate
        self.executeOnly = executeOnly
        self.inColonOnly = inColonOnly
        self.meta={}

    def __str__(self):
        return "CompiledPrimitive {}".format(self.name)

    def execute(self, engine, caller):
        # logging.debug("about to execute primitive'{}'".format(self.name))
        self.func(engine, caller)


class CompiledConstant():
    """
    Compiled Constants is a primitive that will push a constant on the stack
    """
    def __init__(self, constVal):
        self.constantValue = constVal

    def __str__(self):
        return "CompiledConstant '{}'".format(self.constantValue)

    def execute(self, engine, caller):
        # logging.debug("about to execute constant'{}'".format(self.constantValue))
        engine.stack.append(self.constantValue)


vocabulary = {}


class forthprim:
    """
    Decorator class to decorate pyForth Primitives.
    use to decorate a primitive implementation like this:

       @forthprim('."', isImmediate=True)

    this will take the next function and instantiate a CompiledPrimitive and stick it intoa vocabulary."
    """
    global vocabulary

    def __init__(self, name, isImmediate=False, executeOnly=False, inColonOnly=False, voc=vocabulary):
        self.name = name
        self.isImmediate = isImmediate
        self.executeOnly = executeOnly
        self.inColonOnly = inColonOnly
        self.voc = voc
        # print ("forthprim init for f={}".format(name))

    def __call__(self, f):
        # print("Decorating '{}->{}'".format(f.__name__, self.name))
        self.voc[self.name] = CompiledPrimitive(f, name=self.name, isImmediate=self.isImmediate,
                                                executeOnly=self.executeOnly, inColonOnly=self.inColonOnly)


@forthprim(".")
def forth_print(engine, caller):
    sp = engine.stack
    top = sp[-1]
    sp.pop()
    print(top)


@forthprim('."', isImmediate=True)
def dot_quote(engine, caller):
    """fetch the next words up and until then next quote char.
    if compiling then compile this as a string constant and a print , otherwise print it out"""
    s = engine.getInputTill('"')[1:]
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
    """ n1 n2 -> n3"""
    engine.push(engine.pop() or engine.pop())


@forthprim("XOR")
def forthXor(engine, caller):
    """ n1 n2 -> n3"""
    engine.push(engine.pop() ^ engine.pop())


@forthprim("+!")
def forthSubtract(engine, caller):
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
    sp = engine.stack
    n2 = sp.pop()
    n1 = sp.pop()
    sp.append(n1 > n2)


@forthprim("<")
def lt(engine, caller):
    sp = engine.stack
    n2 = sp.pop()
    n1 = sp.pop()
    sp.append(n1 < n2)


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
def gt(engine, caller):
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
def forthover(engine, caller):
    """n1 n2 -> n2 n1"""
    n2 = engine.pop()
    n1 = engine.pop()
    engine.push(n2)
    engine.push(n1)



"""Return Stack"""
@forthprim(">R")
def toR(engine, caller):
    """move TOS to Return stack
    ( n -> )"""
    engine.rp.append(engine.pop())


@forthprim("R>")
def toR(engine, caller):
    """move top of Return stack to stack
    (  -> n)"""
    engine.push(engine.rp.pop())


@forthprim("R")
def toR(engine, caller):
    """copy top of Return stack to stack
    (  -> n)"""
    engine.push(engine.rp[-1])



"""looping"""


@forthprim("I")
def forthI(engine, caller):
    engine.push(engine.rp[-1])


@forthprim("DO", isImmediate=True)
def forthDo(engine, caller):
    """set a marker for the LOOP statement
    ( I Limit -- )
    """
    engine.compileWord(">R")  #Limit
    engine.compileWord(">R")   # I

    engine.stack.append(len(engine.compilingMethod.code))  # address of compiled (DO)
    engine.stack.append("DOFLAG")
    engine.compileWord("(DO)")
    engine.compileWord("0BRANCH")
    engine.compileConstant(0)       # at addr + 2



@forthprim("(DO)")
def forthRunTimeDo(engine, caller):
    """push start index and loop limit onto return stack"""
    index =engine.rp[-1]
    limit = engine.rp[-2]
    if index >= limit:
        engine.push(0)
    else:
        engine.push(1)



@forthprim("LOOP", isImmediate=True)
def forthLoop(engine, caller):
    """compile a decrement i and jump to marker"""
    if "DOFLAG" != engine.pop():
        raise ValueError("LOOP statement did not see a paired DO")
    engine.compileWord("(LOOP)")
    doAddr = engine.pop()
    engine.compileConstant(doAddr - len(engine.compilingMethod.code)) # constant for the branch of the (LOOP)

    # fixup the const for the 0Branch after the (DO) word
    branchConst = engine.compilingMethod.code[doAddr+2]
    branchConst.constantValue = len(engine.compilingMethod.code) - doAddr - 2



@forthprim("+LOOP", isImmediate=True)
def forthPlusLoop(engine, caller):
    """compile a decrement i and jump to marker

    """
    if "DOFLAG" != engine.pop():
        raise ValueError("LOOP statement did not see a paired DO")
    engine.compileWord("(+LOOP)")
    doAddr = engine.pop()
    engine.compileConstant(doAddr - len(engine.compilingMethod.code)) # constant for the branch of the (LOOP)

    # fixup the const for the 0Branch after the (DO) word
    branchConst = engine.compilingMethod.code[doAddr+2]
    branchConst.constantValue = len(engine.compilingMethod.code) - doAddr - 2


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



@forthprim("BEGIN", isImmediate=True)
def ForthBegin(engine, caller):
    engine.stack.append(len(engine.compilingMethod.code))
    engine.stack.append("BEGINFLAG")


@forthprim("UNTIL", isImmediate=True)
def ForthUntil(engine, caller):
    if "BEGINFLAG" != engine.pop():
        raise ValueError("UNTIL statement did not see a paired BEGIN")
    addr = engine.pop()
    engine.compileWord("0BRANCH")
    engine.compileConstant(addr - len(engine.compilingMethod.code))


@forthprim("WHILE", isImmediate=True)
def ForthWhile(engine, caller):
    flag = engine.pop()
    if flag != "BEGINFLAG":
        raise ValueError("WHILE statement did not see a paired BEGIN")
    engine.compileWord("0BRANCH")
    engine.compileConstant(0)
    addr = len(engine.compilingMethod.code) - 1
    engine.push(addr)
    engine.push("WHILEFLAG")


@forthprim("REPEAT", isImmediate=True)
def ForthRepeat(engine, caller):
    flag = engine.pop()
    if flag != "WHILEFLAG":
        raise ValueError("REPEAT statement did not see a paired WHILE")
    whileAddr = engine.pop()
    beginAddr = engine.pop()
    engine.compileWord("BRANCH")
    addr = len(engine.compilingMethod.code)
    engine.compileConstant(beginAddr - addr)
    # update the branch distance at the WHILE
    branchDistance = engine.compilingMethod.code[whileAddr]  # get the JUMP constant at the WHILE statement
    branchDistance.constantValue = len(engine.compilingMethod.code) - whileAddr  # update it to point past this code


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
    branchDistance = engine.compilingMethod.code[branchValueLocation]  # get the constant with the jump distance
    branchDistance.constantValue = len(engine.compilingMethod.code) - branchValueLocation
    logging.debug(
        "Compiling ELSE: fixing up branch value at {} to {}".format(branchValueLocation, branchDistance.constantValue))
    engine.push(addr)
    engine.push("DOIF")  # flag


@forthprim("ENDIF", isImmediate=True)
def compileEndif(engine, caller):
    flag = engine.pop()
    if flag != "DOIF":
        raise ValueError("ENDIF statement did not see a paired IF")

    branchValueLocation = engine.pop()
    branchDistance = engine.compilingMethod.code[branchValueLocation]  # get the constant with the jump distance
    branchDistance.constantValue = len(engine.compilingMethod.code) - branchValueLocation  # relative jump
    logging.debug(
        "Compiling Endif: fixing up branch value at {} to {}".format(branchValueLocation, branchDistance.constantValue))


@forthprim("VARIABLE")
def compileVariable(engine, caller):
    """compile a word, that when called will leave an address of a variable, which then can be used with @ and !"""
    varName = engine.nextWord()
    engine.startCompiling(varName)
    addr = engine.allocMem(engine.pop())
    engine.compileConstant(addr)
    engine.completeCompile()


@forthprim("CONSTANT")
def compileConstant(engine, caller):
    """compile a constant, that when called will push the constant value on the stack"""
    varName = engine.nextWord()
    engine.startCompiling(varName)
    engine.compileConstant(engine.pop())
    engine.completeCompile()


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
    with open(engine.pop(), "r") as fd:
        engine.readFrom(fd)

@forthprim("FORMAT")
def formatString(engine, caller):
    """format a string , using the python format command.
    ( arg1, arg2 .. argn, formatString -> formattedResult )
    """
    #count all open curlies in the format string
    formatString = engine.pop()
    nParams = formatString.count("{")
    args = [engine.stack.pop() for p in range(nParams)]
    logging.debug(args)
    result = formatString.format(*tuple(reversed(args)))
    engine.push(result)

# execute words

@forthprim("'")
def tick(engine, caller):
    """ take the next word and put the associated method on the stack.
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
    method.execute(engine, caller)



"""Array stuff"""

@forthprim("[")
def forthArrayStart(engine, caller):
    """execute the method that is on TOS"""
    engine.push("LABEL[")


@forthprim("]")
def forthArrayEnd(engine, caller):
    """execute the method that is on TOS"""
    found = False
    result=[]
    while len(engine.stack)>0:
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
def forthArrayUnpack(engine, caller):
    """unpack an array
    (n1 , n2, ..nx depth - arr)
    """
    depth = engine.pop()
    result = [engine.pop() for n in range (depth)]
    engine.push (reversed(result))

@forthprim ("LEN")
def forthLen(engine, caller):

    """determine the len attribute of the TOS
    ( n -- n len)
    """
    engine.push(len(engine.stack[-1]))