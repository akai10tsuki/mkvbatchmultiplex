"""Utility functions"""

import time

# Algorithm for gregorian date calculations
# Before October 1582 are imprecise
# https://alcor.concordia.ca/~gpkatch/gdate-algorithm.html

YEAR, MONTH, DAY = range(3)

def gregorianDay(tDate):

    m = (tDate[MONTH] + 9) % 12
    y = tDate[YEAR] - int(m / 10)

    return (365 * y) + int(y/4) - int(y/100) + int(y/400) + \
            int((m * 306 + 5) / 10) + (tDate[DAY] - 1)

def gregorianDay2Date(intGday):

    y = int((10000 * intGday + 14780) / 3652425)
    ddd = intGday - (365 * y + int(y / 4) - int(y / 100) + int(y / 400))
    if ddd < 0:
        y = y - 1
        ddd = intGday - (365 * y + int(y / 4) - int(y / 100) + int(y / 400))

    mi = int((100 * ddd + 52) / 3060)
    mm = (mi + 2) % 12 + 1
    y = y + int((mi + 2) / 12)
    dd = ddd - int((mi * 306 + 5) / 10) + 1

    return (y, mm, dd)

def isLeapYear(year):

    if year < 1582:
        return False

    return (year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))

def daysBetweenDates(tDate1, tDate2):

    cumDays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334] #cumulative Days by month
    cumDaysLeapYear = [0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335] # Cumulative Days by month for leap year
    totalDays = 0

    if tDate1[YEAR] == tDate2[YEAR]:
        if isLeapYear(tDate1[YEAR]):
            return (cumDaysLeapYear[tDate2[MONTH]-1] + tDate2[DAY]) - \
                    (cumDaysLeapYear[tDate1[MONTH]-1] + tDate1[DAY])
        else:
            return (cumDays[tDate2[MONTH]-1] + tDate2[DAY]) - \
            (cumDays[tDate1[MONTH]-1] + tDate1[DAY])

    if isLeapYear(tDate1[YEAR]):
        totalDays = totalDays + 366 - (cumDaysLeapYear[tDate1[MONTH]-1] + tDate1[DAY])
    else:
        totalDays = totalDays + 365 - (cumDays[tDate1[MONTH]-1] + tDate1[DAY])

    year = tDate1[YEAR] + 1
    while year < tDate2[YEAR]:
        if isLeapYear(year):
            totalDays = totalDays + 366
        else:
            totalDays = totalDays + 365
        year = year + 1

    if isLeapYear(tDate2[YEAR]):
        totalDays = totalDays + (cumDaysLeapYear[tDate2[MONTH]-1] + tDate2[DAY])
    else:
        totalDays = totalDays + (cumDays[tDate2[MONTH]-1] + tDate2[DAY])
    return totalDays

def setDate(strSeparator=None):
    "Return date string YYYYMMDDHHMMSS with optional separator"

    tmTime = time.localtime(time.time())
    strTime = str(tmTime[0])

    for i in range(1,6):
        strTmp = str(tmTime[i])
        if (strSeparator and (i < 5)):
            strTime = strTime + strSeparator + strTmp.zfill(2)
        else:
            strTime = strTime + strTmp.zfill(2)

    return strTime

def padNumber(number, digitCount):

	# Normalizes a single digit number to have digitCount 0s in front of it
    strFormat = "%0" + str(digitCount) + "d"

    return strFormat % number

# parse numbers 1-10,17,20
from itertools import chain

def __parseRange(rng):

    atom = rng.split('-')

    if len(atom) > 2:
        raise ValueError("Bad range: '%s'" % (rng,))

    atom = [int(i) for i in atom]
    start = atom[0]
    end = start if len(atom) == 1 else atom[1]

    if start > end:
        end, start = start, end

    return range(start, end + 1)

def parseNumberRange(rngs, bReverseOrder=False):

    if bReverseOrder:
        return sorted( set( chain( *[__parseRange(rng) for rng in rngs.split(',')] ) ), reverse=True )

    return sorted( set( chain( *[__parseRange(rng) for rng in rngs.split(',')] ) ) )

# return ascii number for control codes of the form Ctrl-? where ? is the code from A-Z+
def ctrlCodeNumber(chCtrlCode):

    chrIndex = r'@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_'

    chCode = chCtrlCode[len(chCtrlCode) - 1]

    nIndex = chrIndex.find(chCode.upper())

    return nIndex

# Strip suffix from a string if found
def stripSuffix(text, suffix):

    if not text.endswith(suffix):
        return text

    return text[:-len(suffix)]