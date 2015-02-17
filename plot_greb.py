import numpy as np
import matplotlib.pyplot as plt
import iris
import iris.plot as iplt
import iris.quickplot as qplt
import os

# author: Nicholas Loveday
# modified by Nicholas Tyrrell Feb 2015 to use Iris
#This script contains functions for creating plots for the GREB model

def bounds(cube):
    cube.coord('latitude').guess_bounds()
    cube.coord('longitude').guess_bounds()
    return 

    

var_list = ['t_surf', 't_atmos', 't_ocean', 'vapour', 'albedo']

tsurf_clim = iris.load_cube('./ncfiles/t_surf.clim.nc')
tsurf_a1b = iris.load_cube('./ncfiles/t_surf.a1b.nc')
bounds(tsurf_clim)
bounds(tsurf_a1b)

tsurf_clim_mean = tsurf_clim.collapsed('time',iris.analysis.MEAN)
grid_areas = iris.analysis.cartography.area_weights(tsurf_clim)
tsurf_clim_amean = tsurf_clim.collapsed(['latitude', 'longitude'],
                           iris.analysis.MEAN,
                           weights=grid_areas)

tsurf_a1b_mean = tsurf_a1b.collapsed('time',iris.analysis.MEAN)
grid_areas = iris.analysis.cartography.area_weights(tsurf_a1b)
tsurf_a1b_amean = tsurf_a1b.collapsed(['latitude', 'longitude'],
                           iris.analysis.MEAN,
                           weights=grid_areas)

#Dimensions
xdim  = 96
ydim  = 48
dx    = 3.75
tstep = 4 #timesteps per day
xydim = xdim*ydim





