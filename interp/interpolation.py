import numpy as np

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

def get_ac(ac_parameters, var, lat, lon):
    '''
    based on the aircraft parameters, transform the original
    variable to the aircraft-based grid, 
    note that the grid hasn't been rotated. 

    params ac_parameters: a dictionary containing air-borne radar's parameters
    params var          : the product to transfer, should be 2D matrix
    params lat, lon     : 2D matrix, latitude and longtitude for var
    
    return 
    radarX, radarY : distance from radar site in x and y direction
    var_ac         : np.array after interpolation.
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
    long_ac = np.zeros((360, ngate), dtype = float ) 
    lat_ac  = np.zeros((360, ngate), dtype = float )  # initialize
    var_ac = np.zeros((360, ngate), dtype = float ) 
    #print( np.arange(Azmin, Azmax + 1))
    for i_az in np.arange(Azmin, Azmax + 1):  # azimuth comes from east, the direction is counterclockwise
        for i_bin in np.arange(0, ngate):
            i_az_valied = int(AngleToValid(i_az))
            x = i_bin * Bin_length * np.sin(np.deg2rad(i_az_valied))
            y = i_bin * Bin_length * np.cos(np.deg2rad(i_az_valied))
            radarX[i_az_valied, i_bin] = x
            radarY[i_az_valied, i_bin] = y            

            lat_grid = y / 1000.0 /111.0 + lat0
            lon_grid = np.rad2deg(x / 1000.0 /(R_earth * np.cos(np.deg2rad(lat_grid)))) + lon0

            long_ac[i_az_valied, i_bin]  = lon_grid
            lat_ac[i_az_valied, i_bin]    = lat_grid

            y_index = np.argmin(np.abs(lat - lat_grid)) # lat：原始数据中的等经纬度网格；lat_grid：机载网格中点(i_az, i_bin)的经度。
            x_index = np.argmin(np.abs(lon - lon_grid))

            var_ac[i_az_valied, i_bin] = var[y_index, x_index] 

    return radarX, radarY, var_ac 