import numpy as np
import copy
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from scipy.spatial import KDTree
import os
import webcolors
from osgeo import gdal
from scipy.interpolate import griddata

class Dataset:
    def __init__(self, in_file):
        self.in_file = in_file #Tiff_file
        dataset = gdal.Open(self.in_file)
        self.XSize = dataset.RasterXSize
        self.YSize = dataset.RasterYSize
        self.GeoTransform = dataset.GetGeoTransform()
        self.GetProjection = dataset.GetProjection()

    def get_lat_lon(self):
        gtf = self.GeoTransform
        x_range = range(0, self.XSize)
        y_range = range(0, self.YSize)
        x, y = np.meshgrid(x_range, y_range)
        lon = gtf[0] + x*gtf[1] + y*gtf[2]
        lat = gtf[3] + x*gtf[4] + y*gtf[5]
        return lat, lon

class CRefMosaicData(object):
    """
    获得带经纬度信息的全国雷达站组合反射率因子
    """

    #图例的像素位置区域范围
    left_x = 955
    upper_y = 665
    right_x = 973
    lower_y = 858

    #右下角图例显示的13个色块所表示颜色的编码，可利用MacOS上一colorSLurp的取色器取色
    COLORS = [
        '#AD90F0',
        '#9600B4',
        '#FF00F0',
        '#C00001',
        '#D60100',
        '#FF0200',
        '#FF9000',
        '#E7C000',
        '#FEFF00',
        '#009000',
        '#00D800',
        '#00ECEC',
        '#01A0F6'
    ]

    #把颜色的hex码转换为RGB整数值
    colors_arrays = np.array([list(webcolors.hex_to_rgb(c)) for c in COLORS])
    cm_user=np.array(colors_arrays[::-1])/255.0
    icmap=colors.ListedColormap(cm_user,name='my_color') 


    def __init__(self, filename):
        self.in_file = filename 
        self.lat, self.lon, self.data = self.data_prepare()

    def data_prepare(self):
        self.save_dbz()
        cmd = "gdal_translate -of GTiff -a_srs \"+proj=lcc +lat_1=30 +lat_2=62 +lat_0=39.0 +lon_0=110 +a=6378137 +b=6378137 +units=m +no_defs\" -a_ullr -3116700.0385205294 1693154.412068708 2017567.3399639379 -2737364.450775645 "
        src = "dbz.png"
        dst = "dbz.tiff"
        os.system(' '.join([cmd, src, dst]))
        #os.system("gdal_translate -of GTiff -a_srs \"+proj=lcc +lat_1=30 +lat_2=62 +lat_0=39.0 +lon_0=110 +a=6378137 +b=6378137 +units=m +no_defs\" -a_ullr -3116700.0385205294 1693154.412068708 2017567.3399639379 -2737364.450775645 dbz.png dbz.tif")
        # 进一步转为等经纬度的GeoTiff文件
        os.system("gdalwarp -t_srs EPSG:4326 dbz.tiff dbz_new.tiff")
        
        ds = gdal.Open("dbz_new.tiff")
        dataset = Dataset("dbz_new.tiff")

        os.system("rm dbz.tiff dbz.png dbz_new.tiff")

        lat, lon = dataset.get_lat_lon() #每个格点的经纬度信息
        rbg_value = np.stack([ds.GetRasterBand(i).ReadAsArray() for i in (1,2,3)]) #每个格点的RGB信息

        dBZ_levels = np.arange(72.5, 7.5, -5) #由图右下角的colorbar

        dBZ_figure = np.empty(shape=(rbg_value.shape[1],rbg_value.shape[2]))
        for n, colors_array in enumerate(CRefMosaicData.colors_arrays):
            dist = np.sum( (np.transpose(rbg_value,(1,2,0)) - colors_array)**2, axis = 2 )
            dbz_index = np.where( (dist == dist.min()) & (dist.min()< 10) )
            #print(dist.min())
            dBZ_figure[dbz_index] = dBZ_levels[n] # -0.1 

        dBZ_figure = np.where(dBZ_figure < 10.0, np.nan , dBZ_figure)

        return lat, lon, dBZ_figure
    
    def save_dbz(self):
        raw_img_array = plt.imread(self.in_file)
        #0-255整数形式的RGB数值更为精确和通用，plt.imread读取的颜色为0-1的浮点数，因此转换为int型
        rgb_img_array = (raw_img_array * 255).astype(int)
        #将底图与dbz颜色分离
        #初始化阶段将原始图片数组分别存入两个数组。
        #存dbz的数组为data_img_array
        flaw_img_array = copy.deepcopy(rgb_img_array)
        #存底图的数组为flaw_img_array，由于后期底图的数组主要用于对缝隙的填补，因此使用flaw。
        data_img_array = copy.deepcopy(rgb_img_array)

        # 方法2: 先将图中的dbz剔除掉，得到纯净的底图，然后获取底图带颜色区域的坐标，利用该坐标将底图赋值为白色，从而获取dbz
        # 1. 剔除dbz像素点，提取出底图部分的坐标
        for colors_array in CRefMosaicData.colors_arrays:
            dist = np.sum((rgb_img_array - colors_array) ** 2, axis=2)
            dbz_index = np.where(dist==dist.min())
            flaw_img_array[dbz_index] = np.array([255,255,255])

        flaw_index = np.where(flaw_img_array.sum(axis=2)<255*3) #非白色的坐标位置，即底图的坐标位置

        # 2. 将底图部分赋值为空白
        data_img_array[flaw_index] = np.array([255,255,255])

        data_img_array[CRefMosaicData.upper_y:CRefMosaicData.lower_y+1,CRefMosaicData.left_x:CRefMosaicData.right_x+1] = np.array([255,255,255])

        #以上图片中都有dBZ裂痕，下面进行填补
        # 1. 获取裂痕坐标
        flaw_yx = np.where(flaw_img_array.sum(axis=2)<255*3) #和方法2中的思路一样
        # 2. create a mask
        mask = np.full(raw_img_array.shape[:2], False)
        mask[flaw_yx] = True
        # 3. use scipy.spatial.KDTree to look for the nearest value to fill the cracks
        flaw_xy = flaw_yx[::-1]
        data_xy = np.where(~mask)[::-1]

        data_points = np.array(data_xy).T
        flaw_points = np.array(flaw_xy).T

        data_img_array[mask] = data_img_array[~mask][KDTree(data_points).query(flaw_points)[1]] #返回值是离查询点最近的点的距离和索引
        #save the image array to png
        plt.imsave("dbz.png",np.uint8(data_img_array))

class CRefMosaic2ll(object):
    '''interpolation'''

    def __init__(self, CRefMosaic, lat_des, lon_des, interpolation_method:str):
        self.CRefMosaic = CRefMosaic
        self.lat_des = lat_des
        self.lon_des = lon_des
        self.interp_md = interpolation_method
        self.cmosiac_ll = {}

    def interp(self):
        # 插值前的经纬度, 维度是(nlat*nlon,2)
        LatLon_Before = np.hstack(
            (self.CRefMosaic.lat.reshape(-1, 1), self.CRefMosaic.lon.reshape(-1, 1)) ) # 按水平方向进行叠加，形成两列
        
        units = 'dBZ'
        data_des = griddata(LatLon_Before, self.CRefMosaic.data.reshape(-1, 1), (self.lat_des, self.lon_des),  method=self.interp_md).squeeze()

        field_dict = {
            'data': data_des, \
            'units': units \
            }

        self.cmosiac_ll['cref'] = field_dict

        return(self.cmosiac_ll)

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

    Lat_des_1D = np.arange( Max_Lat, Min_Lat, -0.1 )  # 生成插值后的纬度  -0.04
    Lon_des_1D = np.arange( Min_Lon, Max_Lon,  0.1 )  # 生成插值后的经度


    Lon_des_2D, Lat_des_2D = np.meshgrid(Lon_des_1D, Lat_des_1D) #打网格 (x,y)

    path = '/Users/xiaowu/Library/Mobile Documents/com~apple~CloudDocs/work/MeteoDataFusion'
    infile = os.path.join(path,'test','data','0920test','Z_RADA_C_BABJ_20220920050600_P_DOR_RDCP_R_ACHN.PNG')

    cmosiac_ll = CRefMosaic2ll(CRefMosaicData(infile), Lat_des_2D, Lon_des_2D, 'linear').interp()
    
    plt.figure(figsize=(12,6))
    plt.contourf( Lon_des_2D, Lat_des_2D, cmosiac_ll['cref']['data'], levels = np.linspace(10,70,13) )  #   LonAfter_2D, Lat_After_2D
    plt.colorbar() #location="bottom"
    plt.title('mosaic composite reflectivity in dBZ')

    #plt.imshow(cmosiac_ll['cref']['data'])
    plt.savefig('test_cref_ll_0920.png')