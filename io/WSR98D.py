import numpy as np
import pyart
from pycwr.io import read_auto
import pytda


class WSR98DData(object):
    '''
    获取带经纬度信息的地基单站雷达信息
    '''

    def __init__(self, filename):
        self.infile = filename
        self.lat, self.lon, self.data = self.data_prepare()

    def data_prepare(self):
        PRD = read_auto(self.infile)
        
