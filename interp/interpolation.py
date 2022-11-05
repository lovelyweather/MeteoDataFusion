import numpy as np

class transform(object):
    '''
    A class for storing the 


    '''

    def __init__(self, FusionData, ac_para, var:list):
        self.Data = FusionData
        self.ac_para = ac_para
        self.var = var
        self.acgrid_data = {}

        for i_var in var:




def AngleToValid(angle):
    '''
    constrain the angles within 0-360 degree. 
    eg: -90 will be turned into 270.
    '''
    ans = angle - int(np.floor_divide(angle, 360.0)) * 360

    return ans

def DMS2Decimal(dms):
    ''' degrees minutes seconds to Decimal '''

    degrees = int( dms ) 
    minutes = int ( ( dms - degrees ) * 100 )
    seconds = ( dms - degrees - 0.01* minutes ) * 10000
    decimal = degrees + minutes/60.0 + seconds/3600.0
        
    return decimal

def get_ac(ac_parameters, var, lat, lon):
    '''
    based on the aircraft parameters, transform the original
    variable to the aircraft-based grid, 
    note that the grid hasn't been rotated. 

    params ac_parameters: a dictionary containing air-borne radar's parameters
    params var          : the product to transfer, should be 2D matrix
    params lat, lon     : 2D matrix, latitude and longtitude for var

    '''
    Rmax      = ac_parameters['Rmax_Air']
    Rmin      = ac_parameters['Rmin_Air']
    heading_angle = ac_parameters['heading_angle']
    range_angle   = ac_parameters['range_angle']
    Bin_length    = ac_parameters['Bin_length']
    DMS           = ac_parameters['DMS']
    if ( DMS == False ):
        lat0 =  ac_parameters['ll_center'][0]
        lon0 =  ac_parameters['ll_center'][1]
    else:
        lat0 = DMS2Decimal( ac_parameters['ll_center'][0] )
        lon0 = DMS2Decimal( ac_parameters['ll_center'][1] )

    # constant
    R_earth = 6371.393

    Azmin = heading_angle - range_angle
    Azmax = heading_angle + range_angle
    ngate = int(np.round((Rmax - Rmin) * 1000 / Bin_length))

    radarX = np.zeros((360, ngate), dtype = float ) 
    radarY = np.zeros((360, ngate), dtype = float ) 
    var_ac = np.zeros((360, ngate), dtype = float ) 
    for i_az in np.arange(Azmin, Azmax + 1):  # azimuth comes from east, the direction is counterclockwise
        for i_bin in np.arange(0, ngate):
            i_az_valied = int(AngleToValid(i_az))
            x = i_bin * Bin_length * np.sin(np.deg2rad(i_az))
            y = i_bin * Bin_length * np.cos(np.deg2rad(i_az))
            radarX[i_az_valied, i_bin] = x
            radarY[i_az_valied, i_bin] = y

            lat_grid = y / 1000.0 /111.0 + lat0
            lon_grid = np.rad2deg(x / 1000.0 /(R_earth * np.cos(np.deg2rad(lat_grid)))) + lon0

            y_index = np.argmin(np.abs(lat - lat_grid)) # lat：原始数据中的等经纬度网格；lat_grid：机载网格中点(i_az, i_bin)的经度。
            x_index = np.argmin(np.abs(lon - lon_grid))

            var_ac[i_az_valied, i_bin] = var[y_index, x_index] 

    return radarX, radarY, var_ac