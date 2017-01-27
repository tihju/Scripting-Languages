# Initializes file system

import os
import __builtin__


class TextFile:
    def __init__(self, name, startIndex, endIndex):
        self.fileName = name
        # stating position at fsname
        self.byteStart = startIndex
        # ending position at fsname
        self.byteEnd = endIndex  # -1 is undefined
        self.mode = ''
        self.isOpen = False
        # position of the system file/native file
        self.fsPos = startIndex
        # position of the user input/edit file
        self.filePos = 0

    def length(self):
        return self.byteEnd - self.byteStart + 1
        # for i in fileLength:

    def seek(self, pos):
        # if seek position greater than bytes, exception
        if pos >= self.length():
            raise ValueError("Out of bound")
        else:
            # master file/fsname position moves pos position
            self.fsPos = self.byteStart + pos;
            # user file position now is equal pos
            self.filePos = pos

    def write(self, content):
        # make sure the string length is less than or equal to the file length
        if len(content) <= self.length() - self.filePos:  # tracks the seek pointer
            if self.mode is 'w' or self.mode is 'r+w':
                for i in range(len(content)):
            # start write to master/fsname, find the position first
                    fd.seek(self.fsPos)
                # write into master/fsname file
                    fd.write(content[i])
            # increment the postion on both master file and user file
                    self.fsPos += 1
                    self.filePos += 1
            else:
                raise ValueError('is not Write mode')
        else:
            raise ValueError('Content exceeds size of file')  # haven't finished readlines
    def readlines(self):
        if self.mode is 'r' or self.mode is 'r+w':
            print("placeholder")  # haven't start directory class
class Directory:
    def __init__(self):
        self.dirlist = []
        self.files = []


# list to hold file object
fileList = []


def init(fsname):
    # file descriptor of fsname
    global fd
    fd = __builtin__.open(fsname, 'r+w')
    # size of system file 
    size = os.path.getsize(fsname)
    print size
    # size = 6
    # list of flag for space availibility of system file fsname
    # 0 for available and 1 for used
    global memory
    # make the flag list have the same size with the master/fsname file
    memory = [0] * size
    # memory = [1,1,0,0,0,1]
    # print(memory[size-1])


# use seek(5) and write to it # check if it has enough space, make a list to keep check the space available

# \xoo is null in python # create set lines to null


# fd = open('abc')

# fd.write
# fd.open

# focus on create file first then directory
# #Creates a file with a size of nbytes
def create(filename, nbytes):
    byteCount = 0
    startIndex = -1
    endIndex = -1

    # find number of consecutive bytes that are available in fsname for the file with nbyte
    for index, byte in enumerate(memory):
        if byte is 0:
            byteCount = byteCount + 1
        if byteCount is nbytes:
            endIndex = index
            startIndex = index - byteCount + 1
            for i in range(startIndex, endIndex + 1):
                memory[i] = 1
            break
            # if consecutive available bytes is less thatn nbyte and the following flag is 1
            # set byteCount to 0 and continue the for loop
        elif byteCount is not nbytes and byte is 1:
            byteCount = 0

    # print(memory)

    if (startIndex is -1 and endIndex is -1):
        raise ValueError('Cannot Create File')
    else:
        file = TextFile(filename, startIndex, endIndex)
        # file.write('\x00')
        fileList.append(file)


# #Opens a file with the given mode
def open(filename, mode):
    for file in fileList:
        # if file object is created before
        if file.fileName is filename:
            file.mode = mode
            file.isOpen = True
            return file
    raise ValueError('No such File')


#
# #Closes a certain file
def close(fd):
    fd.isOpen = False
    return fd


#
# #Returns the length (in bytes) of a given file
def length(fd):
    return fd.length()


#
# #Returns the current read/write position in the file
def pos(fd):
    return fd.filePos


#
# #Sets the read/write position to pos
def seek(fd, pos):
    fd.seek(pos)

#
# #returns a string; raises an exception if the read would extend beyond the current length of the file
# def read(fd, nbtes):
#
# #Writes to a file, where writebuf is a string
# def write(fd, writebuf):
#
# #reads the entire file, returning a list of strings; treats any 0xa byte it encounters as end of a line; does NOT change the pos value
# def readlines(fd):
#
# #Deletes a given file
# def delfile(filename):
#
# #Creates a directory named "dirname"
# def mkdir(dirname):
#
# #Deletes a given directory
# def deldir(dirname):
#
# #Returns true if "dirname" is a directory, false otherwise
# def isdir(dirname):
#
# #Lists all files in directory "dirname"
# def listdir(dirname):
#
# #Suspends the current file system
# def suspend():
#
# #Resumes the previously suspended file system
# def resume():
