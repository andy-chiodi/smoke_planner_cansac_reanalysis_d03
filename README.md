# smoke_planner_WRF-4km-PNW

Collection of Python and PyFerret scripts that process archived 4km PNW WRF output (gzipped, hourly, netcdf files with multiple variables and all x-y grid points
in a single file) into uncompressed netcdf files that contain all hours at a single x-y grid point.

## Preliminary notes

-The WRF archive in this case underwent a domain change in October 2011.  Files with the grid listed in the file name, for example 
the PyFerret script `main346x265.jnl` is meant for the original, pre 18 October 2011 grid.  Files without the horizontal grid listed are meant for the 18 October 2011 - 2020 period.

-Typically, these scripts are executed in Python from a command line, wherein the PyFerret scripts are executed as a pseudo-python module.  For example: typing the following in a command line `python wrf.py daylist hourlist main` will run the script `main.jnl` over each day and hour listed in the daylist and hourlst files (see next step for more information)

-Some of these scripts are coded to read in data from a given directory and save files to another given directory.  The lines of code specifiying these directories will need to be changed to suit the local environment

## Step 1. Process the archived WRF model output data
Prerequesites

- The wrf output data files
- Python script `wrf.py`.  example linux command line usage `python wrf.py days.txt hours.txt PyFerret_Script.jnl`
  here, *PyFerret_Script.py* could be any of the top level scripts, such as main.jnl, uv.jnl, pbl.jnl
  `wrf.py` loops though the lists of days and hours in the *days.txt* and *hours.txt* files (see below) and runs
  the PyFerret script it is given (e.g. main.jnl) for each listed hour (f12-f35 for a continuous record) of each listed day
  
- Pyferret scripts:
  - `main.jnl` [`main346x265.jnl`]   loads an uncompressed WRF data file, calls recipe.jnl & vi.jnl, then saves out variables, as listed in `main.jnl`
  - `uv.jnl` [`uv345x265.jnl`]       same as *main.jnl* except sprecifically for 10m winds rotated from Lambert Conformal to earth coordinates
  - 'uv_tw.jnl [`uv345x264.jnl`]     save as above, except for transport winds rotated from Lambert Conformal to earth coordinates
  - `pbl.jnl` [`pbl345x264.jnl`]     same as above, except specifically for (scalar) planetary boundary layer height (a variable added after main.jnl was written)   
  - `recipe.jnl` defines variables necessary for fire-weather (e.g. relative humidity, virtual potential temperature) based on saved-out WRF variables
  - `vi.jnl` [`vi_346x265.jnl`] calculates mixing height, transport wind and ventilation index based on variables provided by WRF or defined by `recipe.jnl`
  - `tc.jnl` a script needed to asign a datetime to each hour of processed data (enables time aggregation in a later step)

Verson 2.0 of main and vi, e.g. `main_2.0.jnl` and `vi_2.0.jnl` include all variables supported as of 10 June 2021. These are: mixing height (mh), transport wind speed (tw), tranport wind vector components rotated to earth coordinates (utwe,vtwe) ventilation index (vi), planetary boundary height (pbl), 10 m wind speed (w10), 10 m wind vector (u10e, v10e), 10 m wind direction (wdir10), 2m temperature (temp2), 2m rh (rh2), 500 mb geopotential height (z500) 

Other files:
  - *list_of_hours*  Text file with the names of the forecast hours you want to process on separate lines, such as
```
f12
f13
f14
``` 
an example file *hours.list* is provided in this repository

  - *list_of_days*  Text file with dates you want to process on each line, for example
```

2010010100
2010010200
2010010300
```
an example file *wrf_2018_days.list* is provided in this repository

  - alpha.nc and alpha345x264.nc are netcdf files needed to rotate the WRF wind vectors to an earth-relative perspective

## Step 2. `[if working with earlier 345x264 data]` Regrid the 17 Oct 2011, and before, files to the 18 Oct 2011, and after, grid

See files and README.md in `regrid` directory

## Step 3. Aggregate the hourly files to months

See files and README.md in `aggregate` directory

## Step 4. Reshape the WRF data into individual netcdf files with all times at a single lat-lon (X-Y) point.

See files and README.md in `reshape` directory

## Step 5. Calculate daily statistics and store results in daily netcdf files

See files and README.nc in `todaily` directory

## Step 6. Create JSON files and upload them to aws bucket

See files and README.nc in `json` directory
