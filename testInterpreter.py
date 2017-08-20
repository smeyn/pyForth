from  Runtime import Interpreter
import logging

def _dumpCode_(method):
    s = ["  {}:{}\n".format(idx, str(item)) for idx, item in enumerate(method.code)]
    return " ".join(s)

def checkError(interp, assertOnError = True):
    if interp.lastError:
        logging.exception(interp.lastError)
        if assertOnError:
            assert(False)
    else:
        assert(assertOnError) # no error found so only if AssertOnError is false

def testInterpreterSmokeTest():
    interp = Interpreter()
    interp.interpret("12 3 * DUP .")
    assert (interp.stack[0] == 36)

def testNumber():
    interp = Interpreter()
    interp.interpret("1 0 2 -1 -2")
    print (interp.stack)
    assert (interp.stack[0] == 1)
    assert (interp.stack[1] == 0)
    assert (interp.stack[2] == 2)
    assert (interp.stack[3] == -1)
    assert (interp.stack[4] == -2)

def testCompile():
    interp = Interpreter()
    interp.interpret (": beta 3 4 * ;")
    assert ("beta" in interp._coreVocabulary)
    interp.interpret("beta")
    assert (interp.stack[0] == 12)

def testDotQuoteAtRunTime():
    interp = Interpreter()
    interp.interpret('." test this"')
    logging.info("Stack='{}'".format(interp.stack))
    assert (len(interp.stack) ==0)

def testDotQuoteAtCompileTime():
    interp = Interpreter()
    interp.interpret(': test ." test this "  5 ;')
    interp.interpret('test')
    logging.info("Stack='{}'".format(interp.stack))
    assert (interp.stack[0] == 5)
    assert (len(interp.stack) ==1)

def testLoop():
    interp = Interpreter()
    interp.interpret(': test 0 0 5 DO I . 1 + LOOP ;')
    logging.info (_dumpCode_(interp.vocabulary['test']))
    #assert(False)
    interp.interpret('test')
    logging.info("Stack='{}'".format(interp.stack))

    assert (len(interp.stack) == 1)
    assert (interp.stack[0] == 5)

def testNoIterationLoop():
    interp = Interpreter()
    interp.interpret(': test 0 6 5 DO I . 1 + LOOP ;')
    logging.info (_dumpCode_(interp.vocabulary['test']))
    #assert(False)
    interp.interpret('test')
    logging.info("Stack='{}'".format(interp.stack))
    assert (len(interp.stack) == 1)
    assert (interp.stack[0] == 0)


def testPlusLoop():
    interp = Interpreter()
    interp.interpret(': test 0 0 5 DO I . 1 + 2 +LOOP ;')
    logging.info (_dumpCode_(interp.vocabulary['test']))
    #assert(False)
    interp.interpret('test')
    logging.info("Stack='{}'".format(interp.stack))

    assert (len(interp.stack) == 1)
    assert (interp.stack[0] == 3)

def testIf():
    interp = Interpreter()
    interp.interpret(': test 1 IF 5 ENDIF ;')
    logging.info("Stack before test='{}'".format(interp.stack))
    assert (len(interp.stack) == 0)
    for s in _dumpCode_(interp._coreVocabulary["test"]):
        logging.info(" : {}".format(s))

    interp.interpret('test')
    logging.info("Stack='{}'".format(interp.stack))

    assert (len(interp.stack) == 1)
    assert(interp.stack[0] == 5)

def testElse1():
    interp = Interpreter()
    interp.interpret(': test 1 IF 5 ELSE 3 ENDIF ;')
    logging.info("Stack before test='{}'".format(interp.stack))
    assert (len(interp.stack) == 0)
    for s in _dumpCode_(interp._coreVocabulary["test"]):
        logging.info(" : {}".format(s))

    interp.interpret('test')
    logging.info("Stack='{}'".format(interp.stack))

    assert (len(interp.stack) == 1)
    assert (interp.stack[0] == 5)

def testElse2():
    interp = Interpreter()
    interp.interpret(': test 0 IF 2 ELSE 3 ENDIF ;')
    logging.info("Stack before test='{}'".format(interp.stack))
    assert (len(interp.stack) == 0)
    for s in _dumpCode_(interp._coreVocabulary["test"]):
        logging.info(" : {}".format(s))

    interp.interpret('test')
    logging.info("Stack='{}'".format(interp.stack))

    assert (len(interp.stack) == 1)
    assert (interp.stack[0] == 3)

def testBeginUntil():
    interp = Interpreter()
    interp.interpret(': test 3 BEGIN 1 -   DUP 0 =   UNTIL ;')
    for s in _dumpCode_(interp._coreVocabulary["test"]):
        logging.info(" : {}".format(s))
    #assert(False)
    interp.interpret('test')
    logging.info("Stack='{}'".format(interp.stack))

    assert (len(interp.stack) == 1)
    assert (interp.stack[0] == 0)

def testWhile():
    interp = Interpreter()
    interp.interpret(': test 7 BEGIN 1 -   DUP WHILE DUP .   REPEAT ;')
    for s in _dumpCode_(interp._coreVocabulary["test"]):
        logging.info(" : {}".format(s))
    #assert(False)
    interp.interpret('test')
    logging.info("Stack='{}'".format(interp.stack))

    assert (len(interp.stack) == 1)
    assert (interp.stack[0] == 0)

def testVariable():
    interp = Interpreter()
    interp.interpret('1234 VARIABLE BUU')
    assert (len(interp.stack) == 0)
    interp.interpret('BUU @')
    logging.info("Stack='{}'".format(interp.stack))
    assert (len(interp.stack) == 1)
    assert (interp.stack[0] == 1234)
    interp.interpret('BUU @ 1 +')
    assert (len(interp.stack) == 2)
    assert (interp.stack[1] == 1235)


def testConstant():
    interp = Interpreter()
    interp.interpret('1234 CONSTANT BUU')
    assert (len(interp.stack) == 0)
    interp.interpret('BUU')
    logging.info("Stack='{}'".format(interp.stack))
    assert (len(interp.stack) == 1)
    assert (interp.stack[0] == 1234)

def testAString():
    interp = Interpreter()
    interp.interpret('1234 "CONSTANT BUU"')
    logging.info("Stack='{}'".format(interp.stack))
    assert (len(interp.stack) == 2)
    assert (interp.stack[0] == 1234)
    assert (interp.stack[1] == "CONSTANT BUU")

def testSplit1():
    interp = Interpreter()
    interp.interpret('"CONSTANT BUU xyz" " "')
    logging.info("Stack='{}'".format(interp.stack))
    assert (len(interp.stack) == 2)
    interp.interpret("SPLIT")
    logging.info("Stack='{}'".format(interp.stack))
    assert (interp.stack[0] == ["CONSTANT", "BUU", "xyz"])

def testSplit2():
    interp = Interpreter()
    interp.interpret('"CONSTANT BUU.xyz" "."')
    logging.info("Stack='{}'".format(interp.stack))
    assert (len(interp.stack) == 2)
    interp.interpret("SPLIT")
    logging.info("Stack='{}'".format(interp.stack))

    assert (interp.stack[0] == ["CONSTANT BUU", "xyz"])

def testLoadFromFile():
    interp = Interpreter()
    interp.interpret('"sample.fth" LOAD')
    logging.info("loaded.")
    interp.interpret("HELLO HELLO3")
    logging.info("done.")

    checkError(interp, assertOnError=True)
    logging.info(interp._coreVocabulary["HELLO"].docstring)
    assert(interp._coreVocabulary["HELLO"].docstring[0] == ' a simple hello ')
    logging.info(interp._coreVocabulary["HELLO3"].docstring)

    assert (interp._coreVocabulary["HELLO3"].docstring[0].strip() == '3 hellos')
    assert (interp._coreVocabulary["HELLO3"].docstring[1].strip() == 'all good')

def testWordNotFoundError():
    interp = Interpreter()
    interp.interpret('DoesNotExist')
    checkError(interp, assertOnError=False)


def testCompilationError():
    interp = Interpreter()
    interp.interpret(': a DoesNotExist ;')
    checkError(interp, assertOnError=False)

def testFormatting1():
    interp = Interpreter()
    interp.interpret('12 "this is {} years" FORMAT')
    logging.info(interp.stack)
    assert(interp.stack[0] == "this is 12 years")

def testFormatting3():
    interp = Interpreter()
    interp.interpret('2 4 8 "{} x {} = {}" FORMAT')
    logging.info(interp.stack)
    assert(interp.stack[0] == "2 x 4 = 8")

def testExecute():
    interp = Interpreter()
    interp.interpret(': HELLO "Hello World" . 99 ;')
    interp.interpret("'  HELLO  EXECUTE")
    logging.info(interp.stack)

    assert(interp.stack[0] == 99)
    assert (len(interp.stack) == 1)

def testArrayPush():
    interp = Interpreter()
    interp.interpret('[ 12 34 667 ] ')
    logging.info(interp.stack)
    assert (interp.stack[0] == [ 12 ,34 ,667 ])
    assert (len(interp.stack) == 1)
    interp.interpret('.')

def testArrayMap():
    interp = Interpreter()
    interp.interpret(': test 2 * . ;')
    interp.interpret("[ 12 34 667 ] ' test MAP ")
    logging.info(interp.stack)

    assert (len(interp.stack) == 0)

def testLen():
    interp = Interpreter()

    interp.interpret("[ 12 34 667 ] LEN ")
    logging.info(interp.stack)

    assert (len(interp.stack) == 2)
    assert (interp.stack[-1] == 3)
