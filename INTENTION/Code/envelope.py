import numpy as np
import matplotlib.pyplot as plt
from numpy.fft import fft, fftfreq, fftshift
from scipy import signal
#from matplotlib.figure import Figure

import pandas as pd


File = pd.read_csv('211221_ONSET_Subject_Jaime_02.csv')



Time = File['Tiempo']
Canal1_Raw = File['Canal1_Raw']
Canal2_Raw = File['Canal2_Raw']
Canal3_Raw = File['Canal3_Raw']
Canal4_Raw = File['Canal4_Raw']
Canal1_Env = File['Canal1_Env']
Canal2_Env = File['Canal2_Env']
Canal3_Env = File['Canal3_Env']
Canal4_Env = File['Canal4_Env']

Canal1_Filterinst_Total = []
Canal1_RMSinst_Total = []
Canal1_env_Total = []





Fsamp = 2000
PlotTime = 0.1
arraysize = int(Fsamp*1)
chansize = int(Fsamp*PlotTime)
arraychsize = int(arraysize-chansize)
emgArray1 = np.zeros(arraysize)
rmsize = int(chansize*1.2)
rmsArray1 = np.zeros(rmsize)



b, a = signal.butter(2,6/(Fsamp/2.),btype='low')


def filter_function(emg):
#    emgArray1[0:arraychsize] = emgArray1[chansize:arraysize]
#    emgArray1[arraychsize:arraysize] = emg   
    chansize = len(emg)
    arraychsize = int(arraysize-chansize)
    emgArray1[0:arraychsize] = emgArray1[chansize:arraysize] #shift de losvalores del array 
    emgArray1[arraychsize:arraysize] = emg #actualiza ultimos valores del array 
    emgAbs = np.abs(emgArray1)
    inst_filt = signal.filtfilt(b,a,emgAbs)    
    emg_filt = inst_filt[arraychsize:arraysize]
    return emg_filt
    

def rolling_rmg(x, N):
    return (pd.DataFrame(abs(x)**2).rolling(N).mean())**0.5

def rms(emg):
    chansize = len(emg)
    arraychsize = int(rmsize-chansize)
    rmsArray1[0:arraychsize] = rmsArray1[chansize:rmsize]# shift
    rmsArray1[arraychsize:rmsize] = emg # uppdate
    
    return np.sqrt(np.mean(rmsArray1**2))

def hilbert (x):
    sig = signal.hilbert(x)
    return np.abs(sig)

#def rolling_rmg_inst(x, N):
#    xc = np.cumsum(abs(x)**2);
#    return np.sqrt((xc[N:] - xc[:-N]) / N)


  

#### Signal ####
emg = Canal3_Raw
envelope = Canal3_Env

global_rms=rolling_rmg(emg, 1600)
#global_rms=hilbert(Canal1_Raw)
rawAbs=np.abs(emg)
global_filt= signal.filtfilt(b,a,rawAbs)   
global_filt= hilbert(global_filt) 


step = int(chansize*1)
skip = 190
zeroArray = np.zeros(skip+step)

for i in range(0,np.size(emg),step):
    if (i+step)<np.size(emg):
        inst_emg = emg[i:i+step]
    else: inst_emg = emg[i:-1]
#    if len(zeroArray[skip-1:-1]) == len(inst_emg):
##        zeroArray[skip-1:-1]=inst_emg
##        inst_env=rolling_rmg(zeroArray, skip)
#        #RMS
#    inst_env=rolling_rmg(inst_emg, skip)
    inst_env=rms(inst_emg)
    Canal1_RMSinst_Total=np.concatenate((Canal1_RMSinst_Total,inst_env),axis=None)
    
    #FILTER & ABS
    emg_filt=filter_function(inst_emg)
    Canal1_Filterinst_Total=np.concatenate((Canal1_Filterinst_Total,emg_filt),axis=None)
    
    #ENVELOPE
    emg_env=hilbert(emg_filt)
    Canal1_env_Total=np.concatenate((Canal1_env_Total,emg_env),axis=None)
    
    
#    for j in range(0,np.size(emg_values))
duracion = (Time[len(Time)-1])
fsRMS = (len(Canal1_RMSinst_Total)/duracion)
range_array = np.arange(0,duracion,1/fsRMS)
TimeRMS = list(range_array)


#### PLOT ###

figenv, axs_env = plt.subplots(4)
axs_env[0].plot(Time, emg)
axs_env[0].set_title('Canal1_Raw')

axs_env[1].plot(Time, envelope)
axs_env[1].set_title('Canal1_Env')

axs_env[2].plot(Time, global_filt)
axs_env[2].set_title('filter global_env')

axs_env[3].plot(Time, global_rms)
axs_env[3].set_title('rms global_env')


figinstenv, axs_instenv = plt.subplots(4)
axs_instenv[0].plot(Time, emg)
axs_instenv[0].set_title('Canal1_Raw')

axs_instenv[1].plot(envelope)
axs_instenv[1].set_title('Canal1_Env')

axs_instenv[2].plot(Canal1_Filterinst_Total[200:-1])
axs_instenv[2].set_title('filter insta global_env')

axs_instenv[3].plot(TimeRMS,Canal1_RMSinst_Total)
axs_instenv[3].set_title('RMS insta global_env')

#axs_instenv[2].plot(Canal1_env_Total)
#axs_instenv[2].set_title('hilert insta global_env')

for ax in axs_env.flat:
    ax.set(xlabel='Time [s]', ylabel='Aplitude')
    
for ax in axs_env.flat:
    ax.label_outer()
    
    
for ax in axs_instenv.flat:
    ax.set(xlabel='Time [s]', ylabel='Aplitude')
    
for ax in axs_instenv.flat:
    ax.label_outer()

plt.show()