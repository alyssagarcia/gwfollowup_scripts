#!/usr/bin/env python

################################
## This script is to be used for quickly updating the exposures*.list files
## found in gw_workflow from the DESGW Follow-up pipeline
## run the script in the directory just above gw_workflow
## last updated Oct 15, 2021
################################

import os
import pandas
import psycopg2
import argparse
import subprocess
import numpy as np

parser = argparse.ArgumentParser(description=__doc__, 
                                formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--minexp',type=int, required=True,
                    help='Query for exposures greater than or equal to this')
parser.add_argument('--outfile',type=str, required=True,
                    help='resulting .list file')
parser.add_argument('--maxexp',type=int, 
                    help='Query for exposures less than or equal to this')
parser.add_argument('--propid',type=str, help='prop id for exposures')
args = parser.parse_args()

if args.maxexp:
    if not args.propid:
        query = """
            SELECT id as EXPNUM,
            TO_CHAR(date - '12 hours'::INTERVAL, 'YYYYMMDD') AS NITE,
            EXTRACT(EPOCH FROM date - '1858-11-17T00:00:00Z')/(24*60*60) AS MJD_OBS,
                ra AS RADEG,
                declination AS DECDEG,
                filter AS BAND,
                exptime AS EXPTIME,
                propid AS PROPID,
                flavor AS OBSTYPE,
                qc_teff as TEFF,
                object as OBJECT
            FROM exposure.exposure
            WHERE flavor='object' and exptime>29.999 and RA is not NULL and 
                id>="""+str(args.minexp)+"""and id<="""+str(arg.maxexp)+"""
            ORDER BY id"""
    else:
        query = """
            SELECT id as EXPNUM,
            TO_CHAR(date - '12 hours'::INTERVAL, 'YYYYMMDD') AS NITE,
            EXTRACT(EPOCH FROM date - '1858-11-17T00:00:00Z')/(24*60*60) AS MJD_OBS,
                ra AS RADEG,
                declination AS DECDEG,
                filter AS BAND,
                exptime AS EXPTIME,
                propid AS PROPID,
                flavor AS OBSTYPE,
                qc_teff as TEFF,
                object as OBJECT
            FROM exposure.exposure
            WHERE flavor='object' and exptime>29.999 and RA is not NULL and 
                id>="""+str(args.minexp)+"""and id<="""+str(arg.maxexp)+"""
                and propid ='"""+str(args.propid)+"""'
            ORDER BY id"""
else:
    if not args.propid:
        query = """
            SELECT id as EXPNUM,
            TO_CHAR(date - '12 hours'::INTERVAL, 'YYYYMMDD') AS NITE,
            EXTRACT(EPOCH FROM date - '1858-11-17T00:00:00Z')/(24*60*60) AS MJD_OBS,
                ra AS RADEG,
                declination AS DECDEG,
                filter AS BAND,
                exptime AS EXPTIME,
                propid AS PROPID,
                flavor AS OBSTYPE,
                qc_teff as TEFF,
                object as OBJECT
            FROM exposure.exposure
            WHERE flavor='object' and exptime>29.999 and RA is not NULL and 
                id>="""+str(args.minexp)+"""
            ORDER BY id"""
    else:
        query = """
            SELECT id as EXPNUM,
            TO_CHAR(date - '12 hours'::INTERVAL, 'YYYYMMDD') AS NITE,
            EXTRACT(EPOCH FROM date - '1858-11-17T00:00:00Z')/(24*60*60) AS MJD_OBS,
                ra AS RADEG,
                declination AS DECDEG,
                filter AS BAND,
                exptime AS EXPTIME,
                propid AS PROPID,
                flavor AS OBSTYPE,
                qc_teff as TEFF,
                object as OBJECT
            FROM exposure.exposure
            WHERE flavor='object' and exptime>29.999 and RA is not NULL and 
                id>="""+str(args.minexp)+"""
                and propid ='"""+str(args.propid)+"""'
            ORDER BY id"""



conn =  psycopg2.connect(database='decam_prd',
                           user='decam_reader',
                           host='des61.fnal.gov',
                           port=5443) 
some_exposures = pandas.read_sql(query, conn)
conn.close()

outfile = args.outfile

mystrings=''
mystrings=some_exposures.to_string(index_names=False,index=False,justify="left")
myout=open(outfile,'w')
myout.write(mystrings)
myout.write('\n')
myout.close()

master_exps_list = 'gw_workflow/exposures.list'
expnum_master = np.genfromtxt(master_exps_list, usecols=(0), unpack=True)
new_expnum = np.genfromtxt(outfile, usecols=(0), unpack=True, skip_header=1)
new_expnum_teff = np.genfromtxt(outfile,usecols=(9),unpack=True, skip_header=1)

#add only new exposures to exposures.list
for exp,teff in zip(new_expnum,new_expnum_teff):
    if exp not in expnum_master:
        print int(exp)
        if np.isnan(teff):
            continue
        else:
            os.system("awk '($1 == "+str(int(exp))+") {print $0}' "+str(outfile)+" >> gw_workflow/exposures.list")

#make band specific lists
os.system('''for band in u g r i z Y VR; do awk '($6 == "'$band'")' gw_workflow/exposures.list > gw_workflow/exposures_${band}.list; done''')



