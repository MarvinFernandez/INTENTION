import os
import sys
import re
import numpy as np
from scipy.interpolate import splrep, splev
#%%
class motReader:
    def __init__(self, f_path=None, trial_name=None):
        self.f_path = f_path
        self.trial_name = trial_name
        self.col_names = []
        self.data = {}
        self.spl_time = {}
        self.spl_cycle = {}
        self.time = None
        self.cycle = None
        self.n_cols = None
        self.n_rows = None
        self.in_deg = None
        self.version = None
        self.parse()
        
    def parse(self):
        if self.f_path is None: return False
        with open(self.f_path, 'r') as f:
            lines = f.readlines()
            line_idx_col_names = 0
            for line_idx, line in enumerate(lines):
                if 'endheader' in line:
                    line_idx_col_names = line_idx+1
                    break
                if line.startswith(('nRows', 'nColumns', 'inDegrees', 'version')):
                    l_data = re.sub(r'\s+', ' ', line).strip().split('=')
                elif line.startswith(('datarows', 'datacolumns')):
                    l_data = re.sub(r'\s+', ' ', line).strip().split(' ')
                else:
                    continue
                if l_data[0] == 'nRows' or l_data[0] == 'datarows':
                    self.n_rows = l_data[1]
                elif l_data[0] == 'nColumns' or l_data[0] == 'datacolumns':
                    self.n_cols = l_data[1]
                elif l_data[0] == 'inDegrees':
                    if l_data[1] == 'yes':
                        self.in_deg = True
                    elif l_data[1] == 'no':
                        self.in_deg = False
                    else:
                        self.in_deg = None
                elif l_data[0] == 'version':
                    self.version = l_data[1]
                else:
                    continue
            self.col_names = lines[line_idx_col_names].split()
            line_data = (re.sub(r'\s+', ' ', line).strip() for line in lines[line_idx_col_names+1:])
            data = np.loadtxt(line_data, delimiter=' ', dtype=float)
            for col_idx, col_name in enumerate(self.col_names):
                self.data.update({col_name: data[:,col_idx]})
            self.time = self.data.get('time', None)
            self.cycle = (self.time-self.time[0])/(self.time[-1]-self.time[0])*np.float(100)
            for col_idx, col_name in enumerate(self.col_names):
                if col_name.lower() == 'time': continue
                spl_time = splrep(self.time, self.data[col_name])
                self.spl_time.update({col_name: spl_time})
                spl_cycle = splrep(self.cycle, self.data[col_name])
                self.spl_cycle.update({col_name: spl_cycle})
            
    def get_data(self, col_name):
        if len(self.data) == 0: return None
        return self.data[col_name]
    
    def get_time(self):
        return self.time

    def splev_time(self, col_name, time):
        # col_splrep = splrep(self.data['time'], self.data[col_name])
        spl = self.spl_time.get(col_name, None)
        if spl is not None:
            return splev(time, spl)
        else:
            return None
    
    def splev_cycle(self, col_name, cycle):
        # col_splrep = splrep(self.cycle, self.data[col_name])
        spl = self.spl_cycle.get(col_name, None)
        if spl is not None:
            return splev(cycle, spl)
        else:
            return None
        