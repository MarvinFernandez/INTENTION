

import numpy as np
import time
from PCANBasic import PCAN_PCIBUS3, PCAN_ERROR_QRCVEMPTY, TPCANMsg, PCAN_MESSAGE_STANDARD

msg = TPCANMsg()
msg1 = TPCANMsg()

FS_Lankle_ang = np.array([6,6,6,6,7,7,8,8,9,10,11,11,12,12,12,12,13,13,14,16,17,18,19,20,20])
FS_Lknee_ang = np.array([0,0,0,0,0,0,0,0,0,0,1,1,1,2,2,2,3,3,3,4,4,4,5,5,5])
FS_Lhip_ang= np.array([0,0,0,0,0,0,0,0,-1,-1,-1,-2,-2,-3,-3,-4,-5,-6,-7,-8,-8,-9,-10,-12,-13])
FS_Rankle_ang = np.array([4,2,0,-2,-5,-7,-9,-10,-11,-12,-12,-12,-11,-8,-3,1,5,7,8,8,7,6,6,6,5])
FS_Rknee_ang= np.array([2,4,7,10,13,17,21,26,31,38,43,47,50,50,47,41,33,25,19,13,9,7,6,5,5])
FS_Rhip_ang= np.array([2,4,7,10,12,14,16,18,20,21,22,23,24,25,26,27,27,27,28,28,29,29,30,30,30])

#    RHip = np.array([31,30,30,29,29,29,28,28,28,26,25,24,24,24,23,22,21,20,20,20,19,18,17,17,16,16,15,14,13,13,12,11,11,10,9,9,8,7,7,6,6,5,4,3,3,2,2,1,0,-1,-1,-2,-2,-2,-3,-3,-4,-5,-5,-6,-6,-6,-7,-8,-8,-9,-9,-9,-9,-10,-10,-11,-11,-11,-11,-12,-12,-13,-13,-13,-13,-14,-14,-15,-15,-15,-15,-15,-15,-14,-14,-14,-14,-14,-14,-14,-13,-13,-12,-12,-12,-12,-11,-11,-10,-10,-9,-8,-7,-6,-4,-3,-2,0,1,2,4,5,6,8,9,10,11,12,13,14,15,16,17,17,18,19,20,21,22,23,24,25,26,26,26,27,27,28,28,29,29,29,30,30,30])
#    RKnee = np.array([5,6,6,6,6,6,7,7,8,8,8,9,10,11,11,11,11,12,12,12,12,12,12,11,11,11,11,10,9,9,8,8,7,7,7,6,6,6,5,5,5,4,4,4,3,3,3,2,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,2,2,2,2,3,3,4,4,4,4,5,5,6,7,7,8,9,9,10,11,11,12,13,14,15,16,17,19,20,22,24,26,28,30,32,34,36,38,41,44,47,50,52,55,56,58,59,59,60,60,60,60,59,57,53,49,45,41,38,35,31,28,26,23,21,19,17,15,13,11,10,9,8,7,7,7,6,6,5,5,5,5,6])
#    RAnkle = np.array([5,5,5,4,3,3,3,3,3,2,2,2,2,2,3,3,3,3,4,5,5,6,6,7,7,7,7,8,8,9,10,10,11,11,11,11,11,11,12,12,12,12,12,12,12,12,12,12,12,12,13,13,13,13,13,13,13,14,14,15,16,16,17,17,17,18,18,18,18,19,19,20,20,20,20,20,20,20,20,20,20,20,20,20,19,19,18,17,17,16,16,15,14,13,12,11,10,8,7,5,3,2,0,-2,-4,-6,-8,-9,-11,-12,-13,-14,-14,-14,-13,-12,-11,-9,-8,-6,-4,-3,-1,0,1,3,4,5,6,7,7,7,8,8,8,8,8,8,7,7,6,6,6,6,6,6,6,6,6,7,7])
#    LHip = np.array([-13,-13,-13,-14,-14,-15,-15,-15,-15,-15,-15,-15,-15,-15,-14,-14,-14,-14,-14,-14,-14,-13,-13,-12,-12,-12,-12,-11,-11,-10,-10,-9,-8,-7,-6,-4,-3,-2,0,1,2,4,5,6,8,9,10,11,12,13,14,15,16,17,17,18,19,20,21,22,23,24,25,26,26,26,27,27,28,28,29,29,29,30,30,30,30,30,30,29,29,29,28,28,28,26,25,24,24,24,23,22,21,20,20,20,19,18,17,17,16,16,15,14,13,13,12,11,11,10,9,9,8,7,7,6,6,5,4,3,3,2,2,1,0,-1,-1,-2,-2,-2,-3,-3,-4,-5,-5,-6,-6,-6,-7,-8,-8,-9,-9,-9,-9,-10,-10,-11,-11,-11,-11])
#    LKnee = np.array([5,5,5,5,5,6,7,7,8,9,9,10,11,11,12,13,14,15,16,17,19,20,22,24,26,28,30,32,34,36,38,41,44,47,50,52,55,56,58,59,59,60,60,60,60,59,57,53,49,45,41,38,35,31,28,26,23,21,19,17,15,13,11,10,9,8,7,7,7,6,6,5,5,5,5,5,5,6,6,6,6,6,7,7,8,8,8,9,10,11,11,11,11,12,12,12,12,12,12,11,11,11,11,10,9,9,8,8,7,7,7,6,6,6,5,5,5,4,4,4,3,3,3,2,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,2,2,2,2,3,3,4])
#    LAnkle = np.array([21,21,21,21,20,20,20,20,20,19,19,18,17,17,16,16,15,14,13,12,11,10,8,7,5,3,2,0,-2,-4,-6,-8,-9,-11,-12,-13,-14,-14,-14,-13,-12,-11,-9,-8,-6,-4,-3,-1,0,1,3,4,5,6,7,7,7,8,8,8,8,8,8,7,7,6,6,6,6,6,6,6,6,6,6,6,5,5,5,4,3,3,3,3,3,2,2,2,2,2,3,3,3,3,4,5,5,6,6,7,7,7,7,8,8,9,10,10,11,11,11,11,11,11,12,12,12,12,12,12,12,12,12,12,12,12,13,13,13,13,13,13,13,14,14,15,16,16,17,17,17,18,18,18,18,19,19,20,20,20,20])


Rhip_ang= np.array([30,29,28,26,24,22,20,18,16,14,12,10,8,6,4,2,0,-2,-3,-5,-6,-8,-9,-10,-11,-12,-13,-14,-15,-15,-14,-14,-13,-12,-11,-9,-6,-2,2,6,10,13,16,18,21,24,26,28,29,30,30])
Rknee_ang = np.array([3,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,3,4,5,7,9,11,14,17,21,27,33,40,49,56,59,60,57,46,35,26,19,13,9,7,6,5,4])
Rankle_ang = np.array([5,4,3,2,2,3,4,6,7,8,10,11,11,12,12,12,12,13,13,14,16,17,18,19,20,20,20,20,19,17,15,12,9,4,-1,-7,-12,-14,-12,-8,-3,1,5,7,8,8,7,6,6,6,6])
Lhip_ang= np.array([-13,-13,-14,-14,-14,-15,-15,-14,-13,-11,-8,-5,-1,4,8,12,16,20,23,26,28,29,30,30,30,29,28,26,24,22,20,18,16,14,12,10,8,6,4,2,0,-2,-4,-6,-7,-9,-10,-11,-11,-12,-12])
Lknee_ang= np.array([5,5,6,7,8,9,11,13,16,20,15,32,39,50,58,60,57,48,39,31,22,14,9,7,6,5,4,3,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,2,3,4])
Lankle_ang = np.array([20,20,19,17,15,12,9,4,-1,-7,-11,-13,-12,-8,-3,1,5,7,8,8,7,6,6,6,6,5,4,3,3,2,3,4,6,7,8,10,11,11,12,12,12,12,13,13,14,16,17,18,19,20,20])

LS_Rhip_ang= np.array([30,  29,  28,  26,  24,  22,  20,  18,  16,  14,  12,  10,
                       8,   6,   4,   2,   0,  -2,  -3,  -5,  -6,  -8,  -9, -10, -11,
                       -12, -13, -14, -15, -15, -14, -14, -13, -12, -11,  -9,  -6,  -2,
                       2,   6,  10,   9,   8,   7,   6,   5,   4,   4,   4,   4,   4,
                       4,   4,   4,   4,   4,   4,   4,   4])
LS_Rknee_ang = np.array([3,  2,  2,  1,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
                         0,  0,  0,  0,  0,  0,  1,  2,  3,  4,  5,  7,  9, 11, 14, 17, 21,
                         27, 33, 40, 49, 56, 59, 60, 57, 50, 44, 38, 33, 29, 25, 22, 19, 17,
                         15, 13, 11, 10,  9,  8,  7,  6,  5])
LS_Rankle_ang = np.array([5,   4,   3,   2,   2,   3,   4,   6,   7,   8,  10,  11,
                          11,  12,  12,  12,  12,  13,  13,  14,  16,  17,  18,  19,  20,
                          20,  20,  20,  19,  17,  15,  12,   9,   4,  -1,  -7, -12, -14,
                          -12,  -8,  -3,  -3,  -3,  -3,  -3,  -3,  -3,  -3,  -3,  -3,  -3,
                          -3,  -3,  -3,  -3,  -3,  -3,  -3,  -3])
LS_Lhip_ang= np.array([-13, -13, -14, -14, -14, -15, -15, -14, -13, -11,  -8,  -5,
                       -1,   4,   8,  12,  16,  20,  23,  26,  28,  29,  30,  30,  30,
                       29,  28,  26,  24,  22,  20,  18,  16,  14,  12,  10,   8,   6,
                       4,   2,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
                       0,   0,   0,   0,   0,   0,   0,   0])
LS_Lknee_ang= np.array([5,  5,  6,  7,  8,  9, 11, 13, 16, 20, 15, 32, 39, 50, 58, 60,
                        57, 48, 39, 31, 22, 14,  9,  7,  6,  5,  4,  3,  2,  2,  1,  1,  1,
                        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
                        0,  0,  0,  0,  0,  0,  0,  0,  0])
LS_Lankle_ang = np.array([20,  20,  19,  17,  15,  12,   9,   4,  -1,  -7, -11, -13,
                          -12,  -8,  -3,   1,   5,   7,   8,   8,   7,   6,   6,   6,   6,
                          5,   4,   3,   3,   2,   3,   4,   6,   7,   8,  10,  11,  11,
                          12,  12,  12,  10,   9,   8,   7,   6,   5,   4,   4,   4,   4,
                          4,   4,   4,   4,   4,   4,   4,   4])


def firstStep(objPCAN):
    
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
    
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.ID = 72 #POSITION SET POINT
    msg.LEN = 6
    
    print("FIRST STEP")
    for index_FS in range(0,len(FS_Rankle_ang)-1,1):
        msg.DATA[0] = FS_Rhip_ang[index_FS]
        msg.DATA[1] = FS_Rknee_ang[index_FS]
        msg.DATA[2] = FS_Rankle_ang[index_FS]
        msg.DATA[3] = FS_Lhip_ang[index_FS]
        msg.DATA[4] = FS_Lknee_ang[index_FS]
        msg.DATA[5] = FS_Lankle_ang[index_FS]
        objPCAN.Write(PCAN_PCIBUS3,msg)
        time.sleep(0.1)
        
def lastStep(objPCAN):
    
    print("LAST STEP")
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.ID = 72 #POSITION SET POINT
    msg.LEN = 6
    for index_LStep in range(0,len(LS_Rhip_ang)-1,1):
        msg.DATA[0] = LS_Rhip_ang[index_LStep]
        msg.DATA[1] = LS_Rknee_ang[index_LStep]
        msg.DATA[2] = LS_Rankle_ang[index_LStep]
        msg.DATA[3] = LS_Lhip_ang[index_LStep]
        msg.DATA[4] = LS_Lknee_ang[index_LStep]
        msg.DATA[5] = LS_Lankle_ang[index_LStep]
        objPCAN.Write(PCAN_PCIBUS3,msg)
        time.sleep(0.1)
        
def steps(objPCAN,steps):
    
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.ID = 72 #POSITION SET POINT
    msg.LEN = 6
    
    for i in range(0,steps):
        print("STEP: ",i+1)
        for index_Step in range(0,len(Rhip_ang)-1,1):
            msg.DATA[0] = Rhip_ang[index_Step]
            msg.DATA[1] = Rknee_ang[index_Step]
            msg.DATA[2] = Rankle_ang[index_Step]
            msg.DATA[3] = Lhip_ang[index_Step]
            msg.DATA[4] = Lknee_ang[index_Step]
            msg.DATA[5] = Lankle_ang[index_Step]
            objPCAN.Write(PCAN_PCIBUS3,msg) 
            time.sleep(0.1)
    
def OwnWalk(objPCAN, gaits):
    
    ## TYPE CONTROL (1:POSITION / 2:STIFFNESS / 3:TORQUE / 4:DISABLE / 5:STOPPED)
    msg3 = TPCANMsg() 
    msg3.ID = 71
    msg3.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg3.LEN = 6
    msg3.DATA[0] = 1
    msg3.DATA[1] = 1
    msg3.DATA[2] = 1
    msg3.DATA[3] = 1
    msg3.DATA[4] = 1
    msg3.DATA[5] = 1
    objPCAN.Write(PCAN_PCIBUS3,msg3)
    
    #"FIRST STEP"
    firstStep(objPCAN)
    #"STRIDE"
    steps(objPCAN,gaits)
    #"LAST STEP"
    lastStep(objPCAN)
    
    
def gait(objPCAN, steps):
    
    rHip_Record = []
    rKnee_Record = []
    rAnkle_Record = []
    lHip_Record = []
    lKnee_Record = []
    lAnkle_Record = []
    
    repeat_step=steps
    
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.ID = 72 #POSITION SET POINT
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
    msg3 = TPCANMsg() 
    msg3.ID = 71
    msg3.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg3.LEN = 6
    msg3.DATA[0] = 1
    msg3.DATA[1] = 1
    msg3.DATA[2] = 1
    msg3.DATA[3] = 1
    msg3.DATA[4] = 1
    msg3.DATA[5] = 1
    objPCAN.Write(PCAN_PCIBUS3,msg3)
    
    #####################FIRST STEP####################     
    print("FIRST STEP")
    for index_FS in range(0,len(FS_Rankle_ang)-1,1):
        msg.DATA[0] = FS_Rhip_ang[index_FS]
        msg.DATA[1] = FS_Rknee_ang[index_FS]
        msg.DATA[2] = FS_Rankle_ang[index_FS]
        msg.DATA[3] = FS_Lhip_ang[index_FS]
        msg.DATA[4] = FS_Lknee_ang[index_FS]
        msg.DATA[5] = FS_Lankle_ang[index_FS]
        objPCAN.Write(PCAN_PCIBUS3,msg)
        time.sleep(0.1)
        
    for i in range(0,repeat_step):
        print("STEP: ",i+1)
        for index_Step in range(0,len(Rhip_ang)-1,1):
            msg.DATA[0] = Rhip_ang[index_Step]
            msg.DATA[1] = Rknee_ang[index_Step]
            msg.DATA[2] = Rankle_ang[index_Step]
            msg.DATA[3] = Lhip_ang[index_Step]
            msg.DATA[4] = Lknee_ang[index_Step]
            msg.DATA[5] = Lankle_ang[index_Step]
            objPCAN.Write(PCAN_PCIBUS3,msg) 
            
            #READ ANGLE FROM H3
            tR0=time.time() 
            read=objPCAN.Read(PCAN_PCIBUS3)
            joinangle=0
            while read[0] != PCAN_ERROR_QRCVEMPTY: #32 = buffere empty
                if read[1].ID == 110:
                    joinangle=read[1].DATA
                read=objPCAN.Read(PCAN_PCIBUS3)
            tR1=time.time()- tR0
            anglejoin=np.array([joinangle[0],joinangle[1],joinangle[2],joinangle[3],
                                joinangle[4],joinangle[5]]) 
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
                    
                rHip_Record=np.concatenate((rHip_Record,anglejoin[0]),axis=None)
                rKnee_Record=np.concatenate((rKnee_Record,anglejoin[1]),axis=None)
                rAnkle_Record=np.concatenate((rAnkle_Record,anglejoin[2]),axis=None)
                lHip_Record=np.concatenate((lHip_Record,anglejoin[3]),axis=None)
                lKnee_Record=np.concatenate((lKnee_Record,anglejoin[4]),axis=None)
                lAnkle_Record=np.concatenate((lAnkle_Record,anglejoin[5]),axis=None)
#                if joinangle[1] > 15:
#                    ##  ASISTANCE
#                    msg1.DATA[0] = 10
#                    msg1.DATA[1] = 10
#                    msg1.DATA[2] = 10
#                    msg1.DATA[3] = 10
#                    msg1.DATA[4] = 10
#                    msg1.DATA[5] = 10
#                    objPCAN.Write(PCAN_PCIBUS3,msg1)
#                if joinangle[1] > 38:
#                    ##  ASISTANCE
#                    msg1.DATA[0] = 80
#                    msg1.DATA[1] = 80
#                    msg1.DATA[2] = 80
#                    msg1.DATA[3] = 80
#                    msg1.DATA[4] = 80
#                    msg1.DATA[5] = 80
#                    objPCAN.Write(PCAN_PCIBUS3,msg1)
#            recordAngle_Time=np.concatenate((recordAngle_Time,tR1),axis=None)
            time.sleep(0.1-tR1)
            
#        if i == 3:
#            ##  ASISTANCE
#            msg1.DATA[0] = 10
#            msg1.DATA[1] = 10
#            msg1.DATA[2] = 10
#            msg1.DATA[3] = 10
#            msg1.DATA[4] = 10
#            msg1.DATA[5] = 10
#            objPCAN.Write(PCAN_PCIBUS3,msg1)
            
            
        ############################LAST STEP#################################
    print("LAST STEP")        
    for index_LStep in range(0,len(LS_Rhip_ang)-1,1):
        msg.DATA[0] = LS_Rhip_ang[index_LStep]
        msg.DATA[1] = LS_Rknee_ang[index_LStep]
        msg.DATA[2] = LS_Rankle_ang[index_LStep]
        msg.DATA[3] = LS_Lhip_ang[index_LStep]
        msg.DATA[4] = LS_Lknee_ang[index_LStep]
        msg.DATA[5] = LS_Lankle_ang[index_LStep]
        objPCAN.Write(PCAN_PCIBUS3,msg)
        time.sleep(0.1)
        
    return rHip_Record, rKnee_Record, rAnkle_Record, lHip_Record, lKnee_Record, lAnkle_Record




def impedance(objPCAN, gaits, assistance, stiffness):
    
    rHip_Record = []
    rKnee_Record = []
    rAnkle_Record = []
    lHip_Record = []
    lKnee_Record = []
    lAnkle_Record = []
    
    msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg.ID = 72 #POSITION SET POINT
    msg.LEN = 6
    
    ## TYPE CONTROL (1:POSITION / 2:STIFFNESS (admitance) / 3:TORQUE / 4:DISABLE / 5:STOPPED)
    msg3 = TPCANMsg() 
    msg3.ID = 71
    msg3.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg3.LEN = 6
    msg3.DATA[0] = 2
    msg3.DATA[1] = 2
    msg3.DATA[2] = 2
    msg3.DATA[3] = 2
    msg3.DATA[4] = 2
    msg3.DATA[5] = 2
    objPCAN.Write(PCAN_PCIBUS3,msg3)
    
#    stiffness = 10
    msg1.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg1.ID = 74 #STIFFNESS SET POINT
    msg1.LEN = 6
    msg1.DATA[0] = stiffness
    msg1.DATA[1] = stiffness
    msg1.DATA[2] = stiffness
    msg1.DATA[3] = stiffness
    msg1.DATA[4] = stiffness
    msg1.DATA[5] = stiffness
    objPCAN.Write(PCAN_PCIBUS3,msg1)
    
#    assistance = 100 
    msg2 = TPCANMsg() 
    msg2.MSGTYPE = PCAN_MESSAGE_STANDARD
    msg2.ID = 76 #PERCENTAGE OF ASSISTANCE
    msg2.LEN = 6
    msg2.DATA[0] = assistance
    msg2.DATA[1] = assistance
    msg2.DATA[2] = assistance
    msg2.DATA[3] = assistance
    msg2.DATA[4] = assistance
    msg2.DATA[5] = assistance
    objPCAN.Write(PCAN_PCIBUS3,msg2)
    
    firstStep(objPCAN)
    
    for i in range(0,gaits):
        print("STEP: ",i+1)
        for index_Step in range(0,len(Rhip_ang)-1,1):
            msg.DATA[0] = Rhip_ang[index_Step]
            msg.DATA[1] = Rknee_ang[index_Step]
            msg.DATA[2] = Rankle_ang[index_Step]
            msg.DATA[3] = Lhip_ang[index_Step]
            msg.DATA[4] = Lknee_ang[index_Step]
            msg.DATA[5] = Lankle_ang[index_Step]
            objPCAN.Write(PCAN_PCIBUS3,msg) 
            
            #READ ANGLE FROM H3
            tR0=time.time() 
            read=objPCAN.Read(PCAN_PCIBUS3)
            joinangle=0
            while read[0] != PCAN_ERROR_QRCVEMPTY: #32 = buffere empty
                if read[1].ID == 110:
                    joinangle=read[1].DATA
                read=objPCAN.Read(PCAN_PCIBUS3)
#            tR1=time.time()- tR0
            anglejoin=np.array([joinangle[0],joinangle[1],joinangle[2],joinangle[3],
                                joinangle[4],joinangle[5]]) 
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
                    
                rHip_Record=np.concatenate((rHip_Record,anglejoin[0]),axis=None)
                rKnee_Record=np.concatenate((rKnee_Record,anglejoin[1]),axis=None)
                rAnkle_Record=np.concatenate((rAnkle_Record,anglejoin[2]),axis=None)
                lHip_Record=np.concatenate((lHip_Record,anglejoin[3]),axis=None)
                lKnee_Record=np.concatenate((lKnee_Record,anglejoin[4]),axis=None)
                lAnkle_Record=np.concatenate((lAnkle_Record,anglejoin[5]),axis=None)
                
            tR1=time.time()- tR0
            time.sleep(0.1-tR1)
            
    
    lastStep(objPCAN)
    return rHip_Record, rKnee_Record, rAnkle_Record, lHip_Record, lKnee_Record, lAnkle_Record

 
def readAngle(objPCAN,sec): #READ ANGLE FROM H3  + steps*1000
    
    joinangle = 0
    rHip_Record = []
    rKnee_Record = []
    rAnkle_Record = []
    lHip_Record = []
    lKnee_Record = []
    lAnkle_Record = []
    
    condition = True
        
    tR0 = time.time() 
    while condition:
    
        if time.time() - tR0 >= sec:
            condition = False
            
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
            
    #        print("right hip",anglejoin[0])
    #        print("right knee",anglejoin[1])
    #        print("right ankle",anglejoin[2])
    #        print("left hip",anglejoin[3])
    #        print("left knee",anglejoin[4])
    #        print("left ankle",anglejoin[5])
        else:
            raise TypeError("no exo angles recived")

    return rHip_Record, rKnee_Record, rAnkle_Record, lHip_Record, lKnee_Record, lAnkle_Record