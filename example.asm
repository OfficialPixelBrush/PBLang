; example.pbl
; Compiled with the PBLang Compiler
; by T. Virtmann (2025)

#include "pb3.asm"

; COMMENT: Counting Program

start:

; x = 0
ldi 0
st x

; y = 1
ldi 1
st y

loop:

; x += y
ld y
st tmp
ld x
add tmp
st x

; GOTO IF !CARRY
jpnc loop

; HALT
hlt

; GOTO
ldi 0
jpz start


; VARIABLES
tmp	= 0
x	= 1
y	= 2
