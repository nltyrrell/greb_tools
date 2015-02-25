import numpy as np
import matplotlib.pyplot as plt
import iris
import iris.plot as iplt
import iris.quickplot as qplt
import os

# author: Nicholas Loveday
# modified by Nicholas Tyrrell Feb 2015 to use Iris
#This script contains functions for creating plots for the GREB model

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
    elif infile == 'outfile.bin':
        long_name = 'unknown'
        standard_name = 'duration_of_sunshine'
        unit = iris.unit.Unit('s')

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
input_files = ['meridional.wind', 'zonal.wind','tsurf','soil.moisture','vapor','ocean.mld','cloud.cover','outfile.bin']
time_length = 'annual' # Choose out of 'annual', 'DJF', 'MAM', 'JJA', 'SON' and months
# years = 50 # must match data from GREB model. Choose the number of years that the GREB model is set to run for
# climate_infile = albedo # Choose climate variable to plot

#read and plot data
for i in input_files:
    file_size = os.stat(i).st_size
    n_tsteps = file_size/(xdim*ydim*ireal)
    greb_data, newcube = read_data(i, n_tsteps)




