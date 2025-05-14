import pytest
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning
import os
import xarray as xr
import numpy as np
import tempfile
from function_writegroupnumber import write_groupnumber  # Replace 'your_module' with the actual module name

# Create a temporary nc file with random group IDs
@pytest.fixture
def mock_netcdf_file():
    # Create a mock NetCDF dataset
    particles = 10
    group_ids = np.random.randint(1, 5, size=particles)  # Random group IDs
    ds = xr.Dataset(
        {"group_id": (("particles"), group_ids)},
        coords={"particles": np.arange(particles)}
    )
    
    # Save to a temporary NetCDF file
    temp_file = tempfile.NamedTemporaryFile(suffix=".nc", delete=False)
    ds.to_netcdf(temp_file.name)
    temp_file.close()
    return temp_file.name

# Create a temporary output directory to save outputfiles
@pytest.fixture
def temp_output_dir():
    # Create a temporary directory for output files
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

# Test the function to write group numbers to the generated NetCDF files 
def test_write_groupnumber(mock_netcdf_file, temp_output_dir):
    # Call the function to update the NetCDF file
    write_groupnumber([mock_netcdf_file], temp_output_dir)
    
    # Check the output file
    output_file = os.path.join(temp_output_dir, f"updated_{os.path.basename(mock_netcdf_file)}")
    assert os.path.exists(output_file), "Output file was not created."
    
    # Open the updated NetCDF file and verify contents
    updated_ds = xr.open_dataset(output_file)
    assert "group_number" in updated_ds.variables, "group_number column is missing in the output file."
    
    # Print group_id and group_number
    group_ids = updated_ds['group_id'].values
    group_numbers = updated_ds['group_number'].values
    for gid, gnum in zip(group_ids, group_numbers):
        print(f"group_id: {gid}, group_number: {gnum}")
    
    # Validate group_number values
    expected_group_numbers = [f"{int(gid):02}{int(gid):02}" for gid in group_ids]
    assert np.array_equal(group_numbers, expected_group_numbers), "Group numbers do not match group_idgroup_id format."

    # Keep the generated file for inspection
    final_output_path = os.path.join(os.getcwd(), f"updated_{os.path.basename(mock_netcdf_file)}")
    os.rename(output_file, final_output_path)
    print(f"Updated NetCDF file kept at: {final_output_path}")
