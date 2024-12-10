import pytest
import os
import glob
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr

# Function to load the FVCOM outputs data get group_id column 
# count the number of particles in each group_id and the add a new column to the netcdf file called group_number 
# and writes the number of particles in each group_id to the group_number column

def write_groupnumber(files, data_dir):
    """
    Updates each NetCDF file by adding a group_number column based on group_id.
    The updated NetCDF files are saved with a new filename prefix in the specified directory.

    Parameters:
    - files (list of str): List of paths to NetCDF files to be processed.
    - data_dir (str): Directory where the updated NetCDF files will be saved.
    """
    for file in files:
        # Read the NetCDF file
        ds = xr.open_dataset(file)

        # Convert the NetCDF 'group_id' variable to a DataFrame for processing
        netcdf_df = ds['group_id'].to_dataframe().reset_index()

        # Create the `group_number` by concatenating `group_id` with itself as a string
        netcdf_df['group_number'] = netcdf_df['group_id'].apply(lambda x: f"{int(x):02}{int(x):02}")

        # Add the updated group_number column back into the NetCDF dataset
        ds['group_number'] = (('particles'), netcdf_df['group_number'].values)

        # Save the updated NetCDF file
        output_file_path = os.path.join(data_dir, f"updated_{os.path.basename(file)}")
        ds.to_netcdf(output_file_path)

        print(f"Updated NetCDF file saved: {output_file_path}")
