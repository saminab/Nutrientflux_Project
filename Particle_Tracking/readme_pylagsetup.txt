# pylag reqirements:
step 1: NetCDf file
*All input files must cotain a time variables with a units attributes that allows time converted to datetime objects
* time in my data is float like "19322.041" and in pylag input is based on  "yy-m-d:s:ms" like this 2016-01-16T00:00:00.000000000
Also files should contain grid information like depth, lat, lon arrays

step 2: A grid metrics file 
command to make grid file 
pylag.grid_metrics.create_fvcom_grid_metrics_file(fvcome_file_name, obc_file_name, grid_metric_file_name)
obc_file_name : To distinguish between open adn land boundry nodes, a list of open boundry nodes can be specified using the opec_file

step 3: An initial position files
the initial position must have the following format
n: total number of particles
group_id x1 x2 x3
group id is an integer number thst can be used to group particles 
- x1 is the particle's first position coordinate. in cartesian coordinate sysytem, this should be x in meters
- x2 particle's second position coordinate. in cartesian coordinate system this should be y in meters
- x3 the particles third position and it's always depth , z in meters
step 4: A run configuration file 
this file has some details about the data directories. Also pylag computes a set of interpolation weigths which we set in this file


# FVCOME data 
- file name order: MMDDHH_0001.nc where MM,DD,HH, indicate the Month, Day, and Hour, respectively, of the run time.
 - for forecasts, MDH indicates the time of initialization (i.e. forecast hour 0)
 - since nowcasts simulate the preceeding 12 hours, MDH in the filename indicates the LAST valid hour
 
 KML Files: 
 =============
 - nodes.kml indicate spatial points which represent the FVCOME nodes in the model (variables represented on nodes)
 - elems.kml spatial polygones represent the FVCOME elements in the model (vector variables are stored on elements)
 
### 