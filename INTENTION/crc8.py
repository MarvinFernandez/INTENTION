
import numpy as np
import math

def compute_crc8(data, initial_value = 0):
	crc = initial_value

	for byte in data:
		for _ in range(0,8):
			if(crc>>7) ^(byte & 0x01):
				crc=((crc<<1)^0x07)& 0xFF
			else:
				crc = (crc<<1) & 0xFF
			byte = byte >> 1

	return crc


def fcn_crc8(data):
    crc = 0
    for i in range(len(data)):
        byte = data[i]
        for b in range(8):
            fb_bit = (crc ^ byte) & 0x01
            if fb_bit == 0x01:
                crc = crc ^ 0x18
                crc = (crc >> 1) & 0x7f
                if fb_bit == 0x01:
                    crc = crc | 0x80
                    byte = byte >> 1
    return crc

def fcn_crc8_ot(data,length):
    crc = 0
    j = 0
    while length > 0:
        extract  = data[j]
      
        for i in reversed(range(0,8)):
            sum = (crc % 2)^(extract % 2)
            crc = math.floor(crc/2)
            if sum > 0:
                str_ = np.zeros(8,dtype=int)
                a = format(crc,'#010b')#bin(crc)
                b = format(140,'#010b')#bin(140)
                
                for k in range(2, 10):
                    str_[k-2] = int(a[k] != b[k])
                
                crc = int("".join(str(x) for x in str_),2)
            
            extract = math.floor(extract/2)
        
        length = length - 1
        j = j+1
    return crc