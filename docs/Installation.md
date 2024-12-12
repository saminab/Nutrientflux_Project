# Installation
For the Indirect Nutrient load we used PyLag, an offline particle tracking model.
Pylag can be installed using conda. You can follow the instroctions to Instal Pylag from the following [Pylag](https://pylag.readthedocs.io/en/latest/install/installation.html#installation-using-conda)

Below is showing the quick way to install Pylag:


    ```
    source /opt/miniconda/miniconda3/bin/activate
    conda update conda
    conda config --prepend channels conda-forge
    conda config --prepend channels JimClark
    conda create -n pylag python=3.11
    conda activate pylag
    conda install -n pylag -c JimClark pylag
    
    ```
## Building the docs 
To build PyLag’s documentation, a number of extra dependencies are required. These are not packaged with PyLag by default in order to keep the base installation slim and easier to manage. If you would like to build the documentation, the extra dependencies can be installed using conda or pip. The following commands use conda to install all the extra dependencies in the conda environment already created:

```
conda install -n pylag sphinx nbsphinx sphinx_rtd_theme sphinxcontrib-napoleon sphinx-copybutton \
              jupyter jupyter_client ipykernel seapy cmocean matplotlib shapely cartopy
```
```
conda install -c JimClark -n pylag PyQT-fit
```
## Side Packages
There are some other packages that need to be installed that are listed as below

```
  - python=3.11
  - matplotlib
  - cartopy
  - xarray
  - pandas
  - netcdf4
  - jupyter
  - pip
  - dask
```