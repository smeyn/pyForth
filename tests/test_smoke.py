import logging
from  pyforth.runtime import Interpreter
# import  pyforth.words



def test_smoke1(caplog):
    s = """: x 1 3 DO I . LOOP ." Done" ; x"""
    interp = Interpreter()
    with caplog.at_level(logging.DEBUG):
        interp.interpret(s)
        assert  interp.lastError is None, f"{interp.lastError=}"
