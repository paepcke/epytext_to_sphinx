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
    FUNC_DEF_START =  re.compile(r'[\s]*def[\s]+[^\(]*\([^\)]*\)[\s]*:[\s]*$')
    # Docstring symbol on a line of its own: three single-quotes
    DOCSTRING_START_OR_END = re.compile(r'[\s]*\'\'\'[\s]*$')
    PARAM_SPEC = re.compile(r'[\s]*@(return:|(param|type|rtype)[^:]+:)')
    '''

    def __init__(self, directoryOrFile):
        '''
        Constructor
        '''
        if os.path.isdir(directoryOrFile):
            files = os.listdir(directoryOrFile)
            self.files = filter(self.pyFileFilter(), files)
        else:
            self.files = [directoryOrFile]
        
    
    def pyFileFilter(self, fileName):
        return fileName.endswith('.py')
    
    def convertAll(self):
        for filePath in self.files:
            # Make a safety copy,
            # successively numbering backup files
            # if the same file is converted multiple
            # times:
            backupCopyNum = 0
            while True:
                backupFile = filePath + '.bak' + str(backupCopyNum)
                if os.path.isfile(backupFile):
                    backupCopyNum += 1
                    continue
                else:
                    shutil.copy(filePath,backupFile)
                    break
            self.convertOneFile(filePath)

    def convertOneFile(self, fullFilePath):
        foundFirstParmSpec = False
        inDocstring = False
        with open(fullFilePath, 'r') as fd:
            while True:
                line = fd.readline()
                if line is None:
                    break
                if EpytextConverter.DOCSTRING_START_OR_END.match(line) is not None:
                    if inDocstring:
                        inDocstring = False
                        foundFirstParmSpec = False
                    else:
                        inDocstring = True
                    fd.write(line)
                    continue
                elif EpytextConverter.FUNC_DEF_START.match(line) is not None:
                    fd.write(line)
                    continue
                if not inDocstring:
                    fd.write(line)
                    continue
                # We are inside a docstring. Are we looking
                # at a parameter/type/return/return type?
                if EpytextConverter.PARAM_SPEC.match(line):
                    # The first parameter spec must be separated from
                    # the introductory prose of the docstring by an
                    # empty line:
                    if not foundFirstParmSpec:
                        fd.write('\n')
                        foundFirstParmSpec = True
                    # Replace the leading '@' with a leading ':':
                    # the ^([\s]*) just grabs any leading whitespace,
                    # which the \1 inserts in the replacement:
                    line = re.sub(r'^([\s]*)@', r'\1:', line)
                    fd.write(line)
                    continue
                else:
                    fd.write(line)
                    continue 
                        
    
if __name__ == '__main__':
    
    if len(sys.argv) == 0:
        print("Usage: epytext_to_sphinx(<fullFilePath> | <fullDirectoryPath>")
        sys.exit()
    
    print(str(sys.argv))
    converter = EpytextConverter(sys.argv[1])    