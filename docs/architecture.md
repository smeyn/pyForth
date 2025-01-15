# Architecture

# Module runtime

Contains the interpreter. Often referred to as the `engine`.

It has two key methods:

1. `run()` will run in a console, read in input and display output
2. `interpret(cmd)` will execute the string that was provided

both invoke `__process_cli__()` which parses the input and executes it

Errors and outputs are sent to `stdout`


## key attributes

* _core_vocabulary: a dictionary of vocabulary. It is generated from `primitives`
* stack: the Forth Stack, which can contain a python object
* mem: a memory area where each cell can contain a python object

# Module primitives
This module contains all primitives as well as core classes to make them work.

`class Runnable`
is  an abstract base class. It has the method `execute(engine:Interpreter, caller: Runnable)`

`class CompiledPrimitive` is a subclass of `Runnable`. It contains a python function that defines the primitive. `execute` will invoke the python function

`class CompiledConstant` represents a constant. Its `execute` method will push the constant 
value onto the stack

`class forthprim` is a decorator. Decorating a python function will generate an instance
of `class CompiledPrimitive` and add it to the `vocabulary` global


Primitives are then defined like this:
 
```
@forthprim(".")
def forth_print(engine, caller: CompiledCode):
    """print TOS"""
    sp = engine.stack
    top = sp[-1]
    sp.pop()
    print(top)
```

this will create a word called `.`


# TODOs