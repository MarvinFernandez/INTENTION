
#import logging
from threading import Semaphore
from PCANBasic import TPCANMsg, PCAN_PCIBUS3, PCAN_MESSAGE_STANDARD

#from multiprocessing.pool import ThreadPool
#import multiprocessing
from EAST import EAST, EASTrec
#from EASTCopia import EAST, EASTrec
from EXO_H3 import Exo_H3, ReadAngle, Exo_move, ReadTorque


         

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
        
        sfprocess.acquire()
        
        emg = dataCollector.join()
        

    except KeyboardInterrupt:
        print("INTERRUT3 EAST")
        sfexit._value = 1
        emg = dataCollector.join()
        
    
    
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
        sfRead = Semaphore(2) # read exo joins (angle / torque)
        sfexit = Semaphore(0) # break forzoso
        
    #    dataCollector = Thread(target = getData, args = (repeat,sfprocess,sfMove,sfRead)) 
        dataCollector = EAST(target = EASTrec, args = (sfprocess,sfMove,sfRead,sfexit,seconds)) 
        anglefn = Exo_H3(target = ReadAngle, args = (objPCAN,sfprocess,sfRead,sfexit)) 
        torquefn = Exo_H3(target = ReadTorque, args = (objPCAN,sfprocess,sfRead,sfexit)) 
        exoMovement = Exo_H3(target = Exo_move, args = (objPCAN,msg,sfprocess,sfMove,sfexit)) 
        
        anglefn.start()
        torquefn.start()
        exoMovement.start()
        dataCollector.start() 
        
        
        sfprocess.acquire()
        
        sfexit._value = 1
        sfMove.release()
        sfRead.release()
        sfRead.release()
        
        anglesArray = anglefn.join()
        torqueArray = torquefn.join()
        trajectories = exoMovement.join()
        emg = dataCollector.join()
        
    except KeyboardInterrupt:
        print("INTERRUT3")
        sfexit._value = 1
        sfMove.release()
        sfRead.release()
        sfRead.release()
        anglesArray = anglefn.join()
        torqueArray = torquefn.join()
        trajectories = exoMovement.join()
        emg = dataCollector.join()
        

    return emg, anglesArray, trajectories, torqueArray

