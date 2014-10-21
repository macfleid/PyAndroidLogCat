import sys
import os
import time
import subprocess
import threading
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


    def getPackageLogs_(self, mode, package):
        print("[androidLogger]:getPackageLogs_ for package :"+str(package))
        args = ['-v','long']
        #args = []
        self.myshell = subprocess.Popen([self.sdkPath, 'logcat', args],
                           stdin = subprocess.PIPE,
                           stdout = subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           bufsize=-1,
                           shell = True)
        printNextLine = 0
        for line in iter(self.myshell.stdout.readline, b''):
            lineResult = line.decode(self.encoding)
##            if package not in lineResult: #TODO Iterate
##               continue
            if not any(packageElement in lineResult for packageElement in package ) and printNextLine > 1:
                printNextLine = 0
                continue
            printNextLine+=1
            if mode==1:
                self.printToConsole(line)
            else :
                self.addToFile(line.decode(self.encoding))
        for line in iter(self.myshell.stderr.readline, b''):
            print(line)
        self.myshell.communicate()
        

    def stopLogging(self):
        self.myshell.communicate()
        self.myshell.terminate()

    def addToFile(self,result):
        #if not os.path.fileExists(self.resultFile):
            #os.makedirs('out')
        myFile = open(self.resultFile,encoding=self.encoding,mode='a')
        myFile.write(result)

    def printToConsole(self,line):
        line = str(bcolors.OKGREEN)+' '+str(line)+' '+str(bcolors.ENDC)
        print(line)

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



if __name__ == "__main__":
    doContinue = True
    androidLogger = androidLogger()

    myPackage = ["com.kayentis.eprotouch","com.kayentis.epro"]
    #myPackage = ["com.kayentis.eprotouch"]
    
    while doContinue:
        print('-----------------------')
        print('1 - Console mode')
        print('2 - (File mode)')
        print('3 - (File mode) > DEBUG')
        print('4 - (File mode) > WARNING')
        print('5 - (File mode) application Filtered ')
        print('6 - (File mode) custom Filtered  ')
        print('10 - exit')
        print('-----------------------')
        mode = 0
        try:
           # mode = int(input('Action:'))
            mode = input("Action :")
            print("typed:"+str(mode))
        except ValueError:
            print("Not a number\n")
        if mode == '10':
            print("exiting\n")
            doContinue = False
        elif mode == '1':
            print("starting logger")
            androidLogger.getPackageLogs_(1,myPackage)
        elif mode == '2':
            print("starting logger to file")
            androidLogger.resetFile()
            t = threading.Thread(target=androidLogger.getPackageLogs_,args=(2,myPackage))
            t.daemon = True
            t.start()
            print("started...\n")
            #mode = input("Type anything to stop...")
            #androidLogger.stopLogging()
            os.system("pause")
        elif mode == '4':
            print("starting logger to file")
            androidLogger.resetFile()
            t = threading.Thread(target=androidLogger.getLogs_,args=(2,' -v long *:W'))
            t.daemon = True
            t.start()
            print("started...")
            mode = input("Type anything to stop...")
            androidLogger.stopLogging()
        elif mode == '6':
            print('-------------------------------')
            print('----- Available filters -------')
            print('-------------------------------')
            print('1 - [SyncDateManager]')
            print('10 - exit')
            print('-----------------------')
            try:
                choice = input("Choice:")
                print("typed:"+str(mode))
            except ValueError:
                print("Not a number\n")

            argSyncDateManager = ' com.kayentis.epro.sync.manager.SyncDateManager:D *:S'
            filter = ''
            if choice == '1':
                filter = argSyncDateManager
            
            print("starting logger to file")
            androidLogger.resetFile()
            t = threading.Thread(target=androidLogger.getLogs_,args=(2,' -v long '+filter))
            t.daemon = True
            t.start()
            print("started...")
            try:
                test = input("Type anything to stop...")
            except ValueError:
                print("Not a number\n")
            finally:
                androidLogger.stopLogging()
            print("stopped...")
                
