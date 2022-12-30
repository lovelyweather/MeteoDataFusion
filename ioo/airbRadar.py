import scipy.io as scio
import os

class AcData(object):

    def __init__(self,filename):
        #self.infile = filename
        self.dataset = scio.loadmat(filename)
        self.time = -999

        self.ref = self.dataset['WX_Data']
        self.az = self.dataset['az_out']
        self.Bin_length = 0.15


def AngleToValid(angle):
    '''
    constrain the angles within 0-360 degree.                            
    eg: -90 will be turned into 270.
    '''
    ans = angle - int(np.floor_divide(angle, 360.0)) * 360

    return ans

if __name__=='__main__':

    path = r'/Users/xiaowu/Library/Mobile Documents/com~apple~CloudDocs/work/MeteoDataFusion/test/data/0920test'
    filename = r'azfile.mat'
    infile = os.path.join(path, filename)

    import matplotlib.pyplot as plt
    import numpy as np

    ac = AcData(infile)
    ref = ac.ref
    radarX = np.zeros( ref.shape, dtype = float ) 
    radarY = np.zeros( ref.shape, dtype = float ) 
    for i_az, az in enumerate(ac.az):  # azimuth comes from east, the direction is counterclockwise
        bin_no = np.arange(0, ref.shape[0])
        i_az_valied = AngleToValid(i_az)
        radarX[:,i_az] = bin_no * ac.Bin_length * np.sin(np.deg2rad(az))
        radarY[:,i_az] = bin_no * ac.Bin_length * np.cos(np.deg2rad(az))

    plt.figure(figsize=(12,6))
    plt.contourf( radarX, radarY, ref, levels = np.linspace(10,70,13) )  #   LonAfter_2D, Lat_After_2D
    plt.colorbar() #location="bottom"
    plt.savefig('hi.png')



