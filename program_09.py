#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#
"""
Created on Friday 2020-03-20
Author: Ankit Ghanghas

Name of Script: program_09.py

This script perfroms a basic data quality test on the input file and keeps track of how many changes
are made at each step of the programe.

The data quality is done in 4 main steps.
1. Check for no data values and change all no data values (represented by -999.00) intiaially by NaN
2. Check for gross error in the data. The values of precipitaiton>25 and <0 , values of Temperature>35 and Temperature<-25, values of wind speed>10 and <0 are all set to NaN as these conditions are not feasible in the location where the data has been collected.
3. Check for values where minimum temperature is greater than max temperature. In such cases the values are interchanged.
4. Check for if the temperature range is greater than 25. In such cases the values are set to NaN

The corrected data after all the checks is stored as corrected_data.csv in the present working directory
The Track of how many changes have been made is saved as failed_checks_summar.csv (tab seperated file) in present working directory
Finally a plots of Before Correction and After all correction of all the parameters are saved sepetately as precip_plot.png, wind_plot.png, tmax_plot.png and tmin_plot.png in the working directory.

"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def ReadData( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    raw data read from that file in a Pandas DataFrame.  The DataFrame index
    should be the year, month and day of the observation.  DataFrame headers
    should be "Date", "Precip", "Max Temp", "Min Temp", "Wind Speed". Function
    returns the completed DataFrame, and a dictionary designed to contain all 
    missing value counts."""
    
    # define column names
    colNames = ['Date','Precip','Max Temp', 'Min Temp','Wind Speed']

    # open and read the file
    DataDF = pd.read_csv("DataQualityChecking.txt",header=None, names=colNames,  
                         delimiter=r"\s+",parse_dates=[0])
    DataDF = DataDF.set_index('Date')
    
    # define and initialize the missing data dictionary
    ReplacedValuesDF = pd.DataFrame(0, index=["1. No Data"], columns=colNames[1:])
     
    return( DataDF, ReplacedValuesDF )

 
def Check01_RemoveNoDataValues( DataDF, ReplacedValuesDF ):
    """This check replaces the defined No Data value with the NumPy NaN value
    so that further analysis does not use the No Data values.  Function returns
    the modified DataFrame and a count of No Data values replaced."""

    DataDF[DataDF==-999.00]=np.nan # replaces values of -999.00 with NaN
    ReplacedValuesDF.loc['1. No Data',:]=DataDF.isna().sum() # columnwise sum of NaN and is stored in row with index (1. No Data) in ReplacedValuesDF
    return( DataDF, ReplacedValuesDF )
    
def Check02_GrossErrors( DataDF, ReplacedValuesDF ):
    """This function checks for gross errors, values well outside the expected 
    range, and removes them from the dataset.  The function returns modified 
    DataFrames with data the has passed, and counts of data that have not 
    passed the check."""
 
    DataDF.Precip[(DataDF['Precip']>25) | (DataDF['Precip']<0)]=np.nan # for column containing precip, points with Precip >25 and precip<0 are changed to NaN
    DataDF['Wind Speed'][(DataDF['Wind Speed']>10) | (DataDF['Wind Speed']<0)]=np.nan #values in column 'Wind Speed' with values of wind speed>10 and less than 0 changed to NaN
    DataDF['Max Temp'][(DataDF['Max Temp']>35) | (DataDF['Max Temp']<-25)]=np.nan #values in column 'Max Temp' with values of Temp>35 and <-25 changed to NaN
    DataDF['Min Temp'][(DataDF['Min Temp']>35) | (DataDF['Min Temp']<-25)]=np.nan#values in column 'Min Temp' with values of Temp>35 and <-25 changed to NaN
    ReplacedValuesDF.loc['2. Gross Error',:]=DataDF.isna().sum()-ReplacedValuesDF.sum() # columnwise sum of DataDF of NaN values -  number of NaN values already in ReplacedValuesDF counted in previous step, and is stored in row with index (2. Gross Error) in ReplacedValuesDF
    return( DataDF, ReplacedValuesDF )
    
def Check03_TmaxTminSwapped( DataDF, ReplacedValuesDF ):
    """This function checks for days when maximum air temperture is less than
    minimum air temperature, and swaps the values when found.  The function 
    returns modified DataFrames with data that has been fixed, and with counts 
    of how many times the fix has been applied."""
    count= len(DataDF.loc[DataDF['Min Temp']>DataDF['Max Temp']]) # count of points where min temp is greater than max temperature
    DataDF.loc[DataDF['Min Temp']>DataDF['Max Temp'],['Min Temp','Max Temp']]= DataDF.loc[ DataDF['Min Temp']>DataDF['Max Temp'],['Max Temp','Min Temp']].values  # swapping max and min temperature for points where Min Temp > Max temp
    ReplacedValuesDF.loc['3. Swapped',:]=[0,count,count,0] # count of points where min temp is greater then max temp and is store in row with index (3. Swapped) in ReplacedValuesDF
    return( DataDF, ReplacedValuesDF )
    
def Check04_TmaxTminRange( DataDF, ReplacedValuesDF ):
    """This function checks for days when maximum air temperture minus 
    minimum air temperature exceeds a maximum range, and replaces both values 
    with NaNs when found.  The function returns modified DataFrames with data 
    that has been checked, and with counts of how many days of data have been 
    removed through the process."""
    
    count= len(DataDF.loc[(DataDF['Max Temp']-DataDF['Min Temp']>25)]) # counts where range of temp greater than 25
    DataDF.loc[(DataDF['Max Temp']-DataDF['Min Temp']>25),['Min Temp','Max Temp']]=np.nan # points satisfying given condition set to NaN
    ReplacedValuesDF.loc['4. Range', :]=[0,count,count,0]
 
    return( DataDF, ReplacedValuesDF )

if __name__ == '__main__':
    fig_precip, (ax1)=plt.subplots(1,sharex=True, sharey= True) # creates a figure and axis
    fig_wind, (ax11)=plt.subplots(1,sharex=True, sharey= True)
    fig_tmax, (ax12)=plt.subplots(1,sharex=True, sharey= True)
    fig_tmin, (ax13)=plt.subplots(1,sharex=True, sharey= True)

    fileName = "DataQualityChecking.txt"
    DataDF, ReplacedValuesDF = ReadData(fileName)

    x=DataDF.index # sets x axis as index values
    l1=ax1.plot(x,DataDF['Precip'],'r') # plots data on an axis
    l11=ax11.plot(x,DataDF['Wind Speed'],'r')
    l12=ax12.plot(x,DataDF['Max Temp'],'r')
    l13=ax13.plot(x,DataDF['Min Temp'],'r')
    
    print("\nRaw data.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check01_RemoveNoDataValues( DataDF, ReplacedValuesDF )
    
    print("\nMissing values removed.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check02_GrossErrors( DataDF, ReplacedValuesDF )
    
    print("\nCheck for gross errors complete.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check03_TmaxTminSwapped( DataDF, ReplacedValuesDF )
    
    print("\nCheck for swapped temperatures complete.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check04_TmaxTminRange( DataDF, ReplacedValuesDF )
   
    x=DataDF.index
    l1=ax1.plot(x,DataDF['Precip'],'b')
    fig_precip.suptitle('Precipitaiton') # subtitle of plot
    ax1.set_xlabel('Date') # adds xlabel to plot
    fig_precip.legend(l1,labels=['Before Correction', 'After Correction'], loc="upper right") # adds legend to plot  
    fig_precip.savefig('precip_plot.png') # saves the figure

    
    l11=ax11.plot(x,DataDF['Wind Speed'],'b')
    fig_wind.suptitle('Wind Speed')
    ax11.set_xlabel('Date')
    fig_wind.legend(l11,labels=['Before Correction', 'After Correction'], loc="upper right")   
    fig_wind.savefig('wind_plot.png')
   
    l12=ax12.plot(x,DataDF['Max Temp'],'b')
    fig_tmax.suptitle('Maximum Temperature')
    ax12.set_xlabel('Date')
    fig_tmax.legend(l12,labels=['Before Correction', 'After Correction'], loc="upper right")   
    fig_tmax.savefig('tmax_plot.png')
    
    l13=ax13.plot(x,DataDF['Min Temp'],'b')
    fig_tmin.suptitle('Minimum Temperature')
    ax13.set_xlabel('Date')
    fig_tmin.legend(l13,labels=['Before Correction', 'After Correction'], loc="upper right")   
    fig_tmin.savefig('tmin_plot.png')
    
    print("\nAll processing finished.....\n", DataDF.describe())
    print("\nFinal changed values counts.....\n", ReplacedValuesDF)
    DataDF.to_csv('corrected_data.csv', sep=' ') # saves the data frame
    ReplacedValuesDF.to_csv("failed_checks_summar.csv",sep='\t')
