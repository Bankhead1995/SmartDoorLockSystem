#class T9:
from time import sleep

def T9_input(LCD,KEYPAD,BUZZER):
    """ 
    +---------|---------|----------|--------+
    |    1    |    2    |    3     |        |
    |         |   ABC   |   DEF    |        |
    -----------------------------------------
    |    4    |    5    |    6     |        |
    |   GHI   |   JKL   |   MNO    |        |
    -----------------------------------------
    |    7    |    8    |    9     |        |
    |  PQRS   |   TUV   |   WXYZ   |        |
    -----------------------------------------
    |    *    |    0    |    #     |   D    |
    | Delete  |  Space  | U/L Case |  Enter |
    +---------|---------|----------|--------+
     """
    upperFlag = False
    retVal = ''
    selectionTemp = ''
    pressCount = 0
    keypadArray = [[]               , ['a','b','c'], ['d','e','f'],
                   ['g','h','i']    , ['j','k','l'], ['m','n','o'],
                   ['p','q','r','s'], ['t','u','v'], ['w','x','y','z']
                  ]
    while True:
        inputTemp = ''
        inputTemp = KEYPAD.getKey()
        sleep(0.05)
        if not inputTemp in ('A','B','C','1',None):
            BUZZER.BUZ_ON()
            if inputTemp is '#':
                upperFlag = not upperFlag
            elif inputTemp is '*':
                if retVal is not '':
                    retVal = retVal[:-1]
            elif inputTemp is 'D':
                if selectionTemp is '' and retVal is not '':
                    LCD.clear()
                    LCD.write_string("Entered:"+retVal)
                    return retVal
                else:
                    if (int(pressCount)-1) < len(keypadArray[int(selectionTemp)-1]):
                        if upperFlag:
                            retVal += keypadArray[int(selectionTemp)-1][int(pressCount)-1].upper()
                        else:
                            retVal += keypadArray[int(selectionTemp)-1][int(pressCount)-1]
                    selectionTemp = ''
                    pressCount = 0
            elif inputTemp is '0':
                retVal += ' '
            else:
                if selectionTemp is '':
                    selectionTemp = inputTemp
                    pressCount += 1
                elif selectionTemp is inputTemp:
                    pressCount += 1
                elif selectionTemp is not inputTemp:
                    pressCount = 1
                    selectionTemp = inputTemp
            LCD.clear()
            if pressCount == 0:
                LCD.write_string(retVal)
            elif (int(pressCount)-1) < len(keypadArray[int(selectionTemp)-1]):
                if upperFlag:
                    LCD.write_string(retVal + keypadArray[int(selectionTemp)-1][int(pressCount)-1].upper())
                else:
                    LCD.write_string(retVal + keypadArray[int(selectionTemp)-1][int(pressCount)-1])