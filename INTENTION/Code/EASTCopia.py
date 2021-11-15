
import numpy as np
import serial
import crc8 as crc8
import time

from scipy import signal
from threading import Thread
#from threading import Thread, Semaphore

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
NumChEMG = 8
Fsamp = 2000
#NumCyc = 5
Mode_east = 0 #Always set to 0
Offset = np.array([520, -710, -150, -480, -348, 328, -437,308])
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

# Filter components
b, a = signal.butter(2,6/(2000/2.),btype='low')
c, d = signal.butter(2,[45/(2000/2.), 55/(2000/2.)],btype='bandstop')

#Canal1_raw= queue.Queue()
Canal1_raw = np.zeros(Canalacq)
Canal2_raw = np.zeros(Canalacq)
Canal3_raw = np.zeros(Canalacq)
Canal4_raw = np.zeros(Canalacq)
Canal5_raw = np.zeros(Canalacq)
Canal6_raw = np.zeros(Canalacq)
Canal7_raw = np.zeros(Canalacq)
Canal8_raw = np.zeros(Canalacq)
Canal9_raw = np.zeros(Canalacq)
Canal10_raw = np.zeros(Canalacq)
Canal11_raw = np.zeros(Canalacq)
Canal12_raw = np.zeros(Canalacq)
#Canal13_raw = np.zeros(Canalacq)
#Canal14_raw = np.zeros(Canalacq)

arraysize = Fsamp*2
chansize = int(Fsamp*PlotTime)
arraychsize = int(arraysize-chansize)

emgArray1 = np.zeros(arraysize)
emgArray2 = np.zeros(arraysize)
emgArray3 = np.zeros(arraysize)
emgArray4 = np.zeros(arraysize)
emgArray5 = np.zeros(arraysize)
emgArray6 = np.zeros(arraysize)
emgArray7 = np.zeros(arraysize)
emgArray8 = np.zeros(arraysize)
emgArray9 = np.zeros(arraysize)
emgArray10 = np.zeros(arraysize)
emgArray11 = np.zeros(arraysize)
emgArray12 = np.zeros(arraysize)
#emgArray13 = np.zeros(arraysize)
#emgArray14 = np.zeros(arraysize)

NumMusclue = NumChEMG
#NumMusclue = 12

sg_delete=300 #muestras que eliminar de guarda 
c1 = 0
c2 = 1
c3 = 6 
c4 = 7
#c5 = 8
#c6 = 9
#c7 = 10 
#c8 = 11
#c9 = 12
#c10 = 13
#c11 = 14
#c12 = 15
#c13 = 16
#c14 = 15



#%% EAST RECORD


# rec moviendo exo / sin exo
def EASTrec(sfprocess,sfMove, sfRead, sfexit, repeat):
    global Canal1_Raw_Total
    emg = []
    
    Canal1 = []
    Canal2 = []
    Canal3 = []
    Canal4 = []
#    Canal5 = []
#    Canal6 = []
#    Canal7 = []
#    Canal8 = []
#    Canal9 = []
#    Canal10 = []
#    Canal11 = []
#    Canal12 = []
#    Canal13 = []
#    Canal14 = []
    
    Canal1_Raw_Total = []
    Canal2_Raw_Total = []
    Canal3_Raw_Total = []
    Canal4_Raw_Total = []
#    Canal5_Raw_Total = []
#    Canal6_Raw_Total = []
#    Canal7_Raw_Total = []
#    Canal8_Raw_Total = []
#    Canal9_Raw_Total = []
#    Canal10_Raw_Total = []
#    Canal11_Raw_Total = []
#    Canal12_Raw_Total = []
#    Canal13_Raw_Total = []
#    Canal14_Raw_Total = []
    
    Canal1_Env_Total = []
    Canal2_Env_Total = []
    Canal3_Env_Total = []  
    Canal4_Env_Total = []
#    Canal5_Env_Total = []
#    Canal6_Env_Total = []
#    Canal7_Env_Total = []  
#    Canal8_Env_Total = []
#    Canal9_Env_Total = []
#    Canal10_Env_Total = []
#    Canal11_Env_Total = []
#    Canal12_Env_Total = []
#    Canal13_Env_Total = []  
#    Canal14_Env_Total = []

    
    with serial.Serial(port, bau, timeout=12) as serialComunication:
        serialComunication.write(ConfString_out)
#        print("EMG Start")
#        while sfprocess._value:
        try:
            t_inicial = time.time()
            while time.time()-t_inicial < repeat:
    #        for h in range(0,repeat*10):
                if sfexit._value:
                    break
                
                line = serialComunication.read(acq)
                try:
                    k = 0
                    c = 0
                    info = [line[i:i+2] for i in range(0, len(line), 2)]  
    
                    
                    while k < (acq/2):
                        for j in range(0,NumMusclue,1):
                            if j == c1:
                                Canal1_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[0])/MVC[0]
                                Canal1_Raw_Total=np.concatenate((Canal1_Raw_Total,Canal1_raw[c]),axis=None)
            
                            elif j == c2:
                                Canal2_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
                                Canal2_Raw_Total=np.concatenate((Canal2_Raw_Total,Canal2_raw[c]),axis=None)
                                
                            elif j == c3:
                                Canal3_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
                                Canal3_Raw_Total=np.concatenate((Canal3_Raw_Total,Canal3_raw[c]),axis=None)
                                
                            elif j == c4:
                                Canal4_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
                                Canal4_Raw_Total=np.concatenate((Canal4_Raw_Total,Canal4_raw[c]),axis=None)
#            
#                            elif j == c5:
#                                Canal5_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
#                                Canal5_Raw_Total=np.concatenate((Canal5_Raw_Total,Canal5_raw[c]),axis=None)
#                                
#                            elif j == c6:
#                                Canal6_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
#                                Canal6_Raw_Total=np.concatenate((Canal6_Raw_Total,Canal6_raw[c]),axis=None)
#                                
#                            elif j == c7:
#                                Canal7_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[0])/MVC[0]
#                                Canal7_Raw_Total=np.concatenate((Canal7_Raw_Total,Canal7_raw[c]),axis=None)
#            
#                            elif j == c8:
#                                Canal8_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
#                                Canal8_Raw_Total=np.concatenate((Canal8_Raw_Total,Canal8_raw[c]),axis=None)
                                
#                            elif j == c9:
#                                Canal9_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
#                                Canal9_Raw_Total=np.concatenate((Canal9_Raw_Total,Canal9_raw[c]),axis=None)
#                                
#                            elif j == c10:
#                                Canal10_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
#                                Canal10_Raw_Total=np.concatenate((Canal10_Raw_Total,Canal10_raw[c]),axis=None)
#                                
#                            elif j == c11:
#                                Canal11_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[0])/MVC[0]
#                                Canal11_Raw_Total=np.concatenate((Canal11_Raw_Total,Canal11_raw[c]),axis=None)
#            
#                            elif j == c12:
#                                Canal12_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
#                                Canal12_Raw_Total=np.concatenate((Canal12_Raw_Total,Canal12_raw[c]),axis=None)
                                
            
                            k=k+1 
                        c=c+1
    
                    if not sfMove._value:
                        sfMove.release()#exo move
    
                    if not sfRead._value:
                        sfRead.release()#read angles
                    
                    #envelope
                            #falta bloquear el acceso a Canal1_raw
                    emgArray1[0:arraychsize] = emgArray1[chansize:arraysize]
                    emgArray1[arraychsize:arraysize] = Canal1_raw   
                    emgAbs=np.abs(emgArray1)
#                    Canal1_noise = signal.filtfilt(c,d,emgAbs) 
#                    Canal1_env = signal.filtfilt(b,a,Canal1_noise)    
                    Canal1_env = signal.filtfilt(b,a,emgAbs)  
                    Canal1 = Canal1_env[arraychsize:arraysize]
                    
                    
                    
                    emgArray2[0:arraychsize] = emgArray2[chansize:arraysize]
                    emgArray2[arraychsize:arraysize] = Canal2_raw 
                    emgAbs=np.abs(emgArray2)
#                    Canal2_noise = signal.filtfilt(c,d,emgAbs)
#                    Canal2_env=signal.filtfilt(b,a,Canal2_noise) 
                    Canal2_env=signal.filtfilt(b,a,emgAbs) 
                    Canal2 = Canal2_env[arraychsize:arraysize]
                    
                    
                    emgArray3[0:arraychsize] = emgArray3[chansize:arraysize]
                    emgArray3[arraychsize:arraysize] = Canal3_raw
                    emgAbs=np.abs(emgArray3)
#                    Canal3_noise = signal.filtfilt(c,d,emgAbs) 
#                    Canal3_env=signal.filtfilt(b,a,Canal3_noise)   
                    Canal3_env=signal.filtfilt(b,a,emgAbs) 
                    Canal3 = Canal3_env[arraychsize:arraysize]
                    
                    
                    emgArray4[0:arraychsize] = emgArray4[chansize:arraysize]
                    emgArray4[arraychsize:arraysize] = Canal4_raw
                    emgAbs=np.abs(emgArray4)
#                    Canal4_noise = signal.filtfilt(c,d,emgAbs) 
#                    Canal4_env=signal.filtfilt(b,a,Canal4_noise) 
                    Canal4_env=signal.filtfilt(b,a,emgAbs)
                    Canal4 = Canal4_env[arraychsize:arraysize]
#                    
#                    
#                    emgArray5[0:arraychsize] = emgArray5[chansize:arraysize]
#                    emgArray5[arraychsize:arraysize] = Canal5_raw
#                    emgAbs=np.abs(emgArray5)
#                    Canal5_noise = signal.filtfilt(c,d,emgAbs) 
#                    Canal5_env=signal.filtfilt(b,a,Canal5_noise)   
#                    Canal5 = Canal5_env[arraychsize:arraysize]
#                    
#                    
#                    emgArray6[0:arraychsize] = emgArray6[chansize:arraysize]
#                    emgArray6[arraychsize:arraysize] = Canal6_raw
#                    emgAbs=np.abs(emgArray6)
#                    Canal6_noise = signal.filtfilt(c,d,emgAbs) 
#                    Canal6_env=signal.filtfilt(b,a,Canal6_noise)   
#                    Canal6 = Canal6_env[arraychsize:arraysize]
                    
                    
                    Canal1_Env_Total=np.concatenate((Canal1_Env_Total,Canal1),axis=None)
                    Canal2_Env_Total=np.concatenate((Canal2_Env_Total,Canal2),axis=None)
                    Canal3_Env_Total=np.concatenate((Canal3_Env_Total,Canal3),axis=None)
                    Canal4_Env_Total=np.concatenate((Canal4_Env_Total,Canal4),axis=None)
#                    Canal5_Env_Total=np.concatenate((Canal5_Env_Total,Canal5),axis=None)
#                    Canal6_Env_Total=np.concatenate((Canal6_Env_Total,Canal6),axis=None)
#            
                    
                except:
                    pass

        except KeyboardInterrupt:
            
            print("ERROR DURING RECORDING")
        
        duracion = time.time()-t_inicial
        tiempo = np.linspace(0,duracion,np.size(Canal1_Raw_Total))
        print()
        
        emg = [Canal1_Raw_Total, Canal2_Raw_Total, Canal3_Raw_Total, Canal4_Raw_Total,
               Canal1_Env_Total, Canal2_Env_Total, Canal3_Env_Total, Canal4_Env_Total,
               tiempo]
        
        
        try:
            sfprocess.release()  
    #            print(sfprocess._value)
            print("end EMG,  duracion: ", time.time()-t_inicial)
            ConfString=bytes([25,0,0,120,17,1,1,1,1,1,1,1,1,30,30,4,1,1,0,10,10,10,10,1,25]) 
            serialComunication.write(ConfString)
            serialComunication.close()
        except:
            print("ERROR: close serial port process") 
            return emg 
#            raise NameError("ERROR: close serial port process")  
        

    
        
#        Canal1_Raw_Total = Canal1_Raw_Total[sg_delete:-1]
#        Canal2_Raw_Total = Canal2_Raw_Total[sg_delete:-1]
#        Canal3_Raw_Total = Canal3_Raw_Total[sg_delete:-1]
#        Canal4_Raw_Total = Canal4_Raw_Total[sg_delete:-1]
#        Canal5_Raw_Total = Canal5_Raw_Total[sg_delete:-1]
#        Canal6_Raw_Total = Canal6_Raw_Total[sg_delete:-1]
#        Canal7_Raw_Total = Canal7_Raw_Total[sg_delete:-1]
#        Canal8_Raw_Total = Canal8_Raw_Total[sg_delete:-1]
#        Canal9_Raw_Total = Canal9_Raw_Total[sg_delete:-1]
#        Canal10_Raw_Total = Canal10_Raw_Total[sg_delete:-1]
#        Canal11_Raw_Total = Canal11_Raw_Total[sg_delete:-1]
#        Canal12_Raw_Total = Canal12_Raw_Total[sg_delete:-1]
#        Canal13_Raw_Total = Canal13_Raw_Total[sg_delete:-1]
#        Canal14_Raw_Total = Canal14_Raw_Total[sg_delete:-1]
        
#        Canal1_Env_Total = Canal1_Env_Total[sg_delete:-1]
#        Canal2_Env_Total = Canal2_Env_Total[sg_delete:-1]
#        Canal3_Env_Total = Canal3_Env_Total[sg_delete:-1]
#        Canal4_Env_Total = Canal4_Env_Total[sg_delete:-1] 
#        Canal5_Env_Total = Canal5_Env_Total[sg_delete:-1]
#        Canal6_Env_Total = Canal6_Env_Total[sg_delete:-1] 
        

        
#        emg = [Canal1_Raw_Total, Canal2_Raw_Total, Canal3_Raw_Total, Canal4_Raw_Total, 
#            Canal1_Env_Total, Canal2_Env_Total, Canal3_Env_Total, Canal4_Env_Total]
        
        #    interval= int(chansize/2)
#    for i in range (interval,np.size(Canal1_Env_Total),interval):
#        y = Canal1_Env_Total[i-interval:i]
#        
#        area = integrate(y, interval)
##        areaArray1[0:arraychsize] = areaArray1[chansize:arraysize]
#        areaArray1[i-interval:i] = area
        
    
#    return Canal1_Raw_Total, Canal2_Raw_Total, Canal1_Env_Total, Canal2_Env_Total
    return emg 

#%%  ONSET EMG RECORD  


fase = np.zeros(NumMusclue, dtype=int)
countOff = np.zeros(NumMusclue, dtype=int)
    
detectionOn = np.zeros(NumMusclue, dtype=int)
detectionOff = np.zeros(NumMusclue, dtype=int)
#    timeOnset = np.zeros(NumChEMG)
#    timeOffset = np.zeros(NumChEMG)
stillUp = np.zeros(NumChEMG)
threshold = np.zeros(NumChEMG)
thresholdOff = np.zeros(NumChEMG)
periodOff = np.zeros(NumChEMG)


def Onset_Detection(emg_values, fase=0, stillUp=0, countOff=0, threshold = 0.05, thresholdOff = 0.1, periodOff = 0.2*Fsamp, ferquency = Fsamp, NumSamples = 6):
    detectionOn = 0
    detectionOff = 0
    
    for d in range(0,np.size(emg_values)):
        if fase:
            
            if emg_values[d] < thresholdOff: #offset
                countOff += 1
                
                if countOff > periodOff:
                    detectionOn = 0
                    stillUp = 0
                    detectionOff += 1
                    fase = 0
                    countOff = 0
            else:
                countOff = 0
            
        elif emg_values[d] >= threshold and emg_values[d] < 1023: #onset  
            detectionOn += 1
            stillUp = 1
            fase=1
            
#    return detectionOn, detectionOff, time_detectionOn, time_detectionOff, fase, countOff   
    return detectionOn, detectionOff, fase, stillUp, countOff

            
            
def OnsetGetEMG(features, max_minFeatures, sfMove, sfSend, sfprocess, sfRead, sfexit, repeat):
    

    emg = []
    
    Canal1 = []
    Canal2 = []
    Canal3 = []
    Canal4 = []
#    Canal5 = []
#    Canal6 = []
#    Canal7 = []
#    Canal8 = []
#    Canal9 = []
#    Canal10 = []
#    Canal11 = []
#    Canal12 = []
#    Canal13 = []
#    Canal14 = []
    
    Canal1_Raw_Total = []
    Canal2_Raw_Total = []
    Canal3_Raw_Total = []
    Canal4_Raw_Total = []
#    Canal5_Raw_Total = []
#    Canal6_Raw_Total = []
#    Canal7_Raw_Total = []
#    Canal8_Raw_Total = []
#    Canal9_Raw_Total = []
#    Canal10_Raw_Total = []
#    Canal11_Raw_Total = []
#    Canal12_Raw_Total = []
#    Canal13_Raw_Total = []
#    Canal14_Raw_Total = []
    
    Canal1_Env_Total = []
    Canal2_Env_Total = []
    Canal3_Env_Total = []  
    Canal4_Env_Total = []
#    Canal5_Env_Total = []
#    Canal6_Env_Total = []
#    Canal7_Env_Total = []  
#    Canal8_Env_Total = []
#    Canal9_Env_Total = []
#    Canal10_Env_Total = []
#    Canal11_Env_Total = []
#    Canal12_Env_Total = []
#    Canal13_Env_Total = []  
#    Canal14_Env_Total = []
    
    Onset_Total = 0
    
    threshold[0] = features[0] #Ankle
    thresholdOff[0] = features[1]
    periodOff[0] = 0.1*Fsamp
    threshold[1] = features[3]#knee
    thresholdOff[1] = features[4]
    periodOff[1] = 0.1*Fsamp
    threshold[2] = features[6] #Ankle
    thresholdOff[2] = features[7]
    periodOff[2] = 0.1*Fsamp
    threshold[3] = features[9]#knee
    thresholdOff[3] = features[10]
    periodOff[3] = 0.1*Fsamp
    
    
    max_Canal1 = max_minFeatures[0]
    max_Canal2 = max_minFeatures[2]
    max_Canal3 = max_minFeatures[4]
    max_Canal4 = max_minFeatures[6]

    min_Canal1 = max_minFeatures[1]
    min_Canal2 = max_minFeatures[3]
    min_Canal3 = max_minFeatures[5]
    min_Canal4 = max_minFeatures[7]
    
    fstep = 1
    stepsize = 0
    with serial.Serial(port, bau, timeout=12) as serialComunication:
        serialComunication.write(ConfString_out)
#        print("EMG Start")
#        while sfprocess._value:
#        for h in range(0,repeat*10):
        try:
            t_inicial = time.time()
            while time.time()-t_inicial < repeat:
                
                if sfexit._value:
                    break
                line = serialComunication.read(acq)
                try:
                    k = 0
                    c = 0
                    info = [line[i:i+2] for i in range(0, len(line), 2)]  
                    
                    while k < (acq/2):
                        for j in range(0,NumMusclue,1):
                            if j == c1:
                                Canal1_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[0])/MVC[0]
                                Canal1_Raw_Total=np.concatenate((Canal1_Raw_Total,Canal1_raw[c]),axis=None)
            
                            elif j == c2:
                                Canal2_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
                                Canal2_Raw_Total=np.concatenate((Canal2_Raw_Total,Canal2_raw[c]),axis=None)
                                
                            elif j == c3:
                                Canal3_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
                                Canal3_Raw_Total=np.concatenate((Canal3_Raw_Total,Canal3_raw[c]),axis=None)
                                
                            elif j == c4:
                                Canal4_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
                                Canal4_Raw_Total=np.concatenate((Canal4_Raw_Total,Canal4_raw[c]),axis=None)
            
#                            elif j == c5:
#                                Canal5_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
#                                Canal5_Raw_Total=np.concatenate((Canal5_Raw_Total,Canal5_raw[c]),axis=None)
#                                
#                            elif j == c6:
#                                Canal6_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
#                                Canal6_Raw_Total=np.concatenate((Canal6_Raw_Total,Canal6_raw[c]),axis=None)
#                                
#                            elif j == c7:
#                                Canal7_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[0])/MVC[0]
#                                Canal7_Raw_Total=np.concatenate((Canal7_Raw_Total,Canal7_raw[c]),axis=None)
#            
#                            elif j == c8:
#                                Canal8_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
#                                Canal8_Raw_Total=np.concatenate((Canal8_Raw_Total,Canal8_raw[c]),axis=None)
#                                
#                            elif j == c9:
#                                Canal9_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
#                                Canal9_Raw_Total=np.concatenate((Canal9_Raw_Total,Canal9_raw[c]),axis=None)
#                                
#                            elif j == c10:
#                                Canal10_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
#                                Canal10_Raw_Total=np.concatenate((Canal10_Raw_Total,Canal10_raw[c]),axis=None)
#                                
#                            elif j == c11:
#                                Canal11_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[0])/MVC[0]
#                                Canal11_Raw_Total=np.concatenate((Canal11_Raw_Total,Canal11_raw[c]),axis=None)
#            
#                            elif j == c12:
#                                Canal12_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
#                                Canal12_Raw_Total=np.concatenate((Canal12_Raw_Total,Canal12_raw[c]),axis=None)
                                
    #                        elif j == c13:
    #                            Canal13_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
    #                            Canal13_Raw_Total=np.concatenate((Canal13_Raw_Total,Canal13_raw[c]),axis=None)
    #                            
    #                        elif j == c14:
    #                            Canal14_raw[c] = (ConvFact*(int.from_bytes(info[k],byteorder='little', signed=True)) - Offset[1]) 
    #                            Canal14_Raw_Total=np.concatenate((Canal14_Raw_Total,Canal14_raw[c]),axis=None)
    
                            k=k+1 
                        c=c+1
                    
                    # ENVELOPE
                    emgArray1[0:arraychsize] = emgArray1[chansize:arraysize]
                    emgArray1[arraychsize:arraysize] = Canal1_raw
                    emgAbs=np.abs(emgArray1)
                    Canal1_env=signal.filtfilt(b,a,emgAbs)    
                    Canal1 = Canal1_env[arraychsize:arraysize]
                    
                    
                    emgArray2[0:arraychsize] = emgArray2[chansize:arraysize]
                    emgArray2[arraychsize:arraysize] = Canal2_raw             
                    emgAbs=np.abs(emgArray2)
                    Canal2_env=signal.filtfilt(b,a,emgAbs)   
                    Canal2 = Canal2_env[arraychsize:arraysize]
                    
                    
                    emgArray3[0:arraychsize] = emgArray3[chansize:arraysize]
                    emgArray3[arraychsize:arraysize] = Canal3_raw              
                    emgAbs=np.abs(emgArray3)
                    Canal3_env=signal.filtfilt(b,a,emgAbs)   
                    Canal3 = Canal3_env[arraychsize:arraysize]
                    
                    
                    emgArray4[0:arraychsize] = emgArray4[chansize:arraysize]
                    emgArray4[arraychsize:arraysize] = Canal4_raw              
                    emgAbs=np.abs(emgArray4)
                    Canal4_env=signal.filtfilt(b,a,emgAbs)   
                    Canal4 = Canal4_env[arraychsize:arraysize]
                    
                    
#                    emgArray5[0:arraychsize] = emgArray5[chansize:arraysize]
#                    emgArray5[arraychsize:arraysize] = Canal5_raw
#                    emgAbs=np.abs(emgArray5)
#                    Canal5_noise = signal.filtfilt(c,d,emgAbs) 
#                    Canal5_env=signal.filtfilt(b,a,Canal5_noise)   
#                    Canal5 = Canal5_env[arraychsize:arraysize]
#                    
#                    
#                    emgArray6[0:arraychsize] = emgArray6[chansize:arraysize]
#                    emgArray6[arraychsize:arraysize] = Canal6_raw
#                    emgAbs=np.abs(emgArray6)
#                    Canal6_noise = signal.filtfilt(c,d,emgAbs) 
#                    Canal6_env=signal.filtfilt(b,a,Canal6_noise)   
#                    Canal6 = Canal6_env[arraychsize:arraysize]
                    
                    
                    
    #                print(min_Canal1, max_Canal1, (max_Canal1 - min_Canal1))
#                    print((max_Canal1 - min_Canal1),round((max_Canal1 - min_Canal1),2))
                    Canal1 = (Canal1 - min_Canal1)/round((max_Canal1 - min_Canal1),2)
                    Canal2 = (Canal2 - min_Canal2)/round((max_Canal2 - min_Canal2),2)
                    Canal3 = (Canal3 - min_Canal3)/round((max_Canal3 - min_Canal3),2)
                    Canal4 = (Canal4 - min_Canal4)/round((max_Canal4 - min_Canal4),2)
                    
                    
                    
                    
                    Canal1_Env_Total=np.concatenate((Canal1_Env_Total,Canal1),axis=None)
                    Canal2_Env_Total=np.concatenate((Canal2_Env_Total,Canal2),axis=None)
                    Canal3_Env_Total=np.concatenate((Canal3_Env_Total,Canal3),axis=None)
                    Canal4_Env_Total=np.concatenate((Canal4_Env_Total,Canal4),axis=None)
#                    Canal5_Env_Total=np.concatenate((Canal5_Env_Total,Canal5),axis=None)
#                    Canal6_Env_Total=np.concatenate((Canal6_Env_Total,Canal6),axis=None)
    
#                    print(Canal2_Env_Total)
    
                    # DETECTION
                    if len(Canal1)>0 and len(Canal2)>0:
                        
                        detectionOn[0], detectionOff[0], fase[0], stillUp[0], countOff[0] = Onset_Detection(Canal1, 
                               fase[0], stillUp[0], countOff[0], threshold[0] , thresholdOff[0] , periodOff[0])
                        
                        detectionOn[1], detectionOff[1], fase[1], stillUp[1], countOff[1] = Onset_Detection(Canal2, 
                               fase[1], stillUp[1], countOff[1], threshold[1] , thresholdOff[1] , periodOff[1])
                        
    #                if len(Canal3)>0 and len(Canal4)>0:
    #                    
                        detectionOn[2], detectionOff[2], fase[2], stillUp[2], countOff[2] = Onset_Detection(Canal3, 
                               fase[2], stillUp[2], countOff[2], threshold[2], thresholdOff[2], periodOff[2])
                        
                        detectionOn[3], detectionOff[3], fase[3], stillUp[3], countOff[3] = Onset_Detection(Canal4, 
                               fase[3], stillUp[3], countOff[3], threshold[3] , thresholdOff[3] , periodOff[3])
                        
                        
                        # FS soleo antagonista 
                        if (detectionOn[0] or detectionOn[3]) and fstep:
                            #MUEVE PIERNA IZQUIERDA
                            
                            sfMove.release()
                            Onset_Total=np.concatenate((Onset_Total,detectionOn[0]),axis=None)
                            fstep = 0
                            print("detected FS")
                        
                        
                        # Single muscle
    #                    if detectionOn[1] and sfSend._value and stepsize:
    #                        
    #                        print("detected RIGHT")
    #                        semaforo.release()
    #                        Onset_Total=np.concatenate((Onset_Total,detectionOn[0]),axis=None)
    #                        sfSend.acquire()
    #
    #                    else:
    #                        Onset_Total=np.concatenate((Onset_Total,detectionOn[0]),axis=None)
    #                        
    #                        
    #                    if detectionOn[0] and sfSend._value and not stepsize:
    #                        
    #                        print("detected LEFT")
    #                        semaforo.release()
    #                        Onset_Total=np.concatenate((Onset_Total,detectionOn[1]),axis=None)
    #                        sfSend.acquire()
    #                        
    #                    else:
    #                        Onset_Total=np.concatenate((Onset_Total,detectionOn[1]),axis=None)
                      
                      
                        #multiple muscles Rf or Sol(antagonista)     
                    if (detectionOn[1] or detectionOn[2]) and sfSend._value and stepsize:
                        
                        sfMove.release()
                        stepsize = 0
                        print("detected RIGHT")
                        if detectionOn[1]:
                            Onset_Total=np.concatenate((Onset_Total,detectionOn[0]),axis=None)
                        else:
                            Onset_Total=np.concatenate((Onset_Total,detectionOn[3]),axis=None)
    #                    print("Exo UP1")
                        sfSend.acquire()
                    else:
                        Onset_Total=np.concatenate((Onset_Total,detectionOn[0]),axis=None)
                        
                        
                        
                    if (detectionOn[3] or detectionOn[0]) and sfSend._value and not stepsize:
                        
                        sfMove.release()
                        stepsize = 1
                        print("detected LEFT")
                        if detectionOn[0]:
                            Onset_Total=np.concatenate((Onset_Total,detectionOn[1]),axis=None)
                        else:
                            Onset_Total=np.concatenate((Onset_Total,detectionOn[2]),axis=None)
                        sfSend.acquire()
                    else: 
                        Onset_Total=np.concatenate((Onset_Total,detectionOn[1]),axis=None)
                    
                    if not sfRead._value:
                        sfRead.release()#read angles
                    
                except:
                    pass
        except:
            
            print("ERROR DURING RECORDING")
            
        
#        duracion = np.size(Canal1_Raw_Total)/Fsamp
        duracion = time.time()-t_inicial
        tiempo = np.linspace(0,duracion,np.size(Canal1_Raw_Total))


        emg = [Canal1_Raw_Total, Canal2_Raw_Total, Canal3_Raw_Total, Canal4_Raw_Total,
               Canal5_Raw_Total, Canal6_Raw_Total, Canal7_Raw_Total, Canal8_Raw_Total,
               Canal9_Raw_Total, Canal10_Raw_Total, Canal11_Raw_Total, Canal12_Raw_Total,
               Canal1_Env_Total, Canal2_Env_Total, Canal3_Env_Total, Canal4_Env_Total,
               Canal5_Env_Total, Canal6_Env_Total,tiempo]

        try:
            sfprocess.release()  
            print("end EMG,  duracion: ", time.time()-t_inicial)
            ConfString=bytes([25,0,0,120,17,1,1,1,1,1,1,1,1,30,30,4,1,1,0,10,10,10,10,1,25]) 
            serialComunication.write(ConfString)
            serialComunication.close()
        except:
            return emg, Onset_Total
            raise NameError("ERROR: close serial port process")
          

        
#        Canal1_Raw_Total = Canal1_Raw_Total[sg_delete:-1]
#        Canal2_Raw_Total = Canal2_Raw_Total[sg_delete:-1]
#        Canal3_Raw_Total = Canal3_Raw_Total[sg_delete:-1]
#        Canal4_Raw_Total = Canal4_Raw_Total[sg_delete:-1]
#        Canal5_Raw_Total = Canal5_Raw_Total[sg_delete:-1]
#        Canal6_Raw_Total = Canal6_Raw_Total[sg_delete:-1]
#        Canal7_Raw_Total = Canal7_Raw_Total[sg_delete:-1]
#        Canal8_Raw_Total = Canal8_Raw_Total[sg_delete:-1]
#        Canal9_Raw_Total = Canal9_Raw_Total[sg_delete:-1]
#        Canal10_Raw_Total = Canal10_Raw_Total[sg_delete:-1]
#        Canal11_Raw_Total = Canal11_Raw_Total[sg_delete:-1]
#        Canal12_Raw_Total = Canal12_Raw_Total[sg_delete:-1]
#        Canal13_Raw_Total = Canal13_Raw_Total[sg_delete:-1]
#        Canal14_Raw_Total = Canal14_Raw_Total[sg_delete:-1]
        
#        Canal1_Env_Total = Canal1_Env_Total[sg_delete:-1]
#        Canal2_Env_Total = Canal2_Env_Total[sg_delete:-1]
#        Canal3_Env_Total = Canal3_Env_Total[sg_delete:-1]
#        Canal4_Env_Total = Canal4_Env_Total[sg_delete:-1] 
#        Canal5_Env_Total = Canal5_Env_Total[sg_delete:-1]
#        Canal6_Env_Total = Canal6_Env_Total[sg_delete:-1] 
        
        
        
        print("return EAST")
 
    return emg, Onset_Total

#%%  Class EAST


class EAST (Thread):
    def _init_(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        Thread._init_(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
            
    def join(self, *args):
        Thread.join(self, *args)
        return self._return


#emg =[]
#repeat=3
#sfprocess = Semaphore(0) # semaforo de fin sincronizado de los threads
#sfMove = Semaphore(1) # movimiento del exo
#sfRead = Semaphore(1) # read exo angles
#
#dataCollector = EAST(target = EASTrec, args = (sfprocess,sfMove,sfRead,repeat)) 
#    
#    
#dataCollector.start() 
#    
##t_inicial = time.time()
##while time.time()-t_inicial < repeat:
##    pass
#    
##sfprocess._value=0
#
##while sfprocess._value:
##    pass
#sfprocess.acquire()
#print("END")
#    
#emg2=dataCollector.join()
#print(np.size(emg2[0]))


