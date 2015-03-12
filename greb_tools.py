import numpy as np
import matplotlib.pyplot as plt
import iris
import iris.plot as iplt
import iris.quickplot as qplt
import sys
import os

# author: Nicholas Loveday
# modified by Nicholas Tyrrell Feb 2015 to use Iris
# Read in netcdf input files,
# get data, flatten,
# Write out binary files
def read_anom_data(infile): 

    xdim  = 96
    ydim  = 48
    dx    = 3.75
    ireal = 4
    tstep = 4 #timesteps per day
    xydim = xdim*ydim

    file_size = os.stat(infile).st_size
#     print file_size
    n_tsteps = file_size/(xdim*ydim*ireal)
#     print n_tsteps
    field = np.zeros((xdim,ydim,n_tsteps)) # Create a zero numpy array with correct dimensions
    fid = open(infile,'r') 

    long_name = infile 
    unit = iris.unit.Unit('1')

    for n in np.arange(0,n_tsteps):    #Loop through time steps in data
        xin = np.fromfile(fid, np.float32, count=xydim) #t_surf
#         print xin.shape
#         print n

        for i in np.arange(0,ydim):
            field[:,i,n] = xin[(xdim*(i)):((i+1)*xdim)]  
        #Function to flip and rotate data

    field = np.rot90(field)
    field = np.flipud(field) 
    newcube = iris.cube.Cube(field, long_name=long_name)

    lons = (np.arange(1.875,360,3.75)) # Define longitudes
    lats = (np.arange(-88.125,90,3.75)) #Define latitutdes
    time_coord = iris.coords.DimCoord(np.arange(0,n_tsteps), standard_name='time')
#     time_coord = iris.coords.DimCoord(np.arange(0,600*30,30), standard_name='time', units=iris.unit.Unit('days since 1950-01-15 00:00:0.0', calendar='360_day'))
#     long_name = 'surface temperature'

    newcube.add_dim_coord(iris.coords.DimCoord(lats, 'latitude', units='degrees'), 0)
    newcube.add_dim_coord(iris.coords.DimCoord(lons, 'longitude', units='degrees'), 1)
    newcube.add_dim_coord(time_coord, 2)
#     newcube.standard_name = standard_name
    newcube.units = unit
    newcube.attributes = iris._cube_coord_common.LimitedAttributeDict({'source':'Input Data for GREB model'})
        
    fid.close()

#     iris.save(newcube,'./ncfiles/'+infile+'.nc')
    return newcube

def read_anom_bin():

    var_list = ['cloud.cover.anom', 'meridional.wind.anom', 'soil.moisture.anom', 'zonal.wind.anom']
    cube_list = iris.cube.CubeList()

    #read and plot data
    for i in var_list:
        newcube = read_anom_data(i) # read data
        cube_list.append(newcube)
    return cube_list


def try_cube(cube):
    """ get cubes up to spec in terms of time var name and bounds
    Input: cube
    Output: cube
    """
    try:
        cube.coord('t').standard_name = 'time'
    except:
        pass
    try:
        cube.coord('pressure').standard_name = 'air_pressure'
    except:
        pass
    try:
        cube.coord('latitude').guess_bounds()
    except:
        pass
    try:
        cube.coord('longitude').guess_bounds()
    except:
        pass
    return cube

def writebin(infile_nc,outfile_bin):
    """
    Write netcdf files to binary, for use with greb model
    Input: 
    infile_nc - an iris cube
    outfile_bin: string, with name of output file, e.g. 'zonal.wind'
    Output:
    writes the outfile to disk
    """

    dataflat = infile_nc.data.copy()
    dataflat = np.rot90(dataflat)
    dataflat = np.flipud(dataflat)
    dataflat = dataflat.flatten('F').astype(np.float32)
    ofile = open(outfile_bin,'wb')
    dataflat.tofile(ofile)
    ofile.close()

def write_v_anom(p_m="pos"):
    """
    Reads in netcdf files of meridional wind and anomalous winds
    add anomalies to input files
    p_m = "pos" or "neg" for positive or negative anomaly
    writes out nc and bin files
    """

    mer_wind = iris.load_cube('./ncfiles/meridional.wind.nc')
    anom_v = iris.load_cube('./ncfiles/v_reg_aus_850.nc')
    print 'meridional.wind and anomalous wind loaded'

    anom_v.standard_name = mer_wind.standard_name
    anom_v.units = mer_wind.units
    # Remove 'coord system' for regridding to work
    anom_v.coord('latitude').coord_system = None
    anom_v.coord('longitude').coord_system = None

    # Rearrange order of coords
#     mer_wind.transpose([2,0,1])
    #regrid v anom
    anom_v = anom_v.regrid(mer_wind[:,:,0],iris.analysis.Linear())

    new_merwind = mer_wind.copy()
    anom_v_data = np.repeat(np.expand_dims(anom_v.data,2),mer_wind.shape[-1],2)
    if p_m == "pos":
        print "Positive anomaly"
        new_merwind.data = anom_v_data
    if p_m == "neg":
        print "Negative anomaly"
        new_merwind.data = -anom_v_data
        
    print 'Writing meridional.wind.anom and meridional.wind.anom.nc and anomalous wind loaded'
    iris.save(new_merwind,'./ncfiles/meridional.wind.anom.nc')
    writebin(new_merwind,'./input_files/meridional.wind.anom')

def write_u_anom(p_m="pos"):
    """
    Reads in netcdf files of zonal wind and anomalous winds
    add anomalies to input files
    p_m = "pos" or "neg" for positive or negative anomaly
    writes out nc and bin files
    """

    zon_wind = iris.load_cube('./ncfiles/zonal.wind.nc')
    anom_u = iris.load_cube('./ncfiles/u_reg_aus_850.nc')
    print 'zonal.wind and anomalous wind loaded'

    anom_u.standard_name = zon_wind.standard_name
    anom_u.units = zon_wind.units
    # Remove 'coord system' for regridding to work
    anom_u.coord('latitude').coord_system = None
    anom_u.coord('longitude').coord_system = None

    # Rearrange order of coords
#     zon_wind.transpose([2,0,1])
    #regrid v anom
    anom_u = anom_u.regrid(zon_wind[:,:,0],iris.analysis.Linear())

    new_zonwind = zon_wind.copy()
    anom_u_data = np.repeat(np.expand_dims(anom_u.data,2),zon_wind.shape[-1],2)
    if p_m == "pos":
        print "Positive anomaly"
        new_zonwind.data = anom_u_data
    if p_m == "neg":
        print "Negative anomaly"
        new_zonwind.data = -anom_u_data
        
    print 'Writing zonal.wind.anom and zonal.wind.anom.nc and anomalous wind loaded'
    iris.save(new_zonwind,'./ncfiles/zonal.wind.anom.nc')
    writebin(new_zonwind,'./input_files/zonal.wind.anom')

def write_smc():
    """
    Reads in netcdf files of meridional wind and anomalous winds
    add anomalies to input files
    writes out nc and bin files
    """
    smc = iris.load_cube('./ncfiles/soil.moisture.nc')
#     anom_v = iris.load_cube('./ncfiles/v_reg_aus_850.nc')
    print 'Soil moisture loaded'

    smcdata = smc.data.copy()
    masklt = np.ma.masked_less(smcdata,1)
    smc.data = smcdata * (~masklt.mask).astype(int)
    smc.data = smc.data
    print "all land now very, very dry"

    print 'Writing soil.moisture.smc.anom/nc'
    iris.save(smc,'./ncfiles/soil.moisture.smc.anom.nc')
    writebin(smc,'./input_files/soil.moisture.smc.anom')

    return # smc

def write_blank_anom():
    """
    Create blank bin files of correct length as placeholders for further experiments
    """

    mer_wind = iris.load_cube('./ncfiles/meridional.wind.nc')
    zonal_wind = iris.load_cube('./ncfiles/zonal.wind.nc')
    soil_moisture = iris.load_cube('./ncfiles/soil.moisture.nc')
    cloud_cover = iris.load_cube('./ncfiles/cloud.cover.nc')

    mer_wind.data = np.zeros(mer_wind.shape)
    zonal_wind.data = np.zeros(zonal_wind.shape)
    soil_moisture.data = np.zeros(soil_moisture.shape)
    cloud_cover.data = np.zeros(cloud_cover.shape)

    print 'writing placeholder binary files to orig_input'
    writebin(mer_wind,'./orig_input/meridional.wind.anom')
    writebin(zonal_wind,'./orig_input/zonal.wind.anom')
    writebin(soil_moisture,'./orig_input/soil.moisture.anom')
    writebin(cloud_cover,'./orig_input/cloud.cover.anom')

