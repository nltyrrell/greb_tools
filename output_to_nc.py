import numpy as np
import matplotlib.pyplot as plt
import iris
import iris.plot as iplt
import iris.quickplot as qplt
import sys
import os

# author: Nicholas Loveday
# modified by Nicholas Tyrrell Feb 2015 to use Iris
#This script contains functions for creating plots for the GREB model

#########################################################################################
#Function to read data from GREB 
def read_data(years, infile, variable, scenario_name): 
    xdim  = 96              # x dimensions                  
    ydim  = 48              # y dimensions
    dx    = 3.75            # model resolution
    xydim = xdim*ydim
    tdim  = 12*years        #Total time steps in the data
    print tdim
    
    
    field = np.zeros((xdim,ydim,tdim)) # Create a zero numpy array with correct dimensions
    fid = open(infile,'r') 

    #Process data for plotting
    for n in np.arange(0,tdim):    #Loop through time steps in data
        xin1 = np.fromfile(fid, np.float32, count=xydim) #t_surf
        print "tdim = "+str(n)
        print xin1.mean()
        xin2 = np.fromfile(fid, np.float32, count=xydim) #t_atmos
        xin3 = np.fromfile(fid, np.float32, count=xydim) #t_ocean
        xin4 = np.fromfile(fid, np.float32, count=xydim) #vapour 
        xin5 = np.fromfile(fid, np.float32, count=xydim) #albedo

        
        # Populate array with data from the chosen variable
        if variable == 't_surf':
            xin = xin1 
            long_name = 'surface temperature'
            standard_name = 'surface_temperature'
            unit = iris.unit.Unit('K')
        elif variable == 't_atmos':
            xin = xin2
            long_name = 'atmosphere temperature'
            standard_name = 'air_temperature'
            unit = iris.unit.Unit('K')
        elif variable == 't_ocean':
            xin = xin3
            long_name = 'ocean temperature'
            standard_name = 'sea_surface_temperature'
            unit = iris.unit.Unit('K')
        elif variable == 'vapour':
            xin = xin4
            long_name = 'water vapour'
            standard_name = 'specific_humidity'
            unit = iris.unit.Unit('kg kg-1')
        elif variable == 'albedo':
            xin = xin5                      
            long_name = 'surface temperature'
            standard_name = 'surface_albedo'
            unit = iris.unit.Unit('1')
        print xin.shape
        print xin.mean()
        for i in np.arange(0,ydim):
            field[:,i,n] = xin[(xdim*(i)):((i+1)*xdim)]  
    #Function to flip and rotate data

    field = np.rot90(field)
    field = np.flipud(field) 
    newcube = iris.cube.Cube(field, long_name=long_name)

    lons = (np.arange(1.875,360,3.75)) # Define longitudes
    lats = (np.arange(-88.125,90,3.75)) #Define latitutdes
    time_coord = iris.coords.DimCoord(np.arange(0,tdim*30,30), standard_name='time', units=iris.unit.Unit('days since 1940-01-15 00:00:0.0', calendar='360_day'))

    newcube.add_dim_coord(iris.coords.DimCoord(lats, 'latitude', units='degrees'), 0)
    newcube.add_dim_coord(iris.coords.DimCoord(lons, 'longitude', units='degrees'), 1)
    newcube.add_dim_coord(time_coord, 2)
    newcube.standard_name = standard_name
    newcube.units = unit
    newcube.attributes = iris._cube_coord_common.LimitedAttributeDict({'source':'Data from GREB model'})
        
    fid.close()

    iris.save(newcube,'./ncfiles/'+variable+'.'+scenario_name+'.nc')
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

var_list = ['t_surf', 't_atmos', 't_ocean', 'vapour', 'albedo']
cube_list = iris.cube.CubeList()

#Dimensions
xdim  = 96
ydim  = 48
dx    = 3.75
tstep = 4 #timesteps per day
xydim = xdim*ydim

#Variables 
scenario_name = 'exp5' #'a1b'
file_name = scenario_name+'.bin' #File name of data to plot
file_size = os.stat(file_name).st_size
years = file_size/(xdim*ydim*len(var_list)*tstep*12)
# years = 50 # must match data from GREB model. Choose the number of years that the GREB model is set to run for
# climate_variable = albedo # Choose climate variable to plot

greb_data, newcube = read_data(years, file_name, 't_surf', scenario_name=scenario_name) # read data
#read and plot data
for i in var_list:
    greb_data, newcube = read_data(years, file_name, i, scenario_name=scenario_name) # read data
    cube_list.append(newcube)




