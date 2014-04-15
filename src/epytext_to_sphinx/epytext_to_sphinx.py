'''
Created on Apr 14, 2014

@author: paepcke
'''
import os
import re
import shutil
import sys


class EpytextConverter(object):
    '''
    Go through a set of given Python files, and convert epytext docstrings
    to Sphinx autodoc specs (http://docutils.sourceforge.net/docs/user/rst/quickref.html)
    Epytext is the Python docstring markup for the defunct epydoc.
    NOTE: only basic epytext is covered: @param, @type, @return, and @rtype.
    
    Usage: create an instance, then call convertAll() on it.
    '''
    FUNC_DEF_START =  re.compile(r'[\s]*def[\s]+[^\(]*\([^\)]*\)[\s]*:[\s]*$')
    # Docstring symbol on a line of its own: three single-quotes
    DOCSTRING_START_OR_END = re.compile(r'[\s]*\'\'\'[\s]*$')
    PARAM_SPEC = re.compile(r'[\s]*@(return:|(param|type|rtype)[^:]+:)')
    BLANK_LINE = re.compile(r'^[\s]*$')

    def __init__(self, directoryOrFile):
        '''
        Constructor
        '''
        if os.path.isdir(directoryOrFile):
            files = os.listdir(directoryOrFile)
            fileDir = directoryOrFile
            self.files = [os.path.join(fileDir,file) for file in files if self.pyFileFilter(os.path.join(fileDir,file))]
            #*****self.files = filter(self.pyFileFilter(files), files)
        else:
            self.files = [directoryOrFile]
        
    
    def pyFileFilter(self, fileName):
        return fileName.endswith('.py')
    
    def convertAll(self):
        '''
        For each file in list of files to be converted,
        make a backup copy, deleting the original. Then
        call convertOneFile() with the backup file as src,
        and original file name as dest.
        '''
        for filePath in self.files:
            if not os.path.exists(filePath):
                print("File %s does not exist. Continuing with next file." % filePath)
                continue
            # Make a safety copy,
            # successively numbering backup files
            # if the same file is converted multiple
            # times:
            backupCopyNum = 0
            # Find next available backup copy name,
            # and mv the original file to that backup:
            while True:
                backupFile = filePath + '.bak' + str(backupCopyNum)
                if os.path.isfile(backupFile):
                    backupCopyNum += 1
                    continue
                else:
                    shutil.move(filePath,backupFile)
                    break
            self.convertOneFile(backupFile, filePath)

    def convertOneFile(self, fullFilePathSrc, fullFilePathDest):
        '''
        Convert fullFilePathSrc, placing the converted result
        into fullFilePathDest. That dest file will be overwritten
        if it exists.
        
        @param fullFilePathSrc: file to be converted from epytext to Sphinx autodoc syntax.
        @type fullFilePathSrc: str
        @param fullFilePathDest: destination file name
        @type fullFilePathDest: src
        '''
        inDocstring = False
        prevLineWasEmpty = False
        isFirstParamSpec = True
        with open(fullFilePathSrc, 'r') as srcFd:
            with open(fullFilePathDest, 'w') as destFd:
                for line in srcFd:
                    if EpytextConverter.BLANK_LINE.match(line) is not None:
                        prevLineWasEmpty = True
                        destFd.write(line)
                        continue
                    if EpytextConverter.DOCSTRING_START_OR_END.match(line) is not None:
                        if inDocstring:
                            inDocstring = False
                            prevLineWasEmpty = False
                            isFirstParamSpec = True
                        else:
                            inDocstring = True
                        destFd.write(line)
                        prevLineWasEmpty = False
                        continue
                    if not inDocstring:
                        destFd.write(line)
                        prevLineWasEmpty = False
                        continue
                    # We are inside a docstring. Are we looking
                    # at a parameter/type/return/return type?
                    if EpytextConverter.PARAM_SPEC.match(line):
                        # The first parameter spec must be separated from
                        # the introductory prose of the docstring by an
                        # empty line:
                        if isFirstParamSpec and not prevLineWasEmpty:
                            destFd.write('\n')
                            prevLineWasEmpty = False
                        isFirstParamSpec = False
                        # Replace the leading '@' with a leading ':':
                        # the ^([\s]*) just grabs any leading whitespace,
                        # which the \1 inserts in the replacement:
                        line = re.sub(r'^([\s]*)@', r'\1:', line)
                        destFd.write(line)
                        prevLineWasEmpty = False
                        continue
                    else:
                        destFd.write(line)
                        prevLineWasEmpty = False
                        continue 
                            
    
if __name__ == '__main__':
    
    if len(sys.argv) == 1:
        print("Usage: epytext_to_sphinx(<fullFilePath> | <fullDirectoryPath>")
        sys.exit()
    
    converter = EpytextConverter(sys.argv[1])
    #*******************
    #shutil.copy('/home/paepcke/tmp/mysqldbORIG.py', '/home/paepcke/tmp/mysqldb.py')
    #*******************    
    converter.convertAll()