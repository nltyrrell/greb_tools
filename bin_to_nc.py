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
def read_data(infile, xdim, ydim, n_tsteps): 
    
    xydim = xdim * ydim
    field = np.zeros((xdim,ydim,n_tsteps)) # Create a zero numpy array with correct dimensions
    fid = open(infile,'r') 
    print infile

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

#     iris.save(newcube,'./ncfiles/'+infile+'.nc')
    return field, newcube

    
def bin2iris(infile):
    """
    Reads the binary infile, outputs an Iris cube
    Input: 
    infile - string of binary file to be read
    Output: 
    iris cube of bin file
    """
    #Dimensions
    xdim  = 96
    ydim  = 48
    dx    = 3.75
    ireal = 4

    file_size = os.stat(infile).st_size
    n_tsteps = file_size/(xdim*ydim*ireal)
    field, newcube = read_data(infile, xdim, ydim, n_tsteps)
    return newcube




