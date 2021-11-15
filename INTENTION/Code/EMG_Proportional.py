#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 13:51:59 2021

@author: nrg
"""
import numpy as np
#import time
from Onset import PDetection
from PCANBasic import TPCANMsg, PCAN_MESSAGE_STANDARD, PCAN_PCIBUS3
import serial
import time
from scipy import signal

fs_EMG = 64
PlotTime = 0.1
NumChEMG = 8
Fsamp = 2000

msg = TPCANMsg()
msg1 = TPCANMsg()
msg2 = TPCANMsg()

    # COM settings and open
ConvFact = float(0.000286*1000) 
ConfString=bytes([25,9,0,127,13,0,0,0,0,0,0,0,0,30,30,1,4,0,0,40,12,12,15,1,132])
acq = int(PlotTime*NumChEMG*Fsamp*2)
Canalacq = int(acq/(2*NumChEMG))

bau = 921600
SerialCOM = '/dev/ttyACM0'
port = SerialCOM
s = serial.Serial(port, bau, timeout=12)

#    Mode_east = 0 #Always set to 0
Offset = np.array([520, -710, -150, -480, -348, 328, -437,308])
MVC = np.array([1337, 1337, 1281.046, 1542.164, 9891.648, 551.46])
ankle_ang = np.array([0x00,0x03,0x06,0x09,0x0b,0x0e,0x10,0x13,0x16,0x18,0x19,0x1a,0x1b,0x1b,0x1b,0x1b,0x1a,0x19,0x18,0x16,0x15,0x13,0x10,0x0e,0x0b,0x08,0x06,0x03,0x00,-0x03,-0x06,-0x09,-0x0b,-0x0e,-0x10,-0x13,-0x14,-0x14,-0x15,-0x16,-0x16,-0x17,-0x17,-0x17,-0x16,-0x16,-0x15,-0x15,-0x14,-0x13,-0x10,-0x0e,-0x0b,-0x08,-0x06,-0x03,0x00])

tam_ang = np.size(ankle_ang)  





def Proportional(repeat,objPCAN):
    
    NumCyc=int(repeat/0.1)
    b, a = signal.butter(2,6/(2000/2.),btype='low')
    
    Canal1_env =  np.zeros(tam_ang)
    Canal2_env = np.zeros(tam_ang)
    #    Canal3_env = np.zeros(tam_ang)
    
    Canal1_env_Inter = []
    Canal2_env_Inter = []
    
    Canal1_raw = np.zeros(Canalacq)
    Canal2_raw = np.zeros(Canalacq)
    
    Canal1_Total = []
    Canal2_Total = []

    arraysize = Fsamp*2
    chansize = int(Fsamp*PlotTime)
    arraychsize = int(arraysize-chansize)
    
    emgArray1 = np.zeros(arraysize)
    emgArray2 = np.zeros(arraysize)
    
#    NumMusclue=2
    
#    detectionOn = np.zeros(NumMusclue, dtype=int)
#    detectionOff = np.zeros(NumMusclue, dtype=int)
#    timeOnset = np.zeros(NumChEMG)
#    timeOffset = np.zeros(NumChEMG)
    threshold = np.zeros(NumChEMG)
    thresholdOff = np.zeros(NumChEMG)
    periodOff = np.zeros(NumChEMG)
    
#    detectionOn = np.zeros(NumMusclue, dtype=int)
#    detectionOff = np.zeros(NumMusclue, dtype=int)
#    timeOnset = np.zeros(NumMusclue)
#    timeOffset = np.zeros(NumMusclue)
    fase = np.zeros(NumChEMG, dtype=int)
    countOff = np.zeros(NumChEMG, dtype=int)
    
    threshold[0] = 0.12 #Ankle
    thresholdOff[0] = 200
    threshold[1] = 500#knee
    thresholdOff[1] = 200
    
    periodOff[0] = 2
    periodOff[1] = 2

    total_angle = []
    contAngle = 0

    valormin = 1
    valomax = 30
    ref_ang = 30
    contMAV = 0 

    s.write(ConfString)
    
#        timeLineSpace=np.arange(0,NumCyc,1/NumSamples)
#        TimeP = timeLineSpace*PlotTime
    Stop_Run=False
    try:
        h=0
#        t_inicio=time.time()   
        #NumCyc      
        while not Stop_Run:
            
#                h = h+1    
#            t0=time.time()   
            
            ## Recive Data
            k = 0
            c = 0
#            start_comp_time = time.perf_counter()
            Sig = s.read(acq)
            info = [Sig[i:i+2] for i in range(0, len(Sig), 2)]    
            
            while k < (acq/2):
        
                
                for j in range(0,NumChEMG,1):
                    
                    if j == 0:
                        Canal1_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[0])/MVC[0]                     
                               
                    elif j == 1:
                        Canal2_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1])/MVC[1]

                    k=k+1 
                c=c+1


            Canal1_Total=np.concatenate((Canal1_Total,Canal1_raw),axis=None)
            Canal2_Total=np.concatenate((Canal2_Total,Canal2_raw),axis=None)
            
            
            emgArray1[0:arraychsize] = emgArray1[chansize:arraysize]
            emgArray1[arraychsize:arraysize] = Canal1_raw
            
            emgAbs=np.abs(emgArray1)
            Canal1_env=signal.filtfilt(b,a,emgAbs)
            
            emgArray2[0:arraychsize] = emgArray2[chansize:arraysize]
            emgArray2[arraychsize:arraysize] = Canal2_raw
            
            emgAbs=np.abs(emgArray2)
            Canal2_env=signal.filtfilt(b,a,emgAbs)
            
            
            
            for window in range(0,len(Canal1_raw),4):
                Canal1_env = np.sqrt((np.mean(Canal1_raw[window:window+4]))**2)
                Canal2_env = np.sqrt((np.mean(Canal2_raw[window:window+4]))**2)
                    

                Canal1_env_Inter=np.concatenate((Canal1_env_Inter,Canal1_env),axis=None)
                Canal2_env_Inter=np.concatenate((Canal2_env_Inter,Canal2_env),axis=None)

            

            Canal1=Canal1_env_Inter
#            Canal2=Canal2_env_Inter
            Canal1_Total=np.concatenate((Canal1_Total,Canal1),axis=None)
               #Onset detection fuction
            Canal1_env_Inter=Canal1   
            
            fase[0] = PDetection(Canal1_env_Inter, fase[0], countOff[0],
                       threshold[0] , thresholdOff[0] , periodOff[0])
       
            if fase[0]:
                control= sum(abs(Canal1_env_Inter))/len(Canal1_env_Inter)
                angle=round((control-valormin)*(ref_ang/(valomax-valormin)))
                contMAV=contMAV+1
                if angle<=ref_ang and angle>=0:
#                    total_angle.append(angle)
                    total_angle=np.concatenate((total_angle,angle),axis=None)
#                    total_angle
                    contAngle=contAngle+1
#                    sended=angle
#                    msg.ID = 0x048
#                    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
#                    msg.LEN = 6
#                    msg.DATA[0] = 90
#                    msg.DATA[1] = 80
#                    msg.DATA[2] = angle
#                    msg.DATA[3] = 90
#                    msg.DATA[4] = 90
#                    msg.DATA[5] = 80
#                    objPCAN.Write(PCAN_PCIBUS3,msg) 
            
#            timer_trial = time.perf_counter()-timer_recording_time
            
#            comp_time = np.append(comp_time,(time.perf_counter()-start_comp_time))
#            timer_trial = time.perf_counter()-timer_recording_time
#            timer_emg_get_sample = time.perf_counter()-timer_emg_get_sample_init
#            t1=time.time() - t0
            Canal1_Total=np.concatenate((Canal1_Total,Canal1),axis=None)
            if h>NumCyc:
                print("H",h)
                Stop_Run=True  
            h+=1
            
        return total_angle
    except KeyboardInterrupt:
        Stop_Run=True
        print('interrupt')
        
        
        
        
        
def ProportionalAnkle(repeat,objPCAN,onsetTH,offsetTH,valomax,valormin):

    
#    fs_EMG = 64
    PlotTime = 0.1
    NumChEMG = 8
    Fsamp = 2000
    NumCyc=int(repeat/0.1)
#    Fsamp = 1000
##    NumCyc=int(repeat/0.05)
    b, a = signal.butter(2,6/(2000/2.),btype='low')

    Offset = np.array([520, -710, -150, -480, -348, 328, -437,308])
    MVC = np.array([1337, 1337, 1281.046, 1542.164, 9891.648, 551.46])
    
    try:
        s = serial.Serial(port, bau, timeout=12)    
    except:
        raise NameError("ERROR: serial port connet")
    
    # ConfString 1000 hz
#    ConfString=bytes([25,9,0,127,13,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,254])
    # ConfString 2000 hz
    ConfString=bytes([25,9,0,127,13,0,0,0,0,0,0,0,0,30,30,1,4,0,0,40,12,12,15,1,132])
    s.write(ConfString)

    
    acq = int(PlotTime*NumChEMG*Fsamp*2)
    Canalacq = int(acq/(2*NumChEMG))
#    tam_ang=50
#    Time_emg = np.linspace(0,((Canalacq*tam_ang*repeat)/Fsamp),Canalacq*tam_ang*repeat)
    
   
    Canal1_Raw_Total = []
    Canal2_Raw_Total = []
    
    Canal1_Env_Total=[]
    Canal2_Env_Total=[]

#    Canal1_env_Inter = []
#    Canal2_env_Inter = []
    
    Canal1_raw = np.zeros(Canalacq)
    Canal2_raw = np.zeros(Canalacq)
    
    arraysize = Fsamp*2
    chansize = int(Fsamp*PlotTime)
    arraychsize = int(arraysize-chansize)
    
    emgArray1 = np.zeros(arraysize)
    emgArray2 = np.zeros(arraysize)
    
    threshold = np.zeros(NumChEMG)
    thresholdOff = np.zeros(NumChEMG)
    periodOff = np.zeros(NumChEMG)
    
    fase = np.zeros(NumChEMG, dtype=int)
    countOff = np.zeros(NumChEMG, dtype=int)
    
    total_angle = []
    
    threshold[0] = onsetTH #Ankle
    thresholdOff[0] = offsetTH
    threshold[1] = 180#knee
    thresholdOff[1] = 100
    
    periodOff[0] = 0.2*Fsamp
    periodOff[1] = 0.2*Fsamp

    contAngle = 0

#    valormin = 30
#    valomax = 475
    ref_ang = 30
    contMAV = 0 
          
     
    msg.ID = 72
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.LEN = 6
    
    msg1.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg1.ID = 76 #PERCENTAGE OF ASSISTANCE
    msg1.LEN = 6
    msg1.DATA[0] = 100
    msg1.DATA[1] = 100
    msg1.DATA[2] = 100
    msg1.DATA[3] = 100
    msg1.DATA[4] = 100
    msg1.DATA[5] = 100
    objPCAN.Write(PCAN_PCIBUS3,msg1)
    
        ## TYPE CONTROL (1:POSITION / 2:STIFFNESS (admitance) / 3:TORQUE / 4:DISABLE / 5:STOPPED)
    msg2.ID = 71
    msg2.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg2.LEN = 6
    msg2.DATA[0] = 1
    msg2.DATA[1] = 1
    msg2.DATA[2] = 1
    msg2.DATA[3] = 1
    msg2.DATA[4] = 1
    msg2.DATA[5] = 1
    objPCAN.Write(PCAN_PCIBUS3,msg2)
    
#    start_comp_time = time.perf_counter()

    
    Stop_Run=False
    h=0
    t_inicio=time.time() 
    while not Stop_Run:
#            print("total Canal 1",len(Canal1_EAST_Total), " total Canal 2",len(Canal2_EAST_Total))
        t_inicio_medio=time.time() 
        Sig = s.read(acq)
        k = 0
        c = 0
        info = [Sig[i:i+2] for i in range(0, len(Sig), 2)]  
        
        while k < (acq/2):
            for j in range(0,NumChEMG,1):
                if j == 0:
                    Canal1_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[0])/MVC[0]
#                        Canal1_EAST_Total=np.concatenate((Canal1_EAST_Total,Canal1_EAST[c]),axis=None)
                    
                elif j == 1:
                    Canal2_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
#                        Canal2_EAST_Total=np.concatenate((Canal2_EAST_Total,Canal2_EAST[c]),axis=None)
                    
                
    #            elif j == 2:
    #                Canal3[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True))  - Offset[2])/MVC[2]
#                    Canal3_Raw_Total=np.concatenate((Canal3_Raw_Total,Canal3_raw[c]),axis=None)

                k=k+1 
            c=c+1

        Canal1_Raw_Total=np.concatenate((Canal1_Raw_Total,Canal1_raw),axis=None)
        Canal2_Raw_Total=np.concatenate((Canal2_Raw_Total,Canal2_raw),axis=None)

        
        
        emgArray1[0:arraychsize] = emgArray1[chansize:arraysize]
        emgArray1[arraychsize:arraysize] = Canal1_raw
        
        emgAbs=np.abs(emgArray1)
        Canal1_env=signal.filtfilt(b,a,emgAbs)
        
        emgArray2[0:arraychsize] = emgArray2[chansize:arraysize]
        emgArray2[arraychsize:arraysize] = Canal2_raw
        
        emgAbs=np.abs(emgArray2)
        Canal2_env=signal.filtfilt(b,a,emgAbs)
            
            
#        c2R=Canal2_raw-np.mean(Canal2_raw)
#        Canal2_env=np.abs(np.imag(hilbert(c2R)))
        
                
        t_Instan = time.time() - t_inicio_medio 
        
        Canal1 = Canal1_env[arraychsize:arraysize]

        fase[0] = PDetection(Canal1, fase[0], countOff[0],
           threshold[0] , thresholdOff[0] , periodOff[0])
       
        if fase[0]:
            control= sum(abs(Canal1))/len(Canal1)
            angle=round((control-valormin)*(ref_ang/(valomax-valormin)))
            contMAV=contMAV+1
            if angle<=ref_ang and angle>=0:
                total_angle=np.concatenate((total_angle,angle),axis=None)
                contAngle=contAngle+1
                #exoMove
                
                msg.DATA[0] = 90
                msg.DATA[1] = 80
                msg.DATA[2] = angle
                msg.DATA[3] = 90
                msg.DATA[4] = 90
                msg.DATA[5] = 80
                objPCAN.Write(PCAN_PCIBUS3,msg) 


        Canal1_Env_Total=np.concatenate((Canal1_Env_Total,Canal1_env[arraychsize:arraysize]),axis=None)
        Canal2_Env_Total=np.concatenate((Canal2_Env_Total,Canal2_env[arraychsize:arraysize]),axis=None)
        
        
        if h>NumCyc:
            Stop_Run=True  
            t_Total = time.time() - t_inicio 
#                    print("H",h, " NumCyc:",NumCyc)
            print("t_Instan:",t_Instan)
            print("t_Total:",t_Total)
        
        h+=1
        
    try:
        ConfString=bytes([25,0,0,120,17,1,1,1,1,1,1,1,1,30,30,4,1,1,0,10,10,10,10,1,25]) 
        s.write(ConfString)
        s.close()
    except:
        raise NameError("ERROR: close serial port process")
        
    return Canal1_Raw_Total, Canal2_Raw_Total, Canal1_Env_Total, Canal2_Env_Total, total_angle