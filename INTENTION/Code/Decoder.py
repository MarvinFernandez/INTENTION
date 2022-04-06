#!/usr/bin/env python3


import numpy as np


def manchester(inputData):
    array = [0]*4
    frame = [0]*3
    h=0
    inputBit=format(inputData, '08b')
    for i in range(len(inputBit)-1,0,-2):
        array[h]=inputBit[i]
        h+=1
    frame=array[::-1]
    s=""
    s=s.join(frame)
#    print(inpu)
    return s



def getPayload3(inputData):
    frame = [0]*3
    for i in range(len(inputData)-1,-1,-1):
        frame[i]=manchester(inputData[i])
    s=""
    s=s.join(frame[::-1])
    suma=0
    for bit in s:
        su = bit
        suma+=int(su)
    payload=np.nan
    if suma % 2 ==0:
        if(s[9] == '1' and s[10] == '0' and s[11] == '1'):
            payload=s[1:9]
            payload=int(payload,2)
        else: print("wrong header")
    else: print("no parity")

    return payload

def getPayload4(inputData):
    frame = [0]*4
    for i in range(len(inputData)-1,-1,-1):
        frame[i]=manchester(inputData[i])
    s=""
    s=s.join(frame[::-1])
    suma=0
    for bit in s:
        su = bit
        suma+=int(su)
    payload=np.nan
    counter=np.nan
    if suma % 2 ==0:
        if(s[13] == '1' and s[14] == '1' and s[15] == '1'):
            counter=int(s[1:3],2)
            payload=int(s[3:13],2)
        else: print("wrong header")
    else: print("no parity")

    return counter,payload


#def machester2bin(inputData):
#    inputBit=format(inputData,'08b')
#    print('inputBit',inputBit)
#    nBits=len(inputData)
#    decodeData=np.ones(nBits/2)
#    if nBits % 2 != 0:
#        print("Length of array must be even")
#    for i in range(nBits,-2,2):
#        if inputData[i] != inputData[i-1]:
#            decodeData[i/2]=inputData[i]
#        else:
#            decodeData = []
#            break
#    decodeData=str(decodeData)
#    return decodeData