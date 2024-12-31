#include "pb3.asm"
start:

; x = 0
ldi 0
st x

; y = -1
ldi -1
st y

loop:

; x += y
ld y
st tmp
ld x
add tmp
st x

; GOTO IF x!=0
ld x
xnor x
jpz loop

; HALT
hlt

; GOTO
ldi 0
jpz start


; VARIABLES
tmp	= 0
x	= 1
y	= 2
