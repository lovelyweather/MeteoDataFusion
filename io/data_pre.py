from . import CMOSAIC, FY4ALevel3

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
        return WSR98DFile.WSR98D2NRadar(WSR98DFile.WSR98DBaseData(filename, station_lon, station_lat, station_alt)).ToPRD()
    else:
        raise TypeError("unsupported radar type!")


'''

	1. 各数据接口，写成统一的格式，暂定等经纬度，网格比实际 
    机载网格大一些（因为外推可能也需要周围的数据），之后再截取；data(time, lat, lon);
	2. 外推，包括光流法和深度学习外推方法，进行时间对齐；
	3. 插值到统一的机载雷达网格，实现空间匹配；
	4. 可视化。

	1. 数据接口

'''

