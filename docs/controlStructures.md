# Constrol structures

* IF THEN ELSE 
* DO LOOP etc


## Loops
### DO LOOP

Compilation is like
```
n1, n2 DO .... LOOP
```
with n1 the start index
and n2 the end index


`DO` does the following:
1. compile two >R, at run time this will transfer
the limit and the start index onto the RP stack
2. save on the stack the current address of the compiling method. This is required for the LOOP part to compile a jump to the start of the loop
3. Save on the stack the sentinel string `DOFLAG`
4. Compile the word `(DO)`. 
5. Compile the workd `0BRANCH`
6 Compile a constant (to be filled in laer


so the compiled code looks like
```
                       /-----------------------+
  >R >R (DO) 0BRANCH raddr1 .... (LOOP) raddr2
          ^-----------------------------/
```
with `raddr1` being an offset pointing past `raddr2`
and `raddr2` being an offset point to `(DO)` word

`(DO)` does the following:
it compares rp[-1] with rp[-2]. If they are the same
then push a 0 onto the stack
else push a 1 onto the stack

`0BRANCH` checks the TOS and if 0, then executes a branch towards location stored in the following location. Otherwise sets XP to next after.


`LOOP` does the following:
1. POP TOS and assert it is the word DOFLAG 
2. compile the word `(LOOP)`
3. pop the address from the stack, which points to `(DO)`
4. Compile the difference between this address and current code address

