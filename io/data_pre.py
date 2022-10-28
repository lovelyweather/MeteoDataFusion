from . import CMOSAIC, FY4ALevel3, WSR98D

import numpy as np

def read(filename:str, datatype:str):

    Min_Lat= 15
    Max_Lat = 30
    Min_Lon = 100
    Max_Lon = 130 #中国区域的经度范围70-140E，纬度范围15-55N

    Lat_des_1D = np.arange( Max_Lat, Min_Lat, -0.04 )  # 生成插值后的纬度
    Lon_des_1D = np.arange( Min_Lon, Max_Lon,  0.04 )  # 生成插值后的经度

    Lon_des_2D, Lat_des_2D = np.meshgrid(Lon_des_1D, Lat_des_1D) #打网格 (x,y)
    if datatype == "chinese_mosiac":
        return CMOSAIC.CRefMosaic2ll(CMOSAIC.CRefMosaicData(filename), Lat_des_2D, Lon_des_2D, 'nearest').interp()
    elif datatype == "FY4A":
        return FY4ALevel3.FY4ALevel32ll(FY4ALevel3.FY4ALevel3Data(filename), Lat_des_2D, Lon_des_2D, 'nearest').interp()
    elif datatype == "WSR98D":
        return WSR98D.Radar2ll(WSR98D.WSR98DData(filename, sounding_infile = 'None')).interp()
    else:
        raise TypeError("unsupported radar type!")
