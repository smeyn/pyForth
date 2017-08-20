.. Forth in Python documentation master file, created by
   sphinx-quickstart on Fri Aug 18 11:11:12 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Forth in Python's documentation!
===========================================

This is the PyForth documentation. PyForth is a Forth like language
that has a stack and words that operate on the stack contents.

Unlike Forth, where the only items posasible on a stack are integers, PyForth
allows any Python object to be placed on the stack.


What's Different to Forth
=========================

Strings
-------

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


String Formatting
-----------------

Insead of using the rather tedious Forth style emitting, there is a simple version
of Pythons format concept

   2 4 8 "{} x {} = {}"

returns "2 x 4 = 8"

Comments:
---------

Comments are delimited with triple quotes

    """" this is a quote """

Comments can go over multiple lines.
If a comment is encountered during a compilation to a word, then it is added to
the words docstring collection.

Interpreter Logic
=================

The Interpreter will read in an input line and parse it as follows:

#. if it starts with a quote it will scan the line until it meets a matching end quote and take the quoted contents and place it as a string on a stack.

#. if it finds the next word (space delimited) can be converted to a number it will do so and place it on the stack

#. if neither of the above applies it will try to find the word in the vocabulary and execute it.


Contents
========
.. toctree::
   :maxdepth: 1

   runtime.rst
   primitive.rst
   words.rst





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
