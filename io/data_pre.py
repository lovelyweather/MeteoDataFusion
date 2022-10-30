import os
import copy

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

    def __init__(self, filename:list, datatype:list = ['chinese_mosiac', 'FY4A'], time_range : list = None, extend_ll:list = [15, 30, 100, 130], resolution:float = 0.04):
        #中国区域的经度范围70-140E，纬度范围15-55N

        self.time_s:datetime    = time_range[0]
        self.time_e:datetime    = time_range[1]
        self.extend_ll = extend_ll
        self.resolution= resolution

        self.FusionDS = {}

        for i_type in np.arange(0,len(datatype)):

            filetime = []

            for i_file in filename[i_type]:
                i_filetime, i_ds = self.read_interp(i_file,datatype[i_type])
                filetime.append(i_filetime)
                if i_file == filename[i_type][0]:
                    ds = copy.deepcopy(i_ds[np.newaxis, :, :]) 
                else:
                    ds = np.concatenate([ds, i_ds[np.newaxis, :, :]])
                    
            dic = {"time":filetime,
                    "data": ds}

            self.FusionDS[datatype[i_type]] = dic

    def read_interp(self, filename:str, datatype:str):

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
            file_time = WSR98D.WSR98DData(filename, fields_add = None).time
            if file_time < self.time_e:
                return file_time, WSR98D.Radar2ll(WSR98D.WSR98DData(filename, sounding_infile = 'None'), Lat_des_2D, Lon_des_2D, ['FH', 'compz'], 0, 'linear' ).interp()
        else:
            raise TypeError("unsupported radar type!")

if __name__ == '__main__':


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

    time_range = [ datetime(2022,4,25,6,0,0), datetime(2022,4,25,7,0,0) ]

    Fusion_object = FusionData(filename= [fy4_infile,cref_infile], datatype= ['FY4A', 'chinese_mosiac'], time_range = time_range,\
        extend_ll= [15, 30, 100, 130], resolution = 0.04)
    
    print(Fusion_object.FusionDS.keys())