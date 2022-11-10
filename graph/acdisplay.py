"""
Class for creating plots from Radar objects.
"""


import warnings
import numpy as np
import matplotlib.pyplot as plt

def add_ring(ax, azmin, azmax, rings, color="#5B5B5B", linestyle='-', linewidth=0.6, **kwargs):
    '''
    在图片上加距离环
    params azmin, azmax: 起始方位角
    params rings:list, 要画的环的距离
    Usage:
    add_ring(ax1, 0,np.pi, [0, 40, 80, 120, 160], linestyle='-', linewidth=1)
    '''

    theta = np.linspace(azmin, azmax, 200)

    for i in rings:
        x0 = i * np.cos(theta)
        y0 = i * np.sin(theta)
        gci = ax.plot(x0, y0, linestyle=linestyle, linewidth=linewidth, color=color, **kwargs)  # plot circle
    for rad in np.arange(azmin, azmax + 0.01, np.pi / 6.0):
        gci = ax.plot([0, rings[-1] * np.cos(rad)], \
                      [0, rings[-1] * np.sin(rad)], \
                      linestyle=linestyle, linewidth=linewidth, color=color, **kwargs)  # plot line  

def rotate(x, y, alpha):
    '''
    rotate the graph for alpha degree
    # For a given point (x, y) in the plot, rotate the graph , the new point would be (x0, y0)
    假设对图片上任意点(x,y)，绕一个坐标点(rx0,ry0)逆时针旋转a角度后的新的坐标设为(x0, y0)，有公式：
        x0= (x - rx0)*cos(a) - (y - ry0)*sin(a) + rx0 ;
        y0= (x - rx0)*sin(a) + (y - ry0)*cos(a) + ry0 ;
    '''
    alpha = np.deg2rad(alpha)
    x_r = x * np.cos(alpha) - y * np.sin(alpha)
    y_r = x * np.sin(alpha) + y * np.cos(alpha)

    return x_r, y_r

def plot_ac(ac_parameters,radarX, radarY, var_ac, var_name, min_max, tick_level, cmap):
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1)

    X1, Y1 = rotate(radarX, radarY, ac_parameters.heading_angle) 
    vmin, vmax = min_max
    pc = ax.pcolormesh( X1/1000, Y1/1000, var_ac/1000, vmin = vmin, vmax = vmax, shading='auto', cmap = cmap )
    ax.set_title('%s with heading angle of %.2f'%(var_name, ac_parameters.heading_angle), fontsize=20)
    plt.gca().set_aspect("equal")

    rect = [0.13, 0.24, 0.76, 0.02] # [left, bottom, width, height] 
    cbar_ax = fig.add_axes(rect)
    fig.colorbar(pc, ticks=tick_level, cax=cbar_ax, orientation='horizontal')
    rings = np.linspace(0, Rmax, 5)
    add_ring(ax, 0, np.pi, rings, color='k', linestyle='-', linewidth=1.5)


class AcDisplay(object):
    
    def __init__(self, FusionData):
        self._FusionData = FusionData



