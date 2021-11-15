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
#from EmgTorque_Lower import EmgTorque
#from motReader import motReader
from Gait_Model import *
from Exo_ID import *
from Onset_Thread import Onset_Mode
#from EMG_Proportional import *
from Proportional_Thread import ProportionalAnkle
from Decoder import *
from EAST_T import EASTrecord, EAST_Exorecord
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

from datetime import datetime

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
        
#        for i in range(30):
#            feedbackBox.insert(END, "ERROR: CAN conection"+str(i)) 
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
        try:
            repeat=int(cuadroRepeat.get())
        except:
            raise NameError ("ERROR: Cycles feature")
#        if cuadroRepeat.get() =="":
#            cuadroRepeat.configure(bg=activebuttonCanFrame)
#            feedbackBox.insert(END, "repeat empty")
#        else:
#            repeat=int(cuadroRepeat.get())
#            cuadroRepeat.configure(bg="white")
#        repeat=repeat-2
#        MVC1=cuadroMVC1.get()
#        MVC2=cuadroMVC2.get()
#        MVC3=cuadroMVC3.get()
        
        if subject != "" and date != "" and trial != "" and repeat != "":
            
            print(date + '_' + subject + '_' + trial + '_' + str(repeat))
            
            cuadroRepeat.configure(bg="white")
            cuadroName.configure(bg="white")
            cuadroDate.configure(bg="white")
            cuadroTrial.configure(bg="white")
            
        else:
            cuadroRepeat.configure(bg=activebuttonCanFrame)
            cuadroName.configure(bg=activebuttonCanFrame)
            cuadroDate.configure(bg=activebuttonCanFrame)
            cuadroTrial.configure(bg=activebuttonCanFrame)
            
            raise NameError ("ERROR: features empty")
#        buttonOK.state()
#        buttonTESTE['state']= DISABLED
#        print(buttonOK['state'])
#    except:
#        print("ERROR")
       
        
        
    
def gaitSection():
    global emg
    if cuadroRepeat.get() =="":
        steps=2
        assistance = 80
        cuadroRepeat.configure(bg=activebuttonCanFrame)
        assistanceBox.configure(bg=activebuttonCanFrame)
        raise NameError('"steps" EMPTY')
    else:
        steps=int(cuadroRepeat.get())
        assistance = int(assistanceBox.get())
    
        ctime=datetime.now().time()
        gaitData = gait(objPCAN,steps, assistance)
        dtime=datetime.now().time()
        Passive(objPCAN)
    #            OwnWalk(objPCAN, steps)
        joinangles = gaitData[0]
        trajectorie = gaitData[1]
        emg = gaitData[2]
        timeStampSTART = [ctime.hour, ctime.minute, ctime.second, ctime.microsecond]
        timeStampEND = [dtime.hour, dtime.minute, dtime.second, dtime.microsecond]
        
#    hour = ctime.hour
#    ctime.minute
#    ctime.second
#    ctime.microsecond
    
    cuadroRepeat.configure(bg="white")
    assistanceBox.configure(bg="white")
    
    
    Canal1_Raw_Total = emg[0]
    Canal2_Raw_Total = emg[1]
    Canal3_Raw_Total = emg[2]
    Canal4_Raw_Total = emg[3]
    
    Canal1_Env_Total = emg[12]
    Canal2_Env_Total = emg[13]
    Canal3_Env_Total = emg[14]
    Canal4_Env_Total = emg[15]
    
    saveGaitTest('GAIT', emg, joinangles, trajectorie, timeStampSTART, timeStampEND)
    saveEUROBENCH('GAIT', emg, joinangles, trajectorie, 1)
    
    try:
        window=Tk()
        window.title("EMG Recorded")
        emgpl = [Canal1_Raw_Total, Canal2_Raw_Total, Canal3_Raw_Total, Canal4_Raw_Total, 
                 Canal1_Env_Total, Canal2_Env_Total, Canal3_Env_Total, Canal4_Env_Total]
        plot_button=Button(master=window, command = muscles4Plot(emgpl,window))
        window=Tk()
        window.title("joinangles")
        plot_button=Button(master=window, command=multiPlot(joinangles,window)) 
        window=Tk()
        window.title("trajectories Sent")
        plot_button=Button(master=window, command=multiPlot(trajectorie,window))
        window.mainloop()  
    except:
        interactionMSG.set("ERROR: EMG plot")  
        feedbackBox.insert(END, "ERROR: EMG plot")
        raise Exception("PLOT") 





def impedanceSection(objPCAN):
    
    if cuadroRepeat.get() =="" or assistanceBox.get() =="" or stiffnessBox.get() == "":
        gaits = 2
        assistance = 100
        stiffness = 20
        assistanceBox.configure(bg=activebuttonCanFrame)
        stiffnessBox.configure(bg=activebuttonCanFrame)
        cuadroRepeat.configure(bg=activebuttonCanFrame)
#        speed=2
        raise NameError('Fill in: "cycles, assistance & stiffness"')
    else:
        gaits = int(cuadroRepeat.get())
        assistance = int(assistanceBox.get())
        stiffness = int(stiffnessBox.get())
#        speed=int(speedBox.get())
        
#    [rHip, rKnee, rAnkle, lHip, 
#     lKnee, lAnkle] = Impedance(objPCAN, speed, secods)
#        [rHip, rKnee, rAnkle, lHip, 
#         lKnee, lAnkle] 
    ctime=datetime.now().time()
    valor = impedance(objPCAN, gaits, assistance, stiffness)
    dtime=datetime.now().time()
    Passive(objPCAN)
    
    joinangles = valor[0]
    trajectorie = valor[1]
    emg = valor[2]
    timeStampSTART = [ctime.hour, ctime.minute, ctime.second, ctime.microsecond]
    timeStampEND = [dtime.hour, dtime.minute, dtime.second, dtime.microsecond]
    
    
    Canal1_Raw_Total = emg[0]
    Canal2_Raw_Total = emg[1]
    Canal3_Raw_Total = emg[2]
    Canal4_Raw_Total = emg[3]
    
    Canal1_Env_Total = emg[12]
    Canal2_Env_Total = emg[13]
    Canal3_Env_Total = emg[14]
    Canal4_Env_Total = emg[15]

    assistanceBox.configure(bg="white")
    stiffnessBox.configure(bg="white")
    cuadroRepeat.configure(bg="white")
    
    
    saveGaitTest('IMPEDANCE', emg, joinangles, trajectorie, timeStampSTART, timeStampEND)
    saveEUROBENCH('IMPEDANCE', emg, joinangles, trajectorie, 1)
    
    try:
        
        window=Tk()
        window.title("EMG Recorded")
        emgpl = [Canal1_Raw_Total, Canal2_Raw_Total, Canal3_Raw_Total, Canal4_Raw_Total, 
                 Canal1_Env_Total, Canal2_Env_Total, Canal3_Env_Total, Canal4_Env_Total]
        plot_button=Button(master=window, command=muscles4Plot(emgpl,window))
        window=Tk()
        window.title("joinangles")
        plot_button=Button(master=window, command=multiPlot(joinangles,window)) 
        window=Tk()
        window.title("trajectories Sent")
        plot_button=Button(master=window, command=multiPlot(trajectorie,window))
        window.mainloop()        
 
        window.mainloop()
        
    except:
        interactionMSG.set("ERROR: EMG plot")  
        feedbackBox.insert(END, "ERROR: EMG plot")
        raise Exception("PLOT") 





    
def OnsetEAST():
#    global onst
    global Canal1_Env_Total, Canal2_Env_Total, Canal3_Env_Total, Canal4_Env_Total
    
    if cuadroRepeat.get() =="" or assistanceBox.get() =="":
#            feedbackBox.insert(END, "features empty")
        repeat = 10 # seconds
        assistance = 80
        stiffness = 20
        assistanceBox.configure(bg=activebuttonCanFrame)
        stiffnessBox.configure(bg=activebuttonCanFrame)
        cuadroRepeat.configure(bg=activebuttonCanFrame)
#        raise NameError ("repeat or assistance empty")
    else:
        repeat = int(cuadroRepeat.get())
        assistance = int(assistanceBox.get())
        stiffness = int(stiffnessBox.get())
        
    NumChEMG = 4    
    features = np.zeros(NumChEMG*3)
    
    #features = [th0, thff0, pff0, th1, thff1, pff1]
    features[0] = float(cuadroOnset.get())
    features[1] = float(cuadroOffset.get())
    features[2] = float(period_off.get())
    features[3] = float(cuadroOnset2.get())
    features[4] = float(cuadroOffset2.get())
    features[5] = float(period_off2.get())
    features[6] = float(cuadroOnset3.get())
    features[7] = float(cuadroOffset3.get())
    features[8] = float(period_off3.get())
    features[9] = float(cuadroOnset4.get())
    features[11] = float(period_off4.get())
    
    
    max_minFeatures = np.zeros(NumChEMG*2)
#    "%.3f" % 
#    max_minFeatures[0] = float(round(max(Canal1_Env_Total),3))
    max_minFeatures[0] = float(max_value.get())
    max_minFeatures[2] = float(max_value2.get())
    max_minFeatures[4] = float(max_value3.get())
    max_minFeatures[6] = float(max_value4.get())
    
#    max_minFeatures[1] = float(round(min(Canal1_Env_Total),3))
    max_minFeatures[1] = float(min_value.get())
    max_minFeatures[3] = float(min_value2.get())
    max_minFeatures[5] = float(min_value3.get())
    max_minFeatures[7] = float(min_value4.get())
    
#    print(round((max_value.get() - min_value.get()),2))
#    print(round((max_value2.get() - min_value2.get()),2))
#    print(round((max_value3.get() - min_value3.get()),2))
#    print(round((max_value3.get() - min_value4.get()),2))
    
    ctime=datetime.now().time()
    rawData = Onset_Mode(objPCAN, repeat, assistance, stiffness, features, max_minFeatures)
    dtime=datetime.now().time()
    Passive(objPCAN)
    
    
    assistanceBox.configure(bg="white")
    cuadroRepeat.configure(bg="white")
#    rawData = [Canal1_Total, Canal2_Total, Onset, 0]
    onst = rawData[0]
    angle = rawData[1]
    emg2 = rawData[2]
    trajectorie = rawData[3]
    timeStampSTART = [ctime.hour, ctime.minute, ctime.second, ctime.microsecond]
    timeStampEND = [dtime.hour, dtime.minute, dtime.second, dtime.microsecond]

    
    feedbackBox.insert(END, "EXO Stoped")
    
    Canal1_Raw_Total = emg2[0]
    Canal2_Raw_Total = emg2[1]
    Canal3_Raw_Total = emg2[2]
    Canal4_Raw_Total = emg2[3]
        
    Canal1_Env_Total = emg2[12]
    Canal2_Env_Total = emg2[13]
    Canal3_Env_Total = emg2[14]
    Canal4_Env_Total = emg2[15]
    
    saveOnsetTest(emg2, onst, angle, trajectorie, timeStampSTART, timeStampEND)
    saveEUROBENCH('ONSET', emg2, angle, trajectorie, onst)
    
    try:
        window=Tk()
        window.title("onset")
        plot_button=Button(master=window, command=plot_sample(onst,window))
        window=Tk()
        window.title("Angles")
        plot_button=Button(master=window, command=multiPlot(angle,window)) 
        window=Tk()
        window.title("trajectories Sent")
        plot_button=Button(master=window, command=multiPlot(trajectorie,window)) 
        window=Tk()
        window.title("EMG2")
        emgpl = [Canal1_Raw_Total, Canal2_Raw_Total, Canal3_Raw_Total, Canal4_Raw_Total, 
                 Canal1_Env_Total, Canal2_Env_Total, Canal3_Env_Total, Canal4_Env_Total]
        plot_button=Button(master=window, command=muscles4Plot(emgpl,window))
        
        window.mainloop()   
    except:
        interactionMSG.set("ERROR: PLOT")  
        feedbackBox.insert(END, "ERROR: PLOT")
        raise Exception("PLOT")





def Proportionald():
    global total_angle,canal1_Env_Total,canal1_Raw_Total

    try:
        if cuadroRepeat.get() =="" or assistanceBox.get() == "":
            repeat=5
            assistance = 100
            assistanceBox.configure(bg=activebuttonCanFrame)
            cuadroRepeat.configure(bg=activebuttonCanFrame)
            raise TypeError('"Cycles" EMPTY')
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
        Passive(objPCAN)
#        rawData = ProportionalAnkle(repeat,objPCAN,onsetTH,offsetTH,maxvalue,minvalue)
        assistanceBox.configure(bg="white")
        cuadroRepeat.configure(bg="white")
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
    Passive(objPCAN)
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
 
    
    

def btRUN(event):
    global rAnkle_Record
#    marckboxes()
    print("RUN") 
#    marckboxes()!
    try:
        try:
            btOK() #check features
        except:
            raise
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

            impedanceSection(objPCAN)
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
    
        Passive(objPCAN)
        
    except KeyboardInterrupt:
        Stop_Run=True
        print('interrupt')
        try:
            Passive(objPCAN)
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
        cuadroRepeat.configure(bg=activebuttonCanFrame)
    else:
        repeat=int(cuadroRepeat.get())
            
#    t0=time.time() 
#    print(t0,time.time())
#    _ = time.perf_counter() + delay/1000
#    while time.time()-t0 < repeat:
#    rheel,rtoe,lheel,ltoe = Footsensor(objPCAN,repeat)
    valor = Footsensor(objPCAN,repeat)
    cuadroRepeat.configure(bg="white")
    
#    feedbackBox.insert(END,"Battery Voltage: " + str(rheel[-1]) + "V")
#    feedbackBox.insert(END,"Battery Voltage: " + str(voltage[-1]) + "V")
    window=Tk()
    window.title("foot sensor")
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

def EASTRecord():

    if cuadroRepeat.get() =="":
#            feedbackBox.insert(END, "features empty")
        repeat = 4 # seconds
        cuadroRepeat.configure(bg=activebuttonCanFrame)
    #        raise NameError ("repeat  empty")
    else:
        repeat = int(cuadroRepeat.get())
     
    print("EMG Recording") 
    ctime = datetime.now().time()
    Data = EASTrecord(repeat)
    dtime = datetime.now().time()
        

    return Data, ctime, dtime


def ExoEAST():
    try:
        if cuadroRepeat.get() =="" or assistanceBox.get() =="" or stiffnessBox.get() =="":
    #            feedbackBox.insert(END, "features empty")
            repeat = 4 # seconds
            assistance = 80
            stiffness = 20
            assistanceBox.configure(bg=activebuttonCanFrame)
            stiffnessBox.configure(bg=activebuttonCanFrame)
            cuadroRepeat.configure(bg=activebuttonCanFrame)
        #        raise NameError ("fill repeat assistance and stiffness")
        else:
            repeat = int(cuadroRepeat.get())
            assistance = int(assistanceBox.get())
            stiffness = int(stiffnessBox.get())
            
        print("Exo-EMG Recording") 
        ctime = datetime.now().time()
        Data, angleArray, trajectories = EAST_Exorecord(repeat, objPCAN, assistance, stiffness)
        dtime = datetime.now().time()
    #        cuadroRepeat.configure(bg="white")
        Passive(objPCAN)
        
        
    except KeyboardInterrupt:
        interactionMSG.set('Interrupt')
        feedbackBox.insert(END, "Interrupt")
        Passive(objPCAN)
        return Data, angleArray, trajectories, ctime, dtime
#        raise
        
    return Data, angleArray, trajectories, ctime, dtime
            



def btEAST(event):
    print("BEGINNING") 
    global Canal1_Env_Total, Canal2_Env_Total, Canal3_Env_Total, Canal4_Env_Total
    global Canal1_Raw_Total, Canal2_Raw_Total, Canal3_Raw_Total, Canal4_Raw_Total
    
    try: 
        
        btOK()
        
        MS1=MS.get()
        MD1=MD.get()
        OD1=OD.get()
        EP1=EP.get()
        
        
        if (MS1 == 0) & (MD1 == 1) & (OD1 == 0) & (EP1 == 0):
            try:
                objPCAN
                pass
            except:
                raise NameError ("ERROR: CAN conection")
            exo = 1
            Data, angleArray, trajectories, ctime, dtime = ExoEAST()
            
        else:
#            try:
            exo = 0
            Data, ctime, dtime = EASTRecord()
#            except KeyboardInterrupt:
#                print("ERROR1 EAST")
#                raise NameError ("ERROR: CAN conection")
            
#            repeat = int(cuadroRepeat.get())
#            Data = EASTrecordT(repeat)


#        Data, angleArray, trajectories = EASTrecord(repeat, objPCAN, assistance, stiffness)
        cuadroRepeat.configure(bg="white")
#        Passive(objPCAN)
        timeStampSTART = [ctime.hour, ctime.minute, ctime.second, ctime.microsecond]
        timeStampEND = [dtime.hour, dtime.minute, dtime.second, dtime.microsecond]
    
        interactionMSG.set("Serial Port closed")
        feedbackBox.insert(END, "Serial Port closed")
        Canal1_Raw_Total = Data[0]
        Canal2_Raw_Total = Data[1]
        Canal3_Raw_Total = Data[2]
        Canal4_Raw_Total = Data[3]
        
        Canal1_Env_Total = Data[12]
        Canal2_Env_Total = Data[13]
        Canal3_Env_Total = Data[14]
        Canal4_Env_Total = Data[15]
        
        
        time = Data[18]
        
        sg_delete=300
        
        Canal1_Raw_Total = Canal1_Raw_Total[sg_delete:-1]
        Canal2_Raw_Total = Canal2_Raw_Total[sg_delete:-1]
        Canal3_Raw_Total = Canal3_Raw_Total[sg_delete:-1]
        Canal4_Raw_Total = Canal4_Raw_Total[sg_delete:-1]
        
        Canal1_Env_Total = Canal1_Env_Total[sg_delete:-1]
        Canal2_Env_Total = Canal2_Env_Total[sg_delete:-1]
        Canal3_Env_Total = Canal3_Env_Total[sg_delete:-1]
        Canal4_Env_Total = Canal4_Env_Total[sg_delete:-1]
        
        th1 = 1
        th2 = 1
        th3 = 1
        th4 = 1

        c1normalized, on1 = thValues(Canal1_Env_Total, th1)
        c2normalized, on2 = thValues(Canal2_Env_Total, th2)
        c3normalized, on3 = thValues(Canal3_Env_Total, th3)
        c4normalized, on4 = thValues(Canal4_Env_Total, th4)
        
        
        max_value.set("%.3f" % max(Canal1_Env_Total))
        min_value.set("%.3f" % min(Canal1_Env_Total))
        onset.set("%.3f" % on1)
        offset.set("%.3f" % on1)
        period_off.set(0.1)
        thvalue.set("%.2f" % th1)
        
        max_value2.set("%.3f" % max(Canal2_Env_Total))
        min_value2.set("%.3f" % min(Canal2_Env_Total))
        onset2.set("%.3f" % on2)
        offset2.set("%.3f" % on2)
        period_off2.set(0.1)
        thvalue2.set("%.2f" % th2)
        
        max_value3.set("%.3f" % max(Canal3_Env_Total))
        min_value3.set("%.3f" % min(Canal3_Env_Total))
        onset3.set("%.3f" % on3)
        offset3.set("%.3f" % on3)
        period_off3.set(0.1)
        thvalue3.set("%.2f" % th3)
        
        max_value4.set("%.3f" % max(Canal4_Env_Total))
        min_value4.set("%.3f" % min(Canal4_Env_Total))
        onset4.set("%.3f" % on4)
        offset4.set("%.3f" % on4)
        period_off4.set(0.1)
        thvalue4.set("%.2f" % th4)
        
        
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
            
            Canal1_Raw_Total = Data[0]
            Canal2_Raw_Total = Data[1]
            Canal3_Raw_Total = Data[2]
            Canal4_Raw_Total = Data[3] 
            Canal5_Raw_Total = Data[4]
            Canal6_Raw_Total = Data[5]
            Canal7_Raw_Total = Data[6]
            Canal8_Raw_Total = Data[7]
            Canal9_Raw_Total = Data[8]
            Canal10_Raw_Total = Data[9]
            Canal11_Raw_Total = Data[10]
            Canal12_Raw_Total = Data[11]
            
            
            rawData = [Canal1_Raw_Total, Canal2_Raw_Total, Canal3_Raw_Total, Canal4_Raw_Total]
            envData = [Canal1_Env_Total, Canal2_Env_Total, Canal3_Env_Total, Canal4_Env_Total]
            normalizesCh = [c1normalized, c2normalized, c3normalized, c4normalized]
            
            emgpl1 = [Canal1_Raw_Total, Canal2_Raw_Total, Canal9_Raw_Total, Canal10_Raw_Total, Canal11_Raw_Total, Canal12_Raw_Total]
            emgpl2 = [Canal3_Raw_Total, Canal4_Raw_Total, Canal5_Raw_Total, Canal6_Raw_Total, Canal7_Raw_Total, Canal8_Raw_Total]
    
            
            if exo:
                saveDataExo(rawData, envData, angleArray, trajectories, time, timeStampSTART, timeStampEND)
                
                window=Tk()
                window.title("Angles")
                plot_button=Button(master=window, command = multiPlot(angleArray,window)) 
                
                window=Tk()
                window.title("Angles Sent")
                plot_button=Button(master=window, command = multiPlot(trajectories,window))
                
            else:  
                saveTrainData(rawData, envData, normalizesCh, time, timeStampSTART, timeStampEND)
                
                
#            window=Tk()
#            window.title("EMG Recorded")
#            emgpl = [Canal1_Raw_Total, Canal2_Raw_Total, Canal3_Raw_Total, Canal4_Raw_Total, 
#                     Canal1_Env_Total, Canal2_Env_Total, Canal3_Env_Total, Canal4_Env_Total]
#            plot_button=Button(master=window, command = muscles4Plot(emgpl,window))
            window=Tk()
            window.title("EMG Recorded R")
            plot_button=Button(master=window, command = EUROPlot(emgpl1,window))
            window=Tk()
            window.title("EMG Recorded L")
            plot_button=Button(master=window, command = EUROPlot(emgpl2,window))
            
            window=Tk()
            window.title("envelope")
            plot_button=Button(master=window, command = normalizedPlot(envData,window))
            window=Tk()
            window.title("normalize")
            plot_button=Button(master=window, command = normalizedPlot(normalizesCh,window))
            
            window.mainloop()   
        except:
             interactionMSG.set("ERROR: EMG plot")  
             feedbackBox.insert(END, "ERROR: EMG plot")
             raise Exception("PLOT")
            
    except KeyboardInterrupt:
            print("ERROR DURING RECORDING")
            
            
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

def thValues(Data, th):
    normalized = (Data-min(Data))/round((max(Data)-min(Data)),2)
    std=np.std(normalized)

#    thArray = np.where(normalized > std*th)
#    position = Data[thArray]
    
#    return normalized, position.flat[0]
    return normalized, std*th
        
    
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
    
def normalizedPlot(valor, window):
    
    fig=Figure(figsize=(12,7),dpi=100)
    plot1=fig.add_subplot(411)
    plot1.plot(valor[0])
    plot2=fig.add_subplot(412)
    plot2.plot(valor[1])
    plot3=fig.add_subplot(413)
    plot3.plot(valor[2])
    plot4=fig.add_subplot(414)
    plot4.plot(valor[3])
    
    canvas=FigureCanvasTkAgg(fig,master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()
    toolbar=NavigationToolbar2Tk(canvas,window)
    toolbar.update()
    canvas.get_tk_widget().pack() 

def muscles4Plot(valor, window):
    
    fig=Figure(figsize=(14,7),dpi=110)
    plot1=fig.add_subplot(421)
    plot1.plot(valor[0])
    plot2=fig.add_subplot(423)
    plot2.plot(valor[1])
    plot3=fig.add_subplot(425)
    plot3.plot(valor[2])
    plot4=fig.add_subplot(427)
    plot4.plot(valor[3])
    plot5=fig.add_subplot(422)
    plot5.plot(valor[4])
    plot6=fig.add_subplot(424)
    plot6.plot(valor[5])
    plot7=fig.add_subplot(426)
    plot7.plot(valor[6])
    plot8=fig.add_subplot(428)
    plot8.plot(valor[7])
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
    
def multiPlot2(valor,window):
    
    fig=Figure(figsize=(12,7),dpi=100)
    plot1=fig.add_subplot(211)
    plot1.plot(valor[0])
    plot2=fig.add_subplot(212)
    plot2.plot(valor[1])
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
    
    
def EUROPlot(valor,window):

#    Canal1_Raw_Total = emg[0]
#    Canal2_Raw_Total = emg[1]
#    Canal3_Raw_Total = emg[2]
#    Canal4_Raw_Total = emg[3] 
#    Canal5_Raw_Total = emg[4]
#    Canal6_Raw_Total = emg[5]
#    Canal7_Raw_Total = emg[6]
#    Canal8_Raw_Total = emg[7]
#    Canal9_Raw_Total = emg[8]
#    Canal10_Raw_Total = emg[9]
#    Canal11_Raw_Total = emg[10]
#    Canal12_Raw_Total = emg[11]
    
    fig=Figure(figsize=(14,7),dpi=110)
    plot1=fig.add_subplot(321)
    plot1.plot(valor[0])
    plot2=fig.add_subplot(322)
    plot2.plot(valor[1])
    plot3=fig.add_subplot(323)
    plot3.plot(valor[2])
    plot4=fig.add_subplot(324)
    plot4.plot(valor[3])
    plot5=fig.add_subplot(325)
    plot5.plot(valor[4])
    plot6=fig.add_subplot(326)
    plot6.plot(valor[5])
    
    canvas=FigureCanvasTkAgg(fig,master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()
    toolbar=NavigationToolbar2Tk(canvas,window)
    toolbar.update()
    canvas.get_tk_widget().pack() 

def saveTrainData(rawData, envData, normalizesCh, time, timeStampSTART, timeStampEND):
    global subject, date, trial
    
    Canal1_Raw_Total = rawData[0]
    Canal2_Raw_Total = rawData[1]
    Canal3_Raw_Total = rawData[2]
    Canal4_Raw_Total = rawData[3]
    
    Canal1_Env_Total = envData[0]
    Canal2_Env_Total = envData[1]
    Canal3_Env_Total = envData[2]
    Canal4_Env_Total = envData[3]
    
    c1normalized = normalizesCh[0]
    c2normalized = normalizesCh[1]
    c3normalized = normalizesCh[2]
    c4normalized = normalizesCh[3]
    
    
    df00 = pd.DataFrame(timeStampSTART,columns=['Time_Stamp_Start'])
    dfE = pd.DataFrame(timeStampEND,columns=['Time_Stamp_END'])
    dft = pd.DataFrame(time,columns=['Tiempo'])
    
    df_o = pd.DataFrame(Canal1_Raw_Total,columns=['Canal1_Raw'])
    df1_o = pd.DataFrame(Canal2_Raw_Total,columns=['Canal2_Raw'])
    df2_o = pd.DataFrame(Canal3_Raw_Total,columns=['Canal3_Raw'])
    df3_o = pd.DataFrame(Canal4_Raw_Total,columns=['Canal4_Raw'])
    
    df4_o = pd.DataFrame(Canal1_Env_Total,columns=['Canal1_Env'])
    df5_o = pd.DataFrame(Canal2_Env_Total,columns=['Canal2_Env'])
    df6_o = pd.DataFrame(Canal3_Env_Total,columns=['Canal3_Env'])
    df7_o = pd.DataFrame(Canal4_Env_Total,columns=['Canal4_Env'])
    
    df8_o = pd.DataFrame(c1normalized,columns=['c1_Norm'])
    df9_o = pd.DataFrame(c2normalized,columns=['c2_Norm'])
    df10_o = pd.DataFrame(c3normalized,columns=['c3_Norm'])
    df11_o = pd.DataFrame(c4normalized,columns=['c4_Norm'])
    
    df_o = pd.concat([df00,dfE,dft,df_o,df1_o,df2_o,df3_o,df4_o,df5_o,df6_o,df7_o,df8_o,df9_o,df10_o,df11_o], axis = 1)
    
    df_o.to_csv(date + '_' + 'EMG_Subject' + '_' + subject + '_' + trial + '.csv',sep=',')
    
def saveDataExo(rawData, envData, angleArray, trajectories, time, timeStampSTART, timeStampEND):
    global subject, date, trial, repeat
    
    Canal1_Raw_Total = rawData[0]
    Canal2_Raw_Total = rawData[1]
    Canal3_Raw_Total = rawData[2]
    Canal4_Raw_Total = rawData[3]
    
    Canal1_Env_Total = envData[0]
    Canal2_Env_Total = envData[1]
    Canal3_Env_Total = envData[2]
    Canal4_Env_Total = envData[3]
    
    rHip_Record = angleArray[0]
    rKnee_Record = angleArray[1]
    rAnkle_Recor = angleArray[2]
    lHip_Record = angleArray[3]
    lKnee_Record = angleArray[4]
    lAnkle_Record = angleArray[5]
    
    rHip_Traj = trajectories[0]
    rKnee_Traj = trajectories[1]
    rAnkle_Traj = trajectories[2]
    lHip_Traj = trajectories[3]
    lKnee_Traj = trajectories[4]
    lAnkle_Traj = trajectories[5]
    
    df00 = pd.DataFrame(timeStampSTART,columns=['Time_Stamp_Start'])
    dfE = pd.DataFrame(timeStampEND,columns=['Time_Stamp_END'])
    dft = pd.DataFrame(time,columns=['Tiempo'])
    
    df_o = pd.DataFrame(Canal1_Raw_Total,columns=['Canal1_Raw'])
    df1_o = pd.DataFrame(Canal2_Raw_Total,columns=['Canal2_Raw'])
    df2_o = pd.DataFrame(Canal3_Raw_Total,columns=['Canal3_Raw'])
    df3_o = pd.DataFrame(Canal4_Raw_Total,columns=['Canal4_Raw'])
    
    df4_o = pd.DataFrame(Canal1_Env_Total,columns=['Canal1_Env'])
    df5_o = pd.DataFrame(Canal2_Env_Total,columns=['Canal2_Env'])
    df6_o = pd.DataFrame(Canal3_Env_Total,columns=['Canal3_Env'])
    df7_o = pd.DataFrame(Canal4_Env_Total,columns=['Canal4_Env'])
    
    df8_o = pd.DataFrame(rHip_Record,columns=['rHip_Record'])
    df9_o = pd.DataFrame(rKnee_Record,columns=['rKnee_Record'])
    df10_o = pd.DataFrame(rAnkle_Recor,columns=['rAnkle_Recor'])
    df11_o = pd.DataFrame(lHip_Record,columns=['lHip_Record'])
    df12_o = pd.DataFrame(lKnee_Record,columns=['lKnee_Record'])
    df13_o = pd.DataFrame(lAnkle_Record,columns=['lAnkle_Record'])
    
    df14_o = pd.DataFrame(rHip_Traj,columns=['rHip_Traj'])
    df15_o = pd.DataFrame(rKnee_Traj,columns=['rKnee_Traj'])
    df16_o = pd.DataFrame(rAnkle_Traj,columns=['rAnkle_Traj'])
    df17_o = pd.DataFrame(lHip_Traj,columns=['lHip_Traj'])
    df18_o = pd.DataFrame(lKnee_Traj,columns=['lKnee_Traj'])
    df19_o = pd.DataFrame(lAnkle_Traj,columns=['lAnkle_Traj'])
    
    df_o = pd.concat([df00,dfE,df_o,df1_o,df2_o,df3_o,df4_o,df5_o,df6_o,df7_o, df8_o, df9_o, 
                      df10_o, df11_o, df12_o, df13_o, df14_o, df15_o, df16_o, df17_o, df18_o, df19_o], axis = 1)
#    date='211021'
#    subject='Marvin'
#    trial='01'
    df_o.to_csv(date + '_' + 'Train_Subject' + '_' + subject + '_' + trial + '.csv',sep=',')

def saveOnsetTest(emg, onst, angle, trajectorie, timeStampSTART, timeStampEND):
    global subject, date, trial, repeat

    Canal1_Raw_Total = emg[0]
    Canal2_Raw_Total = emg[1]
    Canal3_Raw_Total = emg[2]
    Canal4_Raw_Total = emg[3] 
    
    Canal1_Env_Total = emg[12]
    Canal2_Env_Total = emg[13]
    Canal3_Env_Total = emg[14]
    Canal4_Env_Total = emg[15]
    
    tiempo = emg[18]
    
    rHip_Record = angle[0] 
    rKnee_Record = angle[1]
    rAnkle_Record = angle[2] 
    lHip_Record = angle[3] 
    lKnee_Record = angle[4] 
    lAnkle_Record = angle[5]
    

    rHip_Sent = trajectorie[0] 
    rKnee_Sent = trajectorie[1]
    rAnkle_Sent = trajectorie[2] 
    lHip_Sent = trajectorie[3] 
    lKnee_Sent = trajectorie[4] 
    lAnkle_Sent = trajectorie[5]
    
    
    df00 = pd.DataFrame(timeStampSTART,columns=['Time_Stamp_Start'])
    dfE = pd.DataFrame(timeStampEND,columns=['Time_Stamp_END'])
    dft = pd.DataFrame(tiempo,columns=['Tiempo'])
    
    df0 = pd.DataFrame(Canal1_Raw_Total,columns=['Canal1_Raw'])
    df1 = pd.DataFrame(Canal2_Raw_Total,columns=['Canal2_Raw'])
    df2 = pd.DataFrame(Canal3_Raw_Total,columns=['Canal3_Raw'])
    df3 = pd.DataFrame(Canal4_Raw_Total,columns=['Canal4_Raw'])
    
    df4 = pd.DataFrame(Canal1_Env_Total,columns=['Canal1_Env'])
    df5 = pd.DataFrame(Canal2_Env_Total,columns=['Canal2_Env'])
    df6 = pd.DataFrame(Canal3_Env_Total,columns=['Canal3_Env'])
    df7 = pd.DataFrame(Canal4_Env_Total,columns=['Canal4_Env'])
    
    df8 = pd.DataFrame(onst,columns=['ONSET'])
    
    df9 = pd.DataFrame(rHip_Record,columns=['rHip_Record'])
    df10 = pd.DataFrame(rKnee_Record,columns=['rKnee_Record'])
    df11 = pd.DataFrame(rAnkle_Record,columns=['rAnkle_Record'])
    df12 = pd.DataFrame(lHip_Record,columns=['lHip_Record'])  
    df13 = pd.DataFrame(lKnee_Record,columns=['lKnee_Record'])
    df14 = pd.DataFrame(lAnkle_Record,columns=['lAnkle_Record'])
    
    df15 = pd.DataFrame(rHip_Sent,columns=['rHip_Sent'])
    df16 = pd.DataFrame(rKnee_Sent,columns=['rKnee_Sent'])
    df17 = pd.DataFrame(rAnkle_Sent,columns=['rAnkle_Sent'])
    df18 = pd.DataFrame(lHip_Sent,columns=['lHip_Sent'])  
    df19 = pd.DataFrame(lKnee_Sent,columns=['lKnee_Sent'])
    df20 = pd.DataFrame(lAnkle_Sent,columns=['lAnkle_Sent'])
    
#    df21 = pd.DataFrame([2000],columns=['FS_EMG'])
#    df8=pd.DataFrame(comp_time,columns=['Computational time'])
    
    df = pd.concat([df00,dfE,dft,df0,df1,df2,df3,df4,df5,df6,df7,df8,df9,df10,df11,df12,
                    df13,df14,df15,df16,df17,df18,df19,df20], axis = 1)

    df.to_csv(date + '_' + 'ONSET_Subject' + '_' + subject + '_' + trial + '.csv',sep=',')
    
    
def saveGaitTest(controlador, emg, angle, trajectorie, timeStampSTART, timeStampEND):
    global subject, date, trial, repeat

    Canal1_Raw_Total = emg[0]
    Canal2_Raw_Total = emg[1]
    Canal3_Raw_Total = emg[2]
    Canal4_Raw_Total = emg[3] 
    
    Canal1_Env_Total = emg[12]
    Canal2_Env_Total = emg[13]
    Canal3_Env_Total = emg[14]
    Canal4_Env_Total = emg[15]
    
    tiempo = emg[18]
    
    rHip_Record = angle[0] 
    rKnee_Record = angle[1]
    rAnkle_Record = angle[2] 
    lHip_Record = angle[3] 
    lKnee_Record = angle[4] 
    lAnkle_Record = angle[5]
    
    rHip_Sent = trajectorie[0] 
    rKnee_Sent = trajectorie[1]
    rAnkle_Sent = trajectorie[2] 
    lHip_Sent = trajectorie[3] 
    lKnee_Sent = trajectorie[4] 
    lAnkle_Sent = trajectorie[5]
    
    
        
        
    df00 = pd.DataFrame(timeStampSTART,columns=['Time_Stamp_Start'])
    dfE = pd.DataFrame(timeStampEND,columns=['Time_Stamp_END'])
    dft = pd.DataFrame(tiempo,columns=['Tiempo'])
    
    df0 = pd.DataFrame(Canal1_Raw_Total,columns=['Canal1_Raw'])
    df1 = pd.DataFrame(Canal2_Raw_Total,columns=['Canal2_Raw'])
    df2 = pd.DataFrame(Canal3_Raw_Total,columns=['Canal3_Raw'])
    df3 = pd.DataFrame(Canal4_Raw_Total,columns=['Canal4_Raw'])
    
    df4 = pd.DataFrame(Canal1_Env_Total,columns=['Canal1_Env'])
    df5 = pd.DataFrame(Canal2_Env_Total,columns=['Canal2_Env'])
    df6 = pd.DataFrame(Canal3_Env_Total,columns=['Canal3_Env'])
    df7 = pd.DataFrame(Canal4_Env_Total,columns=['Canal4_Env'])
    
    df9 = pd.DataFrame(rHip_Record,columns=['rHip_Record'])
    df10 = pd.DataFrame(rKnee_Record,columns=['rKnee_Record'])
    df11 = pd.DataFrame(rAnkle_Record,columns=['rAnkle_Record'])
    df12 = pd.DataFrame(lHip_Record,columns=['lHip_Record'])  
    df13 = pd.DataFrame(lKnee_Record,columns=['lKnee_Record'])
    df14 = pd.DataFrame(lAnkle_Record,columns=['lAnkle_Record'])
    
    df15 = pd.DataFrame(rHip_Sent,columns=['rHip_Sent'])
    df16 = pd.DataFrame(rKnee_Sent,columns=['rKnee_Sent'])
    df17 = pd.DataFrame(rAnkle_Sent,columns=['rAnkle_Sent'])
    df18 = pd.DataFrame(lHip_Sent,columns=['lHip_Sent'])  
    df19 = pd.DataFrame(lKnee_Sent,columns=['lKnee_Sent'])
    df20 = pd.DataFrame(lAnkle_Sent,columns=['lAnkle_Sent'])
    
    
    df = pd.concat([df00,dfE,dft,df0,df1,df2,df3,df4,df5,df6,df7,df9,df10,df11,df12,
                    df13,df14,df15,df16,df17,df18,df19,df20], axis = 1)

    df.to_csv(date + '_' + controlador + '_' + 'Subject' + '_' + subject + '_' + trial + '.csv',sep=',')    



def saveEUROBENCH(controlador, emg, angle, trajectorie, onst):
    global subject, date, trial, repeat

    Canal1_Raw_Total = emg[0]#soleo R
    Canal2_Raw_Total = emg[1]# RF R
    Canal3_Raw_Total = emg[2]# soleo L
    Canal4_Raw_Total = emg[3]# RF L  
    Canal5_Raw_Total = emg[4]
    Canal6_Raw_Total = emg[5]
    Canal7_Raw_Total = emg[6]
    Canal8_Raw_Total = emg[7]
    Canal9_Raw_Total = emg[8]
    Canal10_Raw_Total = emg[9]
    Canal11_Raw_Total = emg[10]
    Canal12_Raw_Total = emg[11]
    
    tiempo = emg[18]
    
    dft = pd.DataFrame(tiempo,columns=['Tiempo'])
    df0 = pd.DataFrame(Canal5_Raw_Total,columns=['BiFe_left'])
    df1 = pd.DataFrame(Canal6_Raw_Total,columns=['GaMe_left'])
    df2 = pd.DataFrame(Canal1_Raw_Total,columns=['Sol_rigth'])
    df3 = pd.DataFrame(Canal2_Raw_Total,columns=['ReFe_rigth'])
    df4 = pd.DataFrame(Canal7_Raw_Total,columns=['TiAn_left'])
    df5 = pd.DataFrame(Canal8_Raw_Total,columns=['VaLa_left'])
    df6 = pd.DataFrame(Canal9_Raw_Total,columns=['BiFe_rigth'])   
    df7 = pd.DataFrame(Canal10_Raw_Total,columns=['GaMe_rigth'])
    df8 = pd.DataFrame(Canal3_Raw_Total,columns=['Sol_left'])
    df9 = pd.DataFrame(Canal4_Raw_Total,columns=['ReFe_left'])
    df10 = pd.DataFrame(Canal11_Raw_Total,columns=['TiAn_rigth'])
    df11 = pd.DataFrame(Canal12_Raw_Total,columns=['VaLa_rigth'])
    

    
    
    df = pd.concat([dft,df0,df1,df2,df3,df4,df5,df6,df7,df8,df9,df10,df11], axis = 1)

    df.to_csv(date + '_' + 'EUROBENCH_Subject' + '_' + subject + '_' + 'cond' + '_' + controlador + '_' + 'run' + '_' + trial + '.csv',sep=',')  



         
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
            speedBox.configure(bg=activebuttonCanFrame)
            raise NameError('"speed" EMPTY')
        else:
            speed=int(speedBox.get())
        try:
            objPCAN
        except:
            raise NameError("ERROR: CAN conection")
            
        interactionMSG.set("Walk Start")
        feedbackBox.insert(END, "Walk Start")
        speedBox.configure(bg="white")
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
    global anglejoin
    anglejoin =[]
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
#        pangleThread = Thread(target = readAngle, args = (objPCAN, seconds)) 
#        pangleThread.start()
#        pangleThread.join()
#        print(anglejoin)
#        joinangle = anglejoin
            
#        if len(joinangle) != 0 and seconds == 0:
        if seconds == 0:
            
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

                
                window=Tk()
                window.title("Angles")
                plot_button=Button(master=window, command=multiPlot(joinangle,window)) 
                window.mainloop()
        
            except:
#                raise TypeError("ERROR: EMG plot") 
                raise 
        
    except TypeError as text:
        interactionMSG.set(text)
        feedbackBox.insert(END, text)
        raise
        
        
def btTH(event):
    global Canal1_Env_Total, Canal2_Env_Total, Canal3_Env_Total, Canal4_Env_Total
   
    try:
        
        th1 = float(thBox.get())
        th2 = float(thBox2.get())
        th3 = float(thBox3.get())
        th4 = float(thBox4.get())

        c1normalized, on1 = thValues(Canal1_Env_Total, th1)
        c2normalized, on2 = thValues(Canal2_Env_Total, th2)
        c3normalized, on3 = thValues(Canal3_Env_Total, th3)
        c4normalized, on4 = thValues(Canal4_Env_Total, th4)
        
        onset.set("%.3f" % on1)
        offset.set("%.3f" % on1)
        
        onset2.set("%.3f" % on2)
        offset2.set("%.3f" % on2)
        
        onset3.set("%.3f" % on3)
        offset3.set("%.3f" % on3)
        
        onset4.set("%.3f" % on4)
        offset4.set("%.3f" % on4)
 
        
    except NameError as text:
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
        cuadroRepeat.configure(bg=activebuttonCanFrame)
        assistanceBox.configure(bg=activebuttonCanFrame)
    else:
        MS.set(0)
        cuadroRepeat.configure(bg="white")
        assistanceBox.configure(bg="white")
def chBox2(event):
    if MD.get() == 0:
        MD.set(1)
        assistanceBox.configure(bg=activebuttonCanFrame)
        stiffnessBox.configure(bg=activebuttonCanFrame)
        cuadroRepeat.configure(bg=activebuttonCanFrame)
    else:
        MD.set(0)
        assistanceBox.configure(bg="white")
        stiffnessBox.configure(bg="white")
        cuadroRepeat.configure(bg="white")
def chBox3(event):
    if OD.get() == 0:
        OD.set(1)
        assistanceBox.configure(bg=activebuttonCanFrame)
        cuadroRepeat.configure(bg=activebuttonCanFrame)
        stiffnessBox.configure(bg=activebuttonCanFrame)
    else:
        OD.set(0)
        assistanceBox.configure(bg="white")
        cuadroRepeat.configure(bg="white")
        stiffnessBox.configure(bg="white")
def chBox4(event):
    if EP.get() == 0:
        EP.set(1)
        assistanceBox.configure(bg=activebuttonCanFrame)
        cuadroRepeat.configure(bg=activebuttonCanFrame)
    else:
        EP.set(0)
        assistanceBox.configure(bg="white")
        cuadroRepeat.configure(bg="white")
            
def marckboxes():
    
    MS1=MS.get()
    MD1=MD.get()
    OD1=OD.get()
    EP1=EP.get()
    if (MS1 == 1) & (MD1 == 0) & (OD1 == 0) & (EP1 == 0):
        cuadroRepeat.configure(bg=activebuttonCanFrame)
    if (MS1 == 0) & (MD1 == 1) & (OD1 == 0) & (EP1 == 0):
        assistanceBox.configure(bg=activebuttonCanFrame)
        stiffnessBox.configure(bg=activebuttonCanFrame)
        cuadroRepeat.configure(bg=activebuttonCanFrame)
    if (MS1 == 0) & (MD1 == 0) & (OD1 == 1) & (EP1 == 0):
        assistanceBox.configure(bg=activebuttonCanFrame)
        cuadroRepeat.configure(bg=activebuttonCanFrame)
    if (MS1 == 0) & (MD1 == 0) & (OD1 == 0) & (EP1 == 1):
        assistanceBox.configure(bg=activebuttonCanFrame)
        cuadroRepeat.configure(bg=activebuttonCanFrame)
    else:
        assistanceBox.configure(bg="white")
        stiffnessBox.configure(bg="white")
        cuadroRepeat.configure(bg="white")
            

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
#bgCanFrame="#AF5457"
#bgCanFrame="#F9C6C3"
bgCanFrame="#A5DDFF"
fgCanFrame="#000000"
buttonCanFrame="#A5DDFF"
activebuttonCanFrame="#71D2FF"
CanFrame.config(width="900", height="700", bg=bgCanFrame)
CanFrame.config(cursor="hand2")

MesoFrame=Frame()
#MesoFrame.place(x=500, y=200)
#MesoFrame.pack()
MesoFrame.pack(side=LEFT, fill=BOTH, expand=True)
#bgMesoFrame="#60B06B"
bgMesoFrame="#5677FD"
fgMesoFrame="#000000"
MesoFrame.config(width="300", height="450", bg=bgMesoFrame)
MesoFrame.config(cursor="hand2")
root.bind('Q',btStop)
root.bind('E',exitF)
root.bind('P',btPassive)
root.bind('C',btCompliance)
#root.bind('U',btStandUp)
#root.bind('D',btSitDown)
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
#dest=StringVar()
meso=StringVar()
#ipinit=StringVar()

assis = StringVar()
stiff = StringVar()

assis.set('80')
stiff.set('20')


repeatint = IntVar()
onset = IntVar()
offset = IntVar()
period_off = IntVar()
thvalue = IntVar()
max_value = IntVar()
min_value = IntVar()

onset2 = IntVar()
offset2 = IntVar()
period_off2 = IntVar()
thvalue2 = IntVar()
max_value2 = IntVar()
min_value2 = IntVar()

onset3 = IntVar()
offset3 = IntVar()
period_off3 = IntVar()
thvalue3 = IntVar()
max_value3 = IntVar()
min_value3 = IntVar()

onset4 = IntVar()
offset4 = IntVar()
period_off4 = IntVar()
thvalue4 = IntVar()
max_value4 = IntVar()
min_value4 = IntVar()


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

#def functionTH(event):
#    global objPCAN
#    RunTH = Thread(target = btRUN, args = (event,objPCAN)) 
##            fillBox.daemon=True
#    RunTH.start()

buttonOK=Button(miFrame, text="OK", height = 1, width = 2, command= lambda: btOK()).place(x=1225, y=20)
buttonRUN=Button(miFrame, text="RUN", height = 1, width = 2, command= lambda: btRUN(event=True)).place(x=1225, y=60)
#buttonRUN=Button(miFrame, text="RUN", height = 1, width = 2, command=lambda:functionTH(event=True)).place(x=1225, y=60)
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
Label(CanFrame, text="CAN COMMUNICATION:", bg=bgCanFrame, fg=fgCanFrame,font=("Helvetica bold",12)).grid(row=0, column=0, padx=5, pady=5, columnspan=3, sticky="w")

#Label(CanFrame, text="CAN COMMUNICATION:", bg="#FAF3DD", fg="#2AC4DB",font=("Helvetica bold",12)).place(x=10, y=15)

#buttonCAN=Button(CanFrame, text="Connect CAN", height = 1, width = 10, command= lambda: btCAN()).place(x=10, y=50)
buttonCAN=Button(CanFrame, text="Connect CAN", height = 1, width = 10, bg=buttonCanFrame, activebackground=activebuttonCanFrame, command= lambda: btCAN(event))
buttonCAN.grid(row=1, column=0, padx=5, pady=5)
cuadroCan = Entry(CanFrame,textvariable=can, width = 56)
cuadroCan.grid(row=1, column=1, padx=5, pady=5, columnspan=5, sticky="w")
#cuadroCan.place(x=130, y=50, height = 30, width = 535)

#buttonEXO=Button(CanFrame, text="Exo Test", height = 1, width = 10, command= lambda: btEXO()).place(x=350, y=50)
#cuadroTestCan = Entry(CanFrame, textvariable=canTest)
#cuadroTestCan.grid(row=4, column=2, padx=100, pady=10)
#cuadroTestCan.place(x=470, y=50, height = 30, width = 200)

checkboxMS = Checkbutton(CanFrame, variable=MS, onvalue=1, offvalue=0, bg=bgCanFrame, fg=fgCanFrame, activebackground=bgCanFrame, text="Own Gait")
checkboxMS.grid(row=2, column=0, padx=5, pady=5, sticky="w")
#checkboxMS.place(x=10, y=100)  
checkboxMD = Checkbutton(CanFrame,variable=MD, onvalue=1, offvalue=0, bg=bgCanFrame, fg=fgCanFrame, activebackground=bgCanFrame, text="Impedance Gait")
#checkboxMD.grid(row=2, column=1, padx=5, pady=5, columnspan=1, sticky="w")
checkboxMD.place(x=120, y=78)   
checkboxOD = Checkbutton(CanFrame,variable=OD, onvalue=1, offvalue=0, bg=bgCanFrame, fg=fgCanFrame, activebackground=bgCanFrame, text="Onset Detection")
#checkboxOD.grid(row=2, column=2, padx=5, pady=5, sticky="w") 
checkboxOD.place(x=260, y=78)   
checkboxEP = Checkbutton(CanFrame,variable=EP, onvalue=1, offvalue=0, bg=bgCanFrame, fg=fgCanFrame, activebackground=bgCanFrame, text="EMG Proportional")
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


ConfigSetUP=115
assistanceLabel=Label(CanFrame, bg=bgCanFrame, text="Assistance (0-100):")
assistanceLabel.place(x=50, y=ConfigSetUP)
assistanceBox = Entry(CanFrame, width = 35, textvariable=assis)
assistanceBox.place(x=186, y=ConfigSetUP-3, height = 25, width = 40)

stiffnessLabel=Label(CanFrame, bg=bgCanFrame, text="Stiffness (0-100):")
stiffnessLabel.place(x=265, y=ConfigSetUP)
stiffnessBox = Entry(CanFrame, width = 35, textvariable=stiff)
stiffnessBox.place(x=390, y=ConfigSetUP-3, height = 25, width = 40)

speedLabel=Label(CanFrame, bg=bgCanFrame, text="Speed (1-10):")
speedLabel.place(x=475, y=ConfigSetUP)
speedBox = Entry(CanFrame, width = 35)
speedBox.place(x=580, y=ConfigSetUP-3, height = 25, width = 35)



yPosition1 = 155             
onsetLabel=Label(CanFrame, bg=bgCanFrame, text="Threshold1 On:")
#onsetLabel.grid(row=3, column=0, padx=10, pady=10)
onsetLabel.place(x=10, y=yPosition1)
cuadroOnset = Entry(CanFrame, textvariable=onset)
#cuadroOnset.grid(row=3, column=1, padx=100, pady=10, columnspan=5, sticky="w")
cuadroOnset.place(x=115, y=yPosition1-3, height = 25, width = 60)

offsetLabel=Label(CanFrame, bg=bgCanFrame, text="Threshold1 Off:")
#offsetLabel.grid(row=4, column=0, padx=10, pady=10)
offsetLabel.place(x=180, y=yPosition1)
cuadroOffset = Entry(CanFrame, textvariable=offset)
cuadroOffset.place(x=285, y=yPosition1-3, height = 25, width = 60)
             
#periodLabel=Label(CanFrame, bg=bgCanFrame, text="Period1 Off:")
#periodLabel.grid(row=5, column=0, padx=10, pady=10)
#periodLabel.place(x=350, y=yPosition1)
#cuadroPeriod = Entry(CanFrame, textvariable=period_off)
#cuadroPeriod.place(x=435, y=yPosition1-3, height = 25, width = 60)

maxLabel=Label(CanFrame, bg=bgCanFrame, text="Max1:")
maxLabel.place(x=360, y=yPosition1)
cuadroMax = Entry(CanFrame, textvariable=max_value)
cuadroMax.place(x=410, y=yPosition1-3, height = 25, width = 60)

minLabel=Label(CanFrame, bg=bgCanFrame, text="Min1:")
minLabel.place(x=480, y=yPosition1)
cuadroMin = Entry(CanFrame, textvariable=min_value)
cuadroMin.place(x=525, y=yPosition1-3, height = 25, width = 60)


thLabel=Label(CanFrame, bg=bgCanFrame, text="Th1:")
thLabel.place(x=620, y=yPosition1)
thBox = Entry(CanFrame, textvariable=thvalue)
thBox.place(x=652, y=yPosition1-3, height = 25, width = 35)




yPosition2 = 195
onsetLabel2=Label(CanFrame, bg=bgCanFrame, text="Threshold2 On:")
onsetLabel2.place(x=10, y=yPosition2)
cuadroOnset2 = Entry(CanFrame, textvariable=onset2)
cuadroOnset2.place(x=115, y=yPosition2, height = 25, width = 60)

offsetLabel2=Label(CanFrame, bg=bgCanFrame, text="Threshold2 Off:")
offsetLabel2.place(x=180, y=yPosition2)
cuadroOffset2 = Entry(CanFrame, textvariable=offset2)
cuadroOffset2.place(x=285, y=yPosition2-3, height = 25, width = 60)
             
#periodLabel2 = Label(CanFrame, bg=bgCanFrame, text="Period2 Off:")
#periodLabel2.place(x=350, y=yPosition2)
#cuadroPeriod2 = Entry(CanFrame, textvariable=period_off2)
#cuadroPeriod2.place(x=435, y=yPosition2-3, height = 25, width = 60)

maxLabel=Label(CanFrame, bg=bgCanFrame, text="Max2:")
maxLabel.place(x=360, y=yPosition2)
cuadroMax = Entry(CanFrame, textvariable=max_value2)
cuadroMax.place(x=410, y=yPosition2-3, height = 25, width = 60)

minLabel=Label(CanFrame, bg=bgCanFrame, text="Min2:")
minLabel.place(x=480, y=yPosition2)
cuadroMin = Entry(CanFrame, textvariable=min_value2)
cuadroMin.place(x=525, y=yPosition2-3, height = 25, width = 60)


thLabel2=Label(CanFrame, bg=bgCanFrame, text="Th2:")
thLabel2.place(x=620, y=yPosition2)
thBox2 = Entry(CanFrame, textvariable=thvalue2)
thBox2.place(x=652, y=yPosition2-3, height = 25, width = 35)


yPosition3 = 235
onsetLabel3=Label(CanFrame, bg=bgCanFrame, text="Threshold3 On:")
onsetLabel3.place(x=10, y=yPosition3)
cuadroOnset3 = Entry(CanFrame, textvariable=onset3)
cuadroOnset3.place(x=115, y=yPosition3-3, height = 25, width = 60)

offsetLabel3=Label(CanFrame, bg=bgCanFrame, text="Threshold3 Off:")
offsetLabel3.place(x=180, y=yPosition3)
cuadroOffset3 = Entry(CanFrame, textvariable=offset3)
cuadroOffset3.place(x=285, y=yPosition3-3, height = 25, width = 60)
             
#periodLabel3 = Label(CanFrame, bg=bgCanFrame, text="Period3 Off:")
#periodLabel3.place(x=350, y=yPosition3)
#cuadroPeriod3 = Entry(CanFrame, textvariable=period_off3)
#cuadroPeriod3.place(x=435, y=yPosition3-3, height = 25, width = 60)

maxLabel=Label(CanFrame, bg=bgCanFrame, text="Max3:")
maxLabel.place(x=360, y=yPosition3)
cuadroMax = Entry(CanFrame, textvariable=max_value3)
cuadroMax.place(x=410, y=yPosition3-3, height = 25, width = 60)

minLabel=Label(CanFrame, bg=bgCanFrame, text="Min3:")
minLabel.place(x=480, y=yPosition3)
cuadroMin = Entry(CanFrame, textvariable=min_value3)
cuadroMin.place(x=525, y=yPosition3-3, height = 25, width = 60)

thLabel3=Label(CanFrame, bg=bgCanFrame, text="Th3:")
thLabel3.place(x=620, y=yPosition3)
thBox3 = Entry(CanFrame, textvariable=thvalue3)
thBox3.place(x=652, y=yPosition3-3, height = 25, width = 35)


yPosition4 = 275
onsetLabel4=Label(CanFrame, bg=bgCanFrame, text="Threshold4 On:")
onsetLabel4.place(x=10, y=yPosition4)
cuadroOnset4 = Entry(CanFrame, textvariable=onset4)
cuadroOnset4.place(x=115, y=yPosition4-3, height = 25, width = 60)

offsetLabel4=Label(CanFrame, bg=bgCanFrame, text="Threshold4 Off:")
offsetLabel4.place(x=180, y=yPosition4)
cuadroOffset4 = Entry(CanFrame, textvariable=offset4)
cuadroOffset4.place(x=285, y=yPosition4-3, height = 25, width = 60)
             
#periodLabel4 = Label(CanFrame, bg=bgCanFrame, text="Period4 Off:")
#periodLabel4.place(x=350, y=yPosition4)
#cuadroPeriod4 = Entry(CanFrame, textvariable=period_off4)
#cuadroPeriod4.place(x=435, y=yPosition4-3, height = 25, width = 60)

maxLabel=Label(CanFrame, bg=bgCanFrame, text="Max4:")
maxLabel.place(x=360, y=yPosition4)
cuadroMax = Entry(CanFrame, textvariable=max_value4)
cuadroMax.place(x=410, y=yPosition4-3, height = 25, width = 60)

minLabel=Label(CanFrame, bg=bgCanFrame, text="Min4:")
minLabel.place(x=480, y=yPosition4)
cuadroMin = Entry(CanFrame, textvariable=min_value4)
cuadroMin.place(x=525, y=yPosition4-3, height = 25, width = 60)

thLabel4=Label(CanFrame, bg=bgCanFrame, text="Th4:")
thLabel4.place(x=620, y=yPosition4)
thBox4 = Entry(CanFrame, textvariable=thvalue4)
thBox4.place(x=652, y=yPosition4-3, height = 25, width = 35)



ybtOptions = 350 
ybtOptions2 = 310
buttonStandUp=Button(CanFrame, text="Stand-up", height = 1, width = 10, bg=buttonCanFrame, activebackground=activebuttonCanFrame, command= lambda: btStandUp(event))
#buttonStandUp.grid(row=6, column=0, padx=5, pady=5, sticky="w")
buttonStandUp.place(x=5, y=ybtOptions)
buttonSitDown=Button(CanFrame, text="Sit-down", height = 1, width = 10, bg=buttonCanFrame, activebackground=activebuttonCanFrame, command= lambda: btSitDown(event))
#buttonSitDown.grid(row=6, column=1, padx=5, pady=5, sticky="e")
buttonSitDown.place(x=120, y=ybtOptions)
buttonCompliance=Button(CanFrame, text="Compliance", height = 1, width = 8, bg=buttonCanFrame, activebackground=activebuttonCanFrame, command= lambda: btCompliance(event))
#buttonCompliance.grid(row=6, column=2, padx=5, pady=5, sticky="w")
buttonCompliance.place(x=235, y=ybtOptions)
buttonCompliance=Button(CanFrame, text="Passive", height = 1, width = 6, bg=buttonCanFrame, activebackground=activebuttonCanFrame, command= lambda: btPassive(event))
#buttonCompliance.grid(row=6, column=3, padx=5, pady=5, sticky="w")
buttonCompliance.place(x=333, y=ybtOptions)
buttonEAST=Button(CanFrame, text="Record EMG", height = 1, width = 10, bg=buttonCanFrame, activebackground=activebuttonCanFrame, command= lambda: btEAST(event))
#buttonEAST.grid(row=6, column=4, padx=5, pady=5, sticky="w")
buttonEAST.place(x=416, y=ybtOptions)
buttonWalking=Button(CanFrame, text="Walking", height = 1, width = 10, bg=buttonCanFrame, activebackground=activebuttonCanFrame, command= lambda: btWalking(event))
#buttonWalking.grid(row=6, column=5, padx=5, pady=5, sticky="w")
buttonWalking.place(x=530, y=ybtOptions)
buttonStopExo=Button(CanFrame, text="STOP WALK", height = 1, width = 10, bg=buttonCanFrame, activebackground=activebuttonCanFrame, command= lambda: btStopExo(event))
#buttonStopExo.grid(row=7, column=5, padx=5, pady=5, sticky="w")
buttonStopExo.place(x=640, y=ybtOptions)

buttonWalking=Button(CanFrame, text="TH", height = 1, width = 4, bg=buttonCanFrame, activebackground=activebuttonCanFrame, command= lambda: btTH(event))
#buttonWalking.grid(row=6, column=6, padx=5, pady=5, sticky="w")
buttonWalking.place(x=640, y=ybtOptions2)
interactionMSG=StringVar()
buttonWalking=Button(CanFrame, text="Angles", height = 1, width = 6, bg=buttonCanFrame, activebackground=activebuttonCanFrame, command= lambda: btAngles())
#buttonWalking.grid(row=6, column=6, padx=5, pady=5, sticky="w")
buttonWalking.place(x=540, y=ybtOptions2)
interactionMSG=StringVar()
msgBox = Entry(CanFrame, textvariable=interactionMSG, width=50)
#msgBox.grid(row=7, column=1, padx=5, pady=5, columnspan=5, sticky="w")
msgBox.place(x=80, y=ybtOptions2, height = 30, width = 450)
msgBox.config(justify="center")



#%% ROS FRAME
Label(MesoFrame, text="ROS COMMUNICATION:", bg=bgMesoFrame, fg=fgMesoFrame,font=("Helvetica bold",12)).grid(row=0, column=0, padx=5, pady=5, columnspan=3, sticky="w")

#ipLabel=Label(MesoFrame, text="IP Control Unit:", bg=bgMesoFrame, font=("Helvetica bold",12))
#ipLabel.place(x=10, y=50)
#cuadroIp = Entry(MesoFrame, textvariable=ipinit)
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

buttonR=Button(MesoFrame, text="TURN OFF EXO", height = 1, width = 32, bg='#DB292F', fg='white', activebackground="red", command= lambda: btStop(event))
buttonR.grid(row=2, column=0, padx=10, pady=10, columnspan=3)
#buttonR.place(x=120, y=270)

#%%  Parameters

event=True

'''
buttonEXIT=Button(root, text='Exit')
buttonEXIT.pack(side=BOTTOM)  
'''
        

#fillBox = Thread(target = marckboxes, args = ()) 
#fillBox.daemon=True
#fillBox.start()

#if MD1:
#    checkboxMD.configure(bg=bgCanFrame)
#else:
#    checkboxMD.configure(bg="red")

root.mainloop()