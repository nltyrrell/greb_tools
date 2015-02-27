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

def write_v_anom():
    """
    Reads in netcdf files of meridional wind and anomalous winds
    add anomalies to input files
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
    mer_wind.transpose([2,0,1])

    #regrid v anom
    anom_v = anom_v.regrid(mer_wind[0,::],iris.analysis.Linear())

    new_merwind = mer_wind.copy()
    new_merwind.data = anom_v.data + mer_wind.data

    new_merwind.transpose([1,2,0])

    print 'Writing meridional.wind.v_anom.bin and meridional.wind.v_anom.nc and anomalous wind loaded'
    iris.save(new_merwind,'./ncfiles/meridional.wind.v_anom.pos.nc')
    writebin(new_merwind,'./input_files/meridional.wind.v_anom.pos.bin')



