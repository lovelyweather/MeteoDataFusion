import os
import copy

from sympy import Q

import CMOSAIC, FY4ALevel3, WSR98D

import numpy as np
from datetime import date, datetime,timedelta

'''
- interfaces of mosiac reflectivity, FY4A satellite products, ground based weather radar. 
   -- For weather radar, it can also derive some diagnosing variables like hydrometeor types, turbulence, composite reflectivity, etc.
- interpolation into the unified lat/lon grids. 
- integration into a unified dataset, each variable has the dimensions of [time, lat, lon].
'''

class FusionData(object):

    '''
    A class for storing gridded fusioned weather data in Cartesian coordinate.

    Attributes
    ----------

    time_s, time_e: datetime
        extend of time range.
    extend_ll : list
        extend of the lat & lon. [ lat_begin, lat_end, lon_begin, lon_end ]
    resolution : float
        grid resolution.
    FusionDS   : dict of dict.
        variables from radar or satellite based products.
        eg. FusionDS.WSR88D.turbulence[it,iy,ix]`

    '''

    def __init__(self, filename:list, datatype:list = ['chinese_mosiac', 'FY4A'], \
        var_98d:list = ['FH', 'compz', 'reflectivity'], time_range : list = None, \
        extend_ll:list = [15, 30, 100, 130], resolution:float = 0.04, \
        wsr98d_fields_add = None):
        #中国区域的经度范围70-140E，纬度范围15-55N

        self.time_s:datetime    = time_range[0]
        self.time_e:datetime    = time_range[1]
        self.extend_ll  = extend_ll
        self.resolution = resolution
        self.wsr98d_fields_add  = wsr98d_fields_add

        self.FusionDS = {}
 
        for i_type, obs_source in enumerate(datatype):
            print("source: ", obs_source) # like WSR98D

            vars = [] 
            filetime = []
            field_dict = {}
            for i_time, i_file in enumerate(filename[i_type]): # filename is a list of
                i_filetime, i_ds = self.read_interp(i_file, obs_source, var_98d)
                filetime.append(i_filetime)

                if i_time == 0:
                    nvar  = len(i_ds)
                    ntime = len(filename)
                    ny, nx = i_ds[list(i_ds.keys())[0]]['data'].shape
                    print(ny, nx)
                    ds = np.zeros(shape=(nvar,ntime,ny,nx),dtype=float) # list containg different variables of np.array
                    ds[:,:,:,:] = -999

                for i, i_var in enumerate(list(i_ds.keys())): #count of i_var, variable name

                    print(i, i_var) 
                    if i_var not in vars:
                        vars.append(i_var)

                    if i_time == 0: # the first file
                        #temp  = copy.deepcopy(i_ds[i_var]['data'][np.newaxis, :, :]) 
                        ds[i,i_time,:,:] = i_ds[i_var]['data']
                    else:
                        #temp = np.concatenate([ ds[i,0,:,:], i_ds[i_var]['data'][np.newaxis, :, :] ])
                        ds[i,i_time,:,:] = i_ds[i_var]['data']
  
                if i_file == filename[i_type][-1]: # last time frame
                    for i, i_var in enumerate(list(i_ds.keys())):
                        field_dict[i_var] = { 
                            "units" : i_ds[i_var]['units'],
                            "dims"  : {"time" : filetime, "ny" : ny,"nx" : nx},
                            i_var   : ds[i]
                            }

            self.FusionDS[obs_source] = field_dict

    def read_interp(self, filename:str, datatype:str, var_98d:list=['FH', 'compz']):

        Min_Lat, Max_Lat = self.extend_ll[0], self.extend_ll[1]
        Min_Lon, Max_Lon = self.extend_ll[2], self.extend_ll[3]     

        Lat_des_1D = np.arange( Max_Lat, Min_Lat, -1*self.resolution )  # 生成插值后的纬度
        Lon_des_1D = np.arange( Min_Lon, Max_Lon,  self.resolution )  # 生成插值后的经度

        Lon_des_2D, Lat_des_2D = np.meshgrid(Lon_des_1D, Lat_des_1D) 

        if datatype == "chinese_mosiac":
            year, month, day = filename[-36:-32], filename[-32:-30], filename[-30:-28]
            hour, min  = filename[-28:-26], filename[-26:-24]
            file_time = datetime(int(year), int(month), int(day), int(hour), int(min))
            if file_time < self.time_e:
                return file_time, CMOSAIC.CRefMosaic2ll(CMOSAIC.CRefMosaicData(filename), Lat_des_2D, Lon_des_2D, 'nearest').interp()
        elif datatype == "FY4A":
            file_time = FY4ALevel3.FY4ALevel3Data(filename).time
            if file_time < self.time_e:
                return file_time, FY4ALevel3.FY4ALevel32ll(FY4ALevel3.FY4ALevel3Data(filename), Lat_des_2D, Lon_des_2D, 'nearest').interp()
        elif datatype == "WSR98D":
            file_time = WSR98D.WSR98DData(filename, fields_add = []).time
            if file_time < self.time_e:
                return file_time, WSR98D.Radar2ll(WSR98D.WSR98DData(filename, sounding_infile = 'None'), Lat_des_2D, Lon_des_2D, var_98d, 0, 'linear' ).interp()
        else:
            raise TypeError("unsupported radar type!")

if __name__ == '__main__':

    time_range = [ datetime(2022,4,25,6,0,0), datetime(2022,4,25,7,0,0) ]

    path = r'/Users/xiaowu/Downloads/空天地/空间匹配/sat_data'
    filename = ['FY4A-_AGRI--_N_REGC_1047E_L2-_CTH-_MULT_NOM_20220425063000_20220425063417_4000M_V0001.NC','FY4A-_AGRI--_N_REGC_1047E_L2-_CTH-_MULT_NOM_20220425063418_20220425063835_4000M_V0001.NC']
    fy4_infile = []
    for i_file in filename:
        fy4_infile.append(os.path.join(path,i_file))

    path = '/Users/xiaowu/Library/Mobile Documents/com~apple~CloudDocs/work/MeteoDataFusion'
    filename = ['Z_RADA_C_BABJ_20220425061200_P_DOR_RDCP_R_ACHN.PNG',\
        'Z_RADA_C_BABJ_20220425064200_P_DOR_RDCP_R_ACHN.PNG']
    cref_infile = []
    for i_file in filename:
        cref_infile.append(os.path.join(path,'test','data',i_file))

    filename = ['Z9002.20220425.060745.AR2.bz2']
    wsr98d_file = []
    for i_file in filename:
        wsr98d_file.append(os.path.join(path,'test','data',i_file))

    Fusion_object = FusionData(filename= [fy4_infile, cref_infile, wsr98d_file], datatype= ['FY4A', 'chinese_mosiac', 'WSR98D'], \
        var_98d=['FH', 'compz', 'reflectivity'], time_range = time_range,\
        extend_ll= [15, 30, 100, 130], resolution = 0.04)
    
    print(Fusion_object.FusionDS.keys())
    print(Fusion_object.FusionDS['WSR98D'].keys() )