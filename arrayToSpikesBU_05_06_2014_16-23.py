#!/usr/bin/python

import optparse
import datetime
from datetime import date, datetime, timedelta
import sys
import re
#from event import *

# Example usage string for bash:
# python arrayToSpike.py --file="fakeData1.txt"

def main():
    """
  Input:
    --file=   The ical file that contains the events that are going to be searched
      Output:
    Hopefully output a file or an array as a set of spiking data for input for a
    liquid state machine.
  Program:
    Using the input file the arrayToSpike.py program will:
      1- Parse the information in the data file.
      2- Load the information into an array.
      4- Transform the events into spike amplitudes and times.
      5- save to a file or enter into an array and pass it on to the lsm.
    """ 


    p = optparse.OptionParser()
    p.add_option("-F", "--file=", action="store", type="string", dest="filename")

    options, arguments = p.parse_args()

    eeg_inputs = []
    spikeRates = []
    names_files = []
    names_files = re.split(r",",options.filename)

    for i in range(len(names_files)):
      print(i)
      readfile(names_files[i],eeg_inputs)
    
    print("")
    print("")
    print("")
    print("")
    
    printevents(eeg_inputs)
    
    spikeRates = toSpikes(eeg_inputs)
    
    print("Spike Rates")
    printevents(spikeRates)

def printevents(input_array):
    for i in range(len(input_array)):
        #for j in range(len(input_array[i])):
        print (input_array[i])
        print ("")

def readfile(filename,eeg_inputs):
  """
  Inputs:
  filename        A file name of a data text file
  eeg_inputs      An array for holding that data from the eeg txt file is stored into as parsing progresses
  Output:
  eeg_inputs      An array of data from the eeg txt file
  Function:
  Takes the file and reads the events and addes them to the list.
  When at the end returns the eeg_events list populated with the data
  """
  #print("readfile()")
  index = 0 
  myfile =open(filename)
  CurrentTimeList = []
  for line in myfile:
    splitline = line.splitlines()
    if (splitline):
      for item in splitline:
        for j in item.split():
          print (j)
          CurrentTimeList.append(j)

      eeg_inputs.append(CurrentTimeList)
      CurrentTimeList = []        
  index += 1

  print (eeg_inputs)
  #printevents(eeg_inputs)
  return eeg_inputs

def toSpikes(arrayIn):
  print("toSpikes()")
  outPutSpikes = []
  subOutPutSpikes = []
  max = 600
  # take the cross product to convert to the rate rate code of 200
  for i in range(len(arrayIn)): 
    for j in range (0,14):#(len(arrayIn[i])-1):
      spikeRate = ( ( float( arrayIn[i][j+1]) / max) * 200 )#<todo> adjust for the + ~4000
      print(spikeRate)
      #<todo> think about converting the gyros - seems like bad idea as you want to have it be controlled by thought alone 
      subOutPutSpikes.append(spikeRate)
    outPutSpikes.append(subOutPutSpikes)
    subOutPutSpikes = []
  
  print("end toSpikes()")
  return outPutSpikes

if __name__ == "__main__":
    main()
