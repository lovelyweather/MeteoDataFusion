import os
import warnings
warnings.filterwarnings('ignore') # setting ignore as a parameter

from datetime import datetime
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyart
import pytda
from csu_radartools import csu_fhc
from pyart import retrieve
from pyart.core import cartesian_to_geographic
from pyart.core.transforms import antenna_to_cartesian
from pycwr.io import read_auto
from scipy.interpolate import griddata

# go to pckgs, `$ git clone git@github.com:CSU-Radarmet/CSU_RadarTools.git`, then run `python setup.py install`;
# `$ pip show pip show csu-radartools`, you will see whether it success.

# `$ git clone git@github.com:nasa/PyTDA.git`, run `$ python setup.py install` from the command line in the main PyTDA folder.

class WSR98DData(object):
    '''
    获取带经纬度信息的地基单站雷达信息
    '''

    def __init__(self, filename, sounding_infile = 'None', fields_add:list = ['compz','fh','tb']) :
        self.infile = filename
        self.sounding   = sounding_infile 

        PRD = read_auto(self.infile)
        self.PyartRadar = PRD.ToPyartRadar()
        if 'compz' in fields_add:
            self.compz      = self.retrieve()     
        if 'fh' in fields_add:
            self.PyartRadar =  self.cal_fh()   
        if 'tb' in fields_add:
            self.cal_tb()   # add turbulence to PyartRadar

        ddtime = PRD.scan_info.end_time.values.astype(str)
        self.time = datetime.strptime(ddtime[:19],"%Y-%m-%dT%H:%M:%S")

    def retrieve(self):
        
        # Configure a gatefilter to filter out copolar correlation coefficient values > 0.9
        gatefilter = pyart.filters.GateFilter(self.PyartRadar)
        gatefilter.exclude_transition()
        gatefilter.exclude_below('cross_correlation_ratio', 0.8)

        # the compoz has a reordered ray sequence
        compoz = retrieve.composite_reflectivity(self.PyartRadar, field='reflectivity',  gatefilter=None) 

        return compoz

    def cal_tb(self):
        pytda.calc_turb_vol(self.PyartRadar, name_sw='spectrum_width', name_dz='reflectivity', verbose=False,
                    gate_spacing=250.0/1000.0, use_ntda=False)
        

    def cal_fh(self):
        dz = self.PyartRadar.fields['reflectivity']['data']
        dr = self.PyartRadar.fields['differential_reflectivity']['data']
        kd = self.PyartRadar.fields['specific_differential_phase']['data']
        rh = self.PyartRadar.fields['cross_correlation_ratio']['data']

        if os.path.exists(self.sounding) :
            use_temp = True

            col_names = ['pressure', 'height', 'temperature', 'dewpoint', 'direction', 'speed']
            df = pd.read_fwf('1115Z_20220425.txt',
                 skiprows=6, usecols=[0, 1, 2, 3, 6, 7], names=col_names)

            # Drop any rows with all NaN values for T, Td, winds
            df = df.dropna(subset=('temperature', 'dewpoint', 'direction', 'speed'
                                ), how='all').reset_index(drop=True)
            radar_T, radar_z = self.interpolate_sounding_to_radar(df)            
        else:
            use_temp = False
            radar_T  = None

        fh = csu_fhc.csu_fhc_summer(dz=dz, zdr=dr, rho=rh, kdp=kd, use_temp=use_temp, band='S',
                                        T=radar_T)  

        return self.add_field_to_radar_object(fh, self.PyartRadar)

    def interpolate_sounding_to_radar(self, sounding_df):
        """Takes sounding data and interpolates it to every radar gate."""
        radar_z = self.get_z_from_radar(self.PyartRadar)
        radar_T = None
        snd_T, snd_z = self.check_sounding_for_montonic(sounding_df)
        shape = np.shape(radar_z)
        rad_z1d = radar_z.ravel()
        rad_T1d = np.interp(rad_z1d, snd_z, snd_T)
        return np.reshape(rad_T1d, shape), radar_z

    def check_sounding_for_montonic(sounding_df):
        """
        So the sounding interpolation doesn't fail, force the sounding to behave
        monotonically so that z always increases. This eliminates data from
        descending balloons.
        """
        snd_T = sounding_df['temperature'].values  # In old SkewT, was sounding.data
        snd_z = sounding_df['height'].values  # In old SkewT, was sounding.data
        dummy_z = []
        dummy_T = []
        #if not snd_T.mask[0]:  # May cause issue for specific soundings
        dummy_z.append(snd_z[0])
        dummy_T.append(snd_T[0])
        for i, height in enumerate(snd_z):
            if i > 0:
                if snd_z[i] > snd_z[i-1]: #and not snd_T.mask[i]
                    dummy_z.append(snd_z[i])
                    dummy_T.append(snd_T[i])
        snd_z = np.array(dummy_z)
        snd_T = np.array(dummy_T)
        return snd_T, snd_z

    def add_field_to_radar_object(self, field, radar, field_name='FH', units='unitless', 
                              long_name='Hydrometeor ID', standard_name='Hydrometeor ID',
                              dz_field='reflectivity'):
        """
        Adds a newly created field to the Py-ART radar object. If reflectivity is a masked array,
        make the new field masked the same as reflectivity.
        """
        masked_field = np.ma.asanyarray(field)
        fill_value = -32768
        if hasattr(radar.fields[dz_field]['data'], 'mask'):
            setattr(masked_field, 'mask', radar.fields[dz_field]['data'].mask)
            fill_value = radar.fields[dz_field]['_FillValue']
        field_dict = {'data': masked_field,
                    'units': units,
                    'long_name': long_name,
                    'standard_name': standard_name,
                    '_FillValue': fill_value}
        radar.add_field(field_name, field_dict, replace_existing=True)
        return radar

    def get_z_from_radar(self):
        """Input radar object, return z from radar (km, 2D)"""
        radar        = self.PyartRadar
        azimuth_1D   = radar.azimuth['data']
        elevation_1D = radar.elevation['data']
        srange_1D    = radar.range['data']
        sr_2d, az_2d = np.meshgrid(srange_1D, azimuth_1D)
        el_2d        = np.meshgrid(srange_1D, elevation_1D)[1]
        xx, yy, zz   = antenna_to_cartesian(sr_2d/1000.0, az_2d, el_2d)
        return zz + radar.altitude['data']

    def add_ring(self, ax, azmin,azmax,rings, color="#5B5B5B", linestyle='-', linewidth=0.6, **kwargs):

        theta = np.linspace(azmin, azmax,200)
        
        for i in rings:
            x0 = i * np.cos(theta)
            y0 = i * np.sin(theta)
            gci = ax.plot(x0, y0, linestyle=linestyle, linewidth=linewidth, color=color, **kwargs) # circle
        for rad in np.arange(azmin, azmax+0.01, np.pi / 6.0):
            gci = ax.plot([0, rings[-1] * np.cos(rad)], \
                    [0, rings[-1] * np.sin(rad)], \
                    linestyle=linestyle, linewidth=linewidth, color=color, **kwargs) #line
    
    def plot_list_of_fields(self, sweep=0, fields=['reflectivity'], vmins=[0],
                        vmaxs=[65], units=['dBZ'], cmaps=['RdYlBu_r'],
                        return_flag=False, xlim=[-160, 160], ylim=[-150, 150],
                        mask_tuple=None):
        num_fields = len(fields)
        if mask_tuple is None:
            mask_tuple = []
            for i in np.arange(num_fields):
                mask_tuple.append(None)
        nrows = (num_fields + 1) // 2
        ncols = (num_fields + 1) % 2 + 1
        fig = plt.figure(figsize=(14.0, float(nrows)*5.5))
        display = pyart.graph.RadarDisplay(self.PyartRadar)
        for index, field in enumerate(fields):
            ax = fig.add_subplot(nrows, 2, index+1)
            display.plot_ppi(field, sweep=sweep, vmin=vmins[index],
                            vmax=vmaxs[index],
                            colorbar_label=units[index], cmap=cmaps[index],
                            mask_tuple=mask_tuple[index])
            display.set_limits(xlim=xlim, ylim=ylim)
            #ax = plt.gca()
            ring_range = np.arange(0, xlim[1], np.round(xlim[1]/4) )
            self.add_rings(ax,ring_range, color="#5B5B5B", linestyle='-', linewidth=1)
            
        plt.tight_layout()
        if return_flag:
            return display

class Radar2ll(object):
    '''interpolation'''

    def __init__(self, WSR98DData, lat_des, lon_des, var:list, sweep:int, interpolation_method:str):
        self.PyartRadar = WSR98DData.PyartRadar
        self.compz      = WSR98DData.compz
        self.lat_des = lat_des 
        self.lon_des = lon_des
        self.interp_md = interpolation_method
        self.var       = var
        self.sweep     = sweep
        self.radar_ll  = {}

    def interp(self):

        lat, lon, alt = self.PyartRadar.get_gate_lat_lon_alt(self.sweep)
        
        # lat & lon before, size is (nlat*nlon,2)
        LatLon_Before = np.hstack(
            (lat.reshape(-1, 1), lon.reshape(-1, 1)) ) # 按水平方向进行叠加，形成两列

        for ivar in self.var:
            if ivar in ['compz']: # 2d variables
                data  = self.compz.fields['composite_reflectivity']['data'] # slice is a basic function for slice
                units = self.compz.fields['composite_reflectivity']['units'] 
                lat   = self.compz.latitude
                lon   = self.compz.longitude
                
            else:                 # 3d variables
                data = self.PyartRadar.fields[ivar]['data'][self.PyartRadar.get_slice(self.sweep)] #slice()函数是一个切片函数 
                units =  self.PyartRadar.fields[ivar]['units'] 

            data_des = griddata(LatLon_Before, data.reshape(-1, 1), (self.lat_des, self.lon_des),  method=self.interp_md).squeeze()
            field_dict = {
                'data': data_des, \
                'units': units \
                }
            self.radar_ll[ivar] = field_dict

        return(self.radar_ll)

if __name__ == '__main__':

    Min_Lat= 15
    Max_Lat = 55
    Min_Lon = 70
    Max_Lon = 130 #中国区域的经度范围70-140E，纬度范围15-55N

    Lat_des_1D = np.arange( Max_Lat, Min_Lat, -0.1 )  # 生成插值后的纬度  -0.04
    Lon_des_1D = np.arange( Min_Lon, Max_Lon,  0.1 )  # 生成插值后的经度

    Lon_des_2D, Lat_des_2D = np.meshgrid(Lon_des_1D, Lat_des_1D) #打网格 (x,y)

    path = '/Users/xiaowu/Library/Mobile Documents/com~apple~CloudDocs/work/MeteoDataFusion'
    infile = os.path.join(path,'test','data','Z9002.20220425.060745.AR2.bz2')

    radar_ll = Radar2ll(WSR98DData(infile), Lat_des_2D, Lon_des_2D, ['FH', 'compz'], 0, 'linear').interp()
    
    plt.imshow(radar_ll['compz']['data'])
    plt.savefig('test_98d.png')

'''
    def two_panel_plot( radar, sweep=0, var1='reflectivity', vmin1=0, vmax1=65, cmap1='RdYlBu_r', 
                   units1='dBZ', var2='differential_reflectivity', vmin2=-5, vmax2=5, 
                   cmap2='RdYlBu_r', units2='dB', return_flag=False, xlim=[-150,150],
                   ylim=[-150,150]):
        display = pyart.graph.RadarDisplay(radar)
        fig = plt.figure(figsize=(15, 5))
        ax1 = fig.add_subplot(121)
        display.plot_ppi(var1, sweep=sweep, vmin=vmin1, vmax=vmax1, cmap=cmap1, 
                        colorbar_label=units1, mask_outside=True)
        display.set_limits(xlim=xlim, ylim=ylim)
        ax2 = fig.add_subplot(122)
        display.plot_ppi(var2, sweep=sweep, vmin=vmin2, vmax=vmax2, cmap=cmap2, 
                        colorbar_label=units2, mask_outside=True)
        display.set_limits(xlim=xlim, ylim=ylim)
        if return_flag:
            return fig, ax1, ax2, display

    def adjust_fhc_colorbar_for_pyart(cb):
        cb.set_ticks(np.arange(1.4, 10, 0.9))
        cb.ax.set_yticklabels(['Drizzle', 'Rain', 'Ice Crystals', 'Aggregates',
                            'Wet Snow', 'Vertical Ice', 'LD Graupel',
                            'HD Graupel', 'Hail', 'Big Drops'])
        cb.ax.set_ylabel('')
        cb.ax.tick_params(length=0)
        return cb

    # Actual plotting done here
    lim = [-160, 160]
    hid_colors = ['White', 'LightBlue', 'MediumBlue', 'DarkOrange', 'LightPink',
              'Cyan', 'DarkGray', 'Lime', 'Yellow', 'Red', 'Fuchsia']
    cmaphid = colors.ListedColormap(hid_colors)
    fig, ax1, ax2, display = two_panel_plot(radar, sweep=1, vmin1=10, vmax1=75, var1='reflectivity',  var2='FH', vmin2=0, 
                                            vmax2=10, cmap2=cmaphid, units2='', return_flag=True, 
                                            xlim=lim, ylim=lim)

    #add_rings(ax1,[0, 40, 80, 120, 160], color="#5B5B5B", linestyle='-', linewidth=1)
    display.cbs[1] = adjust_fhc_colorbar_for_pyart(display.cbs[1])

    plt.savefig('cf.png')
'''