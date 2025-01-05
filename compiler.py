import re
from pathlib import Path
import subprocess

filename = 'example.pbl'
printTokens = True
byteNumber = False
writeCommentToggle = True
endOfLineSpacing = True

programLine = 0
tokenIndex = 0
prg = []
binarySize = 0
tokenizedList = []

def getString():
    global prg
    global programLine
    global tokenIndex
    string = ""
    remainingTokens = prg[programLine][tokenIndex+1:]
    for c in remainingTokens:
        string += " " + c
        tokenIndex += 1
    return string.strip()

# Read anything contained within a round bracket
def readBracket(currentToken):
    check = re.search(r"\([^)]*\)", currentToken)
    if (check):
        return check.group(0)[1:-1]
    raise ValueError('No token found inside bracket')

# Interpret all following tokens as part of a string
def turnAllAfterIntoString():
    global programLine
    global tokenIndex
    tokenIndex += 1
    string = ""
    while (tokenIndex < len(prg[programLine])):
        string += " " + prg[programLine][tokenIndex]
        tokenIndex += 1
    return string.strip()

# Get the current token
def getCurrentToken(tkn = ""):
    global programLine
    global tokenIndex
    if (tkn == ""):
        tkn = prg[programLine][tokenIndex]

    if (tkn == "halt"):
        return ("HALT","")

    if (tkn == "#"):
        return ("COMMENT",turnAllAfterIntoString())

    if (tkn == "carry"):
        return ("CARRY","")
    
    if (tkn == "!carry"):
        return ("NOCARRY","")

    elif (tkn == "="):
        return ("EQUALS",tkn)
    elif (tkn == "+="):
        return ("PLUSEQUALS",tkn)

    elif (tkn == "=="):
        return ("COMPEQUAL",tkn)
    elif (tkn == "!="):
        return ("COMPNOTEQUAL",tkn)

    elif (re.match(r"[A-Za-z]+:", tkn)):
        return ("LABEL",tkn[:-1])

    elif (tkn == "if"):
        return ("IF","")

    elif (re.match(r"[A-Za-z]", tkn)):
        if (tkn == "goto"):
            tokenIndex+=1
            return ("GOTO",prg[programLine][tokenIndex])
        return ("VARIABLE",tkn)

    elif (re.match(r"-?[0-9]", tkn)):
        return ("INTEGER",tkn)

# Skip all following tokens until a matching one is found
def continueUntilMatchingToken(tokenType):
    global tokenizedList
    global tokenIndex
    while (tokenIndex < len(tokenizedList)):
        tokenIndex += 1
        if (tokenizedList[tokenIndex][0] == tokenType):
            return
    raise ValueError('No matching token found')

# Skip all following tokens until a non-flair token, such as EoL, is found
def continueUntilNonFlair():
    global tokenizedList
    global tokenIndex
    while (tokenIndex < len(tokenizedList)):
        tokenIndex += 1
        if (tokenizedList[tokenIndex][0] != "ENDOFLINE"):
            return
    raise ValueError('No matching token found')

# Tokenize the Source
def tokenize():
    global prg
    global programLine
    global tokenIndex
    # Tokenize it
    while(programLine < len(prg)):
        tokens = prg[programLine]
        tokenIndex = 0
        while(tokenIndex < len(tokens)):
            ct = getCurrentToken()
            #print(f"{programLine:03d}\t{ct}")
            tokenizedList.append(ct)
            tokenIndex+=1
        tokenizedList.append(("ENDOFLINE",""))
        programLine+=1

# Print the tokenized List
def printTokenizedList():
    for token in tokenizedList:
        if (token==("ENDOFLINE","")):
            print(token)
        else:
            print(token,end="")

# Future Calculator function for more complex assignments
def evalAllFollowing():
    global tokenizedList
    global tokenIndex
    equationResult = 0
    while (tokenIndex < len(tokenizedList)):
        tkn = tokenizedList[tokenIndex]
        tknType,tknContent = tkn
        if (tknType == "INTEGER"):
            equationResult = tknContent
        elif (tknType == "ENDOFLINE"):
            return equationResult
        tokenIndex+=1
    raise ValueError('No matching token found')

# Leak safe token acquisition
def getToken(index):
    if (index > len(tokenizedList) or index < 0):
        return ("","")
    else:
        return tokenizedList[index]

def writeInstruction(file, instruction):
    global byteNumber
    global binarySize
    file.write(instruction)
    if (byteNumber):
        file.write(f"\t\t; {binarySize}")
    file.write("\n")
    binarySize += 1

def writeComment(file, string):
    if (writeCommentToggle):
        file.write("; " + string + "\n")

# Load in PBL Program
with open(filename, 'r') as file:
    for line in file:
        tokens = line.strip().split()
        prg.append(tokens)
    tokenize()

if (printTokens):
    printTokenizedList()
    print()

# Variables used by program
variables = ["tmp"]

asmFilename = Path(filename).stem + ".asm"

# Compile to assembly
with open(asmFilename, 'w') as file:
    writeComment(file,f"{filename}")
    writeComment(file,f"Compiled with the PBLang Compiler")
    writeComment(file,f"by T. Virtmann (2025)")
    file.write("\n#include \"pb3.asm\"\n\n")
    tokenIndex = 0
    while (tokenIndex < len(tokenizedList)):
        tknType,tknContent = getToken(tokenIndex)
        if (tknType == "VARIABLE"):
            # Check if the variable already exists
            if (tknContent not in variables):
                if (len(variables) > 32):
                    raise ValueError('Too many variables!')
                variables.append(tknContent)
        elif (tknType == "EQUALS"):
            tknTypePrev,tknContentPrev = tokenizedList[tokenIndex-1]
            tknTypeNext,tknContentNext = tokenizedList[tokenIndex+1]
            if (tknTypePrev == "VARIABLE"):
                if (tknTypeNext == "INTEGER"):
                    writeComment(file,f"{tknContentPrev} = {tknContentNext}")
                    writeInstruction(file,f"ldi {tknContentNext}")
                    writeInstruction(file,f"st {tknContentPrev}")
                elif (tknTypeNext == "VARIABLE"):
                    writeComment(file,f"{tknContentPrev}={tknContentNext}")
                    writeInstruction(file,f"ld {tknContentNext}")
                    writeInstruction(file,f"st {tknContentPrev}")
            else:
                raise ValueError('Invalid Token preceeding Equals')
        elif (tknType == "PLUSEQUALS"):
            tknTypePrev,tknContentPrev = tokenizedList[tokenIndex-1]
            tknTypeNext,tknContentNext = tokenizedList[tokenIndex+1]
            if (tknTypePrev == "VARIABLE"):
                if (tknTypeNext == "INTEGER"):
                    writeComment(file,f"{tknContentPrev} += {tknContentNext}")
                    writeInstruction(file,f"ldi {tknContentNext}")
                    writeInstruction(file,f"st tmp")
                    writeInstruction(file,f"ld {tknContentPrev}")
                    writeInstruction(file,f"add tmp")
                    writeInstruction(file,f"st {tknContentPrev}")
                elif (tknTypeNext == "VARIABLE"):
                    writeComment(file,f"{tknContentPrev} += {tknContentNext}")
                    writeInstruction(file,f"ld {tknContentNext}")
                    writeInstruction(file,f"st tmp")
                    writeInstruction(file,f"ld {tknContentPrev}")
                    writeInstruction(file,f"add tmp")
                    writeInstruction(file,f"st {tknContentPrev}")
            else:
                raise ValueError('Invalid Token preceeding Equals')
        elif (tknType == "LABEL"):
            file.write(f"{tknContent}:\n")
        elif (tknType == "GOTO"):
            # Conditional
            if (getToken(tokenIndex+1)[0] == "IF"):
                if (getToken(tokenIndex+2)[0] == "CARRY"):
                    writeComment(file,f"GOTO IF CARRY")
                    writeInstruction(file,f"xnor tmp")
                    writeInstruction(file,f"jpnc {tknContent}")
                elif (getToken(tokenIndex+2)[0] == "NOCARRY"):
                    writeComment(file,f"GOTO IF !CARRY")
                    writeInstruction(file,f"jpnc {tknContent}")
                else:
                    var = getToken(tokenIndex+2)[1]
                    operator = getToken(tokenIndex+3)[0]
                    if (operator == "COMPNOTEQUAL"):
                        writeComment(file,f"GOTO IF {var}!={getToken(tokenIndex+4)[1]}")
                        writeInstruction(file,f"ld {var}")
                        writeInstruction(file,f"xnor 31")
                        writeInstruction(file,f"st tmp")
                        writeInstruction(file,f"ld {var}")
                        writeInstruction(file,f"xnor tmp")
                        writeInstruction(file,f"jpz {tknContent}")
                    elif (operator == "COMPEQUAL"):
                        writeComment(file,f"GOTO IF {var}=={getToken(tokenIndex+4)[1]}")
                        writeInstruction(file,f"ld {var}")
                    writeInstruction(file,f"jpz {tknContent}")
            else:
                # Unconditional
                writeComment(file,f"GOTO")
                writeInstruction(file,f"ldi 0")
                writeInstruction(file,f"jpz {tknContent}")
        elif (tknType == "COMMENT"):
            writeComment(file,f"COMMENT: {tknContent}")
        elif (tknType == "HALT"):
            writeComment(file,"HALT")
            writeInstruction(file,"hlt")
        elif (tknType == "ENDOFLINE" and endOfLineSpacing):
            file.write(f"\n")
        tokenIndex += 1
    varIndex = 0
    file.write(f"\n; VARIABLES\n")
    for var in variables:
        file.write(f"{var}\t= {varIndex}\n")
        varIndex += 1
print("-- COMPILED -- ")
print(f"Program Size:\t{binarySize}/256")
print(f"Variables used:\t{len(variables)}/32\n")

subprocess.run(["customasm", asmFilename]) 