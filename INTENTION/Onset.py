#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 10:08:57 2021

@author: nrg
"""
import numpy as np
import time
import serial
from PCANBasic import TPCANMsg, PCAN_MESSAGE_STANDARD, PCAN_PCIBUS3
from scipy import signal
#from Gait_Model import steps

## EAST CONFIGURATION
fs_EMG = 64
PlotTime = 0.1
NumChEMG = 8
Fsamp = 2000

NumChTot = 16 
NumSamples = Fsamp * PlotTime  
    # COM buffer size
BufSize = Fsamp*PlotTime*2*NumChTot
SerialCOM = '/dev/ttyACM0'
ConvFact = float(0.000286*1000) 
ConfString=bytes([25,9,0,127,13,0,0,0,0,0,0,0,0,30,30,1,4,0,0,40,12,12,15,1,132])
#    Mode_east = 0 #Always set to 0
Offset = np.array([520, -710, -150, -480, -348, 328, -437,308])
MVC = np.array([1337, 1337, 1281.046, 1542.164, 9891.648, 551.46])


#%%  MOVE EXO


ankle_ang = np.array([0x00,0x03,0x06,0x09,0x0b,0x0e,0x10,0x13,0x16,0x18,0x19,0x1a,0x1b,0x1b,0x1b,0x1b,0x1a,0x19,0x18,0x16,0x15,0x13,0x10,0x0e,0x0b,0x08,0x06,0x03,0x00,-0x03,-0x06,-0x09,-0x0b,-0x0e,-0x10,-0x13,-0x14,-0x14,-0x15,-0x16,-0x16,-0x17,-0x17,-0x17,-0x16,-0x16,-0x15,-0x15,-0x14,-0x13,-0x10,-0x0e,-0x0b,-0x08,-0x06,-0x03,0x00])

ankle_angUP = np.array([0,3,6,9,11,14,16,18,20,22,25,26,27,27,27])
ankle_angUPOFF = np.array([27,27,27,26,25,24,22,21,19,16,14,11,8,6,3,0])
ankle_angDOWN = np.array([0,-3,-6,-9,-11,-14,-16,-18,-20,-22,-25,-26,-27,-27,-27])
ankle_angDOWNOFF = np.array([-27,-27,-27,-26,-25,-24,-22,-21,-19,-16,-14,-11,-8,-6,-3,0])

def exo_staticmove (msg,join,mode,objPCAN):
    
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.ID = 0x048
    msg.LEN = 6
    if join == "Ankle":
        if mode == "UP":
            for m in range(0,len(ankle_angUP),1):
                msg.DATA[0] = 80
                msg.DATA[1] = 85
                msg.DATA[2] = ankle_angUP[m]
#            msg.DATA[2] = 15 
                msg.DATA[3] = 80
                msg.DATA[4] = 85
                msg.DATA[5] = 0
#                result = objPCAN.Write(PCAN_PCIBUS3,msg)
                objPCAN.Write(PCAN_PCIBUS3,msg)
                time.sleep(0.1)

        if mode == "DOWN":
            for m in range(0,len(ankle_angUPOFF),1):
                msg.DATA[0] = 80
                msg.DATA[1] = 85
                msg.DATA[2] = ankle_angUPOFF[m]
#            msg.DATA[2] = 0 
                msg.DATA[3] = 80
                msg.DATA[4] = 85
                msg.DATA[5] = 0
                objPCAN.Write(PCAN_PCIBUS3,msg)
                time.sleep(0.1)
        
#    if join == "Knee":
#        if mode == "UP":
#            for m in range(0,len(knee_angUP),1):
#                msg.DATA[1] = knee_angUP[m]
##                time.sleep(0.1)_
#        if mode == "DOWN":
#            for m in range(0,len(knee_angUPOFF),1):
#                msg.DATA[1] = knee_angUPOFF[m] 
#        objPCAN.Write(PCAN_PCIBUS3,msg)   

Rhip_ang= np.array([30,29,28,26,24,22,20,18,16,14,12,10,8,6,4,2,0,-2,-3,-5,-6,-8,-9,-10,-11,-12,-13,-14,-15,-15,-14,-14,-13,-12,-11,-9,-6,-2,2,6,10,13,16,18,21,24,26,28,29,30,30])
Rknee_ang = np.array([3,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,3,4,5,7,9,11,14,17,21,27,33,40,49,56,59,60,57,46,35,26,19,13,9,7,6,5,4])
Rankle_ang = np.array([5,4,3,2,2,3,4,6,7,8,10,11,11,12,12,12,12,13,13,14,16,17,18,19,20,20,20,20,19,17,15,12,9,4,-1,-7,-12,-14,-12,-8,-3,1,5,7,8,8,7,6,6,6,6])
Lhip_ang= np.array([-13,-13,-14,-14,-14,-15,-15,-14,-13,-11,-8,-5,-1,4,8,12,16,20,23,26,28,29,30,30,30,29,28,26,24,22,20,18,16,14,12,10,8,6,4,2,0,-2,-4,-6,-7,-9,-10,-11,-11,-12,-12])
Lknee_ang= np.array([5,5,6,7,8,9,11,13,16,20,15,32,39,50,58,60,57,48,39,31,22,14,9,7,6,5,4,3,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,2,3,4])
Lankle_ang = np.array([20,20,19,17,15,12,9,4,-1,-7,-11,-13,-12,-8,-3,1,5,7,8,8,7,6,6,6,6,5,4,3,3,2,3,4,6,7,8,10,11,11,12,12,12,12,13,13,14,16,17,18,19,20,20])

def exo_Dinamicmove(objPCAN,msg):
    
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.ID = 72
    msg.LEN = 6
    for index_Step in range(0,len(Rhip_ang)-1,1):
        msg.DATA[0] = Rhip_ang[index_Step]
        msg.DATA[1] = Rknee_ang[index_Step]
        msg.DATA[2] = Rankle_ang[index_Step]
        msg.DATA[3] = Lhip_ang[index_Step]
        msg.DATA[4] = Lknee_ang[index_Step]
        msg.DATA[5] = Lankle_ang[index_Step]
        objPCAN.Write(PCAN_PCIBUS3,msg)  
        time.sleep(0.1)
        
def Onset_Detection(emg_values, fase=0, stillUp=0, countOff=0, threshold = 0.05, thresholdOff = 0.1, periodOff = 0.2*Fsamp, ferquency = Fsamp, NumSamples = 6):
    detectionOn = 0
    detectionOff = 0
#    time_detectionOn = 0
#    time_detectionOff = 0
#    periodTime=0 
    
#    print('DentroFun, countOff:',countOff)
    for d in range(0,np.size(emg_values)):
        if fase:
#            print('primer flag, emg_values:', emg_values[d],'thresholdOff:',thresholdOff)
#            detectionOn += 1
            if emg_values[d] < thresholdOff: #offset
                countOff += 1
#                print('BAJADA, countOff:',countOff)
#                print('periodOff:',periodOff)
                if countOff > periodOff:
#                    time_detectionOff = (d + periodTime)/ferquency
#                    print('DETECTED OFF', emg_values[d])
                    detectionOn = 0
                    stillUp = 0
                    detectionOff += 1
                    fase = 0
                    countOff = 0
            else:
                countOff = 0
#                print('Breack, countOff:',countOff)
            
        elif emg_values[d] >= threshold and emg_values[d] < 1023: #onset  
#            time_detectionOn.append((d + periodTime)/ferquency)
#            time_detectionOn = (d + periodTime)/ferquency
#            print('DETECTED ON', emg_values[d])
            detectionOn += 1
            stillUp = 1
            fase=1
            
#    return detectionOn, detectionOff, time_detectionOn, time_detectionOff, fase, countOff   
    return detectionOn, detectionOff, fase, stillUp, countOff


def PDetection(emg_values, fase=0, countOff=0, threshold = 0.05, thresholdOff = 0.1, periodOff = 0.2*Fsamp, ferquency = Fsamp, NumSamples = 6):
#    detectionOn = 0
#    detectionOff = 0
#    time_detectionOn = 0
#    time_detectionOff = 0
#    periodTime=0 
    
#    print('DentroFun, countOff:',countOff)
    for d in range(0,np.size(emg_values)):
        if fase:
#            print('primer flag, emg_values:', emg_values[d],'thresholdOff:',thresholdOff)
            if emg_values[d] < thresholdOff: #offset
                countOff += 1
                if countOff > periodOff:
#                    time_detectionOff = (d + periodTime)/ferquency
#                    detectionOff += 1
                    fase = 0
                    countOff = 0
            else:
                countOff = 0
            
        elif emg_values[d] >= threshold and emg_values[d] < 1023: #onset  
#            time_detectionOn.append((d + periodTime)/ferquency)
#            time_detectionOn = (d + periodTime)/ferquency
#            detectionOn += 1
            fase=1
            
    return fase


def Onset_Mode(objPCAN, repeat, assistance, features):
    
    NumCyc=int(repeat/0.1)
    NumMusclue=2
    b, a = signal.butter(2,6/(2000/2.),btype='low')
    
    # ONSET CONFIG
    fase = np.zeros(NumMusclue, dtype=int)
    countOff = np.zeros(NumMusclue, dtype=int)
#    Time_Total=[]


    acq = int(PlotTime*NumChEMG*Fsamp*2)
    Canalacq = int(acq/(2*NumChEMG))
    
#    ankle_ang = np.array([0x00,0x03,0x06,0x09,0x0b,0x0e,0x10,0x13,0x16,0x18,0x19,0x1a,0x1b,0x1b,0x1b,0x1b,0x1a,0x19,0x18,0x16,0x15,0x13,0x10,0x0e,0x0b,0x08,0x06,0x03,0x00,-0x03,-0x06,-0x09,-0x0b,-0x0e,-0x10,-0x13,-0x14,-0x14,-0x15,-0x16,-0x16,-0x17,-0x17,-0x17,-0x16,-0x16,-0x15,-0x15,-0x14,-0x13,-0x10,-0x0e,-0x0b,-0x08,-0x06,-0x03,0x00])

#    tam_ang = np.size(ankle_ang)
    
    detectionOn = np.zeros(NumMusclue, dtype=int)
    detectionOff = np.zeros(NumMusclue, dtype=int)
#    timeOnset = np.zeros(NumChEMG)
#    timeOffset = np.zeros(NumChEMG)
    stillUp = np.zeros(NumChEMG)
    threshold = np.zeros(NumChEMG)
    thresholdOff = np.zeros(NumChEMG)
    periodOff = np.zeros(NumChEMG)
    
    #features[th0, thff0, poff0 th1, thff1, poff1]
    
    threshold[0] = features[0] #Ankle
    thresholdOff[0] = features[1]
    periodOff[0] = 0.1*Fsamp
    threshold[1] = features[3]#knee
    thresholdOff[1] = features[4]
    periodOff[1] = 0.1*Fsamp
    
#    threshold[0] = 500 #Ankle
#    thresholdOff[0] = 200
#    periodOff[0] = 0.1*Fsamp
#    threshold[1] = 500#knee
#    thresholdOff[1] = 200
#    periodOff[1] = 0.1*Fsamp

#    Canal1_env =  np.zeros(tam_ang)
#    Canal2_env = np.zeros(tam_ang)
#    Canal3_env = np.zeros(tam_ang)

    Canal1_Env_Total=[]
    Canal2_Env_Total=[]

    Canal1_raw = np.zeros(Canalacq)
    Canal2_raw = np.zeros(Canalacq)

    Canal1_Total=[]
    Canal2_Total=[]

    arraysize = Fsamp*2
    chansize = int(Fsamp*PlotTime)
    arraychsize = int(arraysize-chansize)
    
    emgArray1 = np.zeros(arraysize)
    emgArray2 = np.zeros(arraysize)


    Onset_Total = [int]
    Onset_Muscle1 = [int]
    Onset_Muscle2 = [int]
#    data = np.array([])

    # COM settings and open
    bau = 921600
    port = SerialCOM
    try:
        s = serial.Serial(port, bau, timeout=12)   
        s.write(ConfString)
    except:
        raise NameError("ERROR: serial port connet")
        
    msg = TPCANMsg()
        
    ## TYPE CONTROL (1:POSITION / 2:STIFFNESS / 3:TORQUE / 4:DISABLE / 5:STOPPED)
    msg3 = TPCANMsg() 
    msg3.ID = 71
    msg3.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg3.LEN = 6
    msg3.DATA[0] = 1
    msg3.DATA[1] = 1
    msg3.DATA[2] = 1
    msg3.DATA[3] = 1
    msg3.DATA[4] = 1
    msg3.DATA[5] = 1
    objPCAN.Write(PCAN_PCIBUS3,msg3)
    
            ## MAX ANGLES ACCEPTED
    msg2 = TPCANMsg() 
    msg2.ID = 80
    msg2.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg2.LEN = 6
    msg2.DATA[0] = 100
    msg2.DATA[1] = 100
    msg2.DATA[2] = 25
    msg2.DATA[3] = 100
    msg2.DATA[4] = 100
    msg2.DATA[5] = 25
    objPCAN.Write(PCAN_PCIBUS3,msg2)
    
    msg1 = TPCANMsg() 
    msg1.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg1.ID = 76 #PERCENTAGE OF ASSISTANCE
    msg1.LEN = 6
    msg1.DATA[0] = assistance
    msg1.DATA[1] = assistance
    msg1.DATA[2] = assistance
    msg1.DATA[3] = assistance
    msg1.DATA[4] = assistance
    msg1.DATA[5] = assistance
    objPCAN.Write(PCAN_PCIBUS3,msg1)
    
    Stop_Run=False
    try:
        h=0
        while not Stop_Run:
            
            Sig = s.read(acq)
            k = 0
            c = 0
            info = [Sig[i:i+2] for i in range(0, len(Sig), 2)]  
            
            while k < (acq/2):
                for j in range(0,NumChEMG,1):
                    if j == 0:
                        Canal1_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[0])/MVC[0]
    #                        Canal1_EAST_Total=np.concatenate((Canal1_EAST_Total,Canal1_EAST[c]),axis=None)
    #                        Canal1_EAST_Total.append(Canal1_EAST[c])
                        Canal1_Total=np.concatenate((Canal1_Total,Canal1_raw[c]),axis=None)
            
                    elif j == 1:
                        Canal2_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
    #                        Canal2_EAST_Total.append(Canal2_EAST[c])
    #                        Canal2_EAST_Total=np.concatenate((Canal2_EAST_Total,Canal2_EAST[c]),axis=None)
                        Canal2_Total=np.concatenate((Canal2_Total,Canal2_raw[c]),axis=None)
                     
        #            elif j == 2:
        #                Canal3[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True))  - Offset[2])/MVC[2]
        #                Canal3_Total.append(Canal3[c])
    
                    k=k+1 
                c=c+1
            
#            c1R=Canal1_raw-np.mean(Canal1_raw)
#            Canal1_env=np.abs(np.imag(hilbert(c1R)))
                            
            emgArray1[0:arraychsize] = emgArray1[chansize:arraysize]
            emgArray1[arraychsize:arraysize] = Canal1_raw
            
            emgAbs=np.abs(emgArray1)
            Canal1_env=signal.filtfilt(b,a,emgAbs)
            
            emgArray2[0:arraychsize] = emgArray2[chansize:arraysize]
            emgArray2[arraychsize:arraysize] = Canal2_raw
            
            emgAbs=np.abs(emgArray2)
            Canal2_env=signal.filtfilt(b,a,emgAbs)
            

            Canal1 = Canal1_env[arraychsize:arraysize]
            Canal2 = Canal2_env[arraychsize:arraysize]
            if len(Canal1)>0 and len(Canal2)>0:
#                Canal1_Total=np.concatenate((Canal1_Total,Canal1_raw),axis=None)
#                Canal2_Total=np.concatenate((Canal2_Total,Canal2_raw),axis=None)
#                        Canal2_Total=np.concatenate((Canal2_Total,Canal2),axis=None)
                   #Onset detection fuction
#                periodTime=(h)*NumSamples
    #            print("C1", detectionOn[0])
                
#                    C1=Canal1[h]
#                    C2=Canal2[h]
#                    print(C1)
                detectionOn[0], detectionOff[0], fase[0], stillUp[0], countOff[0] = Onset_Detection(Canal1, 
                           fase[0], stillUp[0], countOff[0], threshold[0] , thresholdOff[0] , periodOff[0])
                
                detectionOn[1], detectionOff[1], fase[1], stillUp[1], countOff[1] = Onset_Detection(Canal2 , 
                           fase[1], stillUp[1], countOff[1], threshold[1] , thresholdOff[1] , periodOff[1])
                    
                if detectionOn[0] and detectionOn[1]:
                    exo_Dinamicmove(objPCAN,msg)
                    Onset_Total=np.concatenate((Onset_Total,[11]),axis=None)
                    print("Exo UP")
                    
                elif stillUp[0] and stillUp[1]:
                    print("keep")
                elif stillUp[0] and detectionOn[1]:
                    exo_Dinamicmove(objPCAN,msg)
                    Onset_Total=np.concatenate((Onset_Total,[11]),axis=None)
                    print("Exo UP")
                    
                elif detectionOn[0] and stillUp[1]:
                    exo_Dinamicmove(objPCAN,msg)
                    Onset_Total=np.concatenate((Onset_Total,[11]),axis=None)
                    print("Exo UP")

                else:
                    Onset_Total=np.concatenate((Onset_Total,[00]),axis=None)
#                    print("Exo DOWN")                
 
                    if detectionOn[0]:
                        Onset_Muscle1=np.concatenate((Onset_Muscle1,detectionOn[0]),axis=None)
                        print("muscle 1 UP")
    
                    elif not detectionOn[0]:
                        Onset_Muscle1=np.concatenate((Onset_Muscle1,detectionOn[0]),axis=None)
                        print("muscle 1 DOWN")
                        
                    if detectionOn[1]:
                        Onset_Muscle2=np.concatenate((Onset_Muscle2,detectionOn[1]),axis=None)
                        print("muscle 2 UP")
    
                    elif not detectionOn[1]:
                        Onset_Muscle2=np.concatenate((Onset_Muscle2,detectionOn[1]),axis=None)
                        print("muscle 2 DOWN")
                    

                    
            Canal1_Env_Total=np.concatenate((Canal1_Env_Total,Canal1_env[arraychsize:arraysize]),axis=None)
            Canal2_Env_Total=np.concatenate((Canal2_Env_Total,Canal2_env[arraychsize:arraysize]),axis=None)
#            Canal1_Env_Total=np.concatenate((Canal1_Env_Total,Canal1_env),axis=None)
#            Canal2_Env_Total=np.concatenate((Canal2_Env_Total,Canal2_env),axis=None)
           
#                    if len(Canal1)>0 and len(Canal2)<=0:
#    #                    Canal1_Total=np.concatenate((Canal1_Total,Canal1),axis=None)
#                        detectionOn[0], detectionOff[0], timeOnset[0], timeOffset[0], fase[0], countOff[0] = Detection(Canal1, fase[0], countOff[0], threshold[0] , thresholdOff[0] , periodOff[0])
#        
#                        if detectionOn[0]:
#                            exo_move(msg,"Ankle","UP")
#                        elif detectionOff[0]:
#                            exo_move(msg,"Ankle","DOWN")
#                            
#                    if len(Canal1)<=0 and len(Canal2)>0:  
#    #                    Canal2_Total=np.concatenate((Canal2_Total,Canal2),axis=None)
#                        detectionOn[1], detectionOff[1], timeOnset[1], timeOffset[1], fase[1], countOff[1] = Detection(Canal2, fase[1], countOff[1], threshold[1] , thresholdOff[1] , periodOff[1])
#        
#                        if detectionOn[1]:
#                            exo_move(msg,"Ankle","UP")
#                        elif detectionOff[1]:
#                            exo_move(msg,"Ankle","DOWN")
                    
                    
#                time.sleep(1)
            
                #    print("time:", t1)
#            
#                
#        t_Total = time.time() - t_inicio   
#        print("duracion:", t_Total)
#        print('deteccion On:',detectionOnTotal)
#        print('deteccion Off:',detectionOffTotal)
#            timer_trial = time.perf_counter()-timer_recording_time
#            Time_Total.append(timer_trial)
            if h>NumCyc:
                Stop_Run=True  
                print("Onset_Muscle1",Onset_Muscle1)
                print("Onset_Muscle2",Onset_Muscle2)
                print("Onset_Total",Onset_Total)
#                print("H",h, " NumCyc:",NumCyc)
#                print("t_Instan:",t_Instan)
#                print("t_Total:",Time_Total)
            h+=1
    except KeyboardInterrupt:
        Stop_Run=True
        print('interrupt')

        
    return Canal1_Total, Canal2_Total, Canal1_Env_Total, Canal2_Env_Total, Onset_Total
 