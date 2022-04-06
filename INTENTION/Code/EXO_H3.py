
import numpy as np
import time

from threading import Thread
from PCANBasic import PCAN_PCIBUS3, PCAN_ERROR_QRCVEMPTY

#from datetime import datetime

#%% ANGLES

# First Step Right leg
FS_Rhip_ang= np.array([2,4,7,10,12,14,16,18,20,21,22,23,24,25,26,27,27,27,28,28,29,29,30,30,30])
FS_Rknee_ang= np.array([2,4,7,10,13,17,21,26,31,38,43,47,50,50,47,41,33,25,19,13,9,7,6,5,5])
FS_Rankle_ang = np.array([4,2,0,-2,-5,-7,-9,-10,-11,-12,-12,-12,-11,-8,-3,1,5,7,8,8,7,6,6,6,5])
FS_Lhip_ang= np.array([0,0,0,0,0,0,0,0,-1,-1,-1,-2,-2,-3,-3,-4,-5,-6,-7,-8,-8,-9,-10,-12,-13])
FS_Lknee_ang = np.array([0,0,0,0,0,0,0,0,0,0,1,1,1,2,2,2,3,3,3,4,4,4,5,5,5])
FS_Lankle_ang = np.array([6,6,6,6,7,7,8,8,9,10,11,11,12,12,12,12,13,13,14,16,17,18,19,20,20])


# Step by step

Rhip_rstep = np.array([-13,-14,-15,-15,-14,-14,-13,-12,-11,-9,-6,-2,2,6,10,13,16,18,21,24,26,28,29,30,30])
Rknee_rstep = np.array([5,7,9,11,14,17,21,27,33,40,49,56,59,60,57,46,35,26,19,13,9,7,6,5])
Rankle_rstep = np.array([20,20,19,17,15,12,9,4,-1,-7,-12,-14,-12,-8,-3,1,5,7,8,8,7,6,6,6,6])
Lhip_rstep = np.array([30,29,28,26,24,22,20,18,16,14,12,10,8,6,4,2,0,-2,-4,-6,-7,-9,-10,-11,-11])
Lknee_rstep = np.array([3,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,2,3,4,5])
Lankle_rstep = np.array([5,4,3,3,2,3,4,6,7,8,10,11,11,12,12,12,12,13,13,14,16,17,18,19,20])


#Rhip_lstep = np.array([30,29,28,26,24,22,20,18,16,14,12,10,8,6,4,2,0,-2,-3,-5,-6,-8,-9,-10,-11,-12])
#Rknee_lstep = np.array([4,3,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,3,4])
#Rankle_lstep = np.array([5,4,3,2,2,3,4,6,7,8,10,11,11,12,12,12,12,13,13,14,16,17,18,19,20,20])
#Lhip_lstep = np.array([-12,-12,-13,-13,-14,-14,-14,-15,-15,-14,-13,-11,-8,-5,-1,4,8,12,16,20,23,26,28,29,30])
#Lknee_lstep = np.array([5,6,7,8,9,11,13,16,20,15,32,39,50,58,60,57,48,39,31,22,14,9,7,6,5])
#Lankle_lstep = np.array([20,20,19,17,15,12,9,4,-1,-7,-11,-13,-12,-8,-3,1,5,7,8,8,7,6,6,6,6])


Rhip_lstep = np.array([30,29,28,26,24,22,20,18,16,14,12,10,8,6,4,2,0,-2,-4,-6,-7,-9,-10,-11,-11])
Rknee_lstep = np.array([3,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,2,3,4,5])
Rankle_lstep = np.array([5,4,3,3,2,3,4,6,7,8,10,11,11,12,12,12,12,13,13,14,16,17,18,19,20])

Lhip_lstep = np.array([-13,-14,-15,-15,-14,-14,-13,-12,-11,-9,-6,-2,2,6,10,13,16,18,21,24,26,28,29,30,30])
Lknee_lstep = np.array([5,7,9,11,14,17,21,27,33,40,49,56,59,60,57,46,35,26,19,13,9,7,6,5])
Lankle_lstep = np.array([20,20,19,17,15,12,9,4,-1,-7,-12,-14,-12,-8,-3,1,5,7,8,8,7,6,6,6,6])





#Rhip_lstep = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
#Rknee_lstep = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
#Rankle_lstep = np.array([5,4,3,2,2,2,3,4,6,7,8,10,11,11,12,12,12,12,13,13,14,16,17,18,19])
#                         
#Lhip_lstep = np.array([0,   0,   0,   0,   0,   0,   0, 1,   4,   9, 
#                       14,  19,  23,  25,  26,  27,  27, 25,  22,  19,
#                       15,  12,   9,   5,   2])
#
#
#Lknee_lstep = np.array([0,   2,   3,   6,  11,  17,  22, 28,  36,  41,
#                        46,  50,  55,  55,  48,  40,  31, 23,  17,  11,
#                        7,   3,   1,   0,   0])
#
#Lankle_lstep = np.array([20,  20,  19,  17,  15,  12,   9, 4,  -1,  -7,
#                         -11, -13, -12,  -8,  -3,   1,   5, 7,   8,   8,
#                         7,   6,   6,   6,   6])
#
#
#Rhip_rstep = np.array([0,0,0,0,0,0,0,1,4,9,14,19,23,25,26,27,27,25,22,19,15,12,9,5,2])
#Rknee_rstep = np.array([2,3,6,11,17,22,28,36,41,46,50,55,55,48,40,31,23,17,11,7,3,1,0,0])
#Rankle_rstep = np.array([20,20,20,20,19,17,15,12,9,4,-1,-7,-12,-14,-12,-8,-3,1,5,7,8,8,7,6,6,6,6])
#
#Lhip_rstep = np.array([0,   0,   0,   0,   0,
#                       0,   0,   0,   0,   0,   0,   0, 0,   0,   0,
#                       0,   0,   0,   0,   0,   0,   0, 0,   0,   0])
#
#Lknee_rstep = np.array([0,   0, 0,   0,   0,
#                        0,   0,   0,   0,   0,   0,   0, 0,   0,   0,
#                        0,   0,   0,   0,   0,   0,   0, 0,   0,   0])
#Lankle_rstep = np.array([5,   4, 3,   3,   2,
#                         3,   4,   6,   7,   8,  10,  11, 11,  12,  12,
#                         12,  12,  13,  13,  14,  16,  17, 18,  19,  20,
#                         20])



#    RHip = np.array([31,30,30,29,29,29,28,28,28,26,25,24,24,24,23,22,21,20,20,20,19,18,17,17,16,16,15,14,13,13,12,11,11,10,9,9,8,7,7,6,6,5,4,3,3,2,2,1,0,-1,-1,-2,-2,-2,-3,-3,-4,-5,-5,-6,-6,-6,-7,-8,-8,-9,-9,-9,-9,-10,-10,-11,-11,-11,-11,-12,-12,-13,-13,-13,-13,-14,-14,-15,-15,-15,-15,-15,-15,-14,-14,-14,-14,-14,-14,-14,-13,-13,-12,-12,-12,-12,-11,-11,-10,-10,-9,-8,-7,-6,-4,-3,-2,0,1,2,4,5,6,8,9,10,11,12,13,14,15,16,17,17,18,19,20,21,22,23,24,25,26,26,26,27,27,28,28,29,29,29,30,30,30])
#    RKnee = np.array([5,6,6,6,6,6,7,7,8,8,8,9,10,11,11,11,11,12,12,12,12,12,12,11,11,11,11,10,9,9,8,8,7,7,7,6,6,6,5,5,5,4,4,4,3,3,3,2,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,2,2,2,2,3,3,4,4,4,4,5,5,6,7,7,8,9,9,10,11,11,12,13,14,15,16,17,19,20,22,24,26,28,30,32,34,36,38,41,44,47,50,52,55,56,58,59,59,60,60,60,60,59,57,53,49,45,41,38,35,31,28,26,23,21,19,17,15,13,11,10,9,8,7,7,7,6,6,5,5,5,5,6])
#    RAnkle = np.array([5,5,5,4,3,3,3,3,3,2,2,2,2,2,3,3,3,3,4,5,5,6,6,7,7,7,7,8,8,9,10,10,11,11,11,11,11,11,12,12,12,12,12,12,12,12,12,12,12,12,13,13,13,13,13,13,13,14,14,15,16,16,17,17,17,18,18,18,18,19,19,20,20,20,20,20,20,20,20,20,20,20,20,20,19,19,18,17,17,16,16,15,14,13,12,11,10,8,7,5,3,2,0,-2,-4,-6,-8,-9,-11,-12,-13,-14,-14,-14,-13,-12,-11,-9,-8,-6,-4,-3,-1,0,1,3,4,5,6,7,7,7,8,8,8,8,8,8,7,7,6,6,6,6,6,6,6,6,6,7,7])
#    LHip = np.array([-13,-13,-13,-14,-14,-15,-15,-15,-15,-15,-15,-15,-15,-15,-14,-14,-14,-14,-14,-14,-14,-13,-13,-12,-12,-12,-12,-11,-11,-10,-10,-9,-8,-7,-6,-4,-3,-2,0,1,2,4,5,6,8,9,10,11,12,13,14,15,16,17,17,18,19,20,21,22,23,24,25,26,26,26,27,27,28,28,29,29,29,30,30,30,30,30,30,29,29,29,28,28,28,26,25,24,24,24,23,22,21,20,20,20,19,18,17,17,16,16,15,14,13,13,12,11,11,10,9,9,8,7,7,6,6,5,4,3,3,2,2,1,0,-1,-1,-2,-2,-2,-3,-3,-4,-5,-5,-6,-6,-6,-7,-8,-8,-9,-9,-9,-9,-10,-10,-11,-11,-11,-11])
#    LKnee = np.array([5,5,5,5,5,6,7,7,8,9,9,10,11,11,12,13,14,15,16,17,19,20,22,24,26,28,30,32,34,36,38,41,44,47,50,52,55,56,58,59,59,60,60,60,60,59,57,53,49,45,41,38,35,31,28,26,23,21,19,17,15,13,11,10,9,8,7,7,7,6,6,5,5,5,5,5,5,6,6,6,6,6,7,7,8,8,8,9,10,11,11,11,11,12,12,12,12,12,12,11,11,11,11,10,9,9,8,8,7,7,7,6,6,6,5,5,5,4,4,4,3,3,3,2,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,2,2,2,2,3,3,4])
#    LAnkle = np.array([21,21,21,21,20,20,20,20,20,19,19,18,17,17,16,16,15,14,13,12,11,10,8,7,5,3,2,0,-2,-4,-6,-8,-9,-11,-12,-13,-14,-14,-14,-13,-12,-11,-9,-8,-6,-4,-3,-1,0,1,3,4,5,6,7,7,7,8,8,8,8,8,8,7,7,6,6,6,6,6,6,6,6,6,6,6,5,5,5,4,3,3,3,3,3,2,2,2,2,2,3,3,3,3,4,5,5,6,6,7,7,7,7,8,8,9,10,10,11,11,11,11,11,11,12,12,12,12,12,12,12,12,12,12,12,12,13,13,13,13,13,13,13,14,14,15,16,16,17,17,17,18,18,18,18,19,19,20,20,20,20])

# Stride begining with right leg
Rhip_ang= np.array([30,29,28,26,24,22,20,18,16,14,12,10,8,6,4,2,0,-2,-3,-5,-6,-8,-9,-10,-11,-12,-13,-14,-15,-15,-14,-14,-13,-12,-11,-9,-6,-2,2,6,10,13,16,18,21,24,26,28,29,30,30])
Rknee_ang = np.array([3,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,3,4,5,7,9,11,14,17,21,27,33,40,49,56,59,60,57,46,35,26,19,13,9,7,6,5,4])
Rankle_ang = np.array([5,4,3,2,2,3,4,6,7,8,10,11,11,12,12,12,12,13,13,14,16,17,18,19,20,20,20,20,19,17,15,12,9,4,-1,-7,-12,-14,-12,-8,-3,1,5,7,8,8,7,6,6,6,6])
Lhip_ang= np.array([-13,-13,-14,-14,-14,-15,-15,-14,-13,-11,-8,-5,-1,4,8,12,16,20,23,26,28,29,30,30,30,29,28,26,24,22,20,18,16,14,12,10,8,6,4,2,0,-2,-4,-6,-7,-9,-10,-11,-11,-12,-12])
Lknee_ang= np.array([5,5,6,7,8,9,11,13,16,20,15,32,39,50,58,60,57,48,39,31,22,14,9,7,6,5,4,3,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,2,3,4])
Lankle_ang = np.array([20,20,19,17,15,12,9,4,-1,-7,-11,-13,-12,-8,-3,1,5,7,8,8,7,6,6,6,6,5,4,3,3,2,3,4,6,7,8,10,11,11,12,12,12,12,13,13,14,16,17,18,19,20,20])

# Stride begining with left leg
#Rhip_ang= np.array([-13,-14,-15,-15,-14,-14,-13,-12,-11,-9,-6,-2,2,6,10,13,16,18,21,24,26,28,29,30,30,30,29,28,26,24,22,20,18,16,14,12,10,8,6,4,2,0,-2,-3,-5,-6,-8,-9,-10,-11,-12])
#Rknee_ang = np.array([5,7,9,11,14,17,21,27,33,40,49,56,59,60,57,46,35,26,19,13,9,7,6,5,4,3,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,3,4])
#Rankle_ang = np.array([20,20,19,17,15,12,9,4,-1,-7,-12,-14,-12,-8,-3,1,5,7,8,8,7,6,6,6,6, 5,4,3,2,2,3,4,6,7,8,10,11,11,12,12,12,12,13,13,14,16,17,18,19,20,20])
#Lhip_ang= np.array([30,29,28,26,24,22,20,18,16,14,12,10,8,6,4,2,0,-2,-4,-6,-7,-9,-10,-11,-11,-12,-12,-13, -13,-14,-14,-14,-15,-15,-14,-13,-11,-8,-5,-1,4,8,12,16,20,23,26,28,29,30,30])
#Lknee_ang= np.array([3,2,2,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,2,3,4,5, 5,6,7,8,9,11,13,16,20,15,32,39,50,58,60,57,48,39,31,22,14,9,7,6,5,4])
#Lankle_ang = np.array([5,7,8,8,7,6,6,6,6,5,4,3,3,2,3,4,6,7,8,10,11,11,12,12,12,12,13,13,14,16,17,18,19,20,20, 20,20,19,17,15,12,9,4,-1,-7,-11,-13,-12,-8,-3,1])



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

#%%  MOVE EXO

def Exo_move(objPCAN, msg, sfprocess, sfMove, sfexit):
    
    rHip_Sent = 0
    rKnee_Sent = 0
    rAnkle_Sent = 0
    lHip_Sent = 0
    lKnee_Sent = 0
    lAnkle_Sent = 0
    
    fstep=1
    
    print("move ready")
    while not sfprocess._value: # while proces is active
        
        sfMove.acquire() 
        if sfexit._value:
            break
        
        if fstep:
            print("FS step: ")
            fstep = 0
            Rhip = FS_Rhip_ang
            Rknee = FS_Rknee_ang
            Rankle = FS_Rankle_ang
            Lhip = FS_Lhip_ang
            Lknee = FS_Lknee_ang
            Lankle = FS_Lankle_ang
            
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
#        else:
        for stepsize in range(0,2): # makes two steps
            
            if not stepsize:
#                print("L step: ")
                Rhip = Rhip_lstep
                Rknee = Rknee_lstep
                Rankle = Rankle_lstep
                Lhip = Lhip_lstep
                Lknee = Lknee_lstep
                Lankle = Lankle_lstep
                
            else:
#                print("R step: ")
                Rhip = Rhip_rstep
                Rknee = Rknee_rstep
                Rankle = Rankle_rstep
                Lhip = Lhip_rstep
                Lknee = Lknee_rstep
                Lankle = Lankle_rstep 
#        print("L step: ")
#        Rhip = Rhip_lstep
#        Rknee = Rknee_lstep
#        Rankle = Rankle_lstep
#        Lhip = Lhip_lstep
#        Lknee = Lknee_lstep
#        Lankle = Lankle_lstep
            
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
    
    ############################LAST STEP#################################           
    print ("end move")            
    trajectories = [rHip_Sent, rKnee_Sent, rAnkle_Sent, lHip_Sent, lKnee_Sent, lAnkle_Sent]
    return trajectories



def Exo_waitfor_move(objPCAN, msg, sfMove, sfSend, sfprocess, sfexit):
    
    
    trajectories = []
    
    rHip_Sent = 0
    rKnee_Sent = 0
    rAnkle_Sent = 0
    lHip_Sent = 0
    lKnee_Sent = 0
    lAnkle_Sent = 0
    
    fstep=1
    stepsize = 0
    
#    msg.DATA[0] = 30
#    msg.DATA[1] = 5
#    msg.DATA[2] = 5
#    msg.DATA[3] = -13
#    msg.DATA[4] = 5
#    msg.DATA[5] = 20
#    objPCAN.Write(PCAN_PCIBUS3,msg) 
    
    while not sfprocess._value:

        sfMove.acquire()
        if sfexit._value:
            break
        
        if fstep:
            print("FS step: DERECHA")#MUEVE PIERNA DERECHA
            fstep = 0
            Rhip = FS_Rhip_ang
            Rknee = FS_Rknee_ang
            Rankle = FS_Rankle_ang
            Lhip = FS_Lhip_ang
            Lknee = FS_Lknee_ang
            Lankle = FS_Lankle_ang


        elif not stepsize:
            print("L step: ")
            stepsize = 1
            Rhip = Rhip_lstep
            Rknee = Rknee_lstep
            Rankle = Rankle_lstep
            Lhip = Lhip_lstep
            Lknee = Lknee_lstep
            Lankle = Lankle_lstep
            
        else:
            print("R step: ")
            stepsize = 0
            Rhip = Rhip_rstep
            Rknee = Rknee_rstep
            Rankle = Rankle_rstep
            Lhip = Lhip_rstep
            Lknee = Lknee_rstep
            Lankle = Lankle_rstep
            
            
#        if not stepsize:
##                print("L step: ")
#            stepsize = 1
#            Rhip = Rhip_lstep
#            Rknee = Rknee_lstep
#            Rankle = Rankle_lstep
#            Lhip = Lhip_lstep
#            Lknee = Lknee_lstep
#            Lankle = Lankle_lstep
#            
#        else:
##                print("R step: ")
#            stepsize = 0
#            Rhip = Rhip_rstep
#            Rknee = Rknee_rstep
#            Rankle = Rankle_rstep
#            Lhip = Lhip_rstep
#            Lknee = Lknee_rstep
#            Lankle = Lankle_rstep 
        
        #TimeStamp
#        sendTime=datetime.now().time()
#        print("send")
#        print("min: ", sendTime.minute, " sec: ", sendTime.second, " mls: ", sendTime.microsecond)
        
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
            
#            current_Rhip = Rhip[index_Step]
#            current_Rknee = Rhip[index_Step]
#            current_Rankle = Rhip[index_Step]
#            current_Lhip = Rhip[index_Step]
#            current_Lknee = Rhip[index_Step]
#            current_Lankle = Rhip[index_Step]
            time.sleep(0.1)
            
#        rHip_Sent=np.concatenate((rHip_Sent,current_Rhip),axis=None)
#        rKnee_Sent=np.concatenate((rKnee_Sent,current_Rknee),axis=None)
#        rAnkle_Sent=np.concatenate((rAnkle_Sent,current_Rankle),axis=None)
#        lHip_Sent=np.concatenate((lHip_Sent,current_Lhip),axis=None)
#        lKnee_Sent=np.concatenate((lKnee_Sent,current_Lknee),axis=None)
#        lAnkle_Sent=np.concatenate((lAnkle_Sent,current_Lankle),axis=None)  
        
        sfSend.release() 
        
    print ("end move_wait")     
    if np.size(rHip_Sent) == 1:
        rHip_Sent=np.concatenate((rHip_Sent,0),axis=None)
        rKnee_Sent=np.concatenate((rKnee_Sent,0),axis=None)
        rAnkle_Sent=np.concatenate((rAnkle_Sent,0),axis=None)
        lHip_Sent=np.concatenate((lHip_Sent,0),axis=None)
        lKnee_Sent=np.concatenate((lKnee_Sent,0),axis=None)
        lAnkle_Sent=np.concatenate((lAnkle_Sent,0),axis=None)
        
    trajectories = [rHip_Sent, rKnee_Sent, rAnkle_Sent, lHip_Sent, lKnee_Sent, lAnkle_Sent]
       
    return trajectories




def firstStep(objPCAN,msg):
    
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


def lastStep(objPCAN, msg):
    
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




#%%  READ ANGLES

def ReadAngle(objPCAN,sfprocess,sfRead,sfexit):
    
    joinangle = 0
    rHip_Record = 0
    rKnee_Record = 0
    rAnkle_Record = 0
    lHip_Record = 0
    lKnee_Record = 0
    lAnkle_Record = 0
    
    print ("ready for read angle")
    while not sfprocess._value:
        
        sfRead.acquire()
        
        if sfexit._value:
            break
        
        read=objPCAN.Read(PCAN_PCIBUS3)
#        print("rec angle")
        while read[0] != PCAN_ERROR_QRCVEMPTY: #32 = buffere empty
            if read[1].ID == 110:
                joinangle=read[1].DATA
            read=objPCAN.Read(PCAN_PCIBUS3)
    
        anglejoin=np.array([int(joinangle[0]),int(joinangle[1]),int(joinangle[2]),int(joinangle[3]),
                            int(joinangle[4]),int(joinangle[5])]) 
        if joinangle != 0:
            #TimeStamp
#            recTime=datetime.now().time()
#            print("rec")
#            print("min: ", recTime.minute, " sec: ", recTime.second, " mls: ", recTime.microsecond)
            
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
                
        else:
            pass
        
    print ("end angle read")
    anglesArray = [rHip_Record, rKnee_Record, rAnkle_Record, lHip_Record, lKnee_Record, lAnkle_Record]
    
    return anglesArray

#%%  READ TORQUE
    
def ReadTorque(objPCAN,sfprocess,sfRead,sfexit):
    read=objPCAN.Read(PCAN_PCIBUS3)
    joinTorque=0
    rHip = 0
    rKnee = 0
    rAnkle = 0
    lHip = 0
    lKnee = 0
    lAnkle = 0
    
    print ("ready for read torque")
    while not sfprocess._value:
        
        sfRead.acquire()
        
        if sfexit._value:  
            break
        
        read=objPCAN.Read(PCAN_PCIBUS3)
#        print("rec torque")  
        while read[0] != PCAN_ERROR_QRCVEMPTY: #32 = buffere empty
            if read[1].ID == 120: #130=foot switch / 120=join Torque
                joinTorque=read[1].DATA
                rHip=np.concatenate((rHip,joinTorque[0]),axis=None)
                rKnee=np.concatenate((rKnee,joinTorque[1]),axis=None)
                rAnkle=np.concatenate((rAnkle,joinTorque[2]),axis=None)
                lHip=np.concatenate((lHip,joinTorque[3]),axis=None)
                lKnee=np.concatenate((lKnee,joinTorque[4]),axis=None)
                lAnkle=np.concatenate((lAnkle,joinTorque[5]),axis=None) 
            read=objPCAN.Read(PCAN_PCIBUS3)
            
    print ("end toque read")        
    torque = [rHip,rKnee,rAnkle,lHip,lKnee,lAnkle]
   
    return torque







class Exo_H3 (Thread):
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
    