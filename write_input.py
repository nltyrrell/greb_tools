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

