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

def writebin(infile_nc,outfile_bin):
    """
    Write netcdf files to binary, for use with greb model
    Input: 
    infile_nc - an iris cube
    outfile_bin: string, with name of output file, e.g. 'zonal.wind'
    Output:
    writes the outfile to disk
    """
    dataflat = infile_nc.data.flatten().astype(np.float32)
    ofile = open(outfile_bin,'wb')
    dataflat.tofile(ofile)
    ofile.close()

mer_wind = iris.load_cube('./ncfiles/meridional.wind.nc')
anom_v = iris.load_cube('./ncfiles/v_reg_aus_850.nc')
anom_u = iris.load_cube('./ncfiles/u_reg_aus_850.nc')

anom_v.standard_name = mer_wind.standard_name
anom_v.units = mer_wind.units
# Remove 'coord system' for regridding to work
anom_v.coord('latitude').coord_system = None
anom_v.coord('longitude').coord_system = None

# Rearrange order of coords
mer_wind.transpose([2,0,1])

#regrid v anom
anom_v = anom_v.regrid(mer_wind[0,::],iris.analysis.Linear())

new_merwind = mer_wind.copy()
new_merwind.data = anom_v.data + mer_wind.data

new_merwind.transpose([1,2,0])

iris.save(new_merwind,'./ncfiles/meridional.wind.vanom.nc')
writebin(new_merwind,'./input_files/meridional.wind.vanom.bin')


# mer_wind.data = mer_wind.data 

# cube_list = iris.cube.CubeList()
# input_files = ['meridional.wind', 'zonal.wind','tsurf','soil.moisture','vapor','ocean.mld','cloud.cover']
# 
# for i in files:
#     infile = iris.load_cube('./ncfiles/'+i+'nc')
#     cube_list.append(infile)
# 

sys.exit()

#########################################################################################
#Function to read data from GREB 
def read_data(infile, n_tsteps): 
    
    field = np.zeros((xdim,ydim,n_tsteps)) # Create a zero numpy array with correct dimensions
    fid = open(infile,'r') 
    print infile

    if infile == 'meridional.wind':
        long_name = 'meridional_wind'
        standard_name = 'y_wind'
        unit = iris.unit.Unit('m s-1')
    elif infile == 'zonal.wind':
        long_name = 'zonal_wind'
        standard_name = 'x_wind'
        unit = iris.unit.Unit('m s-1')
    elif infile == 'tsurf':
        long_name = 'surface temperature'
        standard_name = 'surface_temperature'
        unit = iris.unit.Unit('K')
    elif infile == 'cloud.cover':
        long_name = 'cloud cover'
        standard_name = 'cloud_area_fraction'
        unit = iris.unit.Unit('1')
    elif infile == 'soil.moisture':
        long_name = 'soil moisture'
        standard_name = 'soil_moisture_content'
        unit = iris.unit.Unit('kg m-2')
    elif infile == 'vapor':
        long_name = 'water vapor'
        standard_name = 'specific_humidity'
        unit = iris.unit.Unit('kg kg-1')
    elif infile == 'ocean.mld':
        long_name = 'ocean mld'
        standard_name = 'ocean_mixed_layer_thickness'
        unit = iris.unit.Unit('m')

    for n in np.arange(0,n_tsteps):    #Loop through time steps in data
        xin = np.fromfile(fid, np.float32, count=xydim) #t_surf
        
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
    newcube.standard_name = standard_name
    newcube.units = unit
    newcube.attributes = iris._cube_coord_common.LimitedAttributeDict({'source':'Input Data for GREB model'})
        
    fid.close()

    iris.save(newcube,'./ncfiles/'+infile+'.nc')
    return field, newcube

    
#########################################################################################
#End of defined funcs   
#########################################################################################
#Sample plotting script begins
##########################################################################################
#Parameters
# t_surf = 'surface temperature'
# t_atmos = 'temperature of atmosphere'
# t_ocean = 'temperature of ocean'
# vapour = 'water vapour'
# albedo = 'albedo'    

# var_list = ['t_surf', 't_atmos', 't_ocean', 'vapour', 'albedo']

#Dimensions
xdim  = 96
ydim  = 48
dx    = 3.75
tstep = 2 #timesteps per day
ireal = 4
xydim = xdim*ydim

#Variables 
input_files = ['meridional.wind', 'zonal.wind','tsurf','soil.moisture','vapor','ocean.mld','cloud.cover']
time_length = 'annual' # Choose out of 'annual', 'DJF', 'MAM', 'JJA', 'SON' and months
# years = 50 # must match data from GREB model. Choose the number of years that the GREB model is set to run for
# climate_infile = albedo # Choose climate variable to plot

#read and plot data
for i in input_files:
    file_size = os.stat(i).st_size
    n_tsteps = file_size/(xdim*ydim*ireal)
    greb_data, newcube = read_data(i, n_tsteps)




