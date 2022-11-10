"""
Class for creating plots from Radar objects.
"""

import warnings
import matplotlib.pyplot as plt
import numpy as np
'''
class FusionDisplay(object):
    
    def __init__(self, FusionData):
        self._FusionData = FusionData
'''


def plot_sat(data, Lat_2D, Lon_2D, is_ac_plot:bool, ac_ll=None,varname=None,ll_extend=None, \
    min_max=None, orientation="vertical",cmap='Blues', tick_level=None, cbar_ticklabels=None):
    # orientation这里没起作用，后面需要改colorbar的相关信息还需要改进
    from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
    import matplotlib.ticker as mticker
    import cartopy.crs as ccrs
    import cartopy.feature as cfeat
    
    if min_max is not None:
        vmin, vmax = min_max
    else:
        vmin = np.nanmin(data)
        vmax = np.nanmax(data)

    fig = plt.figure(figsize=(20,12))
    axe = plt.subplot(121, projection=ccrs.PlateCarree())
    with open(r'CN-border-La.gmt') as src:
        context = ''.join([line for line in src if not line.startswith('#')])
        blocks = [cnt for cnt in context.split('>') if len(cnt) > 0]
        borders = [np.fromstring(block, dtype=float, sep=' ') for block in blocks]

    for line in borders:
        axe.plot(line[0::2], line[1::2], '-', color='k', transform=ccrs.Geodetic())

    var_name = ['CLM', 'CTH'] #如果是其它的变量，自行往里添加
    long_name = ['cloud mask', 'cloud top height $\mathrm{(km)}$']
    dict_var_long = dict(zip(var_name, long_name))
    if (varname is not None):
        axe.set_title(dict_var_long[varname],fontsize=18)
    axe.add_feature(cfeat.COASTLINE.with_scale('10m'), linewidth=0.8,color='k')
    LAKES_border = cfeat.NaturalEarthFeature('physical', 'lakes', '50m', edgecolor='blue', facecolor='never')
    axe.add_feature(LAKES_border, linewidth=0.8)
    
    if ll_extend is not None:
        Min_Lat, Max_Lat, Min_Lon, Max_Lon = ll_extend #中国区域的经度范围70-140E，纬度范围15-55N
    else: 
        Min_Lat= 15
        Max_Lat = 55
        Min_Lon = 70
        Max_Lon = 140 #中国区域的经度范围70-140E，纬度范围15-55N

    gl = axe.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.8, color='gray',linestyle=':')
    gl.top_labels,gl.bottom_labels,gl.right_labels,gl.left_labels = False,False,False,False
    gl.xformatter = LONGITUDE_FORMATTER ##坐标刻度转换为经纬度样式
    gl.yformatter = LATITUDE_FORMATTER 
    gl.xlocator = mticker.FixedLocator(np.arange(Min_Lon, Max_Lon, 10))
    gl.ylocator = mticker.FixedLocator(np.arange(Min_Lat, Max_Lat, 10))

    axe.set_xticks(np.arange(Min_Lon, Max_Lon+1, 10), crs=ccrs.PlateCarree())
    axe.set_yticks(np.arange(Min_Lat, Max_Lat+1, 10), crs=ccrs.PlateCarree())
    axe.xaxis.set_major_formatter(LongitudeFormatter())
    axe.yaxis.set_major_formatter(LatitudeFormatter())
    axe.tick_params(labelcolor='k',length=5)

    axe.set_extent([Min_Lon,Max_Lon, Min_Lat, Max_Lat], crs=ccrs.PlateCarree()) #这里crs=ccrs.PlateCarree()一定要加上，不然那个范围就设置不对，暂时不知道为什么，留待以后发现了补充

    if (tick_level is None):
        tick_level = np.arange(vmin-0.5,vmax)
    contourf = axe.contourf(Lon_2D, Lat_2D, data, tick_level, cmap='Blues', extend='neither', shading='auto', alpha = 0.8)  #, vmax=vmax, vmin=vmin

    rect = [0.125, 0.26, 0.35, 0.015] 
    cbar_ax = fig.add_axes(rect)
    cb = fig.colorbar(contourf, drawedges=True, cax=cbar_ax, orientation='horizontal',spacing='uniform', ticks = cbar_ticklabels)  
    plt.show()
    plt.savefig('test_fy4_ll.png')

