import re
from pathlib import Path
import subprocess

filename = 'example.pbl'
printTokens = False
byteNumber = False
writeSourceCode = True
endOfLineSpacing = True

programLine = 0
tokenIndex = 0
prg = []
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

def readBracket(currentToken):
    check = re.search(r"\([^)]*\)", currentToken)
    if (check):
        return check.group(0)[1:-1]
    raise ValueError('No token found inside bracket')

def turnAllAfterIntoString():
    global programLine
    global tokenIndex
    tokenIndex += 1
    string = ""
    while (tokenIndex < len(prg[programLine])):
        string += " " + prg[programLine][tokenIndex]
        tokenIndex += 1
    return string.strip()


def getCurrentToken(tkn = ""):
    global programLine
    global tokenIndex
    if (tkn == ""):
        tkn = prg[programLine][tokenIndex]

    if (tkn == "halt"):
        return ("HALT","")

    if (tkn == "#"):
        return ("COMMENT",turnAllAfterIntoString())

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
def push():
    global tokenIndex
    stack.append(tokenIndex)

def pop():
    if (len(stack)-1 > 0):
        tokenIndex = stack[-1]
        del stack[-1]
        return 0
    else:
        return 1

def continueUntilMatchingToken(tokenType):
    global tokenizedList
    global tokenIndex
    while (tokenIndex < len(tokenizedList)):
        tokenIndex += 1
        if (tokenizedList[tokenIndex][0] == tokenType):
            return
    raise ValueError('No matching token found')

def continueUntilNonFlair():
    global tokenizedList
    global tokenIndex
    while (tokenIndex < len(tokenizedList)):
        tokenIndex += 1
        if (tokenizedList[tokenIndex][0] != "ENDOFLINE"):
            return
    raise ValueError('No matching token found')


def tokenize():
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

def printTokenizedList():
    for token in tokenizedList:
        if (token==("ENDOFLINE","")):
            print(token)
        else:
            print(token,end="")

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

# Load in PBL Program
with open(filename, 'r') as file:
    for line in file:
        tokens = line.strip().split()
        prg.append(tokens)
    tokenize()

if (printTokens):
    printTokenizedList()
    print()

variables = ["tmp"]

asmFilename = Path(filename).stem + ".asm"

def getToken(index):
    if (index > len(tokenizedList)):
        return ("","")
    else:
        return tokenizedList[index]

prgSize = 0
def writeInstruction(file, instruction):
    global byteNumber
    global prgSize
    file.write(instruction)
    if (byteNumber):
        file.write(f"\t\t; {prgSize}")
    file.write("\n")
    prgSize += 1

def writeSource(file, string):
    if (writeSourceCode):
        file.write("; " + string + "\n")


with open(asmFilename, 'w') as file:
    file.write("#include \"pb3.asm\"\n")
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
                    writeSource(file,f"{tknContentPrev} = {tknContentNext}")
                    writeInstruction(file,f"ldi {tknContentNext}")
                    writeInstruction(file,f"st {tknContentPrev}")
                elif (tknTypeNext == "VARIABLE"):
                    writeSource(file,f"{tknContentPrev}={tknContentNext}")
                    writeInstruction(file,f"ld {tknContentNext}")
                    writeInstruction(file,f"st {tknContentPrev}")
            else:
                raise ValueError('Invalid Token preceeding Equals')
        elif (tknType == "PLUSEQUALS"):
            tknTypePrev,tknContentPrev = tokenizedList[tokenIndex-1]
            tknTypeNext,tknContentNext = tokenizedList[tokenIndex+1]
            if (tknTypePrev == "VARIABLE"):
                if (tknTypeNext == "INTEGER"):
                    writeSource(file,f"{tknContentPrev} += {tknContentNext}")
                    writeInstruction(file,f"ldi {tknContentNext}")
                    writeInstruction(file,f"st tmp")
                    writeInstruction(file,f"ld {tknContentPrev}")
                    writeInstruction(file,f"add tmp")
                    writeInstruction(file,f"st {tknContentPrev}")
                elif (tknTypeNext == "VARIABLE"):
                    writeSource(file,f"{tknContentPrev} += {tknContentNext}")
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
                var = getToken(tokenIndex+2)[1]
                if (getToken(tokenIndex+3)[0] == "COMPNOTEQUAL"):
                    writeSource(file,f"GOTO IF {var}!={getToken(tokenIndex+4)[1]}")
                    writeInstruction(file,f"ld {var}")
                    writeInstruction(file,f"xnor {var}")
                    writeInstruction(file,f"jpz {tknContent}")
                elif (getToken(tokenIndex+3)[0] == "COMPEQUAL"):
                    writeSource(file,f"GOTO IF {var}=={getToken(tokenIndex+4)[1]}")
                    writeInstruction(file,f"ld {var}")
                    writeInstruction(file,f"jpz {tknContent}")
            else:
                # Unconditional
                writeSource(file,f"GOTO")
                writeInstruction(file,f"ldi 0")
                writeInstruction(file,f"jpz {tknContent}")
        elif (tknType == "COMMENT"):
            writeSource(file,f"COMMENT: {tknContent}")
        elif (tknType == "HALT"):
            writeSource(file,"HALT")
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
print(f"Program Size:\t{prgSize}/256")
print(f"Variables used:\t{len(variables)}/32\n")

subprocess.run(["customasm", asmFilename]) 