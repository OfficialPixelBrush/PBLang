import re
from pathlib import Path

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

def getCurrentToken(tkn = ""):
    global tokenIndex
    if (tkn == ""):
        tkn = prg[programLine][tokenIndex]

    if (tkn == "halt"):
        return ("HALT","")

    elif (tkn == "="):
        return ("EQUALS",tkn)
    elif (tkn == "+="):
        return ("PLUSEQUALS",tkn)

    elif (re.match(r"[A-Za-z]+:", tkn)):
        return ("LABEL",tkn[:-1])

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
filename = 'example.pbl'
with open(filename, 'r') as file:
    for line in file:
        tokens = line.strip().split()
        prg.append(tokens)
    tokenize()

printTokenizedList()

variables = []

with open(Path(filename).stem + ".asm", 'w') as file:
    currentByte = 0
    tokenIndex = 0
    print(variables)
    while (tokenIndex < len(tokenizedList)):
        tknType,tknContent = tokenizedList[tokenIndex]
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
                    file.write(f"ldi {tknContentNext}\nst {len(variables)-1}\n")
                elif (tknTypeNext == "VARIABLE"):
                    file.write(f"ld {variables.index(tknContentNext)}\nst {variables.index(tknContentPrev)}\n")
            else:
                raise ValueError('Invalid Token preceeding Equals')
        elif (tknType == "LABEL"):
            file.write(f"{tknContent}:\n")
        elif (tknType == "GOTO"):
            file.write(f"ldi 0\njpz {tknContent}\n")
        elif (tknType == "HALT"):
            file.write("hlt\n")
            break
        tokenIndex += 1