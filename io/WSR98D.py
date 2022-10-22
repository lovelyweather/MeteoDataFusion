import os

import numpy as np
from pycwr.io import read_auto
import pyart
from pyart import retrieve
import matplotlib.pyplot as plt


class WSR98DData(object):
    '''
    获取带经纬度信息的地基单站雷达信息
    '''

    def __init__(self, filename):
        self.infile = filename
        self.data, self.compz = self.data_prepare()

    def data_prepare(self):
        PRD = read_auto(self.infile)
        #convert to Pyart format
        PyartRadar = PRD.ToPyartRadar()

        #for field_name in PyartRadar.fields.keys():
        #    print(field_name)

        # Configure a gatefilter to filter out copolar correlation coefficient values > 0.9
        gatefilter = pyart.filters.GateFilter(PyartRadar)
        gatefilter.exclude_transition()
        gatefilter.exclude_below('cross_correlation_ratio', 0.9)

        compoz = retrieve.composite_reflectivity(PyartRadar, field='reflectivity') #,  gatefilter=gatefilter)

        return PyartRadar, compoz

if __name__ == '__main__':

    path = '/Users/xiaowu/Library/Mobile Documents/com~apple~CloudDocs/work/MeteoDataFusion'
    infile = os.path.join(path,'test','data','Z9002.20220425.060745.AR2.bz2')
    radar = WSR98DData(infile).data

    fig = plt.figure(figsize=(8,6))
    ax  = plt.subplot(111)
    composite_display = pyart.graph.RadarDisplay(radar)
    composite_display.plot("composite_reflectivity", ax=ax,
                       vmin=-20, vmax=80, cmap='pyart_HomeyerRainbow')

    plt.savefig('cf.png')