"""Test all priomitives"""


import logging
from  pyforth.runtime import Interpreter, vocabulary
import  pyforth.words
# pylint: disable="missing-function-docstring"
# pylint: disable="invalid-name"
# pylint: disable="logging-format-interpolation"
# pylint: disable="consider-using-f-string"
# pylint: disable="protected-access"


   

def _dumpCode_(method):
    s = ["  {}:{}\n".format(idx, str(item)) for idx, item in enumerate(method.code)]
    return " ".join(s)

def checkError(interp, assertOnError = True):
    if interp.lastError:
        logging.exception(interp.lastError)
        if assertOnError:
            assert False
    else:
        assert assertOnError # no error found so only if AssertOnError is false

def test_InterpreterSmokeTest():
    interp = Interpreter()
    interp.interpret("12 3 * DUP .")
    assert interp.stack[0] == 36

def test_Number():
    interp = Interpreter()
    interp.interpret("1 0 2 -1 -2")
    print (interp.stack)
    assert interp.stack[0] == 1
    assert interp.stack[1] == 0
    assert interp.stack[2] == 2
    assert interp.stack[3] == -1
    assert interp.stack[4] == -2

def test_Compile():
    interp = Interpreter()
    interp.interpret (": beta 3 4 * ;")
    assert "beta" in interp._core_vocabulary
    interp.interpret("beta")
    assert interp.stack[0] == 12

def test_DotQuoteAtRunTime():
    interp = Interpreter()
    interp.interpret('." test_ this"')
    logging.info(f"Stack='{interp.stack}'")
    assert len(interp.stack) ==0

def test_DotQuoteAtCompileTime():
    interp = Interpreter()
    interp.interpret(': test_ ." test_ this "  5 ;')
    interp.interpret('test_')
    logging.info("Stack='{}'".format(interp.stack))
    assert interp.stack[0] == 5
    assert len(interp.stack) ==1

def test_Loop(caplog):
    interp = Interpreter()
    interp.interpret(': test_ 0 0 5 DO I . 1 + LOOP ;')       
    logging.info (_dumpCode_(interp.vocabulary['test_']))
    #assert(False)
    with caplog.at_level(logging.DEBUG):
        interp.interpret('test_')
    logging.info("Stack='{}'".format(interp.stack))
    assert len(interp.rp) == 0

    assert len(interp.stack) == 1
    assert interp.stack[0] == 5

def test_double_loop():
    """ two nested loops"""
    interp = Interpreter()
    
    src=''' : test_
            (  --  "ok" n1 n2)
            0 0 1 6 DO  ( n1 n2)
               1 +   ( n1  n2 +1)
               I . DUP . ( print I c)        
               DUP I "Outer before- ctr: {} I: {}" FORMAT . ( print I c)
               SWAP 1 3 DO  ( n2 n1)
                 1 +  ( n2 n1+1)
                 DUP I J "Inner after- ctr: {} I: {} J:{}" FORMAT . ( print I c)                
               LOOP 
               SWAP 
               DUP I "Outer after - ctr: {} I: {}" FORMAT . ( print I c)                              
            LOOP
            "ok" ; ( 5 15  "ok" )                               
        '''

    interp.interpret(src) 
    assert interp.lastError is None, interp.lastError
    interp.interpret('test_')
    assert len(interp.stack) == 3
    
    assert interp.stack[-3] == 10
    assert interp.stack[-2] == 5
    assert interp.stack[-1] == "ok"    

def test_NoIterationLoop():
    interp = Interpreter()
    interp.interpret(': test_ 0 6 5 DO I . 1 + LOOP ;')
    logging.info (_dumpCode_(interp.vocabulary['test_']))
    #assert(False)
    interp.interpret('test_')
    logging.info("Stack='{}'".format(interp.stack))
    assert len(interp.stack) == 1
    assert interp.stack[0] == 0

def test_PlusLoop():
    interp = Interpreter()
    interp.interpret(': test_ 0 0 5 DO I . 1 + 2 +LOOP "ok" ;')
    logging.info (_dumpCode_(interp.vocabulary['test_']))
    #assert(False)
    interp.interpret('test_')
    logging.info("Stack='{}'".format(interp.stack))

    assert len(interp.stack) == 2
    assert interp.stack[0] == 3
    assert interp.stack[1] == "ok"

def test_If():
    interp = Interpreter()
    interp.interpret(': test_ 1 IF 5 ENDIF ;')
    logging.info("Stack before test_='{}'".format(interp.stack))
    assert len(interp.stack) == 0
    for s in _dumpCode_(interp._core_vocabulary["test_"]):
        logging.info(" : {}".format(s))

    interp.interpret('test_')
    logging.info("Stack='{}'".format(interp.stack))

    assert len(interp.stack) == 1
    assert interp.stack[0] == 5

def test_Else1():
    interp = Interpreter()
    interp.interpret(': test_ 1 IF 5 ELSE 3 ENDIF ;')
    logging.info("Stack before test_='{}'".format(interp.stack))
    assert len(interp.stack) == 0
    for s in _dumpCode_(interp._core_vocabulary["test_"]):
        logging.info(" : {}".format(s))

    interp.interpret('test_')
    logging.info("Stack='{}'".format(interp.stack))

    assert len(interp.stack) == 1
    assert interp.stack[0] == 5

def test_Else2():
    interp = Interpreter()
    interp.interpret(': test_ 0 IF 2 ELSE 3 ENDIF ;')
    logging.info("Stack before test_='{}'".format(interp.stack))
    assert len(interp.stack) == 0
    for s in _dumpCode_(interp._core_vocabulary["test_"]):
        logging.info(" : {}".format(s))

    interp.interpret('test_')
    logging.info("Stack='{}'".format(interp.stack))

    assert len(interp.stack) == 1
    assert interp.stack[0] == 3

def test_BeginUntil():
    interp = Interpreter()
    interp.interpret(': test_ 3 BEGIN 1 -   DUP 0 =   UNTIL "ok" ;')
    for s in _dumpCode_(interp._core_vocabulary["test_"]):
        logging.info(" : {}".format(s))
    #assert(False)
    interp.interpret('test_')
    logging.info("Stack='{}'".format(interp.stack))

    assert len(interp.stack) == 2
    assert interp.stack[0] == 0
    assert interp.stack[1] == "ok"

def test_BeginUntilLeave():
    interp = Interpreter()
    src=''': test_ 
      6 BEGIN 
        1 -
        DUP 4 < IF LEAVE ENDIF
        DUP 0 =
       UNTIL
       "ok" ;'''
    interp.interpret(src)
    assert interp.lastError is None

    # for s in _dumpCode_(interp._core_vocabulary["test_"]):
    #     logging.info(" : {}".format(s))
    #assert(False)
    interp.interpret('test_')
    logging.info("Stack='{}'".format(interp.stack))

    assert len(interp.stack) == 2
    assert interp.stack[-1] == "ok"
    assert interp.stack[-2] == 3


        

def test_While():
    interp = Interpreter()
    interp.interpret(': test_ 7 BEGIN 1 -   DUP WHILE DUP .   REPEAT "ok" ;')
    for s in _dumpCode_(interp._core_vocabulary["test_"]):
        logging.info(" : {}".format(s))
    #assert(False)
    interp.interpret('test_')
    logging.info("Stack='{}'".format(interp.stack))

    assert len(interp.stack) == 2
    assert interp.stack[0] == 0
    assert interp.stack[1] == "ok"

def test_While_leave():
    interp = Interpreter()
    src = ''': test_
          7 BEGIN
            1 - 
            DUP  WHILE            
           (  DUP 2 <= IF LEAVE ENDIF)
           DUP .
          REPEAT
          "ok" ;
            '''
    interp.interpret(src)
    # for s in _dumpCode_(interp._core_vocabulary["test_"]):
    #     logging.info(" : {}".format(s))
    #assert(False)
    interp.interpret('test_')
    logging.info("Stack='{}'".format(interp.stack))

    assert len(interp.stack) == 2
    assert interp.stack[0] == 2
    assert interp.stack[1] == "ok"



def test_leave_DO_1():
    interp = Interpreter()
    
    interp.interpret(': test_ 0 0 5 DO I . 1 +  DUP 2 > IF LEAVE ENDIF  LOOP "ok" ;') 
    assert interp.lastError is None, interp.lastError
    interp.interpret(' test_')
    
    assert len(interp.stack) == 2
    assert interp.stack[-2] == 3
    assert interp.stack[-1] == "ok"


def test_leave_DO_2():
    """ have 2 leave statements"""
    interp = Interpreter()
    
    src=''' : test_
            ( n  -- x "ok" )
            0 0 6 DO  ( n c)
               1 +   ( n c+1)
               DUP I "ctr: {} I: {}" FORMAT . ( print I c)
               OVER I < IF "first" LEAVE ENDIF ( n c' "first" )
               2 I < IF "second" LEAVE ENDIF ( n c' "second" )
            LOOP
            "ok" ;                                
        '''

    interp.interpret(src) 
    assert interp.lastError is None, interp.lastError
    interp.interpret('7 test_')
    assert len(interp.stack) == 4
    assert interp.stack[-4] == 7
    assert interp.stack[-3] == 4
    assert interp.stack[-2] == "second"
    assert interp.stack[-1] == "ok"

    interp.interpret('2 test_')
    assert len(interp.stack) > 4
    assert interp.stack[-4] == 2
    assert interp.stack[-3] == 4    
    assert interp.stack[-2] == "first"
    assert interp.stack[-1] == "ok"


def test_leave_double_loop():
    """ have 2 leave statements"""
    interp = Interpreter()
    
    src=''' : test_
            (  --  "ok" n1 n2)
            0 0 1 6 DO  ( n1 n2)
               1 +   ( n1  n2 +1)
               I . DUP . ( print I c)        
               DUP I "Outer before- ctr: {} I: {}" FORMAT . ( print I c)
               SWAP 1 3 DO  ( n2 n1)
                 1 +  ( n2 n1+1)
                 DUP I J "Inner after- ctr: {} I: {} J:{}" FORMAT . ( print I c)
                I 2 >=  IF LEAVE ENDIF 
               LOOP 
               SWAP 
               DUP I "Outer after - ctr: {} I: {}" FORMAT . ( print I c)               
               I 3 >= IF LEAVE ENDIF
            LOOP
            "ok" ; ( 3 6 )                               
        '''

    interp.interpret(src) 
    assert interp.lastError is None, interp.lastError
    interp.interpret('test_')
    assert len(interp.stack) == 3
    
    assert interp.stack[-3] == 6
    assert interp.stack[-2] == 3
    assert interp.stack[-1] == "ok"




def test_Variable():
    interp = Interpreter()
    interp.interpret('1234 VARIABLE BUU')
    assert len(interp.stack) == 0
    interp.interpret('BUU @')
    logging.info("Stack='{}'".format(interp.stack))
    assert len(interp.stack) == 1
    assert interp.stack[0] == 1234
    interp.interpret('BUU @ 1 +')
    assert len(interp.stack) == 2
    assert interp.stack[1] == 1235


def test_Constant():
    interp = Interpreter()
    interp.interpret('1234 CONSTANT BUU')
    assert len(interp.stack) == 0
    interp.interpret('BUU')
    logging.info("Stack='{}'".format(interp.stack))
    assert len(interp.stack) == 1
    assert interp.stack[0] == 1234

def test_AString():
    interp = Interpreter()
    interp.interpret('1234 "CONSTANT BUU"')
    logging.info("Stack='{}'".format(interp.stack))
    assert len(interp.stack) == 2
    assert interp.stack[0] == 1234
    assert interp.stack[1] == "CONSTANT BUU"

def test_Split1():
    interp = Interpreter()
    interp.interpret('"CONSTANT BUU xyz" " "')
    logging.info("Stack='{}'".format(interp.stack))
    assert len(interp.stack) == 2
    interp.interpret("SPLIT")
    logging.info("Stack='{}'".format(interp.stack))
    assert interp.stack[0] == ["CONSTANT", "BUU", "xyz"]

def test_Split2():
    interp = Interpreter()
    interp.interpret('"CONSTANT BUU.xyz" "."')
    logging.info("Stack='{}'".format(interp.stack))
    assert len(interp.stack) == 2
    interp.interpret("SPLIT")
    logging.info("Stack='{}'".format(interp.stack))

    assert interp.stack[0] == ["CONSTANT BUU", "xyz"]

def test_LoadFromFile():
    interp = Interpreter()
    interp.interpret('"sample.fth" LOAD')
    logging.info("loaded.")
    interp.interpret("HELLO HELLO3")
    logging.info("done.")

    checkError(interp, assertOnError=True)
    logging.info(interp._core_vocabulary["HELLO"].docstring)
    assert interp._core_vocabulary["HELLO"].docstring[0] == ' a simple hello '
    logging.info(interp._core_vocabulary["HELLO3"].docstring)

    assert interp._core_vocabulary["HELLO3"].docstring[0].strip() == '3 hellos'
    assert interp._core_vocabulary["HELLO3"].docstring[1].strip() == 'all good'

def test_WordNotFoundError():
    interp = Interpreter()
    interp.interpret('DoesNotExist')
    checkError(interp, assertOnError=False)


def test_CompilationError():
    interp = Interpreter()
    interp.interpret(': a DoesNotExist ;')
    checkError(interp, assertOnError=False)

def test_Formatting1():
    interp = Interpreter()
    interp.interpret('12 "this is {} years" FORMAT')
    logging.info(interp.stack)
    assert interp.stack[0] == "this is 12 years"

def test_Formatting3():
    interp = Interpreter()
    interp.interpret('2 4 8 "{} x {} = {}" FORMAT')
    logging.info(interp.stack)
    assert interp.stack[0] == "2 x 4 = 8"

def test_Execute():
    interp = Interpreter()
    interp.interpret(': HELLO "Hello World" . 99 ;')
    interp.interpret("'  HELLO  EXECUTE")
    logging.info(interp.stack)
    assert len(interp.stack) == 1
    assert interp.stack[0] == 99

def test_ArrayPush():
    interp = Interpreter()
    interp.interpret('[ 12 34 667 ] ')
    logging.info(interp.stack)
    assert interp.stack[0] == [ 12 ,34 ,667 ]
    assert len(interp.stack) == 1
    interp.interpret('.')

def test_ArrayMap():
    interp = Interpreter()
    interp.interpret(': test_ 2 * . ;')
    interp.interpret("[ 12 34 667 ] ' test_ MAP ")
    logging.info(interp.stack)

    assert len(interp.stack) == 0

def test_Len():
    interp = Interpreter()

    interp.interpret("[ 12 34 667 ] LEN ")
    logging.info(interp.stack)

    assert len(interp.stack) == 2
    assert interp.stack[-1] == 3


def test_mod():
    interp = Interpreter()

    interp.interpret("17 4 MOD ")
    assert len(interp.stack) == 1
    assert interp.stack[-1] == 1


def test_slashmod():
    interp = Interpreter()

    interp.interpret("17 4 /MOD ")
    assert len(interp.stack) == 2
    assert interp.stack[-2] == 1
    assert interp.stack[-1] == 4

def test_starslash_mod():
    interp = Interpreter()

    interp.interpret("1 17 4 */MOD ")
    assert len(interp.stack) == 2
    assert interp.stack[-2] == 1
    assert interp.stack[-1] == 4

def test_starslash():
    interp = Interpreter()

    interp.interpret("1 17 4 */ ")
    assert len(interp.stack) == 1
    assert interp.stack[-1] == 4

def test_min():
    interp = Interpreter()
    interp.interpret("7 9 MIN")
    assert len(interp.stack) == 1
    assert interp.stack[-1] == 7
    interp.reset()
    interp.interpret("7 3 MIN")
    assert len(interp.stack) == 1
    assert interp.stack[-1] == 3
    interp.reset()
    interp.interpret("324324 324324 MIN")
    assert len(interp.stack) == 1
    assert interp.stack[-1] == 324324

def test_max():
    interp = Interpreter()
    interp.interpret("7 9 MAX")
    assert len(interp.stack) == 1
    assert interp.stack[-1] == 9
    interp.reset()
    interp.interpret("7 3 MAX")
    assert len(interp.stack) == 1
    assert interp.stack[-1] == 7
    interp.reset()
    interp.interpret("324324 324324 MAX")
    assert len(interp.stack) == 1
    assert interp.stack[-1] == 324324    

def test_abs():
    interp = Interpreter()    
    interp.interpret("-7 ABS")
    assert len(interp.stack) == 1
    assert interp.stack[-1] == 7
    interp.reset()
    interp.interpret("7 ABS")
    assert len(interp.stack) == 1
    assert interp.stack[-1] == 7
    interp.reset()
    interp.interpret("0 ABS")
    assert len(interp.stack) == 1
    assert interp.stack[-1] == 0


def test_minus():
    interp = Interpreter()    
    interp.interpret("-7 MINUS")
    assert len(interp.stack) == 1
    assert interp.stack[-1] == 7
    interp.reset()
    interp.interpret("7 MINUS")
    assert len(interp.stack) == 1
    assert interp.stack[-1] == -7
    interp.reset()
    interp.interpret("0 MINUS")
    assert len(interp.stack) == 1
    assert interp.stack[-1] == 0

def test_1plus():
    interp = Interpreter()    
    interp.interpret("-7 1+")
    assert len(interp.stack) == 1
    assert interp.stack[-1] == -6



def test_2plus():
    interp = Interpreter()        
    interp.interpret("-7 2+")
    assert len(interp.stack) == 1
    assert interp.stack[-1] == -5



def test_and():
    interp = Interpreter()        
    interp.interpret("  6 3 AND")
    assert len(interp.stack) == 1
    assert interp.stack[-1] == 2




def test_or():
    interp = Interpreter()        
    interp.interpret("6 3 OR")
    assert len(interp.stack) == 1
    assert interp.stack[-1] == 7



def test_xor():
    interp = Interpreter()        
    interp.interpret("6 3 XOR")
    assert len(interp.stack) == 1
    assert interp.stack[-1] == 5


def test_fill():
    interp = Interpreter()        
    interp.interpret('7 3 "hello" FILL')
    assert len(interp.stack) == 0
    assert interp.mem[7] == "hello"
    assert interp.mem[8] == "hello"
    assert interp.mem[9] == "hello"


def test_move():
    interp = Interpreter()        
    interp.interpret('3 7 !  6 8 ! "Hi" 9  !')
    interp.interpret('7 23 2 MOVE')
    assert len(interp.stack) == 0
    assert interp.mem[7] is None
    assert interp.mem[8] is None
    assert interp.mem[9] == "Hi"
    assert interp.mem[23] == 3
    assert interp.mem[24] == 6
    

def test_erase():
    interp = Interpreter()        
    interp.interpret('7 3 "hello" FILL')
    assert len(interp.stack) == 0
    interp.interpret('7 2 ERASE')
    assert interp.mem[7] is None
    assert interp.mem[8] is None
    assert interp.mem[9] == "hello"


def test_blanks():
    interp = Interpreter()        
    interp.interpret('7 3 "hello" FILL')
    assert len(interp.stack) == 0
    interp.interpret('7 2 BLANKS')
    assert interp.mem[7] == ' '
    assert interp.mem[8] == ' '
    assert interp.mem[9] == "hello"

def test_toggle():    
    interp = Interpreter()        
    interp.interpret('10 20 !')
    assert len(interp.stack) == 0
    interp.interpret('20 7 TOGGLE ')
    assert interp.mem[20] == 13
    

