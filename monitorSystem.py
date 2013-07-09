#!/bin/python
#coding:utf-8
#Author:jomenxiao@gmail.com
#Date:2013-07-04
import os
import sys
import time
import re
import subprocess, shlex
import linecache


def checkLoad():
    loadFile = r'/proc/loadavg'
    try:
        loadList = linecache.getline(loadFile, 1).split() 
        returnMessage = '1 minute load :   ' + str(loadList[0]) + '\n'
        returnMessage = returnMessage + '5 minutes load : ' + str(loadList[1]) + '\n'
        returnMessage = returnMessage + '15 minutes load :  ' + str(loadList[2]) + '\n'
        returnMessage = returnMessage + 'running Process / total Process :' + str(loadList[3]) + '\n'

    except Exception, e:
        print e

    return returnMessage


def checkCpu():
    returnMessage = ''
    procCpuFile = r'/proc/stat'
    tempCpuFile = r'/tmp/savetempCpuFile'
    cpuFile = open(procCpuFile)
    
    if os.path.exists(tempCpuFile) and os.stat(tempCpuFile).st_size != 0:
        tempFile = open(tempCpuFile)
        for getNowCpuLine in cpuFile.readlines():
            nowCpuLine = getNowCpuLine.split()

            
            for getPastCpuLine in tempFile.readlines():
                pastCpuLine = getPastCpuLine.split()
    
                if nowCpuLine[0] == pastCpuLine[0] :
                    nowCpuUseIdleTime = long(nowCpuLine[4])                
                    nowCpuUseTime = long(nowCpuLine[1]) + long(nowCpuLine[2]) + long(nowCpuLine[3])
                    nowCpuTotalTime = long(nowCpuLine[1]) + long(nowCpuLine[2]) + long(nowCpuLine[3]) + long(nowCpuLine[4]) + long(nowCpuLine[5]) + long(nowCpuLine[6]) + long(nowCpuLine[7])

                    pastCpuUseIdleTime = long(pastCpuLine[4])
                    pastCpuUseTime = long(pastCpuLine[1]) + long(pastCpuLine[2]) + long(pastCpuLine[3])
                    pastCpuTotalTime = long(pastCpuLine[1]) + long(pastCpuLine[2]) + long(pastCpuLine[3]) + long(pastCpuLine[4]) + long(pastCpuLine[5]) + long(pastCpuLine[6]) + long(pastCpuLine[7])

                    percentIdle = 100 - 100 * (nowCpuUseIdleTime - pastCpuUseIdleTime) / (nowCpuTotalTime - pastCpuTotalTime)
                    percent = 100 * (nowCpuUseTime - pastCpuUseTime) / (nowCpuTotalTime - pastCpuTotalTime)

                    returnMessage = returnMessage + nowCpuLine[0] + '_byIdlePercent : ' + str(percentIdle) + '%\n' + nowCpuLine[0] + '_percent :       ' + str(percent) + '%\n'
                    tempFile.seek(0)
        
        tempFile.close()
        tempFile = open(tempCpuFile,'w')

        cpuFile.seek(0)
        for getNowTimeCpuLine in cpuFile.readlines():
            if len(getNowTimeCpuLine) < 5:
                continue
            if getNowTimeCpuLine.split()[0].startswith('cpu'):
                tempFile.write(getNowTimeCpuLine)


    else:        
        tempFile = open(tempCpuFile, 'w')
        for getCpuLine in cpuFile.readlines():
            if len(getCpuLine) < 5 :
                continue

            cpuLine = getCpuLine.split()
            if cpuLine[0].startswith('cpu'):
                tempFile.write(getCpuLine)

    cpuFile.close()
    tempFile.close()
    
    return returnMessage





def checkMem():
    memFile = r'/proc/meminfo'
    try:
        memTotal = int(linecache.getline(memFile, 1).split()[1]) / 1024
        memFree = (int(linecache.getline(memFile, 2).split()[1]) + int(linecache.getline(memFile, 3).split()[1]) + int(linecache.getline(memFile, 4).split()[1])) / 1024
        returnTotalMessege = 'MemTotal : %d MB' % memTotal
        returnFreeMessege = 'MemFree  : %d MB' % memFree
    except Exception, e:
        print e

    return returnTotalMessege + '\n' + returnFreeMessege + '\n'

def checkMysql():
    pass

def checkNginx():
    procDir = r'/proc'
    nginxPidFile = open(r'/var/run/crond.pid', 'r')
    nginxPid = nginxPidFile.read()
    nginxPidFile.close()

    procDirList = os.listdir(procDir)
    for processDir in procDirList:
        if processDir.isdigit():
            processFile = open(os.path.join(procDir, processDir, 'stat'), 'r')
            getProcessFile = processFile.readline().split()

            if long(getProcessFile[0]) ==  long(nginxPid) :
                print getProcessFile
                print int(getProcessFile[22]) / 1024,getProcessFile[23]
            processFile.close()


def checkDisk():
    try:
        # diskcommand
        diskCommand = ('df -h').split()
        getDiskCommand = subprocess.Popen(diskCommand, stdout=subprocess.PIPE)
        # diskiostat
        iostatCommand = ('iostat -x 30 1').split()
        getiostatCommand = subprocess.Popen(iostatCommand, stdout=subprocess.PIPE)
    except Exception, e:
        print e

    return getDiskCommand.stdout.read() + '+++++++++++++++++++++++\n' + getiostatCommand.stdout.read()

def checkMoreCpuAndMem():
    try:
        # get cpu info
        moreCommand = ('ps -eo user,pid,ppid,%cpu,%mem,stat,start,time,command').split()
        sortCpuCommand = ('sort -k4nr').split()
        sortMemCommand = ('sort -k5nr').split()
        headCommand = ('head -n 10').split()

        getCommand = subprocess.Popen(moreCommand, stdout=subprocess.PIPE)

        getSortCpuCommand = subprocess.Popen(sortCpuCommand, stdin=getCommand.stdout, stdout=subprocess.PIPE)
        getHeadCpuCommand = subprocess.Popen(headCommand, stdin=getSortCpuCommand.stdout, stdout=subprocess.PIPE)

        # get mem info
        # getMemCommand = subprocess.Popen(moreCommand,stdout=subprocess.PIPE)
        getsortMemCommand = subprocess.Popen(sortMemCommand, stdin=getCommand.stdout, stdout=subprocess.PIPE)
        getheadMemCommand = subprocess.Popen(headCommand, stdin=getsortMemCommand.stdout, stdout=subprocess.PIPE)

        return getHeadCpuCommand.stdout.read() + '+++++++++++++++++++++++++\n' + getheadMemCommand.stdout.read()

    except Exception, e:
        print e



def main():
    htmlFileName = r'/tmp/test'
    if os.path.exists(htmlFileName):
        os.remove(htmlFileName)

    checkRunhtmlFile = open(htmlFileName, 'a+')
    
    # write time
    checkRunhtmlFile.write(time.strftime("%Y_%m_%d %H:%M:%S", time.localtime(time.time())))
    checkRunhtmlFile.write('\n\n')

    # checkload
    checkRunhtmlFile.write('========loadInfo===========\n')
    checkRunhtmlFile.write(checkLoad())
    # checkmem
    checkRunhtmlFile.write('========memInfo=============\n')
    checkRunhtmlFile.write(checkMem())

    # checkdisk
    checkRunhtmlFile.write('=========disk===============\n')
    checkRunhtmlFile.write(checkDisk())

    # check cpu
    checkRunhtmlFile.write('=========cpu===============\n')
    checkRunhtmlFile.write(checkCpu())

    #check nginx
    checkNginx()

    # check the 10 biggest cpu or mem process info
    checkRunhtmlFile.write('========the most cpu and mem info============\n')
    checkRunhtmlFile.write(checkMoreCpuAndMem())

    checkRunhtmlFile.close

if __name__ == '__main__':
    main()
