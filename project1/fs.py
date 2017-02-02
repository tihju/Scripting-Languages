# Initializes file system

import os
import __builtin__
import pickle


class TextFile:
    def __init__(self, name, startIndex, endIndex):
        self.fileName = name
        # stating position at fsname
        self.byteStart = startIndex
        # ending position at fsname
        self.byteEnd = endIndex  # -1 is undefined
        self.bytesUsed = 0
        self.mode = ''
        self.isOpen = False
        # position of the system file/native file
        self.nativeFilePos = startIndex
        # position of the user input/edit file
        self.userFilePos = 0

    def seek(self, pos):
        # master file/fsname position moves pos position
        self.nativeFilePos = self.byteStart + pos
        # user file position now is equal pos
        self.userFilePos = pos

    def write(self, content):
        for i in range(len(content)):
            # start write to master/fsname, find the position first
            nativeFD.seek(self.nativeFilePos)
            # write into master/fsname file
            nativeFD.write(content[i])
            # Increment the length of the file
            self.bytesUsed += 1
            # increment the position on both master file and user file
            self.nativeFilePos += 1
            self.userFilePos += 1

    def read(self, rbyte):
        nativeFD.seek(self.nativeFilePos)
        self.nativeFilePos += rbyte
        self.userFilePos += rbyte
        return nativeFD.read(rbyte)

    # treat 0xa byte as end of line, not change the pos value
    def readlines(self):
        rstring = ""
        wfile_list = []
        nativeFD.seek(self.byteStart)
        for i in nativeFD.read(self.bytesUsed):
            # treat 0xa byte as end of line
            if i == '\n' or i == '0xa':
                # Append current string to List
                if rstring != "":
                    wfile_list.append(rstring)
                # Reset String
                rstring = ""
                continue
            rstring += i
        if rstring != "":
            wfile_list.append(rstring)
        return wfile_list

    def __str__(self):
        name = '\'' + self.fileName + '\''
        mode = '\'' + self.mode + '\''
        return '<open file {0}, mode {1} at {2}>'.format(name, mode, hex(id(self)))


class Directory:
    def __init__(self, name, prevD):
        self.dirName = name
        self.contentList = []
        self.previousDir = prevD


def init(fsname):
    # file descriptor of fsname
    global nativeFD
    # Used to check if the system is suspended or not
    global isActive
    isActive = True
    # Tracks the number of files currently open
    global numFilesOpen
    numFilesOpen = 0
    nativeFD = __builtin__.open(fsname, 'r+')
    # size of system file
    size = os.path.getsize(fsname)
    # print size
    global memory
    # make the flag list have the same size with the master/fsname file
    # 0 for available and 1 for used
    memory = [0] * size
    # Current directory
    global curDir
    # Root directory
    global rootDir
    # DO NOT SET THIS EQUAL TO ANYTHING ELSE
    rootDir = Directory('/', None)
    # This will change
    curDir = rootDir


# THIS DOES NOT WORK YET
# Only works for single directory arguments. Doesn't work for lists of directories (e.g. "/d1/d1_1").
# Account for '/' at end of path
def chdir(dirname):
    global curDir
    # Split dirname into list of strings (or directories in this case). Separater character is '/'
    dirList = dirname.split('/')
    # If '' is last element, that means that '/' is the last character in the path and can be ignored
    if dirList[-1] == '':
        del dirList[-1]
    for dr in dirList:
        # If first character in dirname is '/', the first string will be blank
        if dr == '':
            curDir = rootDir
            continue
        # '.' means current directory, so just move onto the next dir in the list
        if dr == '.':
            continue
        # '..' means previous directory, so change curDir to previousDir, and resume
        if dr == '..':
            curDir = curDir.previousDir
            continue
        # Otherwise, go through the list trying to find the right directory
        curDir = find(dr, 'd')[1]


# return a list
# list[0] = index list[1] = object
def find(name, searchType):
    if searchType is 'd':  # Directory
        for index, d in enumerate(curDir.contentList):
            if isinstance(d, Directory) and d.dirName == name:
                return [index, d]
    elif searchType is 'f':  # file
        for index, f in enumerate(curDir.contentList):
            if isinstance(f, TextFile) and f.fileName == name:
                return [index, f]
    raise Exception('No such file or directory: ' + name)


# travel to the directory that the user specified
# return the file or directory name of the destination
def travel(path):
    fPath = path.split('/')
    fPath = filter(lambda x: x != '', fPath)
    # Last string in list should be file name to be created
    name = fPath[-1]
    # If only one element in the list, then only argument is file name, so no
    # need to change directories
    if len(fPath) > 1:
        # Join all strings except last (the directories) with '/' character so that
        # a path is passed into chdir
        fDir = "/".join(fPath[0:-1])
        if curDir.dirName != fPath[0] and path[0] == '/':
            fDir = '/' + fDir
            chdir(fDir)
    return name


# focus on create file first then directory
# #Creates a file with a size of nbytes
def create(filename, nbytes):
    global curDir
    tempDir = curDir

    fn = travel(filename)
    try:
        find(fn, 'f')
    except:
        byteCount = 0
        startIndex = -1
        endIndex = -1

        # find number of consecutive bytes that are available in fsname for the file with nbyte
        for index, byte in enumerate(memory):
            if byte is 0:
                byteCount += 1
            if byteCount is nbytes:
                endIndex = index
                startIndex = index - byteCount + 1
                for i in range(startIndex, endIndex + 1):
                    memory[i] = 1
                    nativeFD.seek(i)
                    nativeFD.write('\x00')  # write null char in file
                break
                # if consecutive available bytes is less thatn nbyte and the following flag is 1
                # set byteCount to 0 and continue the for loop
            elif byteCount is not nbytes and byte is 1:
                byteCount = 0

        if startIndex is -1 and endIndex is -1:
            curDir = tempDir
            raise Exception('Cannot Create File: Not enough space')
        else:
            f = TextFile(fn, startIndex, endIndex)
            curDir.contentList.append(f)
        curDir = tempDir
        return
    curDir = tempDir
    raise Exception("Already created " + fn + " file")


# Opens a file with the given mode
def open(filename, mode):
    # If file system is suspended, can't open file
    if not isActive:
        raise Exception("Cannot open file: file system is currently suspended")

    global numFilesOpen
    global curDir
    tempDir = curDir

    fn = travel(filename)

    f = find(fn, 'f')[1]
    f.mode = mode
    # Only increment if a non-opened file is being opened
    if not f.isOpen:
        numFilesOpen += 1
    f.isOpen = True
    # Set file pointer to beginning of file
    f.seek(0)
    curDir = tempDir
    return f


# Closes a certain file
def close(fd):
    global numFilesOpen
    # Only decrement if an open file is being closed
    if fd.isOpen:
        numFilesOpen -= 1
    fd.isOpen = False
    return fd


# Returns the length of used bytes in the file
def length(fd):
    return fd.bytesUsed


# Returns the current read/write position in the file
def pos(fd):
    return fd.userFilePos


# Sets the read/write position to pos
def seek(fd, pos):
    if pos >= fd.bytesUsed:
        raise Exception("Out of bounds")
    fd.seek(pos)


# returns a string; raises an exception if the read would extend beyond the current length of the file
def read(fd, nbytes):
    if not fd.isOpen:
        raise Exception("Failed to read: File is not open.")
    if fd.mode != 'r':
        raise Exception("Failed to read: File is not in read mode.")
    if nbytes > fd.byteStart + fd.byteEnd + 1 - fd.userFilePos:
        raise Exception("Failed to read: Exceeded size of file.")
    return fd.read(nbytes)


# Writes to a file, where writebuf is a string
def write(fd, writebuf):
    if not fd.isOpen:
        raise Exception("Failed to write: File is not open.")
    if fd.mode != 'w':
        raise Exception("Failed to write: File is not in write mode.")
    if len(writebuf) > fd.byteStart + fd.byteEnd + 1 - fd.userFilePos:
        raise Exception("Failed to write: Content exceeds size of file.")
    fd.write(writebuf)


# reads the entire file, returning a list of strings; treats any 0xa byte it
# encounters as end of a line; does NOT change the pos value
def readlines(fd):
    if not fd.isOpen:
        raise Exception("Failed to read: File is not open.")
    if fd.mode != 'r':
        raise Exception("Failed to read: File is not in read mode.")
    return fd.readlines()


# Deletes a given file
def delfile(filename):
    global curDir
    tempDir = curDir

    fn = travel(filename)

    temp = find(fn, 'f')
    index = temp[0]
    f = temp[1]
    if f.isOpen:
        curDir = tempDir
        raise Exception("Unable to delete file: File is open.")
    for i in range(f.byteStart, f.byteEnd + 1):
        memory[i] = 0
    del curDir.contentList[index]
    # Set file pointer to beginning of file
    f.seek(0)
    curDir = tempDir


# Creates a directory named "dirname"
def mkdir(dirname):
    global curDir
    tempDir = curDir

    dn = travel(dirname)

    try:
        find(dn, 'd')
    except:
        curDir.contentList.append(Directory(dn, curDir))  # no duplicate dirname
        curDir = tempDir
        return
    curDir = tempDir
    raise Exception("Already created " + dn + " directory")


# Deletes a given directory
def deldir(dirname):
    global curDir
    tempDir = curDir

    dn = travel(dirname)

    temp = find(dn, 'd')
    index = temp[0]
    if temp[1] is curDir:
        curDir = tempDir
        raise Exception("Cannot delete directory: Currently in directory to be deleted")
    del curDir.contentList[index]
    curDir = tempDir


# Returns true if "dirname" is a directory, false otherwise
def isdir(dirname):
    global curDir
    tempDir = curDir  # save curDir ref
    try:
        chdir(dirname)  # change dirname
        found = True
    except:
        found = False
    curDir = tempDir
    return found


# FOR TESTING
def getcwd():
    return curDir.dirName


# Lists all files in directory "dirname"
def listdir(dirname):
    global curDir
    # Save current directory object
    tempDir = curDir
    chdir(dirname)

    fileList = []
    # Place all file/directory names in a list
    for inst in curDir.contentList:
        if isinstance(inst, TextFile):
            fileList.append(inst.fileName)
        elif isinstance(inst, Directory):
            fileList.append(inst.dirName)
    # Restore current directory object
    curDir = tempDir
    return fileList


# Suspends the current file system
def suspend():
    # If any files are still open, cannot suspend file system
    if numFilesOpen != 0:
        raise Exception("Cannot suspend file system: a file is still open.")

    global saveName
    saveName = nativeFD.name + '.fssave'
    global isActive
    isActive = False
    saveDict = {"memory": memory, "rootDir": rootDir, "curDir": curDir, "fsname": nativeFD.name}
    pickle_file = __builtin__.open(saveName, 'wb')
    pickle.dump(saveDict, pickle_file)
    nativeFD.close()  # close the master file
    pickle_file.close()


# #Resumes the previously suspended file system
def resume():
    global isActive
    # Check if the file system is suspended
    if isActive:
        raise Exception("No file system has been suspended")

    pickle_file = __builtin__.open(saveName, 'rb')
    saveDict = pickle.load(pickle_file)
    isActive = True
    global nativeFD
    nativeFD = __builtin__.open(saveDict["fsname"], 'r+')
    global memory
    memory = saveDict["memory"]
    global rootDir
    rootDir = saveDict["rootDir"]
    global curDir
    curDir = saveDict["curDir"]
    pickle_file.close()
