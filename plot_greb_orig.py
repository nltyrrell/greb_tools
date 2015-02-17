#!/bin/csh 
#
# author: Nicholas Loveday
#This script contains functions for creating plots for the GREB model
#import packages
import numpy as np
import matplotlib
from mpl_toolkits.basemap import Basemap, addcyclic, cm
import matplotlib.pyplot as plt


#########################################################################################
#Function to read data from GREB 
def read_data(years, file, variable, time_length): 
    xdim  = 96              # x dimensions                  
    ydim  = 48              # y dimensions
    dx    = 3.75            # model resolution
    xydim = xdim*ydim
    tdim  = 12*years        #Total time steps in the data
    
    t_surf = 'surface temperature'
    t_atmos = 'temperature of atmosphere'
    t_ocean = 'temperature of ocean'
    vapour = 'water vapour'
    ice = 'ice'

    
    field = np.zeros((xdim,ydim,tdim)) # Create a zero numpy array with correct dimensions
    fid = open(file,'r') 

    #Process data for plotting
    for n in np.arange(0,tdim):    #Loop through time steps in data
        xin1 = np.fromfile(fid, np.float32, count=xydim) #t_surf
        xin2 = np.fromfile(fid, np.float32, count=xydim) #t_atmos
        xin3 = np.fromfile(fid, np.float32, count=xydim) #t_ocean
        xin4 = np.fromfile(fid, np.float32, count=xydim) #vapour 
        xin5 = np.fromfile(fid, np.float32, count=xydim) #ice

        
        # Populate array with data from the chosen variable
        if variable == t_surf:
            xin = xin1 
        elif variable == t_atmos:
            xin = xin2
        elif variable == t_ocean:
            xin = xin3
        elif variable == vapour:
            xin = xin4
        elif variable == ice:
            xin = xin5                      
        for i in np.arange(0,ydim):
            field[:,i,n] = xin[(xdim*(i)):((i+1)*xdim)]  
 
    
    #Now calculate appropriate climatology depending on time chosen
    if time_length == 'annual': #Calulate yearly average    
        img = np.zeros((xdim, ydim))
        for i in np.arange(1,13):
            img += np.squeeze(field[:,:,(tdim - i)])
        img = np.divide(img,12)   
        
        
    elif time_length == 'DJF': # DJF climatology
        djf_index = [1, 12, 11]
        img = np.zeros((xdim, ydim))
        for i in djf_index:
            img += np.squeeze(field[:,:,(tdim - i)])
        img = np.divide(img,3)
    elif time_length == 'MAM': # MAM climatology
        mam_index = [10, 9, 8]
        img = np.zeros((xdim, ydim))
        for i in mam_index:
            img += np.squeeze(field[:,:,(tdim-i)])
        img = np.divide(img,3)  
    elif time_length == 'JJA': # DJF climatology
        jja_index = [7, 6, 5]
        img = np.zeros((xdim, ydim))
        for i in jja_index:
            img += np.squeeze(field[:,:,(tdim-i)])
        img = np.divide(img,3)       
    elif time_length == 'SON': # DJF climatology
        son_index = [4, 3, 2]
        img = np.zeros((xdim, ydim))
        for i in son_index:
            img += np.squeeze(field[:,:,(tdim-i)])
        img = np.divide(img,3)   
        
    elif time_length == 'January': #Calulate monthly average 
        img = np.squeeze(field[:,:,(tdim - 12)])
    elif time_length == 'February': #Calulate monthly average 
        img = np.squeeze(field[:,:,(tdim - 11)])
    elif time_length == 'March': #Calulate monthly average    
        img = np.squeeze(field[:,:,(tdim - 10)])
    elif time_length == 'April': #Calulate monthly average 
        img = np.squeeze(field[:,:,(tdim - 9)])            
    elif time_length == 'May': #Calulate monthly average 
        img = np.squeeze(field[:,:,(tdim - 8)])
    elif time_length == 'June': #Calulate monthly average   
        img = np.squeeze(field[:,:,(tdim - 7)])
    elif time_length == 'July': #Calulate monthly average   
        img = np.squeeze(field[:,:,(tdim - 6)])
    elif time_length == 'August': #Calulate monthly average 
        img = np.squeeze(field[:,:,(tdim - 5)])
    elif time_length == 'September': #Calulate monthly average 
        img = np.squeeze(field[:,:,(tdim - 4)])          
    elif time_length == 'October': #Calulate monthly average 
        img = np.squeeze(field[:,:,(tdim - 3)]) 
    elif time_length == 'November': #Calulate monthly average 
        img = np.squeeze(field[:,:,(tdim - 2)]) 
    elif time_length == 'December': #Calulate monthly average    
        img = np.squeeze(field[:,:,(tdim - 1)])             
    else:
        print 'WARNING: invalid time scale selected'  
        import sys
        sys.exit()             
    fid.close()
    return (img) 

##########################################################################################
#Function to flip and rotate data
def flip_data(my_img): 
    img = np.rot90(my_img)
    img = np.flipud(img) 
    return img         
    
##########################################################################################
def plotfig(img, colour_map, levels, map_projection = 'ECP', parallelson = True, returnCB = True, contourplt = True): #Creates plot
    lons = (np.arange(1.875,360,3.75)) # Define longitudes
    lats = (np.arange(-88.125,90,3.75)) #Define latitutdes
    lons, lats = np.meshgrid(lons,lats)
    ll_lon=lons[0][0]		#Define the boundaries of the map ll(lower left)lat/lon
    ll_lat=lats[0][0]		
    ur_lon=lons[-1][-1]		#and ur(upper right)lat/lon
    ur_lat=lats[-1][-1]
    matplotlib.rcParams.update({'font.size': 30}) #Sets font size for everything in plots to size 22
    
    fig = plt.figure(num=None, figsize=(16,10), facecolor='w', edgecolor='k')
    ax = fig.add_axes([0.05,0.05,0.9,0.9])
    if map_projection == 'ECP': #Choose map projection
        m = Basemap(projection='cyl',resolution='c',llcrnrlon=ll_lon,llcrnrlat=ll_lat,urcrnrlon=ur_lon,urcrnrlat=ur_lat)
    elif map_projection == 'robin':
        m = Basemap(projection='robin',lon_0=0,resolution='c')
    else:
        print 'INVALID MAP PROJECTION'
        import sys
        sys.exit()
            
    m.drawcoastlines()
    
    if parallelson == True: #If true create parallel and meridian lines
        parallels = np.arange(-90,90,30.)
        meridians = np.arange(0.,360.,30.)
        m.drawparallels(parallels,labels=[1,0,0,0],fontsize=20)
        m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=20)
   
    if contourplt == True:
        im1 = m.contourf(lons,lats,img,levels,latlon=True,cmap=colour_map, extend='both') #create contourf plot
    else:
        im1 = m.pcolormesh(lons,lats,img,shading='gouraud',latlon=True,cmap=colour_map, vmin=levels[0], vmax=levels[-1])
 
    
    if returnCB == True:
        cb = m.colorbar(im1, "bottom", size="5%", pad="8%")
    else:
        cb = 0

    return (im1, cb)         
    
#########################################################################################
#End of defined funcs   
#########################################################################################
#Sample plotting script begins
##########################################################################################
#Parameters
t_surf = 'surface temperature'
t_atmos = 'temperature of atmosphere'
t_ocean = 'temperature of ocean'
vapour = 'water vapour'
ice = 'ice'    

#Dimensions
xdim  = 96
ydim  = 48
dx    = 3.75
tdim=730
xydim = xdim*ydim

#Variables 
time_length = 'annual' # Choose out of 'annual', 'DJF', 'MAM', 'JJA', 'SON' and months
years = 20 # must match data from GREB model. Choose the number of years that the GREB model is set to run for
climate_variable = t_surf # Choose climate variable to plot
contour_levels = np.arange(-3,3.25,0.25)
file_name = 'response.bin' #File name of data to plot

#read and plot data
greb_data = read_data(years, file_name, climate_variable, time_length) # read data
greb_data = flip_data(greb_data) #Flip data for plotting
im, cb = plotfig(greb_data ,plt.cm.coolwarm, contour_levels)

plt.savefig('test_image.png', bbox_inches='tight')
