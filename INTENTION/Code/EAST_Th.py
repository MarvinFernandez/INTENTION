
import numpy as np
import serial
import time
import crc8 as crc8
#from scipy.signal import hilbert
from scipy import signal
from threading import Thread

#SerialCOM = '/dev/ttyACM0'
#bau = 921600
#port = SerialCOM
#ConvFact = float(0.000286*1000) 
#    Mode_east = 0 #Always set to 0
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
# ConfString 1000 hz
#    ConfString=bytes([25,9,0,127,13,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,254])
#    # ConfString 2000 hz
#    ConfString=bytes([25,9,0,127,13,0,0,0,0,0,0,0,0,30,30,1,4,0,0,40,12,12,15,1,132])
#print(ConfString)

b, a = signal.butter(2,6/(2000/2.),btype='low')
Offset = np.array([520, -710, -150, -480, -348, 328, -437,308])
MVC = np.array([1337, 1337, 1281.046, 1542.164, 9891.648, 551.46])


Canal1_Raw_Total = []
Canal2_Raw_Total = []

Canal1_raw = np.zeros(Canalacq)
Canal2_raw = np.zeros(Canalacq)

arraysize = Fsamp*2
chansize = int(Fsamp*PlotTime)
arraychsize = int(arraysize-chansize)

emgArray1 = np.zeros(arraysize)
emgArray2 = np.zeros(arraysize)

Canal1_Env_Total = []
Canal2_Env_Total = []

Canal1 = []
Canal2 = []
#    print("arraysize",arraysize,"chansize",chansize,"arraychsize",arraychsize)



def getData(t):
    global Canal1_Env_Total, Canal2_Env_Total, Canal1_Raw_Total, Canal2_Raw_Total
    
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
                            
                        k=k+1 
                    c=c+1
                
                #envelope
                        #falta bloquear el acceso a Canal1_raw
                emgArray1[0:arraychsize] = emgArray1[chansize:arraysize]
                emgArray1[arraychsize:arraysize] = Canal1_raw
                
                emgAbs=np.abs(emgArray1)
                Canal1_env=signal.filtfilt(b,a,emgAbs)    
                Canal1 = Canal1_env[arraychsize:arraysize]
                Canal1_Env_Total=np.concatenate((Canal1_Env_Total,Canal1),axis=None)
                
                emgArray2[0:arraychsize] = emgArray2[chansize:arraysize]
                emgArray2[arraychsize:arraysize] = Canal2_raw
                
                emgAbs=np.abs(emgArray2)
                Canal2_env=signal.filtfilt(b,a,emgAbs)   
                Canal2 = Canal2_env[arraychsize:arraysize]
                Canal2_Env_Total=np.concatenate((Canal2_Env_Total,Canal2),axis=None)

#                sfrecive.release()
#                sfrepeat.acquire()
                
            except:
                pass
#        plt.plot(Canal1_Env_Total)
#        sfprocess.acquire() 
        Canal1_Env_Total = Canal1_Env_Total[chansize:-1]
        Canal2_Env_Total = Canal2_Env_Total[chansize:-1]
        try:
            ConfString=bytes([25,0,0,120,17,1,1,1,1,1,1,1,1,30,30,4,1,1,0,10,10,10,10,1,25]) 
            serialComunication.write(ConfString)
            serialComunication.close()
        except:
            raise NameError("ERROR: close serial port process")

    
def EASTrecord(repeat):
    global Canal1_Raw_Total, Canal2_Raw_Total, Canal1_Env_Total, Canal2_Env_Total
#    print("EASThread Start")
#    Thread(target = getData1, args = (repeat)).start
    dataCollector = Thread(target = getData, args = (repeat,))
    
    dataCollector.start()
    dataCollector.join()
#    print("EASThread END")
#    
    return Canal1_Raw_Total, Canal2_Raw_Total, Canal1_Env_Total, Canal2_Env_Total









