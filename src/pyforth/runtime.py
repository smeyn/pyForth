"""
===============
PyForth Runtime
===============
This is the interpreter implementation of PyForth

@author: stephanmeyn
"""

import logging
from typing import Any
import pyforth.primitives as primitives
from pyforth.exceptions import CompilationError, WordNotFoundError, ExecutionError

# pylint: disable="invalid-name"
# pylint: disable="logging-format-interpolation"
# pylint: disable="missing-function-docstring"
# pylint: disable="consider-using-f-string"
# pylint: disable="protected-access"


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
        





class Interpreter(object):
    """
    Forth interpreter
    """

    def __init__(self):
        """
        Constructor
        """

        self._core_vocabulary = primitives.vocabulary
        self.reset()
        self.stack = []
        self.mem = RAM()
        self.rp = []  # return pointer stack
        self.isCompiling = False
        self.CLI = ""
        self.CliIdx = 0
        self.word2Compile = None
        self.compilingMethod = None
        self.lastError = None
        self.CliInDocQuote = False

    def run(self):
        """run the interpreter"""
        prompt = "> "
        while True:
            # words =  str(input(PROMPT)).split()
            # self.CLI = deque([word for word in words if word.strip()])
            self.CLI = str(input(prompt))
            self.CliIdx = 0
            self.__process_cli__()

    def interpret(self, cli):
        savedCli = self.CLI
        savedIdx = self.CliIdx
        self.CLI = cli
        self.CliIdx = 0
        self.__process_cli__()
        self.CLI = savedCli
        self.CliIdx = savedIdx

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
                elif word in self._core_vocabulary:
                    method = self._core_vocabulary[word]
                    if self.isCompiling and not method.isImmediate:
                        self.compileMethod(method)
                    else:
                        method = self._core_vocabulary[word]
                        if method.inColonOnly and not self.isCompiling:
                            raise ExecutionError(
                                word, "Word not allowed to be used in direct execution"
                            )
                        try:
                            method.execute(self, None)
                        except Exception as ex:
                            logging.exception(
                                "exception during execute of word '{}'".format(word)
                            )
                            self.__postMortem__()
                            print(ex)
                            self.reset()
                            self.lastError = ex
                            break
                else:
                    self.reset()
                    self.lastError = WordNotFoundError(
                        word, "Word '{}' not found in vocabulary".format(word)
                    )
                    print("Word '{}' not found in vocabulary".format(word))
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
    def vocabulary(self):
        return self._core_vocabulary

    def nextWord(self):
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
        self.isCompiling = False
        self.lastError = None
        self.CliInDocQuote = False

    def compileConstant(self, constval: object):
        """
        compile a constant primitive.
        :type constval: object
        """
        logging.debug("compile constant '{}'".format(constval))
        self.compilingMethod.code.append(primitives.CompiledConstant(constval))

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
        self.compilingMethod = primitives.CompiledCode(name=methodName)

    def completeCompile(self):
        """save the compiled body"""
        logging.debug(
            "completed compilation of word '{}'".format(self.compilingMethod.name)
        )
        self._core_vocabulary[self.compilingMethod.name] = self.compilingMethod
        self.isCompiling = False

    # stack helpers
    def push(self, value: Any):
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
        logging.debug("Stack Dump:")
        for i in range(len(self.stack)):
            logging.debug("{}: {}".format(i, self.stack[-i - 1]))
            if i > 10:
                break
        logging.debug("RP Dump:")
        for i in range(len(self.rp)):
            logging.debug("{}: {}".format(i, self.rp[-i - 1]))
            if i > 10:
                break
