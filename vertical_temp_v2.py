# Python script to load CMIP6 models which have a given variable and concatenate time
# Extra functionality is to regrid to a common grid. Apply a mask.
# Output is a single file for the requested variable/experiment over trequested time.
# Written by Dann Mitchell, 29/10/2019
# Tested on JASMIN

# NOTES and known problems
# It only ever looks at the latest version of the model data
# At the moment all the forcing index or physics index are used in the ripf system
# Only works for monthly data to start with
# Some models have missing data, so their mask might be different from others
# If requested end year is after 2014 (i.e. end of historical), then script only works with first ensemble member

# Updates
# 11/11/2019 Updated to include 3D and 4D data. DMM
# 11/11/2019 Updated to tag on RCP8.5-SSP2 data if time requested if beyond 2014 (end of historical). DMM
# 11/11/2019 Updated to fix a bug with the globalmean diagnostic and masks. DMM

# Begin script ========================================================================================================

# Import relevant modules
import matplotlib.pyplot as plt
from netCDF4 import Dataset as ncfile
import netCDF4
import numpy as np
import numpy.ma as ma
import glob
from mpl_toolkits import basemap
from os import path 

# ========================================= Identify variables and experimanets=========================================
# Users should only edit this section ==================================================================================

experiment = 'historical' # Could also be piControl etc
members = 'first' # Either select 'all' or 'first'
model_name = 'CanESM5' #Either write a model name, or write 'all'
variable = 'ta'
project = 'CMIP' # only change this if you want to look at non-DECK or ScenarioMIP experiments, e.g. DAMIP, HighResMIP etc

syear = 1979 # select data only after this year (and including it)
eyear = 2017 # ditto end year. If this year is after 2014 then RCP4.5-SSP2 data will be stitched on.

# If you are not sure about interpolation and masking, set these both to False =========================================
inter = True # Set to True for interpolating to a common grid, or False to keep to the native grid. The must supply lats/lons if True.
mask = True # Set to True to mask data, or False to include all data. You must supply the mask below

vtype = 'Amon'
gtype = '*' # this could be gn or gr, this is the grid type (gn = native, gr = regridded)

# Path for data
path_input = '/badc/cmip6/data/CMIP6/'+project+'/' # Path to read in input files
data_path = '/home/users/dmitchell/Radiosonde/Data/Models/' # Path to write out final product

# If the file already exists, should it be overwritten?
overw = True

# Specifics if you interpolate on to a grid. Note that this is set up for radio sonde data, but you will have to change to your require obs

if (inter == True):
    path_obs = './Data/Obs/'
    nc = ncfile(path_obs + 'raobcore15_gridded_2017.nc')
    data_rao2 = nc.variables['anomalies'][:,:,::-1,:] # reverse direction of lats
    data_rao = np.ma.zeros((data_rao2.shape))
    data_rao[:,:,:,0:18] = data_rao2[:,:,:,18:] # Shift lon data to be consistent with model
    data_rao[:,:,:,18:] = data_rao2[:,:,:,:18] # Shift lon data to be consistent with model
    lat_obs = nc.variables['lat'][::-1] # Reverse lat values so they are asscending, for interp 
    lon_obs = nc.variables['lon'][:] + 180  # Shift lon data to be consistent with model
    p_obs = nc.variables['pressure'][:]

# Specify a mask if one is used

if (mask == True):
    mask_vals = np.ma.getmask(data_rao)

# ========================================= Main body of code ==========================================
# Do not alter anything below this line unless you really hve to========================================

def calc_globalmean(data,lat,maskit):
    # Assume data has shape time,lat,lon
    nt,nlat,nlon = data.shape
    # Initialise output array
    data_globalmean = np.zeros([nt])
    # calculate weights (convert degrees to radians)
    weight1D = np.cos(lat/180.*np.pi)
    # repeat the 1D array across all longitudes
    
    weight2D = np.repeat(weight1D[:,np.newaxis],nlon,axis=1)
    #weight2D[data == np.nan] = 0
    # the data array is a masked array, so we need to set the same mask for the weights as the data


    if (maskit == False): weighting = weight2D
    # the sum of weights is needed for the weighted average
    if (maskit == False): weightsum = weighting.sum()

    # Loop over times and calculated the global average
    for t in range(nt):
        if (maskit == True): weighting = np.ma.masked_where(data.mask[t,:],weight2D)
    # the sum of weights is needed for the weighted average
        if (maskit == True): weightsum = weighting.sum()
        data_globalmean[t] = np.nansum((data[t,:]*weighting))/weightsum
        # Return the calculated data
    return data_globalmean

print('Identify number of models with the '+experiment+' experiment and ' + variable + ' data')

# List number of models on server

if (model_name == 'all'): model_name = '*'

models = glob.glob(path_input+'*/'+model_name+'/'+experiment)
if (members == 'all'): ems = glob.glob(path_input+'*/'+model_name+'/'+experiment+'/r*i1p*f*/'+vtype+'/'+variable+'/'+gtype+'/files/')
if (members == 'first'): ems = glob.glob(path_input+'*/'+model_name+'/'+experiment+'/r1i1p1f*/'+vtype+'/'+variable+'/'+gtype+'/files/')

print('There are ' + str(len(models)) + ' models with the required data, and '+str(len(ems)) + ' ensemble members in total') 

if (eyear > 2014): 
    print('The end year exceeds the Historical simulations, tagging on SSP2-RCP4.5 data')
    project2 = 'ScenarioMIP'
    experiment2 = 'ssp245'
    path_input2 = '/badc/cmip6/data/CMIP6/'+project2+'/' # Path to read in input files for extension runs

    if (members == 'all'): ems_add = glob.glob(path_input2+'*/'+model_name+'/'+experiment2+'/r*i1p*f*/'+vtype+'/'+variable+'/'+gtype+'/files/')
    if (members == 'first'): ems_add = glob.glob(path_input2+'*/'+model_name+'/'+experiment2+'/r1i1p1f*/'+vtype+'/'+variable+'/'+gtype+'/files/')

    # Just take the latest version of the ensemble member
    models_v2 = []

    for count in np.arange(len(ems_add)): 
        models_v2.append(glob.glob(ems_add[count]+'*')[-1]) # The -1 selects the last one in the list, corresponding to the latest version


# Just take the latest version of the ensemble member
models_v1 = []

for count in np.arange(len(ems)): 
                     models_v1.append(glob.glob(ems[count]+'*')[-1]) # The -1 selects the last one in the list, corresponding to the latest version

for count in np.arange(len(ems)): # Loop over the ensemble members and models

    module_list = glob.glob(models_v1[count]+'/*')# for each model ensemble member, store all the data files
    if (eyear > 2014): 
        module_list.append(glob.glob(models_v2[count]+'/*')[0])

    local_store = []
    counter = 0
    for count2 in np.arange(len(module_list)): # Select relevant years of the models and ensemble member
        file_s = float(module_list[count2][-16:-12])
        file_e = float(module_list[count2][-9:-5])
        
        if (syear <= file_s <= eyear) or (syear <= file_e <= eyear): # Selects only files in the relevant range 
           
            local_store.append(module_list[count2])
            if (counter == 0): 
                ffile_s = file_s # The start year of the first file in the ensemble member
                date_diff = int((syear - ffile_s)*12) # number of months that Jan 1979 is from beginning
                
                counter = counter+1
    
    if (len(local_store) > 20): # This is a fudge to stop memory issues
        print('File size to big for '+local_store[0])
        continue

    # Need to add a section here to include RCP data in the local_store

    if (len(local_store) > 1):
        try:
            nc = netCDF4.MFDataset(local_store) # this concatenates relevant data for single ensemble member if more than 1 file exists
            # Infortunetely it only seems to work with NetCDF3* and NetCDF4_classic. Some CMIP6 models use NetCDF4
        except:
            print('NetCDF file is not right')
            continue
    else:
        nc = ncfile(local_store[0])

    if (count == 0): # Just do this once to get the dimensionality of the variable array

        data2 = nc.variables[variable][:]
        no_dims = len(np.shape(data2))
    # Load variable of interest, plus dimensions
    
    requested_months = (eyear - syear + 1)*12 #how many months span requested time period
    
    if (no_dims == 4): data2 = nc.variables[variable][date_diff:date_diff+requested_months,:,:,:]
    if (no_dims == 3): data2 = nc.variables[variable][date_diff:date_diff+requested_months:,:,:]
    ma.set_fill_value(data2, np.nan) # Change any masked values to NaN to help with better interpolation (later)
    lat = nc.variables['lat'][:]
    lon = nc.variables['lon'][:]
    if (no_dims == 4):
        p_mod = nc.variables['plev'][:]
        p_units = str(nc.variables['plev'].units)

    # Load relevant metadata
    model_name = str(nc.source_id)
    ensemble_name = str(nc.variant_label)
    expid = str(nc.parent_source_id)
    grid_label = str(nc.grid_label)
    variant_label = str(nc.variant_label)

    # Create name of output file, and check if it has already been created
    if (inter == False): out_name = data_path + variable + '_' + vtype + '_' + expid +'_'+experiment+'_'+variant_label+'_'+grid_label+'_'+str(syear)+'01-'+str(eyear)+'12.nc'
    if (inter == True): out_name = data_path + variable + '_' + vtype + '_' + expid +  '_'+experiment+'_'+variant_label+'_common_grid_'+str(syear)+'01-'+str(eyear)+'12.nc'

    if (path.isfile(out_name) == True): 
        if (overw == True): print('This file already exists, overwriting')
        if (overw == False): 
            print('This file already exists, skipping')
            continue

    print(model_name)
    print(ensemble_name)

    # Check the time slice is the correct length, if not, throw up an error
    actual_months = np.shape(data2)[0]
    if (requested_months != actual_months):
        print('Not all months are available')


    # Interpolate to a common grid
    if (inter == True):
        data_interp = np.ma.zeros((len(data2[:,0,0,0]),len(data2[0,:,0,0]),len(lat_obs),len(lon_obs))) #ensure this is masked array
        int_order = 1# bilieaner 

        lon_mesh,lat_mesh = np.meshgrid(lon_obs,lat_obs)

        for loop_time in np.arange(len(data2[:,0,0,0])):
            for loop_p in np.arange(len(data2[0,:,0,0])):
                step_data = basemap.interp(data2[loop_time,loop_p,:,:], lon, lat, lon_mesh, lat_mesh, order=int_order,masked=True)
                data_interp[loop_time,loop_p,:,:] = step_data

        # If the data is 3D then select relevant p levels
        if (p_units == 'Pa'): p_mod = p_mod/100.

        p_locations = []
        for loop_pvals in np.arange(len(p_obs)):
            loc = np.where(p_mod == p_obs[loop_pvals])[0]
            p_locations.append(loc[0])

        data_final = data_interp[:,p_locations,:,:]
        data_final2 = data_interp[:,p_locations,:,:]

    # If interpolation was not required, rename the variable to be consistent with interpolate case
    if (inter == False): data_final = data2

    # If a mask if requested, add it to array, this only works if inter == True as well.
    if (mask == True):
        years = np.repeat(np.arange(1416/12.) + 2017 - 1416/12. + 1,12) # Defines the years in obs array

        # Isolate time of interest

        time_selected = np.array(np.where((years >= syear) & (years <=eyear)))[0,:]
        mask_time = mask_vals[time_selected,:,:,:] # Isolate mask from only these years        
        
        data_final = np.ma.masked_where(mask_time, data_final)

    # Identify bad data
    #data_final = np.ma.masked_where(data_final < 10, data_final)

    # Output data 

    # Create a consistent file name

    nc = ncfile(out_name, 'w')

    nc.history = 'Modifed CMIP6 data'
    
    time_dim = nc.createDimension("time", None)
    if (no_dims == 4): 
        p_dim = nc.createDimension("p", len(data_final[0,:,0,0]))
        lat_dim = nc.createDimension("lat", len(data_final[0,0,:,0]))
        lon_dim = nc.createDimension("lon", len(data_final[0,0,0,:]))

        gphnc = nc.createVariable(variable,'f8',('time','p','lat','lon',))
        gphnc2 = nc.createVariable('time','f8',('time',))
        gphnc3 = nc.createVariable('plev','f8',('p',))
        gphnc4 = nc.createVariable('lat','f8',('lat',))
        gphnc5 = nc.createVariable('lon','f8',('lon',))

    if (no_dims == 3): 
        #p_dim = nc.createDimension("p", len(data_final[0,:,0]))
        lat_dim = nc.createDimension("lat", len(data_final[0,:,0]))
        lon_dim = nc.createDimension("lon", len(data_final[0,0,:]))

        gphnc = nc.createVariable(variable,'f8',('time','lat','lon',))
        gphnc2 = nc.createVariable('time','f8',('time',))
        gphnc4 = nc.createVariable('lat','f8',('lat',))
        gphnc5 = nc.createVariable('lon','f8',('lon',))

    gphnc[:] = data_final
    gphnc2[:] = np.arange(np.shape(data_final)[0])
    if ((inter == False) and (no_dims == 4)): gphnc3[:] = p_mod
    if (inter == False): gphnc4[:] = lat
    if (inter == False): gphnc5[:] = lon

    if ((inter == True) and (no_dims == 4)): gphnc3[:] = p_obs
    if (inter == True): gphnc4[:] = lat_obs
    if (inter == True): gphnc5[:] = lon_obs

    nc.close() 


print('There are ' + str(len(models_v1)) + ' ensemble members of the relevant data')
