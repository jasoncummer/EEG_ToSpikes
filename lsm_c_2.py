"""
  Use case for the PCSIM construction framework.
  
  A cuboid grid population is constructed by providing two different factories 
  for inhibitory and excitatory neurons. Connection probabilities depend on distance, 
  and synapse parameters are different for excitatory-all,inhibitory-all connections.
  
  Heavily modified by Jason Cummer 2014
"""

import sys
import optparse

sys.path.append("../_build/lib")

from pypcsim import *
import random, getopt
from datetime import datetime
from math import *
import re

# Example usage string for bash:
# python lsm_<>_<>.py --file="tinyChunk.txt"


def sub_time( t1, t2 ):
    return ( t1 - t2 ).seconds+1e-6*(t1-t2).microseconds;

def main():
	random.seed( datetime.today().microsecond )
	random.seed( 134987 )
	tstart=datetime.today()
	
	###################################################################
	# Global parameter values
	###################################################################
	
	nNeurons        = 4000;   # number of neurons
	minDelay        = 1e-3;   # minimum synapse delay [sec]
	ConnP           = 0.02;   # connectivity probability
	Frac_EXC        = 0.8;    # fraction of excitatory neurons
	Tsim            = 0.4;    # duration of the simulation [sec]
	DTsim           = 1e-4;   # simulation time step [sec]
	nRecordNeurons  = 250;    # number of neurons to plot the spikes from
	Tinp            = 50e-3;  # length of the initial stimulus [sec]
	nInputNeurons   = 14 ;    # number of neurons which provide initial input (for a time span of Tinp)
	inpConnP        = 0.01 ;  # connectivity from input neurons to network neurons
	inputFiringRate = 80;     # firing rate of the input neurons during the initial input [spikes/sec]
	
	
	nThreads = 1
	
	###################################################################
	# Retrive spike rates from the input file
	###################################################################
	p = optparse.OptionParser()
	p.add_option("-F", "--file=", action="store", type="string", dest="filename")
	
	options, arguments = p.parse_args()
	
	spikeTrains = []
	
	names_files = []
	names_files = re.split(r",",options.filename)
	
	for i in range(len(names_files)):
		#returns spike times for all the channels	
		readfile(names_files[i],spikeTrains)
	
	###################################################################
	# Create an empty network
	###################################################################
	
	sp = SimParameter( dt=Time.sec( DTsim ) , minDelay = Time.sec(minDelay), simulationRNGSeed = 345678, constructionRNGSeed = 349871 );
	net = SingleThreadNetwork( sp )
	
	###################################################################
	# Create the neuron factories and set their parameters
	###################################################################
	
	# the excitatory neuron factory
	exc_nrn_factory = SimObjectVariationFactory( LifNeuron() ) ;
	exc_nrn_factory.set("Cm", NormalDistribution(2e-10, 1e-11))
	exc_nrn_factory.set("Rm", NormalDistribution(1e8, 5e6))
	exc_nrn_factory.set("Vthresh", ConstantNumber(-50e-3))
	exc_nrn_factory.set("Vresting", ConstantNumber(-49e-3))
	exc_nrn_factory.set("Vreset", ConstantNumber(-60e-3))
	exc_nrn_factory.set("Trefract", UniformDistribution(4.8e-3, 5.2e-3))
	exc_nrn_factory.set("Vinit", ConstantNumber(-60e-3))
	
	
	# the inhibitory neuron factory
	inh_nrn_factory = SimObjectVariationFactory( LifNeuron() ) ;
	inh_nrn_factory.set("Cm", NormalDistribution(2e-10, 2e-11))
	inh_nrn_factory.set("Rm", NormalDistribution(1e8, 5e6))
	inh_nrn_factory.set("Vthresh", ConstantNumber(-50e-3))
	inh_nrn_factory.set("Vresting", ConstantNumber(-49e-3))
	inh_nrn_factory.set("Vreset", ConstantNumber(-57e-3))
	inh_nrn_factory.set("Trefract", UniformDistribution(4.8e-3, 5.2e-3))
	inh_nrn_factory.set("Vinit", ConstantNumber(-57e-3))
	
	all_nrn_popul = SpatialFamilyPopulation( net, [ exc_nrn_factory, inh_nrn_factory ], RatioBasedFamilies( [4, 1]  ), CuboidIntegerGrid3D( 20, 20, 10 ) );
	
	print 
	
	exz_nrn_popul, inh_nrn_popul = tuple( all_nrn_popul.splitFamilies() );
	
	print "Created population of size", all_nrn_popul.size(), ":", exz_nrn_popul.size(), "exzitatory and", inh_nrn_popul.size(), "inhibitory neurons";
	
	###################################################################
	# Create synaptic connections
	###################################################################
	
	print 'Making synaptic connections:'
	t0=datetime.today()
	
	Erev_exc = 0;
	Erev_inh = -80e-3;
	Vmean    = -60e-3;
	Wexc = (Erev_exc-Vmean)*0.27e-9;
	Winh = (Erev_inh-Vmean)*4.5e-9;
	
	n_exz_syn_project = ConnectionsProjection( exz_nrn_popul, all_nrn_popul, 
						StaticSpikingSynapse( W=Wexc, tau=5e-3, delay=1e-3 ),
						EuclideanDistanceRandomConnections( ConnP, 10 ) )
	
	n_inh_syn_project = ConnectionsProjection( inh_nrn_popul, all_nrn_popul, 
						StaticSpikingSynapse( W=Winh, tau=10e-3, delay=1e-3 ),
						EuclideanDistanceRandomConnections( ConnP, 10 ) )
	
	print "nex=", n_exz_syn_project.size(), " nin=", n_inh_syn_project.size()
	
	t1= datetime.today();
	print 'Created',int( n_exz_syn_project.size() + n_inh_syn_project.size()),'current synapses in',sub_time( t1, t0 ),'seconds'
	
	###################################################################
	# Create input neurons for the initial stimulus
	# and connect them to random neurons in circuit
	###################################################################
	
	
	#input_values = [ 0.00390625, 0.01171875, 0.01953125, 0.02734375, 0.03515625, 0.04296875, 0.05078125, 0.05859375, 0.06640625, 0.07421875, 0.08203125, 0.08984375, 0.09765625]
	
	inputNeuronPopulations = []
	#for h in range(len(spikeTrains)):
		#inputNeurons[h].append([])
	
	for i in range(len(spikeTrains)):
		inp_nrn_popul = SimObjectPopulation( net, [ net.add( SpikingInputNeuron( spikeTrains[i] ) ) for i in range(0,1) ] );
		print inp_nrn_popul.size()
		inputNeuronPopulations.append(inp_nrn_popul)
	
	for j in range(len(inputNeuronPopulations)):
		inp_syn_project = ConnectionsProjection( inputNeuronPopulations[j], exz_nrn_popul, StaticSpikingSynapse( W=(Erev_exc-Vmean)*2e-9, tau=5e-3, delay=1e-3 ), RandomConnections( conn_prob = inpConnP ) );
	
	
	###########################################################
	# Create recorders to record spikes and voltage traces
	###########################################################
	
	net.setDistributionStrategy(DistributionStrategy.ModuloOverLocalEngines())
	spike_rec_popul = SimObjectPopulation(net, SpikeTimeRecorder(), all_nrn_popul.size())
	
	rec_conn_project = ConnectionsProjection( all_nrn_popul, spike_rec_popul, Time.ms(1) );  # if delay is specified, wiring method is assumed to be one-to-one
	
	vm_rec_nrn_popul = SimObjectPopulation(net, random.sample( all_nrn_popul.idVector(), nRecordNeurons ));
	vm_recorders_popul = SimObjectPopulation(net, AnalogRecorder(),  nRecordNeurons );
	for i in range(vm_recorders_popul.size()):
		net.connect( vm_rec_nrn_popul[i], 'Vm', vm_recorders_popul[i], 0,  Time.ms(1) );
	
	###########################################################
	# Simulate the circuit
	###########################################################
	
	print 'Running simulation:';
	t0=datetime.today()
	
	net.reset();
	net.advance( int( Tsim / DTsim ) )
	
	t1=datetime.today()
	print 'Done.', sub_time(t1,t0), 'sec CPU time for', Tsim*1000, 'ms simulation time';
	print '==> ', sub_time(t1,tstart), 'seconds total'
		
	###########################################################
	# Make some figures out of simulation results
	###########################################################
	
	if net.mpi_rank() == 0:
		n = [ spike_rec_popul.object(i).spikeCount() for i in range( spike_rec_popul.size() ) ]
		print "spikes total",sum(n)
		print "mean rate:",sum(n)/Tsim/len(n)
	
	isi = [ meanisi(spike_rec_popul.object(i).getSpikeTimes()) for i in range( spike_rec_popul.size() ) ]
	isi = filter( lambda x: x != None, isi);
	print "mean ISI:",sum(isi)/len(isi)
	
	
	CV = [ cv(spike_rec_popul.object(i).getSpikeTimes()) for i in range( spike_rec_popul.size() ) ]
	CV = filter( lambda x: x != None, CV);
	print "mean CV:",mean(CV)


def writeToTextFile(input_array):
	print "writeToTextFile(input_array)"
	outputFile = open('lsmOutput_dbnInput.txt', 'w')
	
	for i in range(len(input_array)):
		for j in range(len(input_array[i])):
			#write a line, with tab delimiting
			#outString = '%5f\t' % input_array[i][j]
			outputFile.write(str(input_array[i][j]))
			#outputFile.write('\t')
		outputFile.write('\n')
	outputFile.close()


def readfile(filename,SpikeRates_input):
  """
  Inputs:
  filename        A file name of a data text file
  eeg_inputs      An array for holding that data from the SpikeRates txt file is stored into as parsing progresses
  Output:
  SpikeRates      An array of data from the parsed SpikeRates txt file 
  Function:
  Takes the file and reads the values and adds them to the list.
  When at the end returns the SpikeRates list populated with the data
  """
  #print("readfile()")
  myfile =open(filename)
  CurrentSpikeRateList = []
  for line in myfile:
    splitline = line.splitlines()
    if (splitline):
      for item in splitline:
        for j in item.split():
          #print (j)
          CurrentSpikeRateList.append(float(j))

      SpikeRates_input.append(CurrentSpikeRateList)
      CurrentSpikeRateList = []        

  #print SpikeRates_input
  #print len(SpikeRates_input)
  return SpikeRates_input

def diff(x):
    return [ x[i+1] - x[i] for i in range(len(x)-1) ]
   
def std(data):
    mu = sum(data)/float(len(data));
    r=[ (x-mu)*(x-mu) for x in data ];
    return sqrt(sum(r)/(len(r)-1))

def mean(data):
    return sum(data)/len(data);

def meanisi(spikes):
    if( len(spikes) > 1):
        return mean(diff(spikes));
    else:
        return None

def cv(spikes):
    if( len(spikes) > 2):
        isi=diff(spikes);
        return std(isi) / mean(isi)
    else:
        return None




if __name__ == "__main__":
    main()