import os

import numpy as np
from netCDF4 import Dataset  # 读取nc文件用到的包
from scipy.interpolate import griddata  # 对SST空间插值用到的函数
import matplotlib.pyplot as plt
import xarray as xr
from datetime import datetime

class FY4ALevel3Data(object):
    # can add the function to determine the resolution by file name later
    with open('/Users/xiaowu/Downloads/空天地/空间匹配/FullMask_Grid_4000.raw', mode = 'rb') as file: #reading binary
        df = np.fromfile(file, dtype=np.float64)
        array = np.reshape(df,[2748, 5496])
        array = np.ma.masked_where(array > 360, array)
        np.ma.set_fill_value(array, -99)
        lat = array[:, 0::2]
        lon = array[:, 1::2]

    def __init__(self,filename):
        self.infile = filename
        self.time, self.lat, self.lon, self.data = self.data_prepare()

    def data_prepare(self):
        dataset = Dataset(self.infile)
        self.ds_name = dataset.dataset_name
        self.long_name = dataset.Title

        time = datetime.strptime(dataset.time_coverage_end[:-5], "%Y-%m-%dT%H:%M:%S")
        ll_extent = dataset.variables['geospatial_lat_lon_extent']
        lat_real = FY4ALevel3Data.lat[ ll_extent.begin_line_number:ll_extent.end_line_number+1 , ll_extent.begin_pixel_number:ll_extent.end_pixel_number+1 ]
        lon_real = FY4ALevel3Data.lon[ ll_extent.begin_line_number:ll_extent.end_line_number+1 , ll_extent.begin_pixel_number:ll_extent.end_pixel_number+1 ] 
        
        data = dataset.variables[self.ds_name][:].data 

        return time, lat_real, lon_real, data

class FY4ALevel32ll(object):
    '''interpolation
    same as CRefMosaic, combine into 1 ?
    '''

    def __init__(self, FY4ALevel3, lat_des, lon_des, interpolation_method):
        self.FY4ALevel3 = FY4ALevel3
        self.lat_des = lat_des
        self.lon_des = lon_des
        self.interp_md = interpolation_method

    def interp(self):
        # 插值前的经纬度, 维度是(nlat*nlon,2)
        LatLon_Before = np.hstack(
            (self.FY4ALevel3.lat.reshape(-1, 1), self.FY4ALevel3.lon.reshape(-1, 1)) ) # 按水平方向进行叠加，形成两列
        
        data_des = griddata(LatLon_Before, self.FY4ALevel3.data.reshape(-1, 1), (self.lat_des, self.lon_des),  method=self.interp_md).squeeze()

        return(data_des)

if __name__=='__main__':
    
    Min_Lat= 15
    Max_Lat = 30
    Min_Lon = 100
    Max_Lon = 130 #中国区域的经度范围70-140E，纬度范围15-55N

    Lat_des_1D = np.arange( Max_Lat, Min_Lat, -0.04 )  # 生成插值后的纬度
    Lon_des_1D = np.arange( Min_Lon, Max_Lon,  0.04 )  # 生成插值后的经度

    Lon_des_2D, Lat_des_2D = np.meshgrid(Lon_des_1D, Lat_des_1D) #打网格 (x,y)


    path = r'/Users/xiaowu/Downloads/空天地/空间匹配/sat_data'
    filename = r'FY4A-_AGRI--_N_REGC_1047E_L2-_CTH-_MULT_NOM_20220425063000_20220425063417_4000M_V0001.NC'
    infile = os.path.join(path, filename)

    data_des = FY4ALevel32ll(FY4ALevel3Data(infile), Lat_des_2D, Lon_des_2D, 'nearest').interp()

    plt.imshow(data_des)
    plt.savefig('test_fy4.png')