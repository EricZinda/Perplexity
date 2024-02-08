import os
import json
from os.path import isfile, join
from shutil import copy
from os import listdir


def GetDataDirectoryName():
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(scriptPath, "data")


def GetStateDirectoryName(userID):
    dataPath = GetDataDirectoryName()
    return os.path.join(dataPath, userID)


def SaveUserState(userID, data):
    stateDir = GetStateDirectoryName(userID)
    f = open(os.path.join(stateDir, "user.dat"), "w")
    f.write(json.dumps(data))
    f.close()


def HasStateDirectory(userID):
    dir = GetStateDirectoryName(userID)
    return os.path.isdir(dir)


def LoadUserState(userID):
    stateDir = GetStateDirectoryName(userID)
    f = open(os.path.join(stateDir, "user.dat"), "r")
    return json.loads(f.read())


def WriteLastPhrase(userID, phrase):
    stateDir = GetStateDirectoryName(userID)
    with open(os.path.join(stateDir, "lastphrase.log"), "w") as f:
        f.write(phrase)
        f.truncate()
    return


def ReadLastPhrase(userID):
    stateDir = GetStateDirectoryName(userID)
    filename = os.path.join(stateDir, "lastphrase.log")
    if os.path.isfile(filename):
        with open(filename, "r") as f:
            return f.read()
    else:
        return ""


def AddLog(userID, logEntry):
    stateDir = GetStateDirectoryName(userID)
    f = open(os.path.join(stateDir, "user.transcript"), "a")
    f.write(logEntry + "\n")
    f.close()
    return


def InitializeNewUser(userID, initialState):
    # Create the directory
    stateDir = GetStateDirectoryName(userID)
    if os.path.exists(stateDir):
        os.remove(stateDir)
    os.mkdir(stateDir)

    # Initialize with data that is always expected
    SaveUserState(userID, initialState)
    return


def GetMessages(path):
    files = [f for f in listdir(path) if (isfile(join(path, f)) and os.path.splitext(f)[1] == ".msg")]
    files.sort()
    fullPathFiles = []
    for file in files:
        fullPathFiles.append(os.path.join(path, file))
    return fullPathFiles


def CopyMessages(userID, startName, endName, destinationPath):
    path = GetStateDirectoryName(userID)
    startName = os.path.join(path, startName)
    endName = os.path.join(path, endName)
    files = GetMessages(path)
    count = 0
    for file in files:
        if startName <= file <= endName:
            count += 1
            copy(join(path, file), destinationPath)

    return count

