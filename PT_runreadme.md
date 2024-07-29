### Samin Abolmaali version of running Particle tracking 7/11/2024 ##################################
######################################## Arc GIS preparation ########################################


######################################### Python preparation ########################################
1- to create initial position files I run the 1_Create_Initial_Position_multigroup.ipynb code 
this code is reading the initial_position that we got from arch gis and for each group it makes a release zone 
for each group id

2- to run Pylag we run the 2_PT_senseflux_intersectpoint.ipynb code 
this code is reading the FVCOME outputs and create a grid metric file. then, we create a cofigure file base on 
our boundary condition and run Pylag.

3- To Extract the first time particles hit the shoreline I run the 3_Estimate_Nurient_arrival.ipynb  code.
