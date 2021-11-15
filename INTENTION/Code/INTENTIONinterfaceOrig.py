#!/usr/bin/env python3

import socket
import sys
import select
import time
import os

sys.path.append('''C:\Python34\Projects\ARM''')
sys.path.append('''C:\Python34\Lib\site-packages\python_can-1.4-py3.4.egg\can\interfaces''')
import serial
from PCANBasic import PCAN_PCIBUS3, PCAN_BAUD_1M, PCANBasic, PCAN_ERROR_OK, PCAN_ERROR_BUSLIGHT, PCAN_ERROR_BUSHEAVY, PCAN_ERROR_BUSOFF, PCAN_MESSAGE_STANDARD , TPCANMsg, PCAN_NONEBUS, PCAN_ERROR_QRCVEMPTY  ## PCAN-Basic library import
import numpy as np
import struct
#from bitstring import BitArray
#from crccheck.checksum import Checksum8
from EmgTorque_Lower import EmgTorque
from motReader import motReader
from Gait_Model import *
from Exo_ID import *
from Onset_Thread import Onset_Mode
#from EMG_Proportional import *
from Proportional_Thread import ProportionalAnkle
from Decoder import *
from EAST_T import EASTrecord
from ImpedanceController import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
#import math
from scipy import signal
from scipy.signal import hilbert
from scipy.signal import filtfilt,butter,iirnotch,freqz
from scipy.fftpack import fft, fftshift, fftfreq
from threading import Thread
import tkinter as tk
from tkinter import *    # Carga módulo tk (widgets estándar)
from tkinter import ttk, constants  # Carga ttk (para widgets nuevos 8.5+)
#from tkinter.constants import DISABLED, NORMAL
#from tk import ttk

#%%  FUNCIONES  
  
        
def send_can_msg(can_bus,message):
    result = objPCAN.Write(can_bus,message)
    if result != PCAN_ERROR_OK:
        # An error occured, get a text describing the error and show it
        result = objPCAN.GetErrorText(result)
        print(result)
#    else:
        #print("Message sent successfully")
    return result


def read_can_msg(can_ch):
    global msg_received
    readResult = objPCAN.Read(channel)
    if readResult[0] == PCAN_ERROR_OK:
        msg_received     = readResult[1] #readResult[1] TPCANMsg() 
    else:
        # An error occured, get a text describing the error and show it
        result = objPCAN.GetErrorText(readResult[0])
        print('Error: ', result[1])
        msg_received     = readResult[1]
    return msg_received

def accurate_delay(delay):
    ''' Function to provide accurate time delay in millisecond '''
    _ = time.perf_counter() + delay/1000
    while time.perf_counter() < _:
        pass



def btOK():
#    try:
        
        for i in range(30):
            feedbackBox.insert(END, "ERROR: CAN conection"+str(i)) 
        global subject
        global date
        global trial
        global repeat
        global MVC1
        global MVC2
        global MVC3
        
        subject=cuadroName.get()
        date=cuadroDate.get()
        trial=cuadroTrial.get()
        if cuadroRepeat.get() =="":
            feedbackBox.insert(END, "repeat empty")
        else:
            repeat=int(cuadroRepeat.get())
#        repeat=repeat-2
        MVC1=cuadroMVC1.get()
        MVC2=cuadroMVC2.get()
        MVC3=cuadroMVC3.get()
        
        if subject != "" and date != "" and trial != "" and repeat != "":
            print(date + '_' + subject + '_' + trial + '_' + str(repeat) + '_' + MVC1 + '_' + MVC2 + '_' + MVC3)
        else:
            feedbackBox.insert(END, "features empty")
#        buttonOK.state()
#        buttonTESTE['state']= DISABLED
#        print(buttonOK['state'])
#    except:
#        print("ERROR")
       
    
def gaitSection():
    
    if cuadroRepeat.get() =="":
        steps=2
#        raise NameError('"steps" EMPTY')
    else:
        steps=int(cuadroRepeat.get())
        
    
    joinangles = gait(objPCAN,steps)
#            OwnWalk(objPCAN, steps)
    
    window=Tk()
    window.title("joinangles")
    plot_button=Button(master=window, command=multiPlot(joinangles,window)) 
    window.mainloop()  

    
def OnsetEAST():
    
    if cuadroRepeat.get() =="" or assistanceBox.get() =="":
#            feedbackBox.insert(END, "features empty")
        repeat = 10
        assistance = 100
#            raise NameError ("repeat or assistance empty")
    else:
        repeat = int(cuadroRepeat.get())
        assistance = int(assistanceBox.get())
        
    NumChEMG = 2    
    features = np.zeros(NumChEMG*3)
    
    #features = [th0, thff0, pff0, th1, thff1, pff1]
    features[0] = float(cuadroOnset.get())
    features[1] = float(cuadroOffset.get())
    features[2] = float(period_off.get())
    features[3] = float(cuadroOnset2.get())
    features[4] = float(cuadroOffset2.get())
    features[5] = float(period_off2.get())
    
#    features[3] = "%.3f" %(np.std(Canal2_Env_Total)*1.5)
#    features[4] = "%.3f" %(np.std(Canal2_Env_Total)*1.5)
#    features[5] = float(period_off.get())
    
    rawData = Onset_Mode(objPCAN, repeat, assistance, features)
#    rawData = [Canal1_Total, Canal2_Total, Onset, 0]
    
    ## SAVE
#        df_o = pd.DataFrame(Canal1_Total,columns=['Canal1'])
#        df1_o = pd.DataFrame(Canal2_Total,columns=['Canal2'])
#        
#        df_o = pd.concat([df_o,df1_o], axis = 1)
#        date=''
#        subject=''
#        trial=''
#        df_o.to_csv(date + '_' + subject + '_' + 'ONSET EAST' + '_' + trial + '.csv',sep=',')

    Passive(objPCAN)
    feedbackBox.insert(END, "EXO Stoped")
    
    window=Tk()
    window.title("Record")
    plot_button=Button(master=window, command = EMGPlot(rawData,window))
#    window=Tk()
#    window.title("Onset_Total")
#    plot_button=Button(master=window, command = plot_sample(rawData[4],window))
    
    window.mainloop()   
    
    

#        print("CAN closed")  
#            
#        df = pd.DataFrame(Canal1,columns=['EMG-TA'])
#        df1 = pd.DataFrame(Canal2,columns=['EMG-PT'])
#        
#        df2 = pd.DataFrame(Canal1_env_Total,columns=['EMG-ENVELOPE-TA'])
#        df3 = pd.DataFrame(Canal2_env_Total,columns=['EMG-ENVELOPE-PT'])
#        
#        df4 = pd.DataFrame(detectionOnTotal,columns=['ONSET'])
#        df5 = pd.DataFrame(detectionOffTotal,columns=['OFFSET'])
#        df6 = pd.DataFrame(Time_ang_total,columns=['TORQUE-TIME'])
#        
#        df7 = pd.DataFrame([2000],columns=['FS_EMG'])
#        df8=pd.DataFrame(comp_time,columns=['Computational time'])
#        
#        df = pd.concat([df,df1,df,df3,df4,df5,df6,df7,df8], axis = 1)
#
#
#
#        df.to_csv(date + '_' + subject + '_' + 'ONSET' + '_' + trial + '.csv',sep=',')
#        return
#        print('Onset Detection')


def Proportionald():
    global total_angle,canal1_Env_Total,canal1_Raw_Total

    try:
        if cuadroRepeat.get() =="":
            repeat=5
            assistance = 100
#            raise TypeError('"Cycles" EMPTY')
        else:
            repeat=int(cuadroRepeat.get())
            assistance = int(assistanceBox.get())
            
        if cuadroOnset.get() =="0" or cuadroOffset.get() =="0" or cuadroMax.get() =="0" or cuadroMin.get() =="0":
            raise TypeError('"Features" EMPTY')
            
        else:
            NumChEMG = 2    
            features = np.zeros(NumChEMG*3)
            
            #features = [th0, thff0, pff0, th1, thff1, pff1]
            features[0] = float(cuadroOnset.get())
            features[1] = float(cuadroOffset.get())
            features[2] = float(period_off.get())
            features[3] = float(cuadroOnset2.get())
            features[4] = float(cuadroOffset2.get())
            features[5] = float(period_off2.get())
            
            refvalor = np.zeros(NumChEMG*3)
            
            #refvalor = [max, min, ref] 
            refvalor[0] = float(cuadroMax.get())
            refvalor[1] = float(cuadroMin.get())
            refvalor[2] = 30
            
            
            
        rawData = ProportionalAnkle(objPCAN, repeat, assistance, features, refvalor)
#        rawData = ProportionalAnkle(repeat,objPCAN,onsetTH,offsetTH,maxvalue,minvalue)
        interactionMSG.set("Serial Port closed")
        feedbackBox.insert(END, "Serial Port closed")
        try:
            
            window=Tk()
            window.title("canal1")
            plot_button=Button(master=window, command = EMGPlot(rawData,window))
            window=Tk()
            window.title("total_angle")
            plot_button=Button(master=window, command = plot_sample(rawData[4],window))
#            window=Tk()
#            window.title("canal1_Raw_Total")
#            plot_button=Button(master=window, command=plot_sample(canal1_Raw_Total,window))
#            window=Tk()
#            window.title("canal1_Env_Total")
#            plot_button=Button(master=window, command=plot_sample(canal1_Env_Total,window))
#            window=Tk()
#            window.title("total_angle")
#            plot_button=Button(master=window, command=plot_sample(total_angle,window))
            
            window.mainloop()
#            print("END")    
        except:
             interactionMSG.set("ERROR: EMG plot")  
             feedbackBox.insert(END, "ERROR: EMG plot")
             raise Exception("PLOT")                
            
    except KeyboardInterrupt:
        interactionMSG.set('Interrupt')
        feedbackBox.insert(END, "Interrupt")
        raise
            
    except TypeError as text:
        interactionMSG.set(text)
        feedbackBox.insert(END, text)
        raise
            
    except NameError as text:
        interactionMSG.set(text)
        feedbackBox.insert(END, text)
        raise   
        
    except:
        raise 
        
    #time.sleep(1)
    ExoClose(objPCAN)
    feedbackBox.insert(END, "CAN closed")
            
'''            
    df = pd.DataFrame(Canal1_Total,columns=['EMG-TA'])
    df1 = pd.DataFrame(Canal2_Total,columns=['EMG-PT'])

    df2 = pd.DataFrame(Canal1_env_Total,columns=['EMG-ENVELOPE-TA'])
    df3 = pd.DataFrame(Canal2_env_Total,columns=['EMG-ENVELOPE-PT'])

    df4 = pd.DataFrame(total_angle,columns=['ANGLES'])
    df5 = pd.DataFrame(periodTime,columns=['TIME'])
    df6 = pd.DataFrame([2000],columns=['FS_EMG'])
    df7=pd.DataFrame(comp_time,columns=['Computational time'])
    df = pd.concat([df,df1,df,df3,df4,df5,df6,df7], axis = 1)

    df.to_csv(date + '_' + subject + '_' + 'PROPORTIONAL' + '_' + trial + '.csv',sep=',')
'''   


def impedanceSection():
    
    if cuadroRepeat.get() =="" or assistanceBox.get() =="" or stiffnessBox.get() == "":
        gaits = 3
        assistance = 100
        stiffness = 30
#        speed=2
#        raise NameError('Fill in: "cycles, assistance & stiffness"')
    else:
        gaits = int(cuadroRepeat.get())
        assistance = int(assistanceBox.get())
        stiffness = int(stiffnessBox.get())
#        speed=int(speedBox.get())
        
#    [rHip, rKnee, rAnkle, lHip, 
#     lKnee, lAnkle] = Impedance(objPCAN, speed, secods)
#        [rHip, rKnee, rAnkle, lHip, 
#         lKnee, lAnkle] 
    valor = impedance(objPCAN, gaits, assistance, stiffness)
    
    try:
        window=Tk()
        window.title("ImpedanceRecord")
        plot_button=Button(master=window, command=multiPlot(valor,window))         
#        window=Tk()
#        window.title("rHip")
#        plot_button=Button(master=window, command=plot_sample(rHip,window)) 
#        window=Tk()
#        window.title("rKnee")
#        plot_button=Button(master=window, command=plot_sample(rKnee,window)) 
#        window=Tk()
#        window.title("rAnkle")
#        plot_button=Button(master=window, command=plot_sample(rAnkle,window)) 
#        window=Tk()
#        window.title("lHip")
#        plot_button=Button(master=window, command=plot_sample(lHip,window)) 
#        window=Tk()
#        window.title("lKnee")
#        plot_button=Button(master=window, command=plot_sample(lKnee,window)) 
#        window=Tk()
#        window.title("lAnkle")
#        plot_button=Button(master=window, command=plot_sample(lAnkle,window)) 
        window.mainloop()
        
    except:
        interactionMSG.set("ERROR: EMG plot")  
        feedbackBox.insert(END, "ERROR: EMG plot")
        raise Exception("PLOT")  
    
    

def btRUN(event):
    global rAnkle_Record
    print("RUN") 
    try:
        try:
            objPCAN
        except:
            raise NameError ("ERROR: CAN conection")
        ## TYPE CONTROL (1:POSITION / 2:STIFFNESS / 3:TORQUE / 4:DISABLE / 5:STOPPED)
        
        ##3 LEER ÁNGULOS PARA COMPROBAR SI ESTA DE PIE!!!!!!!!!!!!!!!!!!!

        Stop_Run=False
        MS1=MS.get()
        MD1=MD.get()
        OD1=OD.get()
        EP1=EP.get()
        if (MS1 == 0) & (MD1 == 0) & (OD1 == 0) & (EP1 == 0):
            interactionMSG.set("select an option") 
            feedbackBox.insert(END, "select an option")
            
        elif (MS1 == 1) & (MD1 == 0) & (OD1 == 0) & (EP1 == 0):
            
            interactionMSG.set("OWN GAIT") 
            feedbackBox.insert(END, "OWN GAIT")
            gaitSection()
            interactionMSG.set("OWN GAIT OFF") 
            feedbackBox.insert(END, "OWN GAIT OFF")
            
            
        elif (MS1 == 0) & (MD1 == 1) & (OD1 == 0) & (EP1 == 0):
            
            interactionMSG.set("IMPEDANCE") 
            feedbackBox.insert(END, "IMPEDANCE")
            impedanceSection()
            interactionMSG.set("IMPEDANCE OFF") 
            feedbackBox.insert(END, "IMPEDANCE OFF")

                 
        elif (MS1 == 0) & (MD1 == 0) & (OD1 == 1) & (EP1 == 0):
            interactionMSG.set("Onset EMG") 
            feedbackBox.insert(END, "Onset EMG")
            OnsetEAST()
            interactionMSG.set("Onset Off") 
            feedbackBox.insert(END, "Onset Off")

        elif (MS1 == 0) & (MD1 == 0) & (OD1 == 0) & (EP1 == 1):
                
            interactionMSG.set("Proporcional EMG") 
            feedbackBox.insert(END, "Proporcional EMG")
            Proportionald()
            interactionMSG.set("Proporcional Off") 
            feedbackBox.insert(END, "Proporcional Off")
            
        else:
            interactionMSG.set("select just one option") 
            feedbackBox.insert(END, "too many options")
    
    except KeyboardInterrupt:
        Stop_Run=True
        print('interrupt')
        try:
            ExoClose(objPCAN)
            text="INTERRUPT"
            feedbackBox.insert(END, "EXO CLOSE")
        except NameError:
            text="ERROR: Turn OFF exo"
        can.set(text)
        feedbackBox.insert(END, text)
        raise
            
    except NameError as text:
        interactionMSG.set(text)
        feedbackBox.insert(END, text)
        raise
            
    except:
        can.set("ERROR: unknown") 
        feedbackBox.insert(END, "ERROR: unknown")
        raise

def btCAN(event):
        
    try:
        global objPCAN
        channel = PCAN_PCIBUS3
        baud    = PCAN_BAUD_1M
        # The Plug & Play Channel (PCAN-USB) is initialized
#        recording_time=2
#        accurate_delay(recording_time*1000)
        objPCAN = PCANBasic()        
        result = objPCAN.Initialize(channel, baud)

        if result != PCAN_ERROR_OK:
            # An error occured, get a text describing the error and show it
            result = objPCAN.GetErrorText(result)
            print(result[1])
#            can.set(result[1])
            feedbackBox.insert(END, str(result[1]))
#            raise TypeError (str(result[1]))
        else:
            can.set("PCAN was initialized")
            feedbackBox.insert(END, "PCAN was initialized")
        
        # Check the status of the USB Channel
        result = objPCAN.GetStatus(channel)
        if result == PCAN_ERROR_BUSLIGHT:
            raise TypeError ("PCAN_PCIBUS (Ch-x): Handling a BUS-LIGHT status...")
        elif result == PCAN_ERROR_BUSHEAVY:
            raise TypeError ("PCAN_PCIBUS (Ch-x): Handling a BUS-HEAVY status...")
        elif result == PCAN_ERROR_BUSOFF:
            raise TypeError ("PCAN_PCIBUS (Ch-x): Handling a BUS-OFF status...")
        elif result == PCAN_ERROR_OK:
#            raise TypeError ("PCAN_PCIBUS (Ch-x): Status is OK")
            can.set("PCAN_PCIBUS (Ch-x): Status is OK")
            feedbackBox.insert(END, "PCAN_PCIBUS (Ch-x): Status is OK")
            
        else:
            # An error occured, get a text describing the error and show it
            result = objPCAN.GetErrorText(result)
            raise TypeError (result[1])
            
        ## Turn On exo
        joinangle = TurnOn(objPCAN)
#        print(joinangle[2]-256)#signed 8-bit

        if len(joinangle) != 0:
            rHip = joinangle[0]
            rknee = joinangle[1]
            rAnkle = joinangle[2]
            lHip = joinangle[3]
            lKnee = joinangle[4]
            lAnkle = joinangle[5]
            
            feedbackBox.insert(END,"left hip " + str(lHip) + "      /   "  + "right hip "+ str(rHip))
            feedbackBox.insert(END,"left knee " + str(lKnee) + "   /   "  +  "right knee "+ str(rknee))
            feedbackBox.insert(END,"left ankle " + str(lAnkle) + "  /   "  +  "right ankle "+ str(rAnkle))
            
        else:
            raise TypeError("no exo angles recived")

    except TypeError as text:
        can.set(text)
        feedbackBox.insert(END, text)
        raise

def battery(event):
    
    voltage = BatteryVoltage(objPCAN)
    
    if voltage == np.nan:
        feedbackBox.insert(END,"Battery Voltage: " + " ERROR")   
    else:
        strvoltage=str(voltage)
        feedbackBox.insert(END,"Battery Voltage: " + strvoltage[0:-1] + "." + strvoltage[-1] + " V")
        
#    state = ExoState(objPCAN)
#    print(state)
        
def Footpressure(event):
    
    if cuadroRepeat.get() =="":
        repeat=10
    else:
        repeat=int(cuadroRepeat.get())
            
#    t0=time.time() 
#    print(t0,time.time())
#    _ = time.perf_counter() + delay/1000
#    while time.time()-t0 < repeat:
#    rheel,rtoe,lheel,ltoe = Footsensor(objPCAN,repeat)
    valor = Footsensor(objPCAN,repeat)
    
#    feedbackBox.insert(END,"Battery Voltage: " + str(rheel[-1]) + "V")
#    feedbackBox.insert(END,"Battery Voltage: " + str(voltage[-1]) + "V")
    window=Tk()
    window.title("rheel")
    plot_button=Button(master=window, command=EMGPlot(valor,window))
#    plot_button=Button(master=window, command=plot_sample(rheel,window))
#    window=Tk()
#    window.title("rtoe")
#    plot_button=Button(master=window, command=plot_sample(rtoe,window))
#    window=Tk()
#    window.title("lheel")
#    plot_button=Button(master=window, command=plot_sample(lheel,window))
#    window=Tk()
#    window.title("ltoe")
#    plot_button=Button(master=window, command=plot_sample(ltoe,window))
#    print(time.time()-t0)


    
def btEAST(event):
    print("BEGINING") 
    global Canal1_Env_Total, Canal2_Env_Total, Canal1_Raw_Total, Canal2_Raw_Total
    try:
        if cuadroRepeat.get() =="":
            repeat=3
#            raise TypeError('"Cycles" EMPTY')
        else:
            repeat=int(cuadroRepeat.get())
        
        Data = EASTrecord(repeat)
        
    
        interactionMSG.set("Serial Port closed")
        feedbackBox.insert(END, "Serial Port closed")
        Canal1_Raw_Total = Data[0]
        Canal2_Raw_Total = Data[1]
        Canal1_Env_Total = Data[2]
        Canal2_Env_Total = Data[3]
        
        
#        b, a = signal.butter(2,6/(2000/2.),btype='low')
#        emgAbs=np.abs(Data[0])
#        envelope=signal.filtfilt(b,a,emgAbs)
        
#        Data[0]=Canal1_env
#        print(Canal1_env)

        
        max_value.set("%.3f" % max(Canal1_Env_Total))
        min_value.set("%.3f" %min(Canal1_Env_Total))
        onset.set("%.3f" %(np.std(Canal1_Env_Total)*1.5))
        offset.set("%.3f" %(np.std(Canal1_Env_Total)*1.5))
        period_off.set(0.1)
        
        max_value2.set("%.3f" % max(Canal2_Env_Total))
        min_value2.set("%.3f" %min(Canal2_Env_Total))
        onset2.set("%.3f" %(np.std(Canal2_Env_Total)*1.5))
        offset2.set("%.3f" %(np.std(Canal2_Env_Total)*1.5))
        period_off2.set(0.1)
        
        ## envelope different
#        c1RT=Canal1_Raw_Total-np.mean(Canal1_Raw_Total)
#        analitic_envelope=np.imag(hilbert(c1RT))
#        envelope= np.abs(analitic_envelope)
#        inst_phase=np.unwrap(np.angle(analitic_envelope))
#        inst_freq=(np.diff(inst_phase))/(2*np.pi)*2000
        
        
#        cutoff = 20
#        emgAbs=np.abs(Canal1_Raw_Total)
#        b, a=signal.butter(2,6/(2000/2.),btype='low')
#        envelope=signal.filtfilt(b,a,emgAbs)
        
        
        try:
            window=Tk()
            window.title("EMG Recorded")
            plot_button=Button(master=window, command = EMGPlot(Data,window))
#            window=Tk()
#            window.title("enve total")
#            plot_button=Button(master=window, command = plot_sample(envelope[200:-1],window))

            window.mainloop()
#            print("END")           
        except:
             interactionMSG.set("ERROR: EMG plot")  
             feedbackBox.insert(END, "ERROR: EMG plot")
             raise Exception("PLOT")
            
    except KeyboardInterrupt:
        interactionMSG.set('Interrupt')
        feedbackBox.insert(END, "Interrupt")
        raise
            
    except TypeError as text:
        interactionMSG.set(text)
        feedbackBox.insert(END, text)
        raise
            
    except NameError as text:
        interactionMSG.set(text)
        feedbackBox.insert(END, text)
        raise   
        
    except:
        raise

    
        
    
def plot_sample(valor,window): 
    
    fig=Figure(figsize=(12,5),dpi=100)
    plot1=fig.add_subplot(111)
    plot1.plot(valor)
    canvas=FigureCanvasTkAgg(fig,master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()
    toolbar=NavigationToolbar2Tk(canvas,window)
    toolbar.update()
    canvas.get_tk_widget().pack()
    
    

def multiPlot(valor,window):
    
    fig=Figure(figsize=(12,7),dpi=100)
    plot1=fig.add_subplot(321)
    plot1.plot(valor[3])
    plot2=fig.add_subplot(322)
    plot2.plot(valor[0])
    plot3=fig.add_subplot(323)
    plot3.plot(valor[4])
    plot4=fig.add_subplot(324)
    plot4.plot(valor[1])
    plot5=fig.add_subplot(325)
    plot5.plot(valor[5])
    plot6=fig.add_subplot(326)
    plot6.plot(valor[2])
    canvas=FigureCanvasTkAgg(fig,master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()
    toolbar=NavigationToolbar2Tk(canvas,window)
    toolbar.update()
    canvas.get_tk_widget().pack()
    
    
    
def EMGPlot(valor,window):
    
    fig=Figure(figsize=(12,7),dpi=100)
    plot1=fig.add_subplot(221)
    plot1.plot(valor[0])
    plot2=fig.add_subplot(222)
    plot2.plot(valor[1])
    plot3=fig.add_subplot(223)
    plot3.plot(valor[2])
    plot4=fig.add_subplot(224)
    plot4.plot(valor[3])
    canvas=FigureCanvasTkAgg(fig,master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()
    toolbar=NavigationToolbar2Tk(canvas,window)
    toolbar.update()
    canvas.get_tk_widget().pack()
    
    
#    root_plot = tk.Tk()
#    root_plot.title('Real Time EMG')
#    root_plot.configure(background='light blue')
#    root_plot.geometry("1400x1000")
    #fig = Figure()
#    fig, (ax1,ax2) = plt.subplots(1,2,sharey=False)
#    
#    
#    #ax = fig.add_subplot(111)
#    ax1.set_title('Channel 1')
#    ax1.set_xlabel('Time')
#    ax1.set_ylabel('EMG Amplitude')
#    ax1.set_xlim(0,0.2)
#    ax1.set_ylim(-200,200)
#    lines1 = ax1.plot([],[])[0]
#    
#    #ax = fig.add_subplot(1)
#    ax2.set_title('Channel 2')
#    ax2.set_xlabel('Time')
#    ax2.set_ylabel('Torque')
#    ax2.set_xlim(0,0.2)
#    ax2.set_ylim(-200,200)
#    lines2 = ax2.plot([],[])[0]
#    
#    lines1.set_ydata(valor)
#    lines2.set_ydata(valor2)  
    
#    canvas = FigureCanvasTkAgg(fig,master=root_plot)
#    canvas.get_tk_widget().place(x=10,y=10,width=1000,height=400)
#    canvas.draw()
#    root_plot.after(200,plot_sample)
#    root_plot.mainloop()
    
#    return(Canal1,Canal3, Canal2)
    
#def exoClose():
#    Close(objPCAN)
         
def exitF(event):  
    root.destroy
    
def btStop(event):  
    Stop_Run=False
    try:
        ExoClose(objPCAN)
        interactionMSG.set("Stop")
        feedbackBox.insert(END, "Stop")
    except:
        try:
            objPCAN
            interactionMSG.set("ERROR: Turn OFF exo")
            feedbackBox.insert(END, "ERROR: Turn OFF exo")
            raise
        except NameError:
            interactionMSG.set("ERROR: CAN conection") 
            feedbackBox.insert(END, "ERROR: CAN conection")
    
def btStandUp(event):
    try:
        interactionMSG.set("Stad-Up")
        feedbackBox.insert(END, "Stad-Up")
        StandUp(objPCAN) 
        interactionMSG.set("Stad-Up end")
        feedbackBox.insert(END, "Stad-Up end")
    except:
        try:
            objPCAN
            interactionMSG.set("ERROR: Stad-Up process")
            feedbackBox.insert(END, "ERROR: Stad-Up process")
            raise
        except NameError:
            interactionMSG.set("ERROR: CAN conection") 
            feedbackBox.insert(END, "ERROR: CAN conection")

def btSitDown(event):
    try: 
        interactionMSG.set("Sit-Down")
        feedbackBox.insert(END, "Sit-Down")
        SitDown(objPCAN)
        interactionMSG.set("Sit-Down end")
        feedbackBox.insert(END, "Sit-Down end")
    except:
        try:
            objPCAN
            interactionMSG.set("ERROR: Sit-Down process")
            feedbackBox.insert(END, "ERROR: Sit-Down process")
            raise
        except NameError:
            interactionMSG.set("ERROR: CAN conection")
            feedbackBox.insert(END, "ERROR: CAN conection")

def btWalking(event):
    
    try:
        if speedBox.get() =="":
            raise NameError('"speed" EMPTY')
        else:
            speed=int(speedBox.get())
        try:
            objPCAN
        except:
            raise NameError("ERROR: CAN conection")
            
        interactionMSG.set("Walk Start")
        feedbackBox.insert(END, "Walk Start")
        recording_time=2
        accurate_delay(recording_time*1000)
        ExoWalk(objPCAN,speed)
        
    except NameError as text:
#        try:
#            objPCAN
        try:
            ExoClose(objPCAN)
            interactionMSG.set("ERROR: walk function")
            feedbackBox.insert(END, "ERROR: walk function")
            raise
        except:
            interactionMSG.set("ERROR: Turn OFF exo")
            feedbackBox.insert(END, "ERROR: Turn OFF exo")
#        except NameError:
#            interactionMSG.set("ERROR: CAN conection") 
#            feedbackBox.insert(END, "ERROR: CAN conection")
        interactionMSG.set(text)
        feedbackBox.insert(END, text)
        raise
    except:
        raise

def btAngles():
    try:
        if cuadroRepeat.get() =="":
            seconds=0
#                raise TypeError('"steps" EMPTY')
        else:
            seconds=int(cuadroRepeat.get())
        try:
            objPCAN
        except:
            raise TypeError("ERROR: CAN conection")
            
        joinangle = readAngle(objPCAN,seconds)
        print(joinangle[0])
            
        if len(joinangle) != 0 and seconds == 0:
            
            rHip = str(joinangle[0])
            rKnee = str(joinangle[1])
            rAnkle = str(joinangle[2])
            lHip = str(joinangle[3])
            lKnee = str(joinangle[4])
            lAnkle = str(joinangle[5])
            
            feedbackBox.insert(END,"---------------------------------------")
            feedbackBox.insert(END,"left hip " + lHip[1:-2] + "      /   "  + "right hip "+ rHip[1:-2])
            feedbackBox.insert(END,"left knee " + lKnee[1:-2] + "   /   "  +  "right knee "+ rKnee[1:-2])
            feedbackBox.insert(END,"left ankle " + lAnkle[1:-2] + "  /   "  +  "right ankle "+ rAnkle[1:-2])
            
        else:
            try:
                rHip = joinangle[0]
                rKnee = joinangle[1]
                rAnkle = joinangle[2]
                lHip = joinangle[3]
                lKnee = joinangle[4]
                lAnkle = joinangle[5]
                
#                window=Tk()
#                window.title("rHip")
#                plot_button=Button(master=window, command=plot_sample(rHip,window)) 
                window=Tk()
                window.title("Angles")
                plot_button=Button(master=window, command=multiPlot(joinangle,window)) 
#                window=Tk()
#                window.title("rAnkle")
#                plot_button=Button(master=window, command=plot_sample(rAnkle,window)) 
#                window=Tk()
#                window.title("lHip")
#                plot_button=Button(master=window, command=plot_sample(lHip,window)) 
#                window=Tk()
#                window.title("lKnee")
#                plot_button=Button(master=window, command=plot_sample(lKnee,window)) 
#                window=Tk()
#                window.title("lAnkle")
#                plot_button=Button(master=window, command=plot_sample(lAnkle,window)) 
                window.mainloop()
        
            except:
#                raise TypeError("ERROR: EMG plot") 
                raise 
        
    except TypeError as text:
        interactionMSG.set(text)
        feedbackBox.insert(END, text)
        raise
    
        


def btCompliance(event):
    try:
        interactionMSG.set("Compliance Mode")
        feedbackBox.insert(END, "Compliance Mode")
        Compliance(objPCAN)
    except:
        try:
            objPCAN
            interactionMSG.set("ERROR: Compliance function")
            feedbackBox.insert(END, "ERROR: Compliance function")
            raise
        except NameError:
            interactionMSG.set("ERROR: CAN conection") 
            feedbackBox.insert(END, "ERROR: CAN conection")
        
        
def btPassive(event):
    try:
        interactionMSG.set("Passive Mode")
        feedbackBox.insert(END, "Passive Mode")
        Passive(objPCAN)
    except:
        try:
            objPCAN
            interactionMSG.set("ERROR: Passive function")
            feedbackBox.insert(END, "ERROR: Passive function")
            raise
        except NameError:
            interactionMSG.set("ERROR: CAN conection") 
            feedbackBox.insert(END, "ERROR: CAN conection")

def btStopExo(event):
    try:
        StopWalk(objPCAN)
        interactionMSG.set("STOP EXO")
        feedbackBox.insert(END, "STOP EXO")
    except:
        try:
            objPCAN
            interactionMSG.set("ERROR: stop walk function")
            feedbackBox.insert(END, "ERROR: stop walk function")
            raise
        except NameError:
            interactionMSG.set("ERROR: CAN conection") 
            feedbackBox.insert(END, "ERROR: CAN conection")
            
def chBox1(event):
    if MS.get() == 0:
        MS.set(1)
    else:
        MS.set(0)
def chBox2(event):
    if MD.get() == 0:
        MD.set(1)
    else:
        MD.set(0)
def chBox3(event):
    if OD.get() == 0:
        OD.set(1)
    else:
        OD.set(0)
def chBox4(event):
    if EP.get() == 0:
        EP.set(1)
    else:
        EP.set(0)
            

#%%  INTERFAZ     
root=Tk()
root.title("The EXTEND Project")
root.config(bg="black")
##

#imgicon = PhotoImage(file=os.path.join('/home/nrg/Documentos','Marvin_Cabeza.gif'))
imgicon = PhotoImage(file=os.path.join('/home/nrg/Documentos','intention2.gif'))
root.tk.call('wm', 'iconphoto', root._w, imgicon)  

miFrame=Frame()
#miFrame.place(x=0, y=0)
miFrame.pack()
#miFrame.pack(side=TOP, fill=BOTH, expand=True)
miFrame.config(width="1400", height="100")
miFrame.config(cursor="hand2")

CanFrame=Frame()
#CanFrame.place(x=0, y=200)
#CanFrame.pack()
CanFrame.pack(side=LEFT, fill=BOTH, expand=True)
CanFrame.config(width="900", height="700", bg="#FAF3DD")
CanFrame.config(cursor="hand2")

MesoFrame=Frame()
#MesoFrame.place(x=500, y=200)
#MesoFrame.pack()
MesoFrame.pack(side=LEFT, fill=BOTH, expand=True)
MesoFrame.config(width="300", height="450", bg="#B8F2E6")
MesoFrame.config(cursor="hand2")
root.bind('Q',btStop)
root.bind('E',exitF)
root.bind('P',btPassive)
root.bind('C',btCompliance)
root.bind('U',btStandUp)
root.bind('D',btSitDown)
root.bind('R',btEAST)
root.bind('w',btWalking)
root.bind('s',btStopExo)
root.bind('<space>',btCAN)
root.bind('<Return>',btRUN)

root.bind('<exclam>',chBox1)
root.bind('<quotedbl>',chBox2)
root.bind('<periodcentered>',chBox3)
root.bind('<dollar>',chBox4)

root.bind('F',Footpressure)
root.bind('B',battery)

#Label(MesoFrame, text="EAST COMMUNICATION:", bg="#B8F2E6", fg="#FF969E",font=("Helvetica bold",12)).place(x=10, y=130)
#%% GENERAL FRAME
Label(miFrame, text="GENERAL INFORMATION:", fg="#5E6472", font=("Helvetica",12)).place(x=10, y=15)
#subject=StringVar()
#date=StringVar()
#trial=StringVar()
can=StringVar()
#canTest=StringVar()
dest=StringVar()
meso=StringVar()
ipinit=StringVar()

repeatint = IntVar()
onset = IntVar()
offset = IntVar()
period_off = IntVar()
max_value = IntVar()
min_value = IntVar()
onset2 = IntVar()
offset2 = IntVar()
period_off2 = IntVar()
max_value2 = IntVar()
min_value2 = IntVar()

MS = IntVar()
MD = IntVar()
OD = IntVar()
EP = IntVar()


#bool(Stop_Run)
Stop_Run = True

IP=StringVar() 

nameLabel=Label(miFrame, fg="#5E6472", text="Name:")
nameLabel.grid(row=0, column=0, padx=10, pady=10)
nameLabel.place(x=10, y=50)
dateLabel=Label(miFrame, fg="#5E6472", text="Date:")
dateLabel.grid(row=0, column=1, padx=10, pady=10)
dateLabel.place(x=250, y=50)
trialLabel=Label(miFrame, fg="#5E6472", text="Trial:")
trialLabel.grid(row=0, column=2, padx=10, pady=10)
trialLabel.place(x=490, y=50)
repeatLabel=Label(miFrame, fg="#5E6472", text="Cycles:")
repeatLabel.grid(row=0, column=3, padx=10, pady=10)
repeatLabel.place(x=730, y=50)
cuadroName = Entry(miFrame)
cuadroName.grid(row=0, column=0, padx=10, pady=10)
cuadroName.place(x=60, y=50)
cuadroDate = Entry(miFrame)
cuadroDate.grid(row=0, column=1, padx=10, pady=10)
cuadroDate.place(x=290, y=50)
cuadroTrial = Entry(miFrame)
cuadroTrial.grid(row=0, column=2, padx=10, pady=10)
cuadroTrial.place(x=530, y=50)
cuadroRepeat = Entry(miFrame)
cuadroRepeat.grid(row=0, column=3, padx=10, pady=10)
cuadroRepeat.place(x=790, y=50)

buttonOK=Button(miFrame, text="OK", height = 1, width = 2, command= lambda: btOK()).place(x=1225, y=20)
buttonRUN=Button(miFrame, text="RUN", height = 1, width = 2, command= lambda: btRUN(event=True)).place(x=1225, y=60)
#buttonTESTE=Button(root, text="TESTE", command=btOK)
#buttonTESTE.pack()

mvc1Label=Label(miFrame, fg="#5E6472", text="MVC1:")
mvc1Label.grid(row=0, column=4, padx=10, pady=10)
mvc1Label.place(x=970, y=10)
mvc2Label=Label(miFrame, fg="#5E6472", text="MVC2:")
mvc2Label.grid(row=0, column=4, padx=10, pady=10)
mvc2Label.place(x=970, y=40)
mvc3Label=Label(miFrame, fg="#5E6472", text="MVC3:")
mvc3Label.grid(row=0, column=4, padx=10, pady=10)
mvc3Label.place(x=970, y=70)
cuadroMVC1 = Entry(miFrame)
cuadroMVC1.grid(row=0, column=4, padx=10, pady=10)
cuadroMVC1.place(x=1020, y=10)
cuadroMVC2 = Entry(miFrame)
cuadroMVC2.grid(row=0, column=4, padx=10, pady=10)
cuadroMVC2.place(x=1020, y=40)
cuadroMVC3 = Entry(miFrame)
cuadroMVC3.grid(row=0, column=4, padx=10, pady=10)
cuadroMVC3.place(x=1020, y=70)

#%% CAN FRAME
Label(CanFrame, text="CAN COMMUNICATION:", bg="#FAF3DD", fg="#2AC4DB",font=("Helvetica bold",12)).grid(row=0, column=0, padx=5, pady=5, columnspan=3, sticky="w")

#Label(CanFrame, text="CAN COMMUNICATION:", bg="#FAF3DD", fg="#2AC4DB",font=("Helvetica bold",12)).place(x=10, y=15)

#buttonCAN=Button(CanFrame, text="Connect CAN", height = 1, width = 10, command= lambda: btCAN()).place(x=10, y=50)
buttonCAN=Button(CanFrame, text="Connect CAN", height = 1, width = 10, command= lambda: btCAN(event))
buttonCAN.grid(row=1, column=0, padx=5, pady=5)
cuadroCan = Entry(CanFrame,textvariable=can, width = 56)
cuadroCan.grid(row=1, column=1, padx=5, pady=5, columnspan=5, sticky="w")
#cuadroCan.place(x=130, y=50, height = 30, width = 535)

#buttonEXO=Button(CanFrame, text="Exo Test", height = 1, width = 10, command= lambda: btEXO()).place(x=350, y=50)
#cuadroTestCan = Entry(CanFrame, textvariable=canTest)
#cuadroTestCan.grid(row=4, column=2, padx=100, pady=10)
#cuadroTestCan.place(x=470, y=50, height = 30, width = 200)

checkboxMS = Checkbutton(CanFrame, variable=MS, onvalue=1, offvalue=0,bg="#FAF3DD", fg="#2AC4DB",text="Own Gait")
checkboxMS.grid(row=2, column=0, padx=5, pady=5, sticky="w")
#checkboxMS.place(x=10, y=100)  
checkboxMD = Checkbutton(CanFrame,variable=MD, onvalue=1, offvalue=0, bg="#FAF3DD", fg="#2AC4DB",text="Impedance Gait")
#checkboxMD.grid(row=2, column=1, padx=5, pady=5, columnspan=1, sticky="w")
checkboxMD.place(x=120, y=78)   
checkboxOD = Checkbutton(CanFrame,variable=OD, onvalue=1, offvalue=0, bg="#FAF3DD", fg="#2AC4DB",text="Onset Detection")
#checkboxOD.grid(row=2, column=2, padx=5, pady=5, sticky="w") 
checkboxOD.place(x=260, y=78)   
checkboxEP = Checkbutton(CanFrame,variable=EP, onvalue=1, offvalue=0, bg="#FAF3DD", fg="#2AC4DB",text="EMG Proportional")
#checkboxEP.grid(row=2, column=3, padx=5, pady=5, sticky="w") 
checkboxEP.place(x=400, y=78)

#alpha1Label=Label(CanFrame, bg="#FAF3DD", text="Alpha1:")
##alpha1Label.grid(row=1, column=0, padx=10, pady=10)
#alpha1Label.place(x=50, y=140)
#cuadroAlpha1 = Entry(CanFrame)
#cuadroAlpha1.grid(row=1, column=0, padx=100, pady=10)
#cuadroAlpha1.place(x=110, y=140, height = 20, width = 100)
#
#alpha2Label=Label(CanFrame, bg="#FAF3DD", text="Alpha2:")
##alpha2Label.grid(row=1, column=0, padx=10, pady=10)
#alpha2Label.place(x=50, y=180)
#cuadroAlpha2 = Entry(CanFrame)
##cuadroAlpha2.grid(row=1, column=0, padx=100, pady=10)
#cuadroAlpha2.place(x=110, y=180, height = 20, width = 100)
#
#alpha3Label=Label(CanFrame, bg="#FAF3DD", text="Alpha3:")
##alpha3Label.grid(row=1, column=0, padx=10, pady=10)
#alpha3Label.place(x=50, y=220)
#cuadroAlpha3 = Entry(CanFrame)
##cuadroAlpha3.grid(row=1, column=0, padx=100, pady=10)
#cuadroAlpha3.place(x=110, y=220, height = 20, width = 100)

#xPosition = 350
#x1 = 140
#xTest = xPosition + 110
#x1Test = x1 + 85
#
#yPosition = 140
#y1 = yPosition + 40
#y2 = yPosition + 80
                 
onsetLabel=Label(CanFrame, bg="#FAF3DD", text="Threshold On:")
onsetLabel.grid(row=3, column=0, padx=10, pady=10)
#onsetLabel.place(x=xPosition, y=yPosition)
cuadroOnset = Entry(CanFrame, textvariable=onset)
#cuadroOnset.grid(row=3, column=1, padx=100, pady=10, columnspan=5, sticky="w")
cuadroOnset.place(x=120, y=115, height = 25, width = 60)

offsetLabel=Label(CanFrame, bg="#FAF3DD", text="Threshold Off:")
offsetLabel.grid(row=4, column=0, padx=10, pady=10)
#offsetLabel.place(x=xPosition, y=y1)
cuadroOffset = Entry(CanFrame, textvariable=offset)
cuadroOffset.place(x=120, y=155, height = 25, width = 60)
             
periodLabel=Label(CanFrame, bg="#FAF3DD", text="Period Off:")
periodLabel.grid(row=5, column=0, padx=10, pady=10)
#periodLabel.place(x=xPosition, y=y2)
cuadroPeriod = Entry(CanFrame, textvariable=period_off)
cuadroPeriod.place(x=120, y=195, height = 25, width = 60)

maxLabel=Label(CanFrame, bg="#FAF3DD", text="Max Value:")
maxLabel.place(x=190, y=115)
cuadroMax = Entry(CanFrame, textvariable=max_value)
cuadroMax.place(x=270, y=112, height = 25, width = 60)

minLabel=Label(CanFrame, bg="#FAF3DD", text="Min Value:")
minLabel.place(x=190, y=155)
cuadroMin = Entry(CanFrame, textvariable=min_value)
cuadroMin.place(x=270, y=152, height = 25, width = 60)



onsetLabel2=Label(CanFrame, bg="#FAF3DD", text="Threshold2 On:")
onsetLabel2.place(x=350, y=115)
cuadroOnset2 = Entry(CanFrame, textvariable=onset2)
cuadroOnset2.place(x=455, y=112, height = 25, width = 60)

offsetLabel2=Label(CanFrame, bg="#FAF3DD", text="Threshold2 Off:")
offsetLabel2.place(x=350, y=155)
cuadroOffset2 = Entry(CanFrame, textvariable=offset2)
cuadroOffset2.place(x=455, y=152, height = 25, width = 60)
             
periodLabel2 = Label(CanFrame, bg="#FAF3DD", text="Period2 Off:")
periodLabel2.place(x=370, y=195)
cuadroPeriod2 = Entry(CanFrame, textvariable=period_off2)
cuadroPeriod2.place(x=455, y=192, height = 25, width = 60)




assistanceLabel=Label(CanFrame, bg="#FAF3DD", text="Assistance (0-100):")
assistanceLabel.place(x=525, y=115)
assistanceBox = Entry(CanFrame, width = 35)
assistanceBox.place(x=660, y=115, height = 25, width = 40)

stiffnessLabel=Label(CanFrame, bg="#FAF3DD", text="Stiffness (0-100):")
stiffnessLabel.place(x=535, y=155)
stiffnessBox = Entry(CanFrame, width = 35)
stiffnessBox.place(x=660, y=155, height = 25, width = 40)

speedLabel=Label(CanFrame, bg="#FAF3DD", text="Speed (1-10):")
speedLabel.place(x=555, y=195)
speedBox = Entry(CanFrame, width = 35)
speedBox.place(x=660, y=192, height = 25, width = 35)






buttonStandUp=Button(CanFrame, text="Stand-up", height = 1, width = 10, command= lambda: btStandUp(event))
buttonStandUp.grid(row=6, column=0, padx=5, pady=5, sticky="w")
#.place(x=30, y=310)
buttonSitDown=Button(CanFrame, text="Sit-down", height = 1, width = 10, command= lambda: btSitDown(event))
buttonSitDown.grid(row=6, column=1, padx=5, pady=5, sticky="e")
#.place(x=190, y=310)
buttonCompliance=Button(CanFrame, text="Compliance", height = 1, width = 8, command= lambda: btCompliance(event))
buttonCompliance.grid(row=6, column=2, padx=5, pady=5, sticky="w")
#.place(x=350, y=310)
buttonCompliance=Button(CanFrame, text="Passive", height = 1, width = 6, command= lambda: btPassive(event))
buttonCompliance.grid(row=6, column=3, padx=5, pady=5, sticky="w")
#.place(x=445, y=310)
buttonEAST=Button(CanFrame, text="Record EMG", height = 1, width = 10, command= lambda: btEAST(event))
buttonEAST.grid(row=6, column=4, padx=5, pady=5, sticky="w")
#.place(x=30, y=380)
buttonWalking=Button(CanFrame, text="Walking", height = 1, width = 10, command= lambda: btWalking(event))
buttonWalking.grid(row=6, column=5, padx=5, pady=5, sticky="w")
#.place(x=530, y=310)
buttonStopExo=Button(CanFrame, text="STOP WALK", height = 1, width = 10, command= lambda: btStopExo(event))
buttonStopExo.grid(row=7, column=5, padx=5, pady=5, sticky="w")
#.place(x=560, y=380)
buttonWalking=Button(CanFrame, text="Angles", height = 1, width = 6, command= lambda: btAngles())
buttonWalking.grid(row=6, column=6, padx=5, pady=5, sticky="w")

interactionMSG=StringVar()
msgBox = Entry(CanFrame, textvariable=interactionMSG, width=50)
#msgBox.grid(row=7, column=1, padx=5, pady=5, columnspan=5, sticky="w")
msgBox.place(x=70, y=277, height = 30, width = 450)
msgBox.config(justify="center")



#%% ROS FRAME
Label(MesoFrame, text="ROS COMMUNICATION:", bg="#B8F2E6", fg="#FF969E",font=("Helvetica bold",12)).grid(row=0, column=0, padx=5, pady=5, columnspan=3, sticky="w")

ipLabel=Label(MesoFrame, text="IP Control Unit:", bg="#B8F2E6", font=("Helvetica bold",12))
#ipLabel.place(x=10, y=50)
cuadroIp = Entry(MesoFrame, textvariable=ipinit)
#cuadroIp.place(x=160, y=45, height = 30, width = 130)
#IP='10.42.0.222'
#cuadroIp.set(IP)

#buttonEAXON=Button(MesoFrame, text="Connect MesoEAXON", height = 1, width = 15, command= lambda: btEAXON()).place(x=310, y=45)
#cuadroMeso = Entry(MesoFrame, textvariable=meso)
#cuadroMeso.place(x=470, y=45, height = 30, width = 165)

scrollVert=Scrollbar(MesoFrame)
scrollVert.grid(row=1, column=1, sticky="nsew")

feedbackMSG=StringVar()
feedbackBox= Listbox(MesoFrame, yscrollcommand=scrollVert.set, width = 50)
feedbackBox.grid(row=1, column=0, padx=10, pady=10)
#feedbackBox.place(x=80, y=255, height = 130, width = 500)

scrollVert.config(command = feedbackBox.yview)

#scrollVert.place(x=80, y=255, height = 90, width = 50, sticky="nsew")
#scrollVert.grid(row=4, column=1, sticky="nsew")
#feedbackBox.config(yscrollcommand=scrollVert.set)

buttonR=Button(MesoFrame, text="TURN OFF EXO", height = 1, width = 32, command= lambda: btStop(event))
buttonR.grid(row=2, column=0, padx=10, pady=10, columnspan=3)
#buttonR.place(x=120, y=270)

#%%  Parameters
#ipinit.set('10.42.0.222')
event=True

'''
buttonEXIT=Button(root, text='Exit')
buttonEXIT.pack(side=BOTTOM)  
'''


root.mainloop()