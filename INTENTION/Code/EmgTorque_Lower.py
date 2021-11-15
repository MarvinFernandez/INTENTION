import numpy as np
from scipy.interpolate import make_interp_spline

class EmgTorque:
    def __init__(self, scale_factor=None):
        self.f_mus_norm_fibre_len = 'mus_norm_fibre_len.csv'
        self.f_mus_moment_arm = 'mus_moment_arm.csv'
        self.mus_names = ['tib_ant', 'soleus', 'lat_gas', 'med_gas', 'per_long']
        self.mus_scale = {}
        if scale_factor is None:
            for mus in self.mus_names:
                self.mus_scale.update({mus: 1.0})
        else:
            self.mus_scale = scale_factor
        self.dict_fun_mus_norm_fibre_len = {}
        self.dict_fun_jnt_moment_arm = {}
        mus_norm_fibre_len_data = np.loadtxt(self.f_mus_norm_fibre_len, delimiter=',', skiprows=1)
        mus_moment_arm_data = np.loadtxt(self.f_mus_moment_arm, delimiter=',', skiprows=1)
        for i, mus_name in enumerate(self.mus_names):
            fun = make_interp_spline(mus_norm_fibre_len_data[:,0], mus_norm_fibre_len_data[:,i+1])
            self.dict_fun_mus_norm_fibre_len.update({mus_name: fun})
            fun = make_interp_spline(mus_moment_arm_data[:,0], mus_moment_arm_data[:,i+1])
            self.dict_fun_jnt_moment_arm.update({mus_name: fun})
        act_f_len_rel_x =\
            np.array([-5, 0, 0.401, 0.402, 0.4035, 0.52725, 0.62875, 0.71875, 0.86125, 1.045, 1.2175, 1.43875, 1.61875, 1.62, 1.621, 2.2, 5], dtype=float)
        act_f_len_rel_y =\
            np.array([0, 0, 0, 0, 0, 0.226667, 0.636667, 0.856667, 0.95, 0.993333, 0.77, 0.246667, 0, 0, 0, 0, 0], dtype=float)
        self.fun_act_f_len = make_interp_spline(act_f_len_rel_x, act_f_len_rel_y)
        pasv_f_len_rel_x = np.array([-5, 0.998, 0.999, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.601, 1.602, 5], dtype=float)
        pasv_f_len_rel_y = np.array([0, 0, 0, 0, 0.035, 0.12, 0.26, 0.55, 1.17, 2, 2, 2, 2])
        self.fun_pasv_f_len = make_interp_spline(pasv_f_len_rel_x, pasv_f_len_rel_y)
        self.global_scale = scale_factor
        self.mus_info = {'tib_ant':{'lm0':0.098, 'lt0': 0.223, 'alpha':0.08726646, 'f0': 905},\
                         'soleus':{'lm0':0.05, 'lt0': 0.25, 'alpha':0.43633231, 'f0': 3549},\
                         'lat_gas':{'lm0':0.064, 'lt0': 0.38, 'alpha':0.13962634, 'f0': 683},\
                         'med_gas':{'lm0':0.06, 'lt0': 0.39, 'alpha':0.29670597, 'f0': 1558},\
                         'per_long':{'lm0':0.049, 'lt0': 0.345, 'alpha':0.17453293, 'f0': 943}}
        self.mus_act = {'tib_ant':0, 'soleus':0, 'lat_gas':0, 'med_gas':0, 'per_long':0}
        
    def calc_mus_act_deriv(self, mus_ext, mus_act):
        min_val = 0.01
        max_val = 1.0
        t_act = 10/1000
        t_deact = 40/1000
        e = np.amin([np.amax([min_val, mus_ext]), max_val])
        a = np.amin([np.amax([min_val, mus_act]), max_val])
        if e > a:
            tau = t_act*(0.5+1.5*a)
        else:
            tau = t_deact*(0.5+1.5*a)
        return (mus_ext-mus_act)/tau
    
    def calc_torque(self, angle, emg_values):
        sum_trq = 0.0
        for i, mus_name in enumerate(self.mus_names):
            ang = angle
            act = emg_values[i]
            cos_alpha = np.cos(self.mus_info[mus_name]['alpha'])
            fmax = self.mus_info[mus_name]['f0']
            norm_fibre_len = self.dict_fun_mus_norm_fibre_len[mus_name](ang)
            moment_arm = self.dict_fun_jnt_moment_arm[mus_name](ang)
            scale = self.mus_scale[mus_name]
            sum_trq += fmax*(act*self.fun_act_f_len(norm_fibre_len)+self.fun_pasv_f_len(norm_fibre_len))*cos_alpha*moment_arm*scale
        return sum_trq
    
    def calc_torque2(self, angle, emg_values, dt):
        sum_trq = 0.0
        for i, mus_name in enumerate(self.mus_names):
            ang = angle
            act = self.mus_act[mus_name]+self.calc_mus_act_deriv(emg_values[i], self.mus_act[mus_name])*dt
            self.mus_act[mus_name] = act
            cos_alpha = np.cos(self.mus_info[mus_name]['alpha'])
            fmax = self.mus_info[mus_name]['f0']
            norm_fibre_len = self.dict_fun_mus_norm_fibre_len[mus_name](ang)
            moment_arm = self.dict_fun_jnt_moment_arm[mus_name](ang)
            scale = self.mus_scale[mus_name]
            sum_trq += fmax*(act*self.fun_act_f_len(norm_fibre_len)+self.fun_pasv_f_len(norm_fibre_len))*cos_alpha*moment_arm*scale
        return sum_trq    
