# Welcome to Forth in Python 

This is the PyForth documentation. PyForth is a Forth like language
that has a stack and words that operate on the stack contents.

Unlike Forth, where the only items posasible on a stack are integers, PyForth
allows any Python object to be placed on the stack.


# What's Different to Forth

## Strings

Strings are surrounded by quotes (double).

Strings can be manipulated like in Python:

     "hello" 3 * .

results in the output of

     hellohellohello

and this:

     "hello " "world" + .

results in the output of

     hello world


The word SPLIT will split a string into substrings. It requires a delimiter on the stack.


## String Formatting

Insead of using the rather tedious Forth style emitting, there is a simple version
of Pythons format concept

    2 4 8 "{} x {} = {}"

returns ```2 x 4 = 8```

## Comments:

Comments are delimited with triple quotes

  """" this is a quote """

Comments can go over multiple lines.
If a comment is encountered during a compilation to a word, then it is added to
the words docstring collection.

# Interpreter Logic

The Interpreter will read in an input line and parse it as follows:

* if it starts with a quote it will scan the line until it meets a matching end quote and take the quoted contents and place it as a string on a stack.
* if it finds the next word (space delimited) can be converted to a number it will do so and place it on the stack
* if neither of the above applies it will try to find the word in the vocabulary and execute it.


# Limitations
Currently it can't do recursion:

1. it's single pass, so it can't refer to things not yet compiled
2. the executor assumes there is always only ever 1 instance active

Recursion is addressed via differnt ways:

* Define a word called RECURSE
* introduce  SMUDGE

neither is nice. Why can't we have dynamic resolution:
1. any reference to a non defined word is marked
2. any definition results in resolving the references

Or:
1. compile a string instance followed by a EXECUTE