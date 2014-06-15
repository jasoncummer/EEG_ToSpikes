#!/usr/bin/python

import optparse
import datetime
from datetime import date, datetime, timedelta
import sys
import re
from random import randint
#from event import *

# Example usage string for bash:
# python arrayToSpike.py --file="fakeData1.txt"

TIMESTEP = 0.0078125
HALFTIMESTEP = 0.00390625
THIRDTIMESTEP = 0.0026041
MAXFIRERATE = 200
MAXNUMBROFSPIKESINTIMESTEP = 1.5625 # MAXFIRERATE * TIMESTEP

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
      #print(i)
      readfile(names_files[i],eeg_inputs)
    
    print("")
    print("")
    print("")
    print("")
    
    #printevents(eeg_inputs)
    
    spikeRatesByTimeStep= toSpikes(eeg_inputs)
    spikeRates = organizeToChannel(spikeRatesByTimeStep)
    
    
    #print("Spike Rates")
    printevents(spikeRates)
    
    spikeProbabilities = []
    spikeProbabilities = findFireRateProbability(spikeRates)
    
    spikeTrains = []
    spikeTrains = buildSpikeTrain(spikeProbabilities)
    
    #print ("spikeTrains , ")
    #print spikeTrains
    
    #write to a file so that its deterministic rather then random
    writeToTextFile(spikeTrains)

def organizeToChannel(spikeRatesByTimeStep):
	#print "starts in 19 high x 14 wide"
	#print spikeRatesByTimeStep[0]
	spikeRatesByChannelVertically = []
	for h in range(0,14):
		spikeRatesByChannelVertically.append([])
	#print spikeRatesByChannelVertically
	for i in range(len(spikeRatesByTimeStep)):
		for j in range(len(spikeRatesByChannelVertically)):
			spikeRatesByChannelVertically[j].append(spikeRatesByTimeStep[i][j])
		
	#print "ends 14 high x 19 wide"
	#print spikeRatesByChannelVertically[0]
	return spikeRatesByChannelVertically

def writeToTextFile(input_array):
	print "writeToTextFile(input_array)"
	outputFile = open('SpikeTrains.txt', 'w')
	
	for i in range(len(input_array)):
		for j in range(len(input_array[i])):
			#write a line, with tab delimiting
			#outString = '%5f\t' % input_array[i][j]
			outputFile.write(str(input_array[i][j]))
			outputFile.write('\t')
		outputFile.write('\n')
	outputFile.close()

def findFireRateProbability(spikeRate_array):
	print "findFireRateProbability(spikeRate_array)"
	spikeProbabilities = []
	subProbList = []
	
	#print len(spikeRate_array)
	#print (type(spikeRate_array[1][1]))
	#print type(TIMESTEP)
	
	
	for i in range(len(spikeRate_array)):
		for j in range(len(spikeRate_array[i])):
			subProbList.append(spikeRate_array[i][j] * TIMESTEP)
			#print subProbList
		spikeProbabilities.append(subProbList)
		subProbList = []
	
	return spikeProbabilities


def buildSpikeTrain(spikeProbabilities):
	print "buildSpikeTrain(spikeProbabilities)"
	time  = 0
	spikeTrains = []
	singleChannelSpikeTrain = []
	for i in range(len(spikeProbabilities)):
		for j in range(len(spikeProbabilities[i])):
			if spikeProbabilities[i][j] > 1:
				#print "fire"
				time += THIRDTIMESTEP
				singleChannelSpikeTrain.append(time)
				#print time
				time += THIRDTIMESTEP
				spikeProbabilities[i][j]-= 1
				if (randint(0,100) * 0.01) < spikeProbabilities[i][j]:
					#print rands[i]," less than " , probs[i]
					#print "fire"
					singleChannelSpikeTrain.append(time)
					#print time
				time += THIRDTIMESTEP
			elif (randint(0,100) * 0.01) < spikeProbabilities[i][j]:
				#print rands[i]," less than " , probs[i]
				#print "fire"
				time += HALFTIMESTEP
				singleChannelSpikeTrain.append(time)
				#print time
				time += HALFTIMESTEP
			else:
				time += TIMESTEP
			#print time
			#print singleChannelSpikeTrain
		spikeTrains.append(singleChannelSpikeTrain)
		singleChannelSpikeTrain=[]
		time = 0
		
	return spikeTrains

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
  eeg_inputs      An array of data from the eeg txt file <what?>
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

  #print (eeg_inputs)
  return eeg_inputs

def toSpikes(arrayIn):
  print("toSpikes()")
  outPutSpikes = []
  subOutPutSpikes = []
  max = 8000
  # take the cross product to convert to the rate rate code of 200
  for i in range(len(arrayIn)):   
    '''The magic numbers here are some what guesses.
    they come from the data so they could be tweeked more.
    I just only have a few days to look at this atm.
    What they are is values that should be max number that the channel should be at. 
    if i can i will find the preprocessing program but not atm
    '''
    #<todo> label chnnels
    spikeRate = ( ( float( arrayIn[i][0]) / max) * 200 )
    if ( spikeRate > 200 ): # if its over the largest threshold bring it into range
      spikeRate = 200
    #print(spikeRate)
    subOutPutSpikes.append(spikeRate)
    
    spikeRate = ( ( float( arrayIn[i][1]) / max) * 200 )
    if ( spikeRate > 200 ): # if its over the largest threshold bring it into range
      spikeRate = 200
    #print(spikeRate)
    subOutPutSpikes.append(spikeRate)
    
    spikeRate = ( ( float( arrayIn[i][2]) / max) * 200 )
    if ( spikeRate > 200 ): # if its over the largest threshold bring it into range
      spikeRate = 200
    #print(spikeRate)
    subOutPutSpikes.append(spikeRate)
          
    spikeRate = ( ( float( arrayIn[i][3]) / max) * 200 )
    if ( spikeRate > 200 ): # if its over the largest threshold bring it into range
      spikeRate = 200
    #print(spikeRate)
    subOutPutSpikes.append(spikeRate)
    
    spikeRate = ( ( float( arrayIn[i][4]) / max) * 200 )
    if ( spikeRate > 200 ): # if its over the largest threshold bring it into range
      spikeRate = 200
    #print(spikeRate)
    subOutPutSpikes.append(spikeRate)
          
    spikeRate = ( ( float( arrayIn[i][5]) / max) * 200 )
    if ( spikeRate > 200 ): # if its over the largest threshold bring it into range
      spikeRate = 200
    #print(spikeRate)
    subOutPutSpikes.append(spikeRate)
    
    spikeRate = ( ( float( arrayIn[i][6]) / max) * 200 )
    if ( spikeRate > 200 ): # if its over the largest threshold bring it into range
      spikeRate = 200
    #print(spikeRate)
    subOutPutSpikes.append(spikeRate)
            
    spikeRate = ( ( float( arrayIn[i][7]) / max) * 200 )
    if ( spikeRate > 200 ): # if its over the largest threshold bring it into range
      spikeRate = 200
    #print(spikeRate)
    subOutPutSpikes.append(spikeRate)
    
    spikeRate = ( ( float( arrayIn[i][8]) / max) * 200 )
    if ( spikeRate > 200 ): # if its over the largest threshold bring it into range
      spikeRate = 200
    #print(spikeRate)
    subOutPutSpikes.append(spikeRate)
 
    spikeRate = ( ( float( arrayIn[i][9]) / max) * 200 )
    if ( spikeRate > 200 ): # if its over the largest threshold bring it into range
      spikeRate = 200
    #print(spikeRate)
    subOutPutSpikes.append(spikeRate)
      
    spikeRate = ( ( float( arrayIn[i][10]) / max) * 200 )
    if ( spikeRate > 200 ): # if its over the largest threshold bring it into range
      spikeRate = 200
    #print(spikeRate)
    subOutPutSpikes.append(spikeRate)
    
    spikeRate = ( ( float( arrayIn[i][11]) / max) * 200 )
    if ( spikeRate > 200 ): # if its over the largest threshold bring it into range
      spikeRate = 200
    #print(spikeRate)
    subOutPutSpikes.append(spikeRate)
    
    spikeRate = ( ( float( arrayIn[i][12]) / max) * 200 )
    if ( spikeRate > 200 ): # if its over the largest threshold bring it into range
      spikeRate = 200
    #print(spikeRate)
    subOutPutSpikes.append(spikeRate)
    
    spikeRate = ( ( float( arrayIn[i][13]) / max) * 200 )
    if ( spikeRate > 200 ): # if its over the largest threshold bring it into range
      spikeRate = 200
    #print(spikeRate)
    subOutPutSpikes.append(spikeRate)
    
      
    outPutSpikes.append(subOutPutSpikes)
    subOutPutSpikes = []
  
  #print outPutSpikes
  print("end toSpikes()")
  return outPutSpikes

if __name__ == "__main__":
    main()
