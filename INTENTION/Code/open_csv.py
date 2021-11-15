import numpy as np
import matplotlib.pyplot as plt
from numpy.fft import fft, fftfreq, fftshift
from matplotlib.figure import Figure
import csv

#read csv

Canal8_Raw_Total = []
with open('121121_EMG_Subject_03_00.csv', newline='') as File:
    reader = csv.DictReader(File)
    for row in reader:
#        print(row['Canal2_Raw'])
        Canal8_Raw_Total=np.concatenate((Canal8_Raw_Total,row['Canal2_Raw']),axis=None)
        
#    plt.plot(Canal8_Raw_Total)

#emg=np.loadtxt('101121_Subject02_EMG_record.csv')[2:3,2:3]

x=fft(Canal8_Raw_Total)
freqz = fftfreq(len(x))
psd= (np.abs(x)**2)/ len(x)
freqz2 = fftfreq(len(psd))

#plt.plot(fftshift(freqz)*2000, fftshift(np.abs(x)))
#plt.plot(fftshift(freqz2)*2000, fftshift(np.abs(psd)))
#plt.plot(Canal8_Raw_Total)

fig3, axs_envelope = plt.subplots(2)
fig3.suptitle('EMG Envelope')
axs_envelope[0].plot(fftshift(freqz)*2000, fftshift(np.abs(x)))
axs_envelope[0].set_title('Tibialis Anterior')
axs_envelope[1].plot(fftshift(freqz2)*2000, fftshift(np.abs(psd)))
axs_envelope[1].set_title('PSD')


#fig=Figure(figsize=(14,7),dpi=110)
#plot1=fig.add_subplot(211)
#plot1.plot(fftshift(freqz)*2000, fftshift(np.abs(x)))
#plot2=fig.add_subplot(212)
#plot2.plot(fftshift(freqz2)*2000, fftshift(np.abs(psd)))
