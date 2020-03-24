#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#
"""
Created on Friday 2020-03-20
Author: Ankit Ghanghas


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

    DataDF[DataDF==-999.00]=np.nan
    ReplacedValuesDF.loc['1. No Data',:]=DataDF.isna().sum()
    return( DataDF, ReplacedValuesDF )
    
def Check02_GrossErrors( DataDF, ReplacedValuesDF ):
    """This function checks for gross errors, values well outside the expected 
    range, and removes them from the dataset.  The function returns modified 
    DataFrames with data the has passed, and counts of data that have not 
    passed the check."""
 
    DataDF.Precip[(DataDF['Precip']>25) | (DataDF['Precip']<0)]=np.nan
    DataDF['Wind Speed'][(DataDF['Wind Speed']>10) | (DataDF['Wind Speed']<0)]=np.nan
    DataDF['Max Temp'][(DataDF['Max Temp']>35) | (DataDF['Max Temp']<-25)]=np.nan
    DataDF['Min Temp'][(DataDF['Min Temp']>35) | (DataDF['Min Temp']<-25)]=np.nan
    ReplacedValuesDF.loc['2. Gross Error',:]=DataDF.isna().sum()-ReplacedValuesDF.sum()
    return( DataDF, ReplacedValuesDF )
    
def Check03_TmaxTminSwapped( DataDF, ReplacedValuesDF ):
    """This function checks for days when maximum air temperture is less than
    minimum air temperature, and swaps the values when found.  The function 
    returns modified DataFrames with data that has been fixed, and with counts 
    of how many times the fix has been applied."""
    count= len(DataDF.loc[DataDF['Min Temp']>DataDF['Max Temp']])
    DataDF.loc[DataDF['Min Temp']>DataDF['Max Temp'],['Min Temp','Max Temp']]= DataDF.loc[ DataDF['Min Temp']>DataDF['Max Temp'],['Max Temp','Min Temp']].values 
    ReplacedValuesDF.loc['3. Swapped',:]=[0,count,count,0]
    return( DataDF, ReplacedValuesDF )
    
def Check04_TmaxTminRange( DataDF, ReplacedValuesDF ):
    """This function checks for days when maximum air temperture minus 
    minimum air temperature exceeds a maximum range, and replaces both values 
    with NaNs when found.  The function returns modified DataFrames with data 
    that has been checked, and with counts of how many days of data have been 
    removed through the process."""
    
    count= len(DataDF.loc[(DataDF['Max Temp']-DataDF['Min Temp']>25)])
    DataDF.loc[(DataDF['Max Temp']-DataDF['Min Temp']>25),['Min Temp','Max Temp']]=np.nan
    ReplacedValuesDF.loc['4. Range', :]=[0,count,count,0]
 
    return( DataDF, ReplacedValuesDF )
    

# the following condition checks whether we are running as a script, in which 
# case run the test code, otherwise functions are being imported so do not.
# put the main routines from your code after this conditional check.

if __name__ == '__main__':
    fig_precip, (ax1,ax2)=plt.subplots(2,sharex=True, sharey= True)
    fig_wind, (ax11,ax21)=plt.subplots(2,sharex=True, sharey= True)
    fig_tmax, (ax12,ax22)=plt.subplots(2,sharex=True, sharey= True)
    fig_tmin, (ax13,ax23)=plt.subplots(2,sharex=True, sharey= True)

    fileName = "DataQualityChecking.txt"
    DataDF, ReplacedValuesDF = ReadData(fileName)

    x=DataDF.index
    l1=ax1.plot(x,DataDF['Precip'],'r')
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
    l2=ax2.plot(x,DataDF['Precip'],'b')
    fig_precip.suptitle('Precipitaiton')
    ax2.set_xlabel('Date')
    fig_precip.legend([l1,l2],labels=['Before Correction', 'After Correction'], loc="upper right")   
    fig_precip.savefig('precip_plot.png')
    
    l21=ax21.plot(x,DataDF['Wind Speed'],'b')
    fig_wind.suptitle('Wind Speed')
    ax21.set_xlabel('Date')
    fig_wind.legend([l11,l21],labels=['Before Correction', 'After Correction'], loc="upper right")   
    fig_wind.savefig('wind_plot.png')
    
    l22=ax22.plot(x,DataDF['Max Temp'],'b')
    fig_tmax.suptitle('Maximum Temperature')
    ax22.set_xlabel('Date')
    fig_tmax.legend([l12,l22],labels=['Before Correction', 'After Correction'], loc="upper right")   
    fig_tmax.savefig('tmax_plot.png')
    
    l23=ax23.plot(x,DataDF['Min Temp'],'b')
    fig_tmin.suptitle('Minimum Temperature')
    ax23.set_xlabel('Date')
    fig_tmin.legend([l13,l23],labels=['Before Correction', 'After Correction'], loc="upper right")   
    fig_tmin.savefig('tmin_plot.png')
    
    print("\nAll processing finished.....\n", DataDF.describe())
    print("\nFinal changed values counts.....\n", ReplacedValuesDF)
    DataDF.to_csv('corrected_data.csv', sep=' ')
    ReplacedValuesDF.to_csv("failed_checks_summar.csv",sep=' ')
