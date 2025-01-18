"""Implement the primitive words for PyForth"""

from __future__ import annotations

import logging
# from typing import TYPE_CHECKING
# from calendar import formatstring
from pyforth.exceptions import WordNotFoundError, ExecutionError

from pyforth.runtime import CallFrame, CompiledPrimitive, vocabulary

# pylint: disable="invalid-name"
# pylint: disable="logging-format-interpolation"
# pylint: disable="missing-function-docstring"
# pylint: disable="consider-using-f-string"
# pylint: disable="protected-access"
# pylint: disable="unused-argument"


# class MethodABC():
#     """base class for words"""
#     def __init__(
#         self,
#         name="AnonCompiled",
#         isImmediate=False,
#         executeOnly=False,
#         inColonOnly=False,
#     ):
#         """
#         :type name: str, name of the word definition
#         :type isImmediate: bool, if true then the word will be executed even if in compulation mode
#         :type executeOnly: bool, if true then the word cannot be used within a word definition
#         :type inColonOnly: bool, if true then the word cannot be used outside a word definition
#         """
#         self.isImmediate = isImmediate
#         self.executeOnly = executeOnly
#         self.inColonOnly = inColonOnly
#         self.name = name
#         self.docstring = []
#         self.meta = {}

#     def execute(self, engine, caller: CallFrame):
#         raise NotImplementedError()

#     def appendDocQuote(self, quote):
#         """append a doc quote to the words meta information"""
#         logging.debug("adding doc string '{}'".format(quote))
        
#         self.docstring.append(quote)

# class CallFrame(MethodABC):
#     """
#     CallFrame is an object containing the compiled code of a word.
#     """

#     def __init__(
#         self,
#         name="AnonCompiled",
#         isImmediate=False,
#         executeOnly=False,
#         inColonOnly=False,
#     ):
#         """
#         :type name: str, name of the word definition
#         :type isImmediate: bool, if true then the word will be executed even if in compulation mode
#         :type executeOnly: bool, if true then the word cannot be used within a word definition
#         :type inColonOnly: bool, if true then the word cannot be used outside a word definition
#         """
#         super().__init__(name=name, isImmediate=isImmediate,
#                         executeOnly=executeOnly, inColonOnly=inColonOnly,
#                         )        
#         self.code = []
#         self.xp = 0

#     def __str__(self):
#         result = f"CompiledPrimitive {self.name}"
#         if self.docstring:
#             doc = "\n".join(self.docstring)
#             result = f"{result}: {doc}"

#         return result


#     # def execute(self, engine, caller: CallFrame):
#     #     """
#     #     execute the code
#     #     """
#     #     # logging.debug("about to execute CallFrame '{}'".format(self.name))
#     #     self.xp = 0
#     #     while self.xp < len(self.code):
#     #         nextWord = self.code[self.xp]
#     #         logging.debug("execute::nextWord @{}: {}".format(self.xp, nextWord))
#     #         self.xp = self.xp + 1
#     #         try:
#     #             nextWord.execute(engine, self)
#     #         except Exception:
#     #             logging.error(
#     #                 "Execute of word {}, xp= {}".format(self.name, self.xp - 1)
#     #             )
#     #             raise

#     # @property
#     # def currentWord(self):
#     #     return self.code[self.xp]

#     # def jump(self, addr):
#     #     """helper - move the xp pointer to this address"""
#     #     self.xp = addr

#     # def jumpRelative(self, distance):
#     #     """helper - jump relative"""
#     #     self.xp += distance

#     # def branch(self):
#     #     """take the next primitive, which should be  a constant
#     #     and do a relative jump based on its value."""
#     #     offset = self.code[self.xp]
#     #     logging.debug("branching by {}".format(offset.constantValue))
#     #     self.jumpRelative(offset.constantValue)




# class CompiledPrimitive(MethodABC):
#     """
#     a compiled primitive will when executed invole the function called func.
#     """

#     def __init__(
#         self,
#         func,
#         name="AnonPrimitive",
#         isImmediate=False,
#         executeOnly=False,
#         inColonOnly=False,
#         docString:str=''
#     ):
#         super().__init__(name=name, isImmediate=isImmediate,
#                         executeOnly=executeOnly, inColonOnly=inColonOnly,
#                         )               
#         self.func = func
#         if func.__doc__:
#             self.docstring= [func.__doc__]

#     def __str__(self):
#         result = f"CompiledPrimitive {self.name}"
#         if self.docstring:
#             doc = "\n".join(self.docstring)
#             result = f"{result}:\n {doc}"

#         return result

#     def execute(self, engine, caller: CallFrame):
#         # logging.debug("about to execute primitive'{}'".format(self.name))
#         self.func(engine, caller)


# class CompiledConstant(MethodABC):
#     """
#     Compiled Constants is a primitive that will push a constant on the stack
#     """

#     def __init__(self, constVal):
#         self.constantValue = constVal

#     def __str__(self):
#         return "Constant '{}'".format(self.constantValue)

#     def execute(self, engine, caller: CallFrame):
#         # logging.debug("about to execute constant'{}'".format(self.constantValue))
#         engine.stack.append(self.constantValue)





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
