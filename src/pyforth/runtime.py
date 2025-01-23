"""
===============
PyForth Runtime
===============
This is the interpreter implementation of PyForth

@author: stephanmeyn
"""

from __future__ import annotations

import logging
from typing import Any, Optional 
from io import StringIO
# import pyforth.primitives as primitives
from pyforth.exceptions import CompilationError, WordNotFoundError, ExecutionError
# from pyforth.primitives import MethodABC, CompiledPrimitive, CompiledCode, CompiledConstant
# pylint: disable="invalid-name"
# pylint: disable="logging-format-interpolation"
# pylint: disable="missing-function-docstring"
# pylint: disable="consider-using-f-string"
# pylint: disable="protected-access"
from collections import OrderedDict


vocabulary = {}


class MethodABC():
    """base class for words"""
    def __init__(
        self,
        name="AnonCompiled",
        isImmediate=False,
        executeOnly=False,
        inColonOnly=False,
    ):
        """
        :type name: str, name of the word definition
        :type isImmediate: bool, if true then the word will be executed even if in compulation mode
        :type executeOnly: bool, if true then the word cannot be used within a word definition
        :type inColonOnly: bool, if true then the word cannot be used outside a word definition
        """
        self.isImmediate = isImmediate
        self.executeOnly = executeOnly
        self.inColonOnly = inColonOnly
        self.name = name
        self.docstring = []
        self.meta = {}

    def execute(self, engine, caller: CompiledCode):
        raise NotImplementedError()

    def appendDocQuote(self, quote):
        """append a doc quote to the words meta information"""
        logging.debug("adding doc string '{}'".format(quote))
        
        self.docstring.append(quote)

class CompiledCode(MethodABC):
    """
    CompiledCode is an object containing the compiled code of a word.
    """

    def __init__(
        self,
        name="AnonCompiled",
        isImmediate=False,
        executeOnly=False,
        inColonOnly=False,
    ):
        """
        :type name: str, name of the word definition
        :type isImmediate: bool, if true then the word will be executed even if in compulation mode
        :type executeOnly: bool, if true then the word cannot be used within a word definition
        :type inColonOnly: bool, if true then the word cannot be used outside a word definition
        """
        super().__init__(name=name, isImmediate=isImmediate,
                        executeOnly=executeOnly, inColonOnly=inColonOnly,
                        )        
        self.code = []
        self.xp = 0

    def __str__(self):
        result = f"CompiledPrimitive {self.name}"
        if self.docstring:
            doc = "\n".join(self.docstring)
            result = f"{result}: {doc}"

        return result

    def showCode(self):
        """return a string of code names"""
        
        names =[str(method.name) for  method in self.code]
        return ",".join (names)


class CompiledPrimitive(MethodABC):
    """
    a compiled primitive will when executed invole the function called func.
    """

    def __init__(
        self,
        func,
        name="AnonPrimitive",
        isImmediate=False,
        executeOnly=False,
        inColonOnly=False,
        docString:str=''
    ):
        super().__init__(name=name, isImmediate=isImmediate,
                        executeOnly=executeOnly, inColonOnly=inColonOnly,
                        )               
        self.func = func
        if func.__doc__:
            self.docstring= [func.__doc__]

    def __str__(self):
        result = f"CompiledPrimitive {self.name}"
        if self.docstring:
            doc = "\n".join(self.docstring)
            result = f"{result}:\n {doc}"

        return result

    def execute(self, engine, caller: CallFrame):
        # logging.debug("about to execute primitive'{}'".format(self.name))
        self.func(engine, caller)


class CompiledConstant(MethodABC):
    """
    Compiled Constants is a primitive that will push a constant on the stack
    """

    def __init__(self, constVal):
        self.constantValue = constVal

    def __str__(self):
        return "Constant '{}'".format(self.constantValue)

    @ property 
    def name(self):
        return f"{self}"
    def execute(self, engine, caller: CallFrame):
        # logging.debug("about to execute constant'{}'".format(self.constantValue))
        engine.stack.append(self.constantValue)


class RAM():
    """Randiom access memory with safe access"""
    def __init__(self):
        self.mem=[]
    
    def __getitem__(self, idx: int)-> Any|None:
        """get an item. If outside of allocated mem, return None"""
        if idx < len(self.mem):
            return self.mem[idx]
        return None

    def __setitem__(self, idx: int, val: Any)-> None:
        """set an item. If outside of allocated mem, allocate mem"""
        while idx >= len(self.mem):
            self.mem.append(None)
        self.mem[idx] = val
        

    def append(self, item)->int:
        """add an item to RAM and return its address"""
        self.mem.append(item)
        return len(self.mem)-1




class CallFrame():
    """invoked for every execution of a Compiled Code"""
    def __init__(self, method:MethodABC):
        self.method = method
        self.xp:int=0
        self.caller:MethodABC = None
        self.engine: Interpreter
        self.isCompiled:bool = False

    def __str__(self):
        return f"Call {self.method.name} at {self.xp}"
    
    def execute(self, engine:Interpreter, caller:MethodABC):
        """run the method"""

        self.caller = caller
        self.engine = engine
        if isinstance(self.method, (CompiledPrimitive, CompiledConstant)):
            self.method.execute(engine, self)
            return
        self.xp = 0
        self.isCompiled = True
        while self.xp < len(self.method.code):
            nextWord = self.method.code[self.xp]
            logging.debug("execute::nextWord @{}: {}".format(self.xp, nextWord))
            self.xp = self.xp + 1
            try:
                # nextWord.execute(engine, self)
                engine.execute(nextWord, self)
            except Exception:
                logging.error(
                    "Execute of word {}, xp= {}".format(self.method.name, self.xp - 1)
                )
                raise

    @property 
    def parent(self)->CallFrame|None:
        """get the parent frame from the engine stack"""
        if len(self.engine.callStack)> 1:
            return self.engine.callStack[-2]
        return None

    #the following methods assume they are called from a primitive
    # and hence parent is valid

    @property
    def currentWord(self):
        return self.parent.method.code[self.xp]

    def jump(self, addr):
        """helper - move the xp pointer to this address"""        
        self.parent.xp = addr

    def jumpRelative(self, distance):
        """helper - jump relative"""
        self.parent.xp += distance

    def branch(self):
        """take the next primitive, which should be  a constant
        and do a relative jump based on its value."""
        offset = self.parent.method.code[self.parent.xp]
        logging.debug("branching by {}".format(offset.constantValue))
        self.jumpRelative(offset.constantValue)





class forthprim():
    """
    Decorator class to decorate pyForth Primitives.
    use to decorate a primitive implementation like this:

       @forthprim('."', isImmediate=True)

    this will take the next function and instantiate a CompiledPrimitive and stick it intoa vocabulary."
    """

    global vocabulary

    def __init__(
        self,
        name,
        isImmediate=False,
        executeOnly=False,
        inColonOnly=False,
        voc=vocabulary,
    ):
        self.name = name
        self.isImmediate = isImmediate
        self.executeOnly = executeOnly
        self.inColonOnly = inColonOnly
        self.voc = voc
        # print ("forthprim init for f={}".format(name))

    def __call__(self, f):
        # print("Decorating '{}->{}'".format(f.__name__, self.name))
        self.voc[self.name] = CompiledPrimitive(
            f,
            name=self.name,
            isImmediate=self.isImmediate,
            executeOnly=self.executeOnly,
            inColonOnly=self.inColonOnly,
        )



class Interpreter(object):
    """
    Forth interpreter
    """

    def __init__(self, vocabulary:dict=vocabulary):
        """
        Constructor
        """
        self.vocabularies = OrderedDict()
        self.vocabularies["FORTH"] = vocabulary        
        self.context = "FORTH"  # start here looking for words to interpret
        self.definitions = "FORTH"   # start here for words to compile
        self._core_vocabulary = vocabulary
        self.reset()
        self.stack = []
        self.mem = RAM()
        self.rp:list[Any] = []  # return pointer stack
        self.callStack:list[CallFrame]=[]
        self.isCompiling:bool = False
        self.CLI = ""
        self.CliIdx = 0
        self.word2Compile = None
        self.compilingMethod:CompiledCode = None
        self.lastError = None
        self.CliInDocQuote = False
        self.leavestack:list[list[int]]=[] # all outstandign leave addresses to be fixed up
        if not self._core_vocabulary:
            from pyforth import words # cause all ords to be compiled  # noqa: F401
    

    def run(self):
        """run the interpreter"""
        prompt = "> "
        while True:
            self.CLI = str(input(prompt))
            self.CliIdx = 0
            self.__process_cli__()

    def interpret(self, cli:str):
        """Interpret a string """
        savedCli = self.CLI
        savedIdx = self.CliIdx
        self.CLI = cli
        self.CliIdx = 0
        self.__process_cli__()
        self.CLI = savedCli
        self.CliIdx = savedIdx

    def execute(self, method:MethodABC, caller:Optional[CallFrame]):
        """execute a method"""
        assert caller is None or isinstance(caller, CallFrame)        
        assert isinstance(method, MethodABC), f"{method} is not a method"
        frame = CallFrame(method)
        try:
            self.callStack.append(frame)
            frame.execute(self, caller)
        finally:
            self.callStack.pop()

    @property 
    def context_vocabulary(self):
        return self.vocabularies[self.context]

    @property 
    def definitions_vocabulary(self):
        return self.vocabularies[self.definitions]


    def get_input_till(self, delimiter: str) -> str:
        """return input up to except for delimiter.
        adjust CliIdx to point past first char after delimiter
        :param delimiter: char
        :return: str
        """

        if self.CliIdx >= len(self.CLI):
            return ""
        start_idx = self.CliIdx

        while self.CliIdx < len(self.CLI) and not self.CLI[self.CliIdx :].startswith(
            delimiter
        ):
            self.CliIdx += 1
        # print ("idx:{}, cliIdx:{}".format(idx, self.CliIdx))
        # print(self.CLI)
        w = self.CLI[start_idx : self.CliIdx]
        if self.CLI[self.CliIdx :].startswith(delimiter):
            self.CliIdx += len(delimiter)

        return w

    def find_word(self, word)->MethodABC|None:
        """find a word in a vocabulary"""
        voc = self.vocabularies[self.context]
        found = voc.get(word)
        if found:
            return found
        # now go through all vocabularies
        for custom_voc in reversed(self.vocabularies.values()):
            found = custom_voc.get(word)
            if found:
                return found
        return None


    def __process_cli__(self):
        """process a command line"""
        logging.debug("processCli start")
        word = self.nextWord()
        while word is not None:
            if isinstance(word, str):
                logging.debug("next word: '{}'".format(word))
                if word.startswith('"'):
                    if self.isCompiling:
                        self.compileConstant(word[1:-1])
                    else:
                        self.push(word[1:-1])
                else:                    
                    method = self.find_word(word)
                    if method is None:
                        self.reset()
                        self.lastError = WordNotFoundError(
                            word, "Word '{}' not found in vocabulary".format(word)
                        )
                        print("Word '{}' not found in vocabulary".format(word))
                        break

                    if self.isCompiling and not method.isImmediate:
                        self.compileMethod(method)
                    else:
                        # method = self._core_vocabulary[word]
                        if method.inColonOnly and not self.isCompiling:
                            raise ExecutionError(
                                word, "Word not allowed to be used in direct execution"
                            )
                        try:
                            # method.execute(self, None)
                            self.execute(method, None)
                        except Exception as ex:
                            logging.exception(
                                "exception during execute of word '{}'".format(word)
                            )
                            self.__postMortem__()
                            print(ex)
                            self.reset()
                            self.lastError = ex
                            break                   
            elif isinstance(word, int) or isinstance(word, float):
                logging.debug("next word is a number: {}".format(word))
                if self.isCompiling:
                    self.compileConstant(word)
                else:
                    self.stack.append(word)
            else:
                logging.warning(
                    "'{}' not found in vocabulary, nor a number".format(word)
                )
                self.reset()
            word = self.nextWord()

    @property
    def vocabulary(self)->dict:
        return self._core_vocabulary

    def nextWord(self)->str:
        """return the next word from the commmand line buffer"""

        while self.CliInDocQuote:
            logging.debug("extracting docQuote ")
            aString = self.get_input_till('"""')
            if self.isCompiling:
                self.compilingMethod.appendDocQuote(aString)
            if self.CliIdx >= len(self.CLI):
                self.CliInDocQuote = True
                return None
            else:
                self.CliInDocQuote = False
                logging.debug("end docQuote ")

        # return self.CLI.popleft()
        # skip blanks
        idx = self.CliIdx
        while idx < len(self.CLI) and self.CLI[idx].isspace():
            idx += 1
        if idx >= len(self.CLI):
            return None
        # check if it's a doc string
        if self.CLI[idx:].startswith('"""'):
            logging.debug("start docQuote ")
            self.CliIdx = idx + 3
            self.CliInDocQuote = True
            return self.nextWord()

        # check if we have a quoted string
        if self.CLI[idx] == '"':
            quote = self.CLI[idx]
            self.CliIdx = idx + 1
            aString = '"' + self.get_input_till(quote) + '"'
            return aString
        else:  # start scanning the word
            self.CliIdx = idx + 1
            while self.CliIdx < len(self.CLI) and not self.CLI[self.CliIdx].isspace():
                self.CliIdx += 1
            # print ("idx:{}, cliIdx:{}".format(idx, self.CliIdx))
            # print(self.CLI)
            w = self.CLI[idx : self.CliIdx]

            num = self.__parseNumber__(w)
            if num is not None:
                return num
            else:
                return w

    def __parseNumber__(self, w):
        """try to parse a number
        :param w: str
        :return: number
        """
        # logging.debug("trying to parse a number from '{}'".format(w))
        try:
            if "." in w:
                n = float(w)
            else:
                n = int(w)
            logging.debug("number is {}".format(n))
            return n

        except ValueError:
            # logging.debug("Not a number: '{}'".format(w))
            return None

    def reset(self):
        """
        reset the interpreter
        """
        logging.info("reset")
        print("Reset")
        self.CLI = ""
        self.CliIdx = 0
        self.stack = []
        self.rp = []
        self.callStack = []
        self.isCompiling = False
        self.lastError = None
        self.CliInDocQuote = False

    def compileConstant(self, constval: object):
        """
        compile a constant primitive.
        :type constval: object
        """
        logging.debug("compile constant '{}'".format(constval))
        self.compilingMethod.code.append(CompiledConstant(constval))

    def compileMethod(self, method):
        logging.debug("compiling method references {}".format(method))
        self.compilingMethod.code.append(method)

    def compileWord(self, methodName):
        method = self._core_vocabulary.get(methodName, None)
        if method:
            self.compileMethod(method)
        else:
            raise CompilationError(
                methodName, "Method named not found in core vocabulary"
            )

    def readFrom(self, aStream):
        """read forth from an iterable input"""
        for line in aStream:
            self.interpret(line)

    def startCompiling(self, methodName):
        logging.debug("Start Compiling")
        self.isCompiling = True
        self.word2Compile = []
        self.compilingMethod = CompiledCode(name=methodName)

    def completeCompile(self)->None:
        """save the compiled body"""
        logging.debug(
            "completed compilation of word '{}'".format(self.compilingMethod.name)
        )
        voc = self.vocabularies[self.definitions]
        voc[self.compilingMethod.name] = self.compilingMethod
        self.isCompiling = False

    # stack helpers
    def push(self, value: Any)->None:
        """
        push an item onto stack
        :param value: Object
        """
        self.stack.append(value)

    def pop(self, nrItems=1)-> Any|list[Any]:
        if nrItems == 1:
            return self.stack.pop()
        else:
            return reversed([self.stack.pop() for _ in range(nrItems)])


    def fillMem(self, loc: int, nrItems: int, item: Any):
        for addr in range(loc, loc+nrItems):
            self.mem[addr] = item

 
    def moveMem(self, origin: int, destination: int, nrItems: int):
        """move items , replace vacated locations with None"""
        # check memory is long enough
        # while len(self.mem) <= destination+nrItems:
        #     self.mem.append(None)
        # make a copy
        cp = [self.mem[idx] for idx in range(origin, origin+nrItems)]
        self.fillMem(origin, nrItems, None)
        for idx, val in enumerate(cp):
            self.mem[destination+idx]=val


    def __postMortem__(self):
        """log a dump"""
        logging.error("Call callStack Dump:")
        for i in range(len(self.callStack)):
            logging.error(f"{i}: {self.callStack[-i - 1]}")
            if i > 10:
                break
 
        logging.error("Stack Dump:")
        for i in range(len(self.stack)):
            logging.error("{}: {}".format(i, self.stack[-i - 1]))
            if i > 10:
                break
        logging.error("RP Dump:")
        for i in range(len(self.rp)):
            logging.error("{}: {}".format(i, self.rp[-i - 1]))
            if i > 10:
                break

    #compilation support
    def start_loop(self):
        """resrve space for loop leave markers"""
        logging.debug("start_loop")
        self.leavestack.append([])
    
    def end_loop(self):
        """end of loop, resolve all jumps for any leave stmts"""
        logging.debug("end_loop")
        code = self.compilingMethod.code
        target_address = len(code)
        for addr in self.leavestack[-1]:
            dist = target_address-addr + 2
            cc:CompiledConstant = code[addr]
            cc.constantValue=dist
        self.leavestack.pop()

    def mark_leave(self, address:int):
        """record the location of a jump address for a leave"""
        logging.debug("mark_leave")
        self.leavestack[-1].append(address)

        