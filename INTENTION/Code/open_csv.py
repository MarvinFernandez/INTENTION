import numpy as np
import matplotlib.pyplot as plt
from numpy.fft import fft, fftfreq, fftshift
from scipy import signal
#from matplotlib.figure import Figure

import pandas as pd

#import matplotlib.animation as animation


def norm(signal, value):
    minimo=(min(value))
    maximo=(max(value))
    if (maximo - minimo) != 0:
        signal_norm=(signal-minimo)/(maximo - minimo)
    else:
#        print(maximo - minimo)
        signal_norm=(signal-minimo)
    
    return signal_norm



def onsetfun(onsetvector, num_up, onset_num):
    count = 0
    onset_array=np.zeros(len(onsetvector))
    for p in range(len(onsetvector)):
        if onsetvector[p]!=num_up and count==0:
            onset_array[p]=0
        elif count == 1 and onsetvector[p]==onset_num:
            count = 0   
            onset_array[p]=onsetvector[p] 
        else:
            count = 1
            onset_array[p]=onset_num
    return onset_array
#    count = 0
#    for p in range(len(onset)):
#        if onset[p]!=1 and count==0:
#            onset_rsol[p]=0
#        elif count == 1 and onset[p]==7:
#            count = 0   
#            onset_rsol[p]=onset[p] 
#        else:
#            count = 1    
    
#onset_rsol = onsetfun(onset, 1, 7)
#            onset_rsol[p]=7





#read csv

#m_ONSET_Subject_Vacio_m2
#131221_ONSET_Subject_marvin_1
#131221_ONSET_Subject_marvin_2
#310122_ONSET_Subject_Andrea_03
    

File = pd.read_csv('080222_ONSET_Subject_04_02.csv')



Time = File['Tiempo']
Canal1_Raw = File['Canal1_Raw']
Canal2_Raw = File['Canal2_Raw']
Canal3_Raw = File['Canal3_Raw']
Canal4_Raw = File['Canal4_Raw']
Canal1_Env = File['Canal1_Env']
Canal2_Env = File['Canal2_Env']
Canal3_Env = File['Canal3_Env']
Canal4_Env = File['Canal4_Env']

b, a = signal.butter(2,15/(2000/2.),btype='low')
e, f = signal.butter(2,[45/(2000/2.), 55/(2000/2.)],btype='bandstop')


#w,h = signal.freqz(b,a, worN=2000)
#plt.figure(0)
#plt.plot(((2000/2.)/np.pi)*w, abs(h), label="orden 2")
##plt.plot(w, 20*np.log10(abs(h)), label="orden 2")
#plt.title('filtro')
#plt.ylabel('aplitude [dB]')
#plt.xlabel('freqz [Hz]')
#plt.xlim([0,100])
#plt.legend(loc='best')


Canal1_EnvS = signal.filtfilt(e,f,Canal1_Raw)
Canal1_EnvS = signal.filtfilt(b,a,Canal1_EnvS)
Canal2_EnvS = signal.filtfilt(e,f,Canal2_Raw)
Canal2_EnvS = signal.filtfilt(b,a,Canal2_EnvS)
Canal3_EnvS = signal.filtfilt(e,f,Canal3_Raw)
Canal3_EnvS = signal.filtfilt(b,a,Canal3_EnvS) 
Canal4_EnvS = signal.filtfilt(e,f,Canal4_Raw)
Canal4_EnvS = signal.filtfilt(b,a,Canal4_EnvS)


#normalize

Canal1_Raw_norm = norm(Canal1_Raw, Canal1_Raw)
Canal2_Raw_norm = norm(Canal2_Raw, Canal2_Raw)
Canal3_Raw_norm = norm(Canal3_Raw, Canal3_Raw)
Canal4_Raw_norm = norm(Canal4_Raw, Canal4_Raw)


Canal1_Env_norm = norm(Canal1_Env, Canal1_Env)
Canal2_Env_norm = norm(Canal2_Env, Canal2_Env)
Canal3_Env_norm = norm(Canal3_Env, Canal3_Env)
Canal4_Env_norm = norm(Canal4_Env, Canal4_Env)


Canal1_EnvS_norm = norm(Canal1_EnvS, Canal1_EnvS)
Canal2_EnvS_norm = norm(Canal2_EnvS, Canal2_EnvS)
Canal3_EnvS_norm = norm(Canal3_EnvS, Canal3_EnvS)
Canal4_EnvS_norm = norm(Canal4_EnvS,Canal4_EnvS)


#op = "NO-ONSET"
op = "ONSET"

if op == "ONSET":
    onset = File['ONSET']
    
    rHip_Record = File['rHip_Record']
    rKnee_Record = File['rKnee_Record']
    rAnkle_Record = File['rAnkle_Record']
    lHip_Record = File['lHip_Record']
    lKnee_Record = File['lKnee_Record']
    lAnkle_Record = File['lAnkle_Record']
    
    rHip_Sent = File['rHip_Sent']
    rKnee_Sent = File['rKnee_Sent']
    rAnkle_Sent = File['rAnkle_Sent']
    lHip_Sent = File['lHip_Sent']
    lKnee_Sent = File['lKnee_Sent']
    lAnkle_Sent = File['lAnkle_Sent']
    
    
    posicion = np.where(onset.isnull())
    nan_list=posicion[0]
    onset=onset[0:nan_list[0]]
    
    

    onset_rsol = onsetfun(onset, 1, 7)
    onset_lsol = onsetfun(onset, 3, 7)
    onset_rrf = onsetfun(onset, 2, 7)
    onset_lrf = onsetfun(onset, 4, 7)
    
    #    onset_box = onsetfun(onset, 0, 7)
    onset_box=np.zeros(len(onset))
    count=0
    for p in range(len(onset)):
        if onset[p]==0 and count == 0:
            onset_box[p]=onset[p] 
        elif count == 1 and onset[p]==7:
            count = 0   
            onset_box[p]=onset[p] 
        else:
            count = 1
            onset_box[p]=7
    
    
    posicion = np.where(rHip_Record.isnull())
    nan_list=posicion[0]
    rHip_Record=rHip_Record[0:nan_list[0]]
    rKnee_Record=rKnee_Record[0:nan_list[0]]
    rAnkle_Record=rAnkle_Record[0:nan_list[0]]
    lHip_Record=lHip_Record[0:nan_list[0]]
    lKnee_Record=lKnee_Record[0:nan_list[0]]
    lAnkle_Record=lAnkle_Record[0:nan_list[0]]
    
    posicion = np.where(rHip_Sent.isnull())
    nan_list=posicion[0] 
    rHip_Sent=rHip_Sent[0:nan_list[0]]
    rKnee_Sent=rKnee_Sent[0:nan_list[0]]
    rAnkle_Sent=rAnkle_Sent[0:nan_list[0]]
    lHip_Sent=lHip_Sent[0:nan_list[0]]
    lKnee_Sent=lKnee_Sent[0:nan_list[0]]
    lAnkle_Sent=lAnkle_Sent[0:nan_list[0]]
    
    
    rHipArray = np.ones(len(onset))*min(rHip_Sent)
    lHipArray = np.ones(len(onset))*min(lHip_Sent)
    
    rKneeArray = np.ones(len(onset))*min(rKnee_Sent)
    lKneeArray = np.ones(len(onset))*min(lKnee_Sent)
    
    rAnkleArray = np.ones(len(onset))*min(rAnkle_Sent)
    lAnkleArray = np.ones(len(onset))*min(lAnkle_Sent)
#    
#    sendEnd=np.where(onset>=1)
#    init=0
#    send_pp = sendEnd[0]
#    for p in range(len(send_pp)):
#        send_p = send_pp[p]

#        if(len(rKneeArray[send_p:send_p+25])>=25):
#            rKneeArray[send_p:send_p+25] = rKnee_Sent[init:init+25]
#            lKneeArray[send_p:send_p+25] = lKnee_Sent[init:init+25]
#            init=init+25
#        else:
#            rKneeArray[send_p:-1] =rKnee_Sent[init:init+len(rKneeArray[send_p:-1])]
#            lKneeArray[send_p:-1] =lKnee_Sent[init:init+len(lKneeArray[send_p:-1])]
    
    sendEnd=np.where(onset==7)
    send_pp = sendEnd[0]
    init=0
    for p in range(len(send_pp)):
        send_p = send_pp[p]
        if(len(rKnee_Sent[init:init+25])>=25):
            rHipArray[send_p-25:send_p] = rHip_Sent[init:init+25]
            lHipArray[send_p-25:send_p] = lHip_Sent[init:init+25]
            rKneeArray[send_p-25:send_p] = rKnee_Sent[init:init+25]
            lKneeArray[send_p-25:send_p] = lKnee_Sent[init:init+25]
            rAnkleArray[send_p-25:send_p] = rAnkle_Sent[init:init+25]
            lAnkleArray[send_p-25:send_p] = lAnkle_Sent[init:init+25]
            
            init=init+25
        else:
            rHipArray[send_p-25:(send_p-25)+len(rHip_Sent[init:-1])] = rHip_Sent[init:-1]
            lHipArray[send_p-25:(send_p-25)+len(lHip_Sent[init:-1])] = lHip_Sent[init:-1]
            rKneeArray[send_p-25:(send_p-25)+len(rKnee_Sent[init:-1])] = rKnee_Sent[init:-1]
            lKneeArray[send_p-25:(send_p-25)+len(lKnee_Sent[init:-1])] = lKnee_Sent[init:-1]
            rAnkleArray[send_p-25:(send_p-25)+len(rAnkle_Sent[init:-1])] = rAnkle_Sent[init:-1]
            lAnkleArray[send_p-25:(send_p-25)+len(lAnkle_Sent[init:-1])] = lAnkle_Sent[init:-1]
    

    
    #normalize
    onset_norm = norm(onset, onset)
    
    onset_box_norm = norm(onset_box, onset_box)
    
    onset_rsol_norm = norm(onset_rsol, onset_rsol)
    
    onset_lsol_norm = norm(onset_lsol, onset_lsol)
    
    onset_rrf_norm = norm(onset_rrf, onset_rrf)
    
    onset_lrf_norm = norm(onset_lrf, onset_lrf)
    
    rHip_Sent_norm = norm(rHip_Sent, (rHip_Sent + lHip_Sent))
    lHip_Sent_norm = norm(lHip_Sent, (rHip_Sent + lHip_Sent))
    rKnee_Sent_norm = norm(rKnee_Sent, (rKnee_Sent + lKnee_Sent))
    lKnee_Sent_norm = norm(lKnee_Sent, (rKnee_Sent + lKnee_Sent))
    rAnkle_Sent_norm = norm(rAnkle_Sent, (rAnkle_Sent + lAnkle_Sent))
    lAnkle_Sent_norm = norm(lAnkle_Sent, (rAnkle_Sent + lAnkle_Sent))
    

    rHip_Record_norm = norm(rHip_Record, (rHip_Record + lHip_Record))
    lHip_Record_norm = norm(lHip_Record, (rHip_Record + lHip_Record))
    rKnee_Record_norm = norm(rKnee_Record, (rKnee_Record + lKnee_Record))
    lKnee_Record_norm = norm(lKnee_Record, (rKnee_Record + lKnee_Record))
    rAnkle_Record_norm = norm(rAnkle_Record, (rAnkle_Record + lAnkle_Record))
    lAnkle_Record_norm = norm(lAnkle_Record, (lAnkle_Record + lAnkle_Record))
    
    
    rHipArray_norm = norm(rHipArray, (rHipArray))
    lHipArray_norm = norm(lHipArray, (lHipArray))
    rKneeArray_norm = norm(rKneeArray, (rKneeArray + lKneeArray))
    lKneeArray_norm = norm(lKneeArray, (rKneeArray + lKneeArray))
    rAnkleArray_norm = norm(rAnkleArray, (rAnkleArray))
    lAnkleArray_norm = norm(lAnkleArray, (lAnkleArray))
    
    
    
    #Time
    duracion = (Time[len(Time)-1])
    
    fsOnset = (len(onset)/duracion)
    range_array = np.arange(0,duracion,1/fsOnset)
    TimeOnset = list(range_array)
    if len(TimeOnset) != len(onset):
        TimeOnset = TimeOnset[0:-1]
    
    fsAngleRec = (len(rHip_Record)/duracion)
    range_array = np.arange(0,duracion,1/fsAngleRec)
    TimeRec = list(range_array)
#    TimeRec = TimeRec[0:-1]
    
    fsAngleSet = (len(rHip_Sent)/duracion)
    range_array = np.arange(0,duracion,1/fsAngleSet)
    TimeSet = list(range_array)
#    TimeSet = TimeSet[0:-1]
    
    
    ######### PLOT ########
    
    figonset, axs_onset = plt.subplots(5)
    axs_onset[0].plot(Time, Canal1_Raw_norm)
    axs_onset[0].plot(Time, Canal1_Env_norm+0.2)
    axs_onset[0].set_title('Sol R')
#    axs_onset[1].plot(Time, Canal1_Raw_norm)
#    axs_onset[1].plot(Time, Canal1_EnvS_norm)
#    axs_onset[1].set_title('Sol EnvS (R)')
    axs_onset[1].plot(Time, Canal2_Raw_norm)
    axs_onset[1].plot(Time, Canal2_Env_norm)
    axs_onset[1].set_title('RF R')
    axs_onset[2].plot(Time, Canal3_Raw_norm)
    axs_onset[2].plot(Time, Canal3_Env_norm+0.1)
    axs_onset[2].set_title('Sol L ')
#    axs_onset[3].plot(Time, Canal3_Raw_norm)
#    axs_onset[3].plot(Time, Canal3_EnvS_norm)
#    axs_onset[3].set_title('Sol EnvS (L)')
    axs_onset[3].plot(Time, Canal4_Raw_norm, label="Raw")
    axs_onset[3].plot(Time, Canal4_Env_norm, label="Env")
    axs_onset[3].set_title('RF L')
    axs_onset[3].legend()
    axs_onset[4].plot(TimeOnset, onset)
    axs_onset[4].set_title('Onset')
    
    for ax in axs_onset.flat:
        ax.set(xlabel='Time [s]', ylabel='Aplitude')
        
    for ax in axs_onset.flat:
        ax.label_outer()
    
    
    figonset2, axs_onset2 = plt.subplots(5)
    axs_onset2[0].plot(Time, Canal1_Raw_norm)
    axs_onset2[0].plot(Time, Canal1_Env_norm+0.2)
    axs_onset2[0].plot(TimeOnset, onset_rsol_norm)
    axs_onset2[0].set_title('Sol R')
    axs_onset2[1].plot(Time, Canal2_Raw_norm)
    axs_onset2[1].plot(Time, Canal2_Env_norm+0.2)
    axs_onset2[1].plot(TimeOnset, onset_rrf_norm)
    axs_onset2[1].set_title('RF R')
    axs_onset2[2].plot(Time, Canal3_Raw_norm)
    axs_onset2[2].plot(Time, Canal3_Env_norm+0.1)
    axs_onset2[2].plot(TimeOnset, onset_lsol_norm)
    axs_onset2[2].set_title('Sol L ')
    axs_onset2[3].plot(Time, Canal4_Raw_norm, label="Raw")
    axs_onset2[3].plot(Time, Canal4_Env_norm+0.1, label="Env")
    axs_onset2[3].plot(TimeOnset, onset_lrf_norm)
    axs_onset2[3].set_title('RF L ')
    axs_onset2[3].legend()
    axs_onset2[4].plot(TimeOnset, onset)
    axs_onset2[4].set_title('Onset')
    
    for ax in axs_onset2.flat:
        ax.set(xlabel='Time [s]', ylabel='Aplitude')
        
    for ax in axs_onset2.flat:
        ax.label_outer()
    
    
    figonset3, axs_onset3 = plt.subplots(3)
    axs_onset3[0].plot(Time, Canal1_Raw_norm, label="Sol R")
    axs_onset3[0].set_title('Sol')
    axs_onset3[0].plot(Time, Canal3_Raw_norm, label="Sol L")
    axs_onset3[0].plot(TimeOnset, onset_box_norm, label="onset")
    axs_onset3[0].legend()
    
    axs_onset3[1].plot(Time, Canal2_Raw_norm, label="RF R")
    axs_onset3[1].set_title('RF')
    axs_onset3[1].plot(Time, Canal4_Raw_norm, label="RF L")
    axs_onset3[1].plot(TimeOnset, onset_box_norm, label="onset")
    axs_onset3[1].legend()
    
    axs_onset3[2].plot(TimeOnset, rKneeArray_norm, label="Knee R")
    axs_onset3[2].plot(TimeOnset, lKneeArray_norm, label="Knee L")
    axs_onset3[2].plot(TimeRec, rKnee_Record_norm, label="Knee(Rec) R")
    axs_onset3[2].plot(TimeRec, lKnee_Record_norm, label="Knee(Rec) L")
    axs_onset3[2].set_title('Knee Angles')
    axs_onset3[2].plot(TimeOnset, onset_box_norm, label="onset")
    axs_onset3[2].legend()
    
    for ax in axs_onset3.flat:
        ax.set(xlabel='Time [s]', ylabel='Aplitude')
        
    for ax in axs_onset3.flat:
        ax.label_outer()
    
    
    figonset3, axs_angles = plt.subplots(3, sharex= True, sharey= True)
    axs_angles[0].plot(TimeOnset, rHipArray_norm, label="Hip R")
    axs_angles[0].plot(TimeOnset, lHipArray_norm, label="Hip L")
#    axs_angles[0].plot(TimeRec, rHip_Record_norm, label="Hip(Rec) R")
#    axs_angles[0].plot(TimeRec, lHip_Record_norm, label="Hip(Rec) L")
    axs_angles[0].set_title('Hip Angles')
    axs_angles[0].plot(TimeOnset, onset_box_norm, label="onset")
    axs_angles[0].legend()
    
    axs_angles[1].plot(TimeOnset, rKneeArray_norm, label="Knee R")
    axs_angles[1].plot(TimeOnset, lKneeArray_norm, label="Knee L")
#    axs_angles[1].plot(TimeRec, rKnee_Record_norm, label="Knee(Rec) R")
#    axs_angles[1].plot(TimeRec, lKnee_Record_norm, label="Knee(Rec) L")
    axs_angles[1].set_title('Knee Angles')
    axs_angles[1].plot(TimeOnset, onset_box_norm, label="onset")
    axs_angles[1].legend()
    
    axs_angles[2].plot(TimeOnset, rAnkleArray_norm, label="Akle R")
    axs_angles[2].plot(TimeOnset, lAnkleArray_norm, label="Akle L")
#    axs_angles[2].plot(TimeRec, rAnkle_Record_norm, label="Akle(Rec) R")
#    axs_angles[2].plot(TimeRec, lAnkle_Record_norm, label="Akle(Rec) L")
    axs_angles[2].set_title('Akle Angles')
    axs_angles[2].plot(TimeOnset, onset_box_norm, label="onset")
    axs_angles[2].legend()
    
#    axs_angles[1].set_xlim(-200,200)
    
    for ax in axs_angles.flat:
        ax.set(xlabel='Time [s]', ylabel='Aplitude')
        
    for ax in axs_angles.flat:
        ax.label_outer()
        
    
#    axs_onset3[3].plot(TimeSet, rKnee_Sent_norm)
#    axs_onset3[3].plot(TimeSet, lKnee_Sent_norm)
#    axs_onset3[3].plot(TimeRec, rKnee_Record)
#    axs_onset3[3].plot(TimeRec, lKnee_Record)
#    axs_onset3[3].set_title('(R-L) Knee_Sent')
    
else:

    fig, axs_raw = plt.subplots(4)
    axs_raw[0].plot(Time, Canal1_Raw)
    axs_raw[0].set_title('Canal1_Raw')
    axs_raw[1].plot(Time, Canal2_Raw)
    axs_raw[1].set_title('Canal2_Raw')
    axs_raw[2].plot(Time, Canal3_Raw)
    axs_raw[2].set_title('Canal3_Raw')
    axs_raw[3].plot(Time, Canal4_Raw)
    axs_raw[3].set_title('Canal4_Raw')
    
    fig2, axs_envelope = plt.subplots(4)
    axs_envelope[0].plot(Time, Canal1_Env)
    axs_envelope[0].set_title('Canal1_Env')
    axs_envelope[1].plot(Time, Canal2_Env)
    axs_envelope[1].set_title('Canal2_Env')
    axs_envelope[2].plot(Time, Canal3_Env)
    axs_envelope[2].set_title('Canal3_Env')
    axs_envelope[3].plot(Time, Canal4_Env)
    axs_envelope[3].set_title('Canal4_Env')
    


#plt.figure(0)
#plt.plot(Onset)




#PSD
'''
señal_raw = Canal3_Raw
señal_env = Canal3_Env
señal_raw_norm = norm(señal_raw, señal_raw)
señal_env_norm = norm(señal_env, señal_env)

x=fft(señal_raw)
freqz = fftfreq(len(x))
psd = (np.abs(x)**2)/ len(x)
freqz2 = fftfreq(len(psd))

#plt.figure(2)
#fig3, axs_psd = plt.subplots(2, sharex= True, sharey= True)
#plt.plot(fftshift(freqz)*2000, fftshift(np.abs(x)), label="PSD")
#plt.plot(fftshift(freqz)*2000, fftshift(20*np.log10(np.abs(x))), label="PSD")

#plt.title('PSD')
#plt.ylabel('aplitude')
#plt.xlabel('freqz [Hz]')
#plt.xlim([-200,200])




#plt.ylim([0,2])

fig3, axs_analy = plt.subplots(3)
fig3.suptitle('EMG Envelope')
axs_analy[0].plot(Time,señal_raw_norm)
axs_analy[0].plot(Time,señal_env_norm, 'tab:red')
axs_analy[1].plot(fftshift(freqz)*2000, fftshift(20*np.log10(np.abs(x))), label="PSD raw")
axs_analy[1].set_title('PSD log')
axs_analy[2].plot(fftshift(freqz)*2000, fftshift(np.abs(x)), label="PSD raw")
axs_analy[2].set_title('PSD raw')


x=fft(señal_env)
freqz = fftfreq(len(x))
psd = (np.abs(x)**2)/ len(x)
freqz2 = fftfreq(len(psd))

plt.figure(2)
#plt.plot(fftshift(freqz)*2000, fftshift(20*np.log10(np.abs(x))), label="PSD")
axs_analy[1].plot(fftshift(freqz)*2000, fftshift(20*np.log10(np.abs(x))), 'tab:red', label="PSD env")
axs_analy[1].set_xlim(-200,200)
#axs_analy[1].legend()


axs_analy[2].plot(fftshift(freqz)*2000, fftshift(np.abs(x)), 'tab:red', label="PSD env")
#axs_analy[2].set_title('PSD env')
axs_analy[2].set_xlim(-200,200)
axs_analy[2].legend()



#for ax_psd in axs_psd.flat:
#    ax_psd.set(xlabel='freqz [Hz]', ylabel='aplitude')
    
for ax_psd in axs_analy.flat:
    ax_psd.label_outer()

#axs_analy[1].plot(fftshift(freqz2)*2000, fftshift(np.abs(psd)))
#axs_analy[1].set_title('PSD')
'''



#fig=Figure(figsize=(14,7),dpi=110)
#plot1=fig.add_subplot(211)
#plot1.plot(fftshift(freqz)*2000, fftshift(np.abs(x)))
#plot2=fig.add_subplot(212)
#plot2.plot(fftshift(freqz2)*2000, fftshift(np.abs(psd)))


plt.show()  