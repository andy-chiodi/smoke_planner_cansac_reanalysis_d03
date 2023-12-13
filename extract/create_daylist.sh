#!/usr/bin/env bash

# Usage:  ./create_daylist.sh 1980

# Create daylist files for a given year
for run in $(ls -d /fire5/cansac_reanalysis/$1/*); do
  ls -1 ${run} | cut -c12-21 | sort -u | grep "^19" > daylist_$1_${run##*/}.txt 
done

