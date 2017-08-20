=============
PyForth Words
=============


Memory Operations
=================
The engine has a dedicated memory area where items can be stored and retrieved by an address.

! (object addr  ->  )
---------------------
Stores TOS at address addr

@ ( addr -> object )
--------------------

Retrieves object at addr

Printing
========
.  (object -> )
---------------
print TOS (top of Stack). Removes stack

."  ( -> )
----------
Print a string Constant.
At runtime prints the next string (delimited by a "). At compile time compiles a constant based on the
next string. On execution it prints that constant

? ( addr ->  )
--------------
Print content of addr


Stack Manipulation
==================

DUP (n1 -> n1 n1 )
------------------
Duplicate TOS

DROP ( n1 ->  )
---------------
Remove TOS

ROT (n1 n2 n3  -> n3 n1 n2  )
-----------------------------
Rotate the top three elements on the Stack.

OVER (n1 n2  -> n1 n2 n1 )
--------------------------
Copy the second element onto TOS


SWAP (n1 n2  -> n2 n1 )
-----------------------
Swap the two top elements on the stack.

Stack Based Operations
======================
\* ( n1 n2  -> n )
------------------

Multiplies n1 with n2

\*/ (n1 n2 n3  ->  n)
---------------------
Multiplies n1 with n2 and divides by n3


\/ (n1 n2   -> n )
------------------
Divides n1 by n2


\+ (n1 n2  ->  n)
-----------------
Adds n1 and n2

\- (n1 n2  ->  n)
-----------------

Subtracts n2 from n1

OR (n1 n2  ->  n)
-----------------
Performs a logical OR

XOR (n1 n2  ->  n)
------------------
Performs a logical XOR

+! ( n addr  ->  )
------------------
Increments object at location addr by n


+- (n  ->  n)
-------------
Reverses the sign of n

\-DUP ( n1 -> n1 )  if n1 is zero
---------------------------------
\        ( n1 -> n1 n1)  if n1 is not zero
------------------------------------------

Checks TOS and duplicates if it is not zero.

0< (n  ->  f)
-------------

0= (n  ->  f)
-------------

1+ (n1  ->  n1+1)
-----------------

2+ (n1  ->  n1+2)
-----------------

< (n1 n2 ->  f)
---------------

= (n1 n2 ->  f)
---------------

> (n1 n2 ->  f)
---------------

< (n1 n2 ->  f)
---------------

>= (n1 n2 ->  f)
----------------

<= (n1 n2 ->  f)
----------------

Compilation
===========
: (  ->  )  immediate
---------------------
Starts compilation of a new method. The next word is the name of the method

;  ( -> )
---------
Completes compilation of a method.

Loop Constructs
===============
The following elements are only relevant within word definitions.

I (  ->  n)
-----------
For DO loops, returns the current index

DO ( n1 n2 ->  )
----------------
Starts a loop with index I that starts at n1 and terminates once I exceeds n1

LOOP (  ->  )
-------------
Complement to DO.
Compiles the word (LOOP)

+LOOP (n  ->  )
---------------
Complement to DO.  Compilation only.
Compiles the word (LOOP). See below.


(DO)  ( -> )
------------
*execute only*

Word compiled by DO. Checks termination condition.

(LOOP) (  ->  )
---------------
*Execute Only.*

Word compiled by LOOP. At runtime increments I by n and terminates if I > the termination value specified in DO

(+LOOP) (  ->  )
----------------
*Execute Only.*

Word compiled by +LOOP. At runtime increments I by n and terminates if I > the termination value specified in DO

BEGIN (  ->  )
--------------
Defines the beginning of a loop. Must be paired with one of :

*  UNTIL
*  WHILE ... REPEAT
*  AGAIN

UNTIL ( f ->  )
---------------
Defines the end of a BEGIN ... UNTIL Loop. Requires a flag. If the flag is true the loop terminates.

WHILE (f  ->  )
---------------
Defines an exit check for a BEGIN ... WHILE ... REPEAT loop.
Requires a flag. If the flag is false. the loop terminates.


REPEAT (  ->  )
---------------
Defines the end of a BEGIN ... WHILE ... REPEAT loop. The execution continues at the BEGIN part of the loop.

BRANCH ( ->  )
--------------
Causes an immediate branch within a method. Following the BRANCH word there must be an integer that defines the offset for the branch.

0BRANCH (f  ->  )
-----------------
Causes a conditional branch within a method. The branch only occurs if the flag is true. Following the BRANCH word there must be an integer that defines the offset for the branch.

IF ( f ->  )
------------
Starts an IF...ENDIF or IF...ELSE...ENDIF construt.
Expects a flag on TOS.


ELSE (  ->  )
-------------
Defines the ELSE branch


ENDIF (  ->  )
--------------
Terminates an IF statement.

VARIABLE ( n ->  )
------------------
Compiles a variable and initialises it with TOS.

CONSTANT (  ->  )
-----------------
Compiles a constant which is the word following this keyword.

WORDS (  ->  )
--------------
Prints out the list of words in the vocabulary.

EXPECT (  ->  )
---------------
Causes a line to be read from the console.

SPLIT (str delim -> str1 str2 ... )
----------------------
Takes a string and splits it using the delimiter.

LOAD ( str ->  )
----------------
Loads a Forth content file. Expects path on stack

FORMAT (n1 n2 ... formatString  ->  str)
----------------------------------------
Takes a formatspecifier and formats the string usung the remainder of the stack as arguments.

' (  ->  )
----------
Takes the next word and compiles puts the next words address on the stack.


EXECUTE (ref  ->  )
-------------------
Executes a method on TOS



