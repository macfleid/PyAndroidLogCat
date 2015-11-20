import sys
import os
import time
import subprocess
import threading
import re
import argparse
from queue import Queue


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    

class androidLogger:
   
    def __init__(self):
        self.encoding = 'ISO-8859-1'
        self.sdkPath = 'C:/Program Files (x86)/Eclipse_android/sdk/platform-tools/adb.exe'
        self.resultFile = 'logs.txt'
        self.endofline = '\r\r'
        
    def getLogs(self, command):
        self.myshell = subprocess.Popen([self.sdkPath, command],
                           stdin = subprocess.PIPE,
                           stdout = subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           bufsize=-1,
                           shell = True)
        print("[androidLogger]:getLogs")
        command = self.sdkPath+' -devices'
        self.myshell.stdin.write(bytes(command,self.encoding))
        print("[androidLogger]:1")
        result = self.myshell.communicate(timeout=5)
        print("[androidLogger]:Length:"+str(sys.getsizeof(result[0])))
        print("[androidLogger]#"+result[0].decode(self.encoding))

        #self._doPrint()
        #sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        #out = os.read(sys.stdout.fileno(), 10)
        #print (out)

        
                        
    def getLogs_(self, mode, args):
        self.myshell = subprocess.Popen([self.sdkPath, 'logcat', args],
                           stdin = subprocess.PIPE,
                           stdout = subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           bufsize=-1,
                           shell = True)
        #result = proc.communicate(timeout=5)
        #print("[androidLogger]:Length:"+str(sys.getsizeof(result[0])))
        #print("[androidLogger]#"+result[0].decode(self.encoding))
        #print("[androidLogger]#"+result[1].decode(self.encoding))
        for line in iter(self.myshell.stdout.readline, b''):
            if mode==1:
                print(line)
            else :
                self.addToFile(line.decode(self.encoding))
        for line in iter(self.myshell.stderr.readline, b''):
            print(line)
        self.myshell.communicate()


    def getPackageLogs_(self, mode, package, packageToRemove, loggerLevel):
        print("[androidLogger]:getPackageLogs_ for package :"+str(package))
        loggerLevel_ = ' *:'+loggerLevel
        args = ['-v','long',loggerLevel_]
        #args = []
        self.myshell = subprocess.Popen([self.sdkPath, 'logcat', args],
                           stdin =subprocess.PIPE,
                           stdout =subprocess.PIPE,
                           stderr =subprocess.PIPE,
                           bufsize = -1,
                           shell = True)
        printNextLine = 0
        for line in iter(self.myshell.stdout.readline, b''):
            lineResult = line.decode(self.encoding)
            isHeader = False
            if printNextLine >= 1:
                if re.search(self.endofline, lineResult, re.I):
                    printNextLine = 0
            else :
                foundPackage = False
                if any(re.search(packageElement,lineResult,re.I) for packageElement in package) and not any(re.search(packageElement,lineResult,re.I) for packageElement in packageToRemove):
                    printNextLine = 1
                    isHeader = True
                else :
                    printNextLine = 0
                    continue
            if mode==1:
                self.printToConsole(line,isHeader)
            else :
                self.addToFile(line,isHeader)
        # for line in iter(self.myshell.stderr.readline, b''):
        #     print(line)
        self.myshell.communicate()

    def clearLogs(self):
        args = ['-c']
        self.myshell = subprocess.Popen([self.sdkPath, 'logcat', args],
                           stdin = subprocess.PIPE,
                           stdout = subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           bufsize=-1,
                           shell = True)
        

    def stopLogging(self):
        self.myshell.terminate()

    def addToFile(self,result,isHeader):
        #if not os.path.fileExists(self.resultFile):
            #os.makedirs('out')
        line = result
        line = line.decode(self.encoding)
        if isHeader:
            line = self.formatHeaderLine(line)
        else:
            line = self.formatLine(line)
        myFile = open(self.resultFile,encoding=self.encoding,mode='a')
        myFile.write(line)

    def printToConsole(self,result,isHeader):
        #line = str(bcolors.OKGREEN)+' '+str(line)+' '+str(bcolors.ENDC)
        line = result
        line = line.decode(self.encoding, "ignore")
        if isHeader:
            line = self.formatHeaderLine(line)
        else:
            line = self.formatLine(line)
        print(line.encode(self.encoding))


    def formatHeaderLine(self,line):
        lineResult = line.rstrip(' \t\n\r')
        lineResult += ' -> '
        return lineResult
    
    def formatLine(self,line):
        lineResult = line.rstrip(' \t\n\r')
        lineResult += '\r'
        return lineResult

    def resetFile(self):
        print("[resetFile]:")
        if os.path.exists(self.resultFile):
           os.remove(self.resultFile)  
    
    def _doPrint(self):
        result = ''
        while True:
            try:
                line = self.myshell.stdout.read(1).decode(self.encoding)
                if line == str('>'):
                    break
                result += str(line)
            except:
                print('error')
                break
        print(str(result))
        #self.myshell.stdout.flush()
        #go to the end of stream
        return result

'''
[EXECUTION PART]
'''
if __name__ == "__main__":
    myDescription = '{:^100}'.format('LOGCAT parser for android.\n Last updated on 2015 November 18. \n Made by G.S')
    parser = argparse.ArgumentParser(description=myDescription,
                                     epilog='Exemple : python main.py -p com.kayentis.epro -s -i com.kayentis.epro.sqlite',
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-p', type=str, dest='package', help='package to catch')
    parser.add_argument('-i', type=str, nargs='+', dest='ignorePackages', help='packages to ignore')
    parser.add_argument('-l', type=str, dest='level', help='level to log (D=debug, E=error, W=warning)')
    parser.add_argument('-s', dest='save', help='save to an external file', action="store_true")
    options = parser.parse_args()
    print(options)

    if not options.package:
        parser.print_help()
    else:
        androidLogger = androidLogger()
        myPackage = [options.package]
        packageToRemove = []
        # ignore packages Part
        if options.ignorePackages:
            packageToRemove.extend(options.ignorePackages)
        # log level Part
        debugLevel = 'D'
        if options.level:
            debugLevel = options.level
        # save into file Part
        if options.save:
            androidLogger.resetFile()
            androidLogger.clearLogs()
            t = threading.Thread(target=androidLogger.getPackageLogs_, args=(2, myPackage, packageToRemove, debugLevel))
            t.daemon = True
            t.start()
            print("started...\n")
            os.system("pause")
            t.join(1)
        # console Part
        else:
            androidLogger.getPackageLogs_(1, myPackage, packageToRemove, debugLevel)



# if __name__ == "__main__":
#     doContinue = True
#     androidLogger = androidLogger()
#
#    # myPackage = ["com.kayentis.eprotouch","com.kayentis.epro"]
#    # myPackage = ["com.kayentis.eprotouch"]
#     myPackage = ["com.kayentis.epro"]
#     # packageToRemove = ["com.kayentis.epro.sqlite"]
#     packageToRemove = []
#
#     while doContinue:
#         print('-----------------------')
#         print('1 - Console mode')
#         print('2 - (File mode)')
#         print('3 - Console mode > WARNING')
#         print('4 - (File mode) > WARNING')
#         print('6 - (File mode) custom Filtered  ')
#         print('10 - exit')
#         print('-----------------------')
#         mode = 0
#         try:
#            # mode = int(input('Action:'))
#             mode = input("Action :")
#             print("typed:"+str(mode))
#         except ValueError:
#             print("Not a number\n")
#
#         if mode == '10':
#             print("exiting\n")
#             doContinue = False
#         elif mode == '1':
#             print("starting logger")
#             androidLogger.clearLogs()
#             androidLogger.getPackageLogs_(1,myPackage,packageToRemove,'D')
#         elif mode == '3':
#             print("starting logger")
#             androidLogger.clearLogs()
#             androidLogger.getPackageLogs_(1,myPackage,packageToRemove,'W')
#         elif mode == '2':
#             print("starting logger to file")
#             androidLogger.resetFile()
#             androidLogger.clearLogs()
#             t = threading.Thread(target=androidLogger.getPackageLogs_,args=(2,myPackage,packageToRemove,'D'))
#             t.daemon = True
#             t.start()
#             print("started...\n")
#             os.system("pause")
#             t.join(1)
#         elif mode == '4':
#             print("starting logger to file")
#             androidLogger.resetFile()
#             androidLogger.clearLogs()
#             t = threading.Thread(target=androidLogger.getPackageLogs_,args=(2,myPackage,packageToRemove,'W'))
#             t.daemon = True
#             t.start()
#             print("started...\n")
#             os.system("pause")
#             t.join(1)
#         elif mode == '6':
#             print('-------------------------------')
#             print('----- Available filters -------')
#             print('-------------------------------')
#             print('1 - [SyncDateManager]')
#             print('10 - exit')
#             print('-----------------------')
#             try:
#                 choice = input("Choice:")
#                 print("typed:"+str(mode))
#             except ValueError:
#                 print("Not a number\n")
#
#             argSyncDateManager = ' com.kayentis.epro.sync.manager.SyncDateManager:D *:S'
#             filter = ''
#             if choice == '1':
#                 filter = argSyncDateManager
#
#             print("starting logger to file")
#             androidLogger.resetFile()
#             t = threading.Thread(target=androidLogger.getLogs_,args=(2,' -v long '+filter))
#             t.daemon = True
#             t.start()
#             print("started...")
#             try:
#                 test = input("Type anything to stop...")
#             except ValueError:
#                 print("Not a number\n")
#             finally:
#                 androidLogger.stopLogging()
#             print("stopped...")
                
