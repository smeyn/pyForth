class PyForthError(Exception):
    """Base PyForth Error"""
    pass

class CompilationError(PyForthError):
    "errors during compilation"

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class WordNotFoundError  (PyForthError):
    "word is not in vocabulary"

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class ExecutionError    (PyForthError):
    """somethign went wrong during execution of a word"""
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message