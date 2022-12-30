import os

import sys
sys.path.append("..")

#from graph import fusiondisplay 
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
        self.time, self.lat, self.lon, self.data, self.units = self.data_prepare()

    def data_prepare(self):
        dataset = Dataset(self.infile)
        self.ds_name = dataset.dataset_name
        self.long_name = dataset.Title

        time = datetime.strptime(dataset.time_coverage_end[:-5], "%Y-%m-%dT%H:%M:%S")
        ll_extent = dataset.variables['geospatial_lat_lon_extent']
        lat_real = FY4ALevel3Data.lat[ ll_extent.begin_line_number:ll_extent.end_line_number+1 , ll_extent.begin_pixel_number:ll_extent.end_pixel_number+1 ]
        lon_real = FY4ALevel3Data.lon[ ll_extent.begin_line_number:ll_extent.end_line_number+1 , ll_extent.begin_pixel_number:ll_extent.end_pixel_number+1 ] 
        
        data = dataset.variables[self.ds_name][:].data 
        units = dataset.variables[self.ds_name].units 

        return time, lat_real, lon_real, data, units

class FY4ALevel32ll(object):
    '''interpolation

    '''

    def __init__(self, FY4ALevel3, lat_des, lon_des, interpolation_method):
        self.FY4ALevel3 = FY4ALevel3
        self.lat_des = lat_des
        self.lon_des = lon_des
        self.interp_md = interpolation_method
        self.fy4_ll    = {}

    def interp(self):
        # 插值前的经纬度, 维度是(nlat*nlon,2)
        LatLon_Before = np.hstack(
            (self.FY4ALevel3.lat.reshape(-1, 1), self.FY4ALevel3.lon.reshape(-1, 1)) ) # 按水平方向进行叠加，形成两列
        
        units    =  self.FY4ALevel3.units
        data_des = griddata(LatLon_Before, self.FY4ALevel3.data.reshape(-1, 1), (self.lat_des, self.lon_des),  method=self.interp_md).squeeze()

        field_dict = {
            'data': data_des, \
            'units': units \
            }

        self.fy4_ll[self.FY4ALevel3.ds_name] = field_dict

        return(self.fy4_ll)

if __name__=='__main__':

    from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    import matplotlib.ticker as mticker
    import cartopy.crs as ccrs
    import cartopy.feature as cfeat
    
    Min_Lat= 20
    Max_Lat = 35
    Min_Lon = 100
    Max_Lon = 130 #中国区域的经度范围70-140E，纬度范围15-55N

    Lat_des_1D = np.arange( Max_Lat, Min_Lat, -0.04 )  # 生成插值后的纬度
    Lon_des_1D = np.arange( Min_Lon, Max_Lon,  0.04 )  # 生成插值后的经度

    Lon_des_2D, Lat_des_2D = np.meshgrid(Lon_des_1D, Lat_des_1D) #打网格 (x,y)

    path = r'/Users/xiaowu/Library/Mobile Documents/com~apple~CloudDocs/work/MeteoDataFusion/test/data/0920test'
    filename = r'FY4A-_AGRI--_N_REGC_1047E_L2-_CLM-_MULT_NOM_20220920131500_20220920131917_4000M_V0001.NC'
    infile = os.path.join(path, filename)

    fy4_ll = FY4ALevel32ll(FY4ALevel3Data(infile), Lat_des_2D, Lon_des_2D, 'nearest').interp()


    fig = plt.figure(figsize=(12,6))
    axe = fig.add_subplot(111)

    '''
    axe = fig.add_subplot(111, projection=ccrs.PlateCarree())
    axe.add_feature(cfeat.COASTLINE.with_scale('10m'), linewidth=0.8,color='k')
    LAKES_border = cfeat.NaturalEarthFeature('physical', 'lakes', '50m', edgecolor='blue', facecolor='never')
    axe.add_feature(LAKES_border, linewidth=0.8)


    #plt.contourf( Lon_des_2D, Lat_des_2D, fy4_ll['TH']['data']/1000, vmax=20, vmin=0, cmap='Blues',  )  #   LonAfter_2D, Lat_After_2D
    '''
    axe.contourf( Lon_des_2D, Lat_des_2D, fy4_ll['CLM']['data'], vmax=4, vmin=0,cmap='Blues') #, tick_level=np.arange(-0.5,4) ) 
    #plt.colorbar() #location="bottom"
    plt.title('cloud top height in km')

    plt.savefig('test_fy4_ll_0920.png')
    