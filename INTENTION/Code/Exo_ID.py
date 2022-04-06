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
    msg.ID = 4
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = -25
    msg.DATA[1] = 0
    msg.DATA[2] = -25
    msg.DATA[3] = -25
    msg.DATA[4] = 0
    msg.DATA[5] = -25
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
    msg.ID = 230
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


def readAngle(objPCAN,repeat):
    
    joinangle = 0
    rHip_Record = 0
    rKnee_Record = 0
    rAnkle_Record = 0
    lHip_Record = 0
    lKnee_Record = 0
    lAnkle_Record = 0
    
   
    if repeat==0:
        read=objPCAN.Read(PCAN_PCIBUS3)
        
        while read[0] != PCAN_ERROR_QRCVEMPTY: #32 = buffere empty
            if read[1].ID == 110:
                joinangle=read[1].DATA
            read=objPCAN.Read(PCAN_PCIBUS3)
    
        anglejoin=np.array([int(joinangle[0]),int(joinangle[1]),int(joinangle[2]),int(joinangle[3]),
                            int(joinangle[4]),int(joinangle[5])]) 
        if joinangle != 0:
            #TimeStamp
#            recTime=datetime.now().time()
#            print("rec")
#            print("min: ", recTime.minute, " sec: ", recTime.second, " mls: ", recTime.microsecond)
            
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
                
            rHip_Record=int(anglejoin[0])
            rKnee_Record=int(anglejoin[1])
            rAnkle_Record=int(anglejoin[2])
            lHip_Record=int(anglejoin[3])
            lKnee_Record=int(anglejoin[4])
            lAnkle_Record=int(anglejoin[5])
    
    
    t0=time.time() 
    while time.time()-t0 < repeat:
        
        read=objPCAN.Read(PCAN_PCIBUS3)
        
        while read[0] != PCAN_ERROR_QRCVEMPTY: #32 = buffere empty
            if read[1].ID == 110:
                joinangle=read[1].DATA
            read=objPCAN.Read(PCAN_PCIBUS3)
    
        anglejoin=np.array([int(joinangle[0]),int(joinangle[1]),int(joinangle[2]),int(joinangle[3]),
                            int(joinangle[4]),int(joinangle[5])]) 
        if joinangle != 0:
            #TimeStamp
#            recTime=datetime.now().time()
#            print("rec")
#            print("min: ", recTime.minute, " sec: ", recTime.second, " mls: ", recTime.microsecond)
            
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
                
            rHip_Record=np.concatenate((rHip_Record,int(anglejoin[0])),axis=None)
            rKnee_Record=np.concatenate((rKnee_Record,int(anglejoin[1])),axis=None)
            rAnkle_Record=np.concatenate((rAnkle_Record,int(anglejoin[2])),axis=None)
            lHip_Record=np.concatenate((lHip_Record,int(anglejoin[3])),axis=None)
            lKnee_Record=np.concatenate((lKnee_Record,int(anglejoin[4])),axis=None)
            lAnkle_Record=np.concatenate((lAnkle_Record,int(anglejoin[5])),axis=None) 
                
        else:
            pass
        
    anglesArray = [rHip_Record, rKnee_Record, rAnkle_Record, lHip_Record, lKnee_Record, lAnkle_Record]
    
    return anglesArray

def JoinTorque(objPCAN,repeat):
    read=objPCAN.Read(PCAN_PCIBUS3)
    joinTorque=0
    rHip = []
    rKnee = []
    rAnkle = []
    lHip = []
    lKnee = []
    lAnkle = []
    
    t0=time.time() 
    while time.time()-t0 < repeat:
        while read[0] != PCAN_ERROR_QRCVEMPTY: #32 = buffere empty
            if read[1].ID == 120:#130=foot switch / 120=join Torque
                joinTorque=read[1].DATA
                rHip=np.concatenate((rHip,joinTorque[0]),axis=None)
                rKnee=np.concatenate((rKnee,joinTorque[1]),axis=None)
                rAnkle=np.concatenate((rAnkle,joinTorque[2]),axis=None)
                lHip=np.concatenate((lHip,joinTorque[3]),axis=None)
                lKnee=np.concatenate((lKnee,joinTorque[4]),axis=None)
                lAnkle=np.concatenate((lAnkle,joinTorque[5]),axis=None)
            read=objPCAN.Read(PCAN_PCIBUS3)
    torque=np.array([rHip,rKnee,rAnkle,lHip,lKnee,lAnkle])    
   
    return torque



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
            if read[1].ID == 130:#130=foot switch / 120=join Torque
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
    msg.DATA[0] = 0
    msg.DATA[1] = 0
    msg.DATA[2] = 0
    msg.DATA[3] = 0
    msg.DATA[4] = 0
    msg.DATA[5] = 0
    objPCAN.Uninitialize(PCAN_NONEBUS)

def ExoWalk(objPCAN,speed):
    
    ## START/STOP CAN DATA
    msg.ID = 85
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 1
    msg.DATA[1] = 2
    msg.DATA[2] = 0
    msg.DATA[3] = 0
    msg.DATA[4] = 0
    msg.DATA[5] = 0
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
    msg.DATA[0] = 1
    msg.DATA[1] = 2
    msg.DATA[2] = 0
    msg.DATA[3] = 0
    msg.DATA[4] = 0
    msg.DATA[5] = 0
    objPCAN.Write(PCAN_PCIBUS3,msg)
    
def Compliance(objPCAN):
     ## START/STOP CAN DATA
    msg.ID = 85
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 1
    msg.DATA[1] = 2
    msg.DATA[2] = 0
    msg.DATA[3] = 0
    msg.DATA[4] = 0
    msg.DATA[5] = 0
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
    msg.DATA[0] = 1
    msg.DATA[1] = 2
    msg.DATA[2] = 0
    msg.DATA[3] = 0
    msg.DATA[4] = 0
    msg.DATA[5] = 0
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
    msg.DATA[0] = 1
    msg.DATA[1] = 2
    msg.DATA[2] = 0
    msg.DATA[3] = 0
    msg.DATA[4] = 0
    msg.DATA[5] = 0
    objPCAN.Write(PCAN_PCIBUS3,msg)
    #seat
    
    ## CONTROL TYPE
    msg.ID = 71
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 1
    msg.DATA[1] = 1
    msg.DATA[2] = 1
    msg.DATA[3] = 1
    msg.DATA[4] = 1
    msg.DATA[5] = 1
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
    msg.DATA[0] = 1
    msg.DATA[1] = 2
    msg.DATA[2] = 0
    msg.DATA[3] = 0
    msg.DATA[4] = 0
    msg.DATA[5] = 0
    objPCAN.Write(PCAN_PCIBUS3,msg)
    #seat
    
    ## CONTROL TYPE
    msg.ID = 71
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    msg.DATA[0] = 1
    msg.DATA[1] = 1
    msg.DATA[2] = 1
    msg.DATA[3] = 1
    msg.DATA[4] = 1
    msg.DATA[5] = 1
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