

import numpy as np
import serial
import time
import crc8 as crc8
#import logging

from scipy import signal
from threading import Thread, Semaphore

from PCANBasic import TPCANMsg, PCAN_PCIBUS3, PCAN_MESSAGE_STANDARD, PCAN_ERROR_QRCVEMPTY

#from multiprocessing.pool import ThreadPool
#import multiprocessing
from EAST import EAST, EASTrec
#from EASTCopia import EAST, EASTrec
from EXO_H3 import Exo_H3, ReadAngle, Exo_move

#%%  TIME DEFINITION
fs_EMG = 64
timer_emg_get_sample = 0.0
timer_emg_get_sample_init = 0.0
sampling_period_emg  = 1/fs_EMG

recording_time_sec = 20
recording_time = recording_time_sec
timer_recording_time = 0.0
timer_trial = 0.0

timer_computing_exo = 0.0
timer_computing_exo = 0.0

#%%  EAST DEFINITION
PlotTime = 0.1
NumChEMG = 16
Fsamp = 2000
#NumCyc = 5
Mode_east = 0 #Always set to 0
#Offset = np.array([520, -710, -150, -480, -348, 328, -437,308])
Offset = np.array([4.39, 4.39, -150, -480, -348, 328, -437,308])
#[4.39, 4.39, 4.39, 4.39,
MVC = np.array([1337, 1337, 1281.046, 1542.164, 9891.648, 551.46])
SerialCOM = '/dev/ttyACM0'
data = np.array([])
ConvFact = float(0.000286*1000) 
bau = 921600
port = SerialCOM
                            #Conversion factor to get the signals in mV

# Stimulation parameters (to calculate CONFSTRING)
StimType = 3
StimFreq = 100
StimDur = 400

Time_stim_on = 1
Time_stim_off = 1
Time_tremor_detect_read = 1
Time_stim_tremor_win = 1

trial_sequence = 1
tremor_threshold = 1
tremor_thr_gain_1 = 1
tremor_thr_gain_2 = 1
tremor_time_rms = 1
tremor_detec_muscle = 1

Mode_NRG = 0
StimActCh = np.array([0,0,0,0,0,0,0,0])
StimAmpCh = np.array([0,0,0,0,0,0,0,0])                     #Stimulation Amplitude in mA. The closest value to the dataset is selected

##Fixed parameters, do not change
Resolution = np.array([2])                                  #Resolution in byte      
ConvFact = float(0.000286*1000)                             #Conversion factor to get the signals in mV
acq = int(PlotTime*NumChEMG*Fsamp*2)
Canalacq = int(acq/(2*NumChEMG))

cond = False
# Datasets for stimulation frequencies, durations and amplitudes
StimFreqDataSet = np.array([1,2,3,4,5,6,7,8,9,10,12,14,16,18,20,22,24,26,28,30,35,40,45,50,55,60,65,70,80,90,100])
StimDurDataSet = np.array([100,125,150,175,200,225,250,275,300,325,350,375,400,425,450,475,500,525,550,575,600,625,650,675,700,750,800,850,900,950,1000])
StimAmpDataSet = np.array([0.5,1,1.5,2,2.5,3,3.5,4,4.5,5,5.5,6,6.5,7,7.5,8,8.5,9,9.5,10,10.5,11,12,13,14,15,16,17,18,19,20])

#%% CONFSTRING GENERATOR

ConfString_length = 25
ConfString = np.zeros(ConfString_length).astype('uint8')

ConfString[0] = ConfString_length                        #Number of byte to send

# Switch case MODE
if Mode_east==0:
    ConfString[1] = int('00000000',2)
elif Mode_east==1:
    ConfString[1] = int('01000000',2)
elif Mode_east ==2:
    ConfString[1] = int('10000000',2)
else:
    ConfString[1] = int('00000000',2)    

# Switch case FSAMP
if Fsamp==16000:
    ConfString[1] = ConfString[1] + int('00110000',2)
elif Fsamp==8000:
    ConfString[1] = ConfString[1] + int('00100000',2)
elif Fsamp==4000:
    ConfString[1] = ConfString[1] + int('00010000',2)
elif Fsamp==2000:
    ConfString[1] = ConfString[1] + int('00000000',2)
else:
    ConfString[1] = ConfString[1] + int('00000000',2)

# Switch case NUMCHEMG
if NumChEMG==16:
    ConfString[1] = ConfString[1] + int('00001100',2)
elif NumChEMG==8:
    ConfString[1] = ConfString[1] + int('00001000',2)
elif NumChEMG==4:
    ConfString[1] = ConfString[1] + int('00000100',2)
elif NumChEMG==2:
    ConfString[1] = ConfString[1] + int('00000000',2)
else:
    ConfString[1] = ConfString[1] + int('00000000',2)

# Start data transfer by setting the GO bit = 1
ConfString[1] = ConfString[1] + 1

# Estimate the STIM ACTIVE CHAN byte
ConfString[2] = 0

for i in range(0, 7):
    ConfString[2] = ConfString[2] + StimActCh[i]*2**(i-1);

# Estimate the STIM FREQ AND TYPE byte
StimFreqIndex = 0
minValue = np.array([0])
Val = np.zeros(len(StimFreqDataSet))

for k in range(0,len(StimFreqDataSet)):

    Val[k] = abs(StimFreqDataSet[k]-StimFreq)

minValue = min(Val)
StimFreqIndex = Val.tolist().index(minValue)

ConfString[3] = (StimType*32 + StimFreqIndex) + 1;

# Estimate the STIM DURATION byte

StimDurIndex = 0
Val2 = np.zeros(len(StimDurDataSet))

for r in range(0,len(StimDurDataSet)):

    Val2[r] = abs(StimDurDataSet[r]-StimDur)
    
    
    minValue = min(Val2)
    StimDurIndex = Val2.tolist().index(minValue)
    
    ConfString[4] = StimDurIndex + 1

# Estimate the STIM AMP CH1-8 byte
Val3 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

for n in range(0,len(StimAmpDataSet)):
    Val3[n] = abs(StimAmpDataSet[n]-StimAmpCh[i])
    
for i in range(0, 8):
    
    StimAmpIndex =  0
    minValue = min(Val3)
    StimAmpIndex = Val3.index(minValue)
    ConfString[5+i] = StimAmpIndex + 1
    
ConfString[13] = Time_stim_off
ConfString[14] = Time_stim_on
ConfString[15] = Time_tremor_detect_read
ConfString[16] = Time_stim_tremor_win
ConfString[17] = trial_sequence
ConfString[18] = Mode_NRG
ConfString[19] = tremor_threshold
ConfString[20] = tremor_thr_gain_1
ConfString[21] = tremor_thr_gain_2
ConfString[22] = tremor_time_rms
ConfString[23] = tremor_detec_muscle



#ConfString[13] = compute_crc8(ConfString,initial_value = 0)
#ConfString[24] = crc8.fcn_crc8(ConfString[0:23])

ConfString[24] = crc8.fcn_crc8_ot(ConfString,24)#254
ConfString_out = bytes(ConfString)
#ConfString_aux=bytes([25,9,0,127,13,0,0,0,0,0,0,0,0,30,30,1,4,0,0,40,12,12,15,1,132])
#print(ConfString)
b, a = signal.butter(2,6/(2000/2.),btype='low')

c, d = signal.butter(2,[45/(2000/2.), 55/(2000/2.)],btype='bandstop')

#Canal1_raw= queue.Queue()
Canal1_raw = np.zeros(Canalacq)
Canal2_raw = np.zeros(Canalacq)
Canal3_raw = np.zeros(Canalacq)
Canal4_raw = np.zeros(Canalacq)

arraysize = Fsamp*2
chansize = int(Fsamp*PlotTime)
arraychsize = int(arraysize-chansize)

emgArray1 = np.zeros(arraysize)
emgArray2 = np.zeros(arraysize)
emgArray3 = np.zeros(arraysize)
emgArray4 = np.zeros(arraysize)



#Canal1 = []
#Canal2 = []

Canal1_Raw_Total = []
Canal2_Raw_Total = []
Canal3_Raw_Total = []
Canal4_Raw_Total = []

#NumMusclue= 2


#fase = np.zeros(NumMusclue, dtype=int)
#countOff = np.zeros(NumMusclue, dtype=int)
#    
#detectionOn = np.zeros(NumMusclue, dtype=int)
#detectionOff = np.zeros(NumMusclue, dtype=int)
##    timeOnset = np.zeros(NumChEMG)
##    timeOffset = np.zeros(NumChEMG)
#stillUp = np.zeros(NumChEMG)
#threshold = np.zeros(NumChEMG)
#thresholdOff = np.zeros(NumChEMG)
#periodOff = np.zeros(NumChEMG)
#
##features[th0, thff0, poff0 th1, thff1, poff1]
#
#threshold[0] = 0.08 #Ankle
#thresholdOff[0] = 0.08
#periodOff[0] = 0.1*Fsamp
##threshold[1] = features[3]#knee
##thresholdOff[1] = features[4]
##periodOff[1] = 0.1*Fsamp

#%%  MOVE EXO
            
# First Step Right leg
FS_Rhip_ang= np.array([2,4,7,10,12,14,16,18,20,21,22,23,24,25,26,27,27,27,28,28,29,29,30,30,30])
FS_Rknee_ang= np.array([2,4,7,10,13,17,21,26,31,38,43,47,50,50,47,41,33,25,19,13,9,7,6,5,5])
FS_Rankle_ang = np.array([4,2,0,-2,-5,-7,-9,-10,-11,-12,-12,-12,-11,-8,-3,1,5,7,8,8,7,6,6,6,5])
FS_Lhip_ang= np.array([0,0,0,0,0,0,0,0,-1,-1,-1,-2,-2,-3,-3,-4,-5,-6,-7,-8,-8,-9,-10,-12,-13])
FS_Lknee_ang = np.array([0,0,0,0,0,0,0,0,0,0,1,1,1,2,2,2,3,3,3,4,4,4,5,5,5])
FS_Lankle_ang = np.array([6,6,6,6,7,7,8,8,9,10,11,11,12,12,12,12,13,13,14,16,17,18,19,20,20])
            
# Stride begining with right leg
#Rhip_ang= np.array([30,29,28,26,24,22,20,18,16,14,12,10,8,6,4,2,0,-2,-3,-5,-6,-8,-9,-10,-11,-12,-13,-14,-15,-15,-14,-14,-13,-12,-11,-9,-6,-2,2,6,10,13,16,18,21,24,26,28,29,30,30])
#Rknee_ang = np.array([3,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,3,4,5,7,9,11,14,17,21,27,33,40,49,56,59,60,57,46,35,26,19,13,9,7,6,5,4])
#Rankle_ang = np.array([5,4,3,2,2,3,4,6,7,8,10,11,11,12,12,12,12,13,13,14,16,17,18,19,20,20,20,20,19,17,15,12,9,4,-1,-7,-12,-14,-12,-8,-3,1,5,7,8,8,7,6,6,6,6])
#Lhip_ang= np.array([-13,-13,-14,-14,-14,-15,-15,-14,-13,-11,-8,-5,-1,4,8,12,16,20,23,26,28,29,30,30,30,29,28,26,24,22,20,18,16,14,12,10,8,6,4,2,0,-2,-4,-6,-7,-9,-10,-11,-11,-12,-12])
#Lknee_ang= np.array([5,5,6,7,8,9,11,13,16,20,15,32,39,50,58,60,57,48,39,31,22,14,9,7,6,5,4,3,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,2,3,4])
#Lankle_ang = np.array([20,20,19,17,15,12,9,4,-1,-7,-11,-13,-12,-8,-3,1,5,7,8,8,7,6,6,6,6,5,4,3,3,2,3,4,6,7,8,10,11,11,12,12,12,12,13,13,14,16,17,18,19,20,20])

# Step by step
Rhip_rstep = np.array([-13,-14,-15,-15,-14,-14,-13,-12,-11,-9,-6,-2,2,6,10,13,16,18,21,24,26,28,29,30,30])
Rknee_rstep = np.array([5,7,9,11,14,17,21,27,33,40,49,56,59,60,57,46,35,26,19,13,9,7,6,5])
Rankle_rstep = np.array([20,20,19,17,15,12,9,4,-1,-7,-12,-14,-12,-8,-3,1,5,7,8,8,7,6,6,6,6])
Lhip_rstep = np.array([30,29,28,26,24,22,20,18,16,14,12,10,8,6,4,2,0,-2,-4,-6,-7,-9,-10,-11,-11])
Lknee_rstep = np.array([3,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,2,3,4,5])
Lankle_rstep = np.array([5,4,3,3,2,3,4,6,7,8,10,11,11,12,12,12,12,13,13,14,16,17,18,19,20])

Rhip_lstep = np.array([30,29,28,26,24,22,20,18,16,14,12,10,8,6,4,2,0,-2,-3,-5,-6,-8,-9,-10,-11,-12])
Rknee_lstep = np.array([4,3,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,3,4])
Rankle_lstep = np.array([5,4,3,2,2,3,4,6,7,8,10,11,11,12,12,12,12,13,13,14,16,17,18,19,20,20])
Lhip_lstep = np.array([-12,-12,-13,-13,-14,-14,-14,-15,-15,-14,-13,-11,-8,-5,-1,4,8,12,16,20,23,26,28,29,30])
Lknee_lstep = np.array([5,6,7,8,9,11,13,16,20,15,32,39,50,58,60,57,48,39,31,22,14,9,7,6,5])
Lankle_lstep = np.array([20,20,19,17,15,12,9,4,-1,-7,-11,-13,-12,-8,-3,1,5,7,8,8,7,6,6,6,6])

def exo_move(objPCAN, msg, sfprocess, sfMove):
    global rHip_Sent, rKnee_Sent, rAnkle_Sent, lHip_Sent, lKnee_Sent, lAnkle_Sent
#    global stepsize
 
    print("lets go")
    while sfprocess._value:
        print("in")
        sfMove.acquire() 
        print("moving")
        for stepsize in range(0,2): 
            
            if not stepsize:
#                print("L step: ")
#                stepsize = 1
                Rhip = Rhip_lstep
                Rknee = Rknee_lstep
                Rankle = Rankle_lstep
                Lhip = Lhip_lstep
                Lknee = Lknee_lstep
                Lankle = Lankle_lstep
                
            else:
#                print("R step: ")
#                stepsize = 0
                Rhip = Rhip_rstep
                Rknee = Rknee_rstep
                Rankle = Rankle_rstep
                Lhip = Lhip_rstep
                Lknee = Lknee_rstep
                Lankle = Lankle_rstep 
            
            for index_Step in range(0,len(Rhip)-1,1):
                msg.DATA[0] = Rhip[index_Step]
                msg.DATA[1] = Rknee[index_Step]
                msg.DATA[2] = Rankle[index_Step]
                msg.DATA[3] = Lhip[index_Step]
                msg.DATA[4] = Lknee[index_Step]
                msg.DATA[5] = Lankle[index_Step]
                objPCAN.Write(PCAN_PCIBUS3,msg)  
                
                rHip_Sent=np.concatenate((rHip_Sent,Rhip[index_Step]),axis=None)
                rKnee_Sent=np.concatenate((rKnee_Sent,Rknee[index_Step]),axis=None)
                rAnkle_Sent=np.concatenate((rAnkle_Sent,Rankle[index_Step]),axis=None)
                lHip_Sent=np.concatenate((lHip_Sent,Lhip[index_Step]),axis=None)
                lKnee_Sent=np.concatenate((lKnee_Sent,Lknee[index_Step]),axis=None)
                lAnkle_Sent=np.concatenate((lAnkle_Sent,Lankle[index_Step]),axis=None)
                time.sleep(0.1)
                
    

#%%  READ ANGLES

def readAngle(objPCAN,sfprocess,sfRead): 
    global rHip_Record, rKnee_Record, rAnkle_Record, lHip_Record, lKnee_Record, lAnkle_Record
    joinangle = 0
    rHip_Record = []
    rKnee_Record = []
    rAnkle_Record = []
    lHip_Record = []
    lKnee_Record = []
    lAnkle_Record = []
#    veces=0
#    condition = True
        
#    tR0 = time.time() 
#    while time.time() - tR0 < sec:
    while sfprocess._value:
            
        sfRead.acquire()
        
        read=objPCAN.Read(PCAN_PCIBUS3)
        
        while read[0] != PCAN_ERROR_QRCVEMPTY: #32 = buffere empty
            if read[1].ID == 110:
                joinangle=read[1].DATA
            read=objPCAN.Read(PCAN_PCIBUS3)
    
        anglejoin=np.array([int(joinangle[0]),int(joinangle[1]),int(joinangle[2]),int(joinangle[3]),
                            int(joinangle[4]),int(joinangle[5])]) 
        if joinangle != 0:
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
            
#            if (anglejoin[0] and anglejoin[1]) == 20:
#                veces=veces+1
#                print("veces: ",veces)
#                print("left hip " + str(anglejoin[3]) + "      /   "  + "right hip "+ str(anglejoin[0]))
#                print("left knee " + str(anglejoin[4]) + "      /   "  + "right knee "+ str(anglejoin[1]))
#                print("left ankle " + str(anglejoin[5]) + "      /   "  + "right ankle "+ str(anglejoin[2]))
                
        else:
            pass
        

#%%  EMG RECORD
    
    
def getData(t,sfprocess,sfMove,sfRead):
    global Canal1_Env_Total, Canal2_Env_Total, Canal3_Env_Total, Canal4_Env_Total
    global Canal1_Raw_Total, Canal2_Raw_Total, Canal3_Raw_Total, Canal4_Raw_Total, Onset_Total
#    global Canal1_Env_Total, Canal2_Env_Total, Canal1, Canal2, Canal1_Raw_Total, Canal2_Raw_Total
    Canal1 = []
    Canal2 = []
    Canal3 = []
    Canal4 = []
    Canal1_Raw_Total = []
    Canal2_Raw_Total = []
    Canal3_Raw_Total = []
    Canal4_Raw_Total = []
    
    with serial.Serial(port, bau, timeout=12) as serialComunication:
        serialComunication.write(ConfString_out)
        t_inicial = time.time()
        while time.time()-t_inicial < t:
            
            line = serialComunication.read(acq)
            try:
                k = 0
                c = 0
                info = [line[i:i+2] for i in range(0, len(line), 2)]  
                
                while k < (acq/2):
                    for j in range(0,NumChEMG,1):
                        if j == 0:
                            Canal1_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[0])/MVC[0]
                            Canal1_Raw_Total=np.concatenate((Canal1_Raw_Total,Canal1_raw[c]),axis=None)

                        elif j == 1:
                            Canal2_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
                            Canal2_Raw_Total=np.concatenate((Canal2_Raw_Total,Canal2_raw[c]),axis=None)
                            
                        elif j == 6:
                            Canal3_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
                            Canal3_Raw_Total=np.concatenate((Canal3_Raw_Total,Canal3_raw[c]),axis=None)
                            
                        elif j == 7:
                            Canal4_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
                            Canal4_Raw_Total=np.concatenate((Canal4_Raw_Total,Canal4_raw[c]),axis=None)

                        k=k+1 
                    c=c+1
                
                if not sfMove._value:
                    sfMove.release()#exo move
                    print("move")
                    
                if not sfRead._value:
                    sfRead.release()#read angles
                
                
                #envelope
                        #falta bloquear el acceso a Canal1_raw
                emgArray1[0:arraychsize] = emgArray1[chansize:arraysize]
                emgArray1[arraychsize:arraysize] = Canal1_raw   
                emgAbs=np.abs(emgArray1)
#                Canal1_noise = signal.filtfilt(c,d,emgAbs) 
                Canal1_env = signal.filtfilt(b,a,emgAbs)    
                Canal1 = Canal1_env[arraychsize:arraysize]
                
                
                emgArray2[0:arraychsize] = emgArray2[chansize:arraysize]
                emgArray2[arraychsize:arraysize] = Canal2_raw 
                emgAbs=np.abs(emgArray2)
#                Canal2_noise = signal.filtfilt(c,d,emgAbs)
                Canal2_env=signal.filtfilt(b,a,emgAbs)   
                Canal2 = Canal2_env[arraychsize:arraysize]
                
                
                emgArray3[0:arraychsize] = emgArray3[chansize:arraysize]
                emgArray3[arraychsize:arraysize] = Canal3_raw
                emgAbs=np.abs(emgArray3)
#                Canal3_noise = signal.filtfilt(c,d,emgAbs) 
                Canal3_env=signal.filtfilt(b,a,emgAbs)   
                Canal3 = Canal3_env[arraychsize:arraysize]
                
                
                emgArray4[0:arraychsize] = emgArray4[chansize:arraysize]
                emgArray4[arraychsize:arraysize] = Canal4_raw
                emgAbs=np.abs(emgArray4)
#                Canal4_noise = signal.filtfilt(c,d,emgAbs) 
                Canal4_env=signal.filtfilt(b,a,emgAbs)   
                Canal4 = Canal4_env[arraychsize:arraysize]
                
                
                Canal1_Env_Total=np.concatenate((Canal1_Env_Total,Canal1),axis=None)
                Canal2_Env_Total=np.concatenate((Canal2_Env_Total,Canal2),axis=None)
                Canal3_Env_Total=np.concatenate((Canal3_Env_Total,Canal3),axis=None)
                Canal4_Env_Total=np.concatenate((Canal4_Env_Total,Canal4),axis=None)

                
            except:
                pass

        sfprocess._value = 0
        try:
            ConfString=bytes([25,0,0,120,17,1,1,1,1,1,1,1,1,30,30,4,1,1,0,10,10,10,10,1,25]) 
            serialComunication.write(ConfString)
            serialComunication.close()
        except:
            raise NameError("ERROR: close serial port process")

           

#def integrate(y_vals, h):
#    i=1
#    total = y_vals[0] + y_vals[-1]
#    for y in y_vals[1:-1]:
#        if i % 2 ==0:
#            total += 2*y
#        else:
#            total += 4*y
#        i += 1
#    return total*(h/3.0)


#%%  CALL METODS
            
          
def EASTrecord(seconds):
    
    try:
        sfprocess = Semaphore(0) # semaforo de fin sincronizado de los threads
        sfMove = Semaphore(1) # movimiento del exo
        sfRead = Semaphore(1) # read exo angles
        sfexit = Semaphore(0) # break forzoso
        
        dataCollector = EAST(target = EASTrec, args = (sfprocess,sfMove,sfRead,sfexit,seconds)) 
        
        
        dataCollector.start() 
        
    #    t_inicial = time.time()
    #    while time.time()-t_inicial < seconds:
    #        pass
        
    #    sfprocess._value=0
        
    #    dataCollector.join()
        
        sfprocess.acquire()
        
        emg = dataCollector.join()
        
    #    emg2 = [Canal1_Raw_Total, Canal2_Raw_Total, Canal3_Raw_Total, Canal4_Raw_Total, 
    #            Canal1_Env_Total, Canal2_Env_Total, Canal3_Env_Total, Canal4_Env_Total]
    except KeyboardInterrupt:
        sfexit._value = 1
        emg = dataCollector.join()
        print("INTERRUT3 EAST")
    
    
    return emg




def EAST_Exorecord(seconds, objPCAN, assistance, stiffness):
    
    msg = TPCANMsg()
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.ID = 72
    msg.LEN = 6
    
    ## CONTROL TYPE (1:POSITION / 2:STIFFNESS / 3:TORQUE / 4:DISABLE / 5:STOPPED)
    controlType = 2
    msg3 = TPCANMsg() 
    msg3.ID = 71
    msg3.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg3.LEN = 6
    msg3.DATA[0] = controlType
    msg3.DATA[1] = controlType
    msg3.DATA[2] = controlType
    msg3.DATA[3] = controlType
    msg3.DATA[4] = controlType
    msg3.DATA[5] = controlType
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
    
    msg4 = TPCANMsg() 
    msg4.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg4.ID = 74 #STIFFNESS SET POINT
    msg4.LEN = 6
    msg4.DATA[0] = stiffness
    msg4.DATA[1] = stiffness
    msg4.DATA[2] = stiffness
    msg4.DATA[3] = stiffness
    msg4.DATA[4] = stiffness
    msg4.DATA[5] = stiffness
    objPCAN.Write(PCAN_PCIBUS3,msg4)
    
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
    
    try:
        sfprocess = Semaphore(0) # semaforo de fin sincronizado de los threads
        sfMove = Semaphore(0) # movimiento del exo
        sfRead = Semaphore(1) # read exo angles
        sfexit = Semaphore(0) # break forzoso
        
    #    dataCollector = Thread(target = getData, args = (repeat,sfprocess,sfMove,sfRead)) 
        dataCollector = EAST(target = EASTrec, args = (sfprocess,sfMove,sfRead,sfexit,seconds)) 
        anglefn = Exo_H3(target = ReadAngle, args = (objPCAN,sfprocess,sfRead,sfexit)) 
        exoMovement = Exo_H3(target = Exo_move, args = (objPCAN,msg,sfprocess,sfMove,sfexit)) 
        
        anglefn.start()
        exoMovement.start()
        dataCollector.start() 
        
    #    t_inicial = time.time()
    #    while time.time()-t_inicial < seconds:
    #        pass
        
    #    sfprocess._value = 0
        sfprocess.acquire()
        
        sfexit._value = 1
        sfMove.release()
        sfRead.release()
        
        anglesArray = anglefn.join()
        trajectories = exoMovement.join()
        emg = dataCollector.join()
        
    except KeyboardInterrupt:
        sfexit._value = 1
        sfMove.release()
        sfRead.release()
        anglesArray = anglefn.join()
        trajectories = exoMovement.join()
        emg = dataCollector.join()
        print("INTERRUT3")

    return emg, anglesArray, trajectories






def EAST_ExorecordE(repeat, objPCAN, assistance, stiffness):
#    global Canal1_Total, Canal2_Total, Canal3_Total, Canal4_Total
    global Canal1_Raw_Total, Canal2_Raw_Total, Canal3_Raw_Total, Canal4_Raw_Total
    global Canal1_Env_Total, Canal2_Env_Total, Canal3_Env_Total, Canal4_Env_Total
    global rHip_Record, rKnee_Record, rAnkle_Record, lHip_Record, lKnee_Record, lAnkle_Record
    global rHip_Sent, rKnee_Sent, rAnkle_Sent, lHip_Sent, lKnee_Sent, lAnkle_Sent
    
#    Canal1_Total = []
#    Canal2_Total = []
#    Canal3_Total = []  
#    Canal4_Total = []
    Canal1_Env_Total = []
    Canal2_Env_Total = []
    Canal3_Env_Total = []  
    Canal4_Env_Total = []
    
    
    rHip_Sent = []
    rKnee_Sent = []
    rAnkle_Sent = []
    lHip_Sent = []
    lKnee_Sent = []
    lAnkle_Sent = []
    
    msg = TPCANMsg()
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.ID = 72
    msg.LEN = 6
    
    ## CONTROL TYPE (1:POSITION / 2:STIFFNESS / 3:TORQUE / 4:DISABLE / 5:STOPPED)
    controlType = 2
    msg3 = TPCANMsg() 
    msg3.ID = 71
    msg3.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg3.LEN = 6
    msg3.DATA[0] = controlType
    msg3.DATA[1] = controlType
    msg3.DATA[2] = controlType
    msg3.DATA[3] = controlType
    msg3.DATA[4] = controlType
    msg3.DATA[5] = controlType
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
    
    msg4 = TPCANMsg() 
    msg4.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg4.ID = 74 #STIFFNESS SET POINT
    msg4.LEN = 6
    msg4.DATA[0] = stiffness
    msg4.DATA[1] = stiffness
    msg4.DATA[2] = stiffness
    msg4.DATA[3] = stiffness
    msg4.DATA[4] = stiffness
    msg4.DATA[5] = stiffness
    objPCAN.Write(PCAN_PCIBUS3,msg4)
    
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
    
#    areaArray1 = np.zeros(arraysize)
    sfprocess = Semaphore(1) # semaforo de fin sincronizado de los threads
    sfMove = Semaphore(1) # movimiento del exo
    sfRead = Semaphore(1) # read exo angles
    
    
    exoMovement = Thread(target = exo_move, args = (objPCAN,msg,sfprocess,sfMove)) 
    anglefn = Thread(target = readAngle, args = (objPCAN,sfprocess,sfRead))
    dataCollector = Thread(target = getData, args = (repeat,sfprocess,sfMove,sfRead)) 
    
    anglefn.start()
    exoMovement.start()
    dataCollector.start() 
    
    dataCollector.join()
#    anglefn.join()
    
#    Canal1_Raw_Total = Canal1_Raw_Total[400:-1]
#    Canal2_Raw_Total = Canal2_Raw_Total[400:-1]
#    Canal3_Raw_Total = Canal3_Raw_Total[400:-1]
#    Canal4_Raw_Total = Canal4_Raw_Total[400:-1]
#    
#    Canal1_Env_Total = Canal1_Env_Total[400:-1]
#    Canal2_Env_Total = Canal2_Env_Total[400:-1]
#    Canal3_Env_Total = Canal3_Env_Total[400:-1]
#    Canal4_Env_Total = Canal4_Env_Total[400:-1] 
    
    emg2 = [Canal1_Raw_Total, Canal2_Raw_Total, Canal3_Raw_Total, Canal4_Raw_Total, 
            Canal1_Env_Total, Canal2_Env_Total, Canal3_Env_Total, Canal4_Env_Total]
    anglesArray = [rHip_Record, rKnee_Record, rAnkle_Record, lHip_Record, lKnee_Record, lAnkle_Record]
    trajectories = [rHip_Sent, rKnee_Sent, rAnkle_Sent, lHip_Sent, lKnee_Sent, lAnkle_Sent]

#    interval= int(chansize/2)
#    for i in range (interval,np.size(Canal1_Env_Total),interval):
#        y = Canal1_Env_Total[i-interval:i]
#        
#        area = integrate(y, interval)
##        areaArray1[0:arraychsize] = areaArray1[chansize:arraysize]
#        areaArray1[i-interval:i] = area
        
    
#    return Canal1_Raw_Total, Canal2_Raw_Total, Canal1_Env_Total, Canal2_Env_Total
    return emg2, anglesArray, trajectories





