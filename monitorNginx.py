import re
import os
import sys
import time

#nginxLogFile = r'/data/logs/nginx-ssl/openrestyaccess.log'
nginxLogFile = r'/tmp/openrestyaccess.log'


def detailIpList(ipList):
    printList = sorted([(number, IP) for IP,number in ipList.items()],reverse=True)[:15]

    for printSortedList in printList:
        print printSortedList[0],  ':', printSortedList[1] 

def detailMessege(messegeList):
    printList = sorted([(number, messege) for messege, number in messegeList.items()], reverse=True)[:15]
    
    for prinSortedMessege in printList:
        print prinSortedMessege[0], ':', prinSortedMessege[1]

def main():
    ipList = {}
    messegeList = {}
    logFile = open(nginxLogFile, 'r')
    for everyLine in logFile.readlines():
        everyIp = everyLine.split()[0]
        if everyIp in ipList:
            ipList[everyIp] += 1
        else:
            ipList[everyIp] = 1
        everyMessege = everyLine.split('\"')[1]
        if everyMessege in messegeList:
            messegeList[everyMessege] += 1
        else:
            messegeList[everyMessege] = 1
            

    detailIpList(ipList)
    print '===================================' + os.linesep
    detailMessege(messegeList)
    #everyTime = re.split(r"[\[\]]", everyLine)



if __name__ == '__main__' : 
    if not os.path.exists(nginxLogFile):
        print 'nginx log file is not exist !!!' + os.linesep
        exit()
    main()