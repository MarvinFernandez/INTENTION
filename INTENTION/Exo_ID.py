#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 13:03:18 2021

@author: nrg
"""
from PCANBasic import PCAN_PCIBUS3, PCAN_BAUD_1M, PCANBasic, PCAN_ERROR_OK, PCAN_ERROR_BUSLIGHT, PCAN_ERROR_BUSHEAVY, PCAN_ERROR_BUSOFF, PCAN_MESSAGE_STANDARD, TPCANMsg, PCAN_NONEBUS, PCAN_ERROR_QRCVEMPTY 
import time
import numpy as np
msg = TPCANMsg()



def TurnOn(objPCAN):
    
    ## MIN ANGLES ACCEPTED
    msg.ID = 0x04
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = -0x19
    msg.DATA[1] = 0x00
    msg.DATA[2] = -0x19
    msg.DATA[3] = -0x19
    msg.DATA[4] = 0x00
    msg.DATA[5] = -0x19
    objPCAN.Write(PCAN_PCIBUS3, msg)
    
    ## JOIN BLOCK
#    msg.ID = 0x051
#    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
#    msg.LEN = 6
#    msg.DATA[0] = 0
#    msg.DATA[1] = 0
#    msg.DATA[2] = 0
#    msg.DATA[3] = 0
#    msg.DATA[4] = 0
#    msg.DATA[5] = 0
#    objPCAN.Write(PCAN_PCIBUS3,msg)
    
    ## Read angle     
    msg.ID = 0xe6
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    objPCAN.Write(PCAN_PCIBUS3, msg)
    
    time.sleep(0.5)
#    tR0=time.time() 
    read=objPCAN.Read(PCAN_PCIBUS3)
    joinangle=0
    while read[0] != PCAN_ERROR_QRCVEMPTY: #32 = buffere empty
        if read[1].ID == 110:
            joinangle=read[1].DATA
        read=objPCAN.Read(PCAN_PCIBUS3)
    anglejoin=np.array([joinangle[0],joinangle[1],joinangle[2],joinangle[3],joinangle[4],joinangle[5]])    
    if joinangle != 0:
        ## PASSIVE MODE
        msg.ID = 0x051
        msg.MSGTYPE = PCAN_MESSAGE_STANDARD
        msg.LEN = 6
        msg.DATA[0] = 0
        msg.DATA[1] = 11
        msg.DATA[2] = 0
        msg.DATA[3] = 0
        msg.DATA[4] = 0
        msg.DATA[5] = 0
        objPCAN.Write(PCAN_PCIBUS3,msg)
        if anglejoin[0]>128:
            anglejoin[0]=anglejoin[0]-2**8
        if anglejoin[1]>128:
            anglejoin[1]=anglejoin[1]-2**8
        if anglejoin[2]>128:
            anglejoin[2]=anglejoin[2]-2**8
        if anglejoin[3]>128:
            anglejoin[3]=anglejoin[3]-2**8
        if anglejoin[4]>128:
            anglejoin[4]=anglejoin[4]-2**8
        if anglejoin[5]>128:
            anglejoin[5]=anglejoin[5]-2**8
        
    ## MAX ANGLES ACCEPTED
    msg.ID = 80
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 0x64
    msg.DATA[1] = 0x64
    msg.DATA[2] = 0x19
    msg.DATA[3] = 0x64
    msg.DATA[4] = 0x64
    msg.DATA[5] = 0x19
    objPCAN.Write(PCAN_PCIBUS3,msg)
    
    ##  ASISTANCE
    msg.ID = 76
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 100
    msg.DATA[1] = 100
    msg.DATA[2] = 100
    msg.DATA[3] = 100
    msg.DATA[4] = 100
    msg.DATA[5] = 100
    objPCAN.Write(PCAN_PCIBUS3,msg)
    
#    tR1=time.time() - tR0
#    print("read end ",tR1)
    return anglejoin


def Footsensor(objPCAN,repeat):
    
    read=objPCAN.Read(PCAN_PCIBUS3)
    footsensored=0
    rheel = []
    rtoe = []
    lheel = []
    ltoe = []
    
    
    t0=time.time() 
    while time.time()-t0 < repeat:
        while read[0] != PCAN_ERROR_QRCVEMPTY: #32 = buffere empty
            if read[1].ID == 130:
                footsensored=read[1].DATA
                rheel=np.concatenate((rheel,footsensored[0]),axis=None)
                rtoe=np.concatenate((rtoe,footsensored[1]),axis=None)
                lheel=np.concatenate((lheel,footsensored[2]),axis=None)
                ltoe=np.concatenate((ltoe,footsensored[3]),axis=None)
#                voltage=footsensored[4]
            read=objPCAN.Read(PCAN_PCIBUS3)
#        rheel = footsensored[0]
#        rtoe = footsensored[1]
#        lheel = footsensored[2]
#        ltoe = footsensored[3]
        
    return rheel,rtoe,lheel,ltoe

def BatteryVoltage(objPCAN):
    
    read=objPCAN.Read(PCAN_PCIBUS3)
    sensored=0
    
    while read[0] != PCAN_ERROR_QRCVEMPTY: #32 = buffere empty
        if read[1].ID == 130:
            sensored=read[1].DATA
        read=objPCAN.Read(PCAN_PCIBUS3)
            
    if sensored !=0:
        voltage = sensored[4]
    else:
        voltage=np.nan  
        
    return voltage


def ExoState(objPCAN):
    
    readState=objPCAN.Read(PCAN_PCIBUS3)
    Satatesensored=0
    
    while readState[0] != PCAN_ERROR_QRCVEMPTY: #32 = buffere empty
        if readState[1].ID == 150:
            Satatesensored=readState[1].DATA
        readState=objPCAN.Read(PCAN_PCIBUS3)
    state = Satatesensored[0]

    return state

def ExoClose(objPCAN):
    
    ## POSITION CONTROL 
#    msg.ID = 0x048
#    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
#    msg.LEN = 6
#    msg.DATA[0] = 0
#    msg.DATA[1] = 0
#    msg.DATA[2] = 0
#    msg.DATA[3] = 0
#    msg.DATA[4] = 0
#    msg.DATA[5] = 0
#    objPCAN.Write(PCAN_PCIBUS3,msg)
#    
#    time.sleep(0.3)
    
    ## PASSIVE MODE
    msg.ID = 81
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 0
    msg.DATA[1] = 11
    msg.DATA[2] = 0
    msg.DATA[3] = 0
    msg.DATA[4] = 0
    msg.DATA[5] = 0
    objPCAN.Write(PCAN_PCIBUS3,msg)
    time.sleep(0.3)
    
    ## START/STOP CAN DATA
    msg.ID = 85
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 0x00
    msg.DATA[1] = 0x00
    msg.DATA[2] = 0x00
    msg.DATA[3] = 0x00
    msg.DATA[4] = 0x00
    msg.DATA[5] = 0x00
    objPCAN.Uninitialize(PCAN_NONEBUS)

def ExoWalk(objPCAN,speed):
    
    ## START/STOP CAN DATA
    msg.ID = 85
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 0x01
    msg.DATA[1] = 0x02
    msg.DATA[2] = 0x00
    msg.DATA[3] = 0x00
    msg.DATA[4] = 0x00
    msg.DATA[5] = 0x00
    objPCAN.Write(PCAN_PCIBUS3,msg)
    
    ##  ASISTANCE
    msg.ID = 76
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 10
    msg.DATA[1] = 10
    msg.DATA[2] = 10
    msg.DATA[3] = 10
    msg.DATA[4] = 10
    msg.DATA[5] = 10
    objPCAN.Write(PCAN_PCIBUS3,msg)
    
    #sWALK, SPEED 3
    msg.ID = 81 # Exo Command
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 0
    msg.DATA[1] = speed # Exo Command (pg:63)
    msg.DATA[2] = 0
    msg.DATA[3] = 0
    msg.DATA[4] = 0
    msg.DATA[5] = 0
    objPCAN.Write(PCAN_PCIBUS3,msg)
    
def StopWalk(objPCAN):
    #STOP WALK
    msg.ID = 81
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 0
    msg.DATA[1] = 0
    msg.DATA[2] = 0
    msg.DATA[3] = 0
    msg.DATA[4] = 0
    msg.DATA[5] = 0
    objPCAN.Write(PCAN_PCIBUS3,msg)
    
    time.sleep(0.3)
    
    ## START/STOP CAN DATA
    msg.ID = 85
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 0x01
    msg.DATA[1] = 0x02
    msg.DATA[2] = 0x00
    msg.DATA[3] = 0x00
    msg.DATA[4] = 0x00
    msg.DATA[5] = 0x00
    objPCAN.Write(PCAN_PCIBUS3,msg)
    
def Compliance(objPCAN):
     ## START/STOP CAN DATA
    msg.ID = 85
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 0x01
    msg.DATA[1] = 0x02
    msg.DATA[2] = 0x00
    msg.DATA[3] = 0x00
    msg.DATA[4] = 0x00
    msg.DATA[5] = 0x00
    objPCAN.Write(PCAN_PCIBUS3,msg)
    
    ## COMPLIANCE
    msg.ID = 81
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 0
    msg.DATA[1] = 12
    msg.DATA[2] = 0
    msg.DATA[3] = 0
    msg.DATA[4] = 0
    msg.DATA[5] = 0
    objPCAN.Write(PCAN_PCIBUS3,msg)

def Passive(objPCAN):
     ## START/STOP CAN DATA
    msg.ID = 85
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 0x01
    msg.DATA[1] = 0x02
    msg.DATA[2] = 0x00
    msg.DATA[3] = 0x00
    msg.DATA[4] = 0x00
    msg.DATA[5] = 0x00
    objPCAN.Write(PCAN_PCIBUS3,msg)
    
    ## PASIVE
    msg.ID = 81
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 0
    msg.DATA[1] = 11
    msg.DATA[2] = 0
    msg.DATA[3] = 0
    msg.DATA[4] = 0
    msg.DATA[5] = 0
    objPCAN.Write(PCAN_PCIBUS3,msg)    
    
def SitDown(objPCAN):
     ## START/STOP CAN DATA
    msg.ID = 85
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 0x01
    msg.DATA[1] = 0x02
    msg.DATA[2] = 0x00
    msg.DATA[3] = 0x00
    msg.DATA[4] = 0x00
    msg.DATA[5] = 0x00
    objPCAN.Write(PCAN_PCIBUS3,msg)
    #seat
    
    ## CONTROL TYPE
    msg.ID = 71
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 0x01
    msg.DATA[1] = 0x01
    msg.DATA[2] = 0x01
    msg.DATA[3] = 0x01
    msg.DATA[4] = 0x01
    msg.DATA[5] = 0x01
    objPCAN.Write(PCAN_PCIBUS3,msg)
    
    ## SIT-DOWN
    msg.ID = 81
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 0
    msg.DATA[1] = 22
    msg.DATA[2] = 0
    msg.DATA[3] = 0
    msg.DATA[4] = 0
    msg.DATA[5] = 0
    objPCAN.Write(PCAN_PCIBUS3,msg)
    
def StandUp(objPCAN):
     ## START/STOP CAN DATA
    msg.ID = 85
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 0x01
    msg.DATA[1] = 0x02
    msg.DATA[2] = 0x00
    msg.DATA[3] = 0x00
    msg.DATA[4] = 0x00
    msg.DATA[5] = 0x00
    objPCAN.Write(PCAN_PCIBUS3,msg)
    #seat
    
    ## CONTROL TYPE
    msg.ID = 71
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 0x01
    msg.DATA[1] = 0x01
    msg.DATA[2] = 0x01
    msg.DATA[3] = 0x01
    msg.DATA[4] = 0x01
    msg.DATA[5] = 0x01
    objPCAN.Write(PCAN_PCIBUS3,msg)
    
    ## SIT-DOWN
    msg.ID = 81
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 0
    msg.DATA[1] = 21
    msg.DATA[2] = 0
    msg.DATA[3] = 0
    msg.DATA[4] = 0
    msg.DATA[5] = 0
    objPCAN.Write(PCAN_PCIBUS3,msg)