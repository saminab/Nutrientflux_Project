# pylag reqirements 
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


## FVCOME data 
- file name order: MMDDHH_0001.nc where MM,DD,HH, indicate the Month, Day, and Hour, respectively, of the run time.
 - for forecasts, MDH indicates the time of initialization (i.e. forecast hour 0)
 - since nowcasts simulate the preceeding 12 hours, MDH in the filename indicates the LAST valid hour
 
 ## KML Files: 
 =============
 - nodes.kml indicate spatial points which represent the FVCOME nodes in the model (variables represented on nodes)
 - elems.kml spatial polygones represent the FVCOME elements in the model (vector variables are stored on elements)
 
### Samin Abolmaali version of running Particle tracking 7/11/2024 ##################################
######################################## Arc GIS preparation ########################################


# Python preparation
1- to create initial position files I run the 1_Create_Initial_Position_multigroup.ipynb code 
this code is reading the initial_position that we got from arch gis and for each group it makes a release zone 
for each group id
1- ArcGIS steps
path to Gis project: D:\Users\abolmaal\Arcgis\NASAOceanProject\lh_intersection_shoreline_lake.aprx

    1-  I convert the following flow accumulation to polyline: raster to polyline
    - S:\Users\luwen\Projects\Samin_SENSEflux\GLB_Bdry_buff10km_dem_fill_flowaccu_con3000.tfw  
    Converted to :  D:\Users\abolmaal\Arcgis\Nutrientsproject\GLB_Bdry_buff10km_dem_fil_flowacc_con300_raster 
    Copy to the following path D:\Users\abolmaal\Arcgis\NASAOceanProject\GIS_layer


    2- I  add lake Huron shoreline polygon: S:\Data\GIS_Data\Downloaded\Great_Lakes\GLGIS_060906\data\physical\shoreline\lh\70K\lh_shore_NOAA_70k.shp
    
    3 – find the intersection between GLB_Bdry_buff10km_dem_fil_flowacc_con300_raster  and lh_shore_NOAA_70k.shp
    And the name is: D:\Users\abolmaal\Arcgis\Nutrientsproject\Nutrientdelievery_LH_intersec\Nutrientdelievery_LH_intersec.gdb
    
    4- Luwen flow direction file is in the following path
    S:\Projects\Active\GLB_Nutrient_Transport\DEM_rasters
    
    5- reclassify :
    Input: S:\Projects\Active\GLB_Nutrient_Transport\DEM_rasters\GLB_Bdry_buff10km_dem_fill_flowaccu
    Output: D:\Users\abolmaal\Arcgis\Nutrientsproject\Nutrientdelievery_LH_intersec\Nutrientdelievery_LH_intersec.gdb\GLB_Bdry_buff10km_dem_fill_Reclass


    6- Raster to polyline:
    Input : D:\Users\abolmaal\Arcgis\Nutrientsproject\Nutrientdelievery_LH_intersec\Nutrientdelievery_LH_intersec.gdb\GLB_Bdry_buff10km_dem_fill_Reclass
    Output:  D:\Users\abolmaal\Arcgis\Nutrientsproject\Nutrientdelievery_LH_intersec\Nutrientdelievery_LH_intersec.gdb\GLB_Bdry_buff10km_dem_fill_Reclass_polyline
    
    7- Buffer
    input : lh_shore_ESri_100k
    Output: lh_lake_ERI_100K_Buffer500m
    Update 7/15/2024
	I change the buffer distance based on baily paper to 240 m 
    ## Segments buffered by 240m, this buffer distance is used by Baily paper; 
    # so in what segment of the coastline they buffer 240 m based on invasion and data correlation
    
    Ouput is : D:\Users\abolmaal\Arcgis\NASAOceanProject\GIS_layer\lh_shore_ESRI_100k_Buffer240m_NAD1983    
    8- Creating a pour point(where the watershed starts)
        new
        I find the intersection of two polyline with Intersection tool
        Input features:lh_shore_ESRI_100k
        Input features: GLB_Bdry_buff10km_dem_fil_flowacc_con300_raster
        Output feature Class: GLB_Bdry_buff10km_dem_fil_flowacc_con300_raster_lh_shore_ESRI_100k_Intersect
        9- Output type: Point
        
    10- We can use  Data management\Add XY Coordinates
        The output POINT_X and POINT_Y field values are based on the coordinate system of the dataset,
    11- Create watershed
        Input D8 flow direction  GLB_Bdry_buff10km_dem_fill_dir.tif
        Input raster of feature pour point data : GLB_Bdry_buff10km__lh_shore_NOAA_70k_Intersect
        Pour point field :watershed_id
        Output D:\Users\abolmaal\Arcgis\Nutrientsproject\Nutrientdelievery_LH_intersec\Nutrientdelievery_LH_intersec.gdb\ Watersh_GLB_intersectporpoints
        New:
        Input raster feature class:GLB_Bdry_buff10km_dem_fil_flowacc_con300_raster_lh_shore_ESRI_100k_Intersect
        Output: 
    10 - add watershed ID to the points based on their row number:

    1. Open the Attribute Table: Open the attribute table of the feature class that you want to add the row numbers to.
    2. Add a new field:
        • Right-click on the table header and select "Add Field."
        • Choose a name for the new field (e.g., "RowID") and select the type as "Long Integer" or "Text," depending on your preference.
    3. Calculate the field with row numbers:
        • Right-click on the header of the newly created field and select "Field Calculator."
        • In the Field Calculator window, make sure the parser is set to Python.
        • Check the "Show Codeblock" option.
        • In the Pre-Logic Script Code box, enter the following code:
    rec=0
    def autoIncrement():
    global rec
    pStart = 1 #adjust start value, if required
    pInterval = 1 #adjust interval value, if required
    if (rec == 0):
        rec = pStart
    else:
                rec = rec + pInterval
    return rec

    In the calculation box below, enter:
    autoIncrement() 


    I want to add a watershed field to this polygon
        1- I convert the raster "Watersh_GLB_intersectporpoint" to polygon 
        Input : Watersh_GLB_intersectporpoin
        Output: Watersh_GLB_intersectporpoints_polygon
        2- Spatial Join 



2- to run Pylag we run the 2_PT_senseflux_intersectpoint.ipynb code 
this code is reading the FVCOME outputs and create a grid metric file. then, we create a cofigure file base on 
our boundary condition and run Pylag.

3- To Extract the first time particles hit the shoreline I run the 3_Estimate_Nurient_arrival.ipynb  code.
