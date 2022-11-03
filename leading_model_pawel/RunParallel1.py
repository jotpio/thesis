from pylab import *
import numpy as np
import sys
#sys.path.append("SozialerLeader/")
import SwarmLeadershipCouzin as slc
import pickle as pkl



#fish parameter

N=2;              # default parameter 300
L=2000                # default parameter 50
time=1000.0          # default parameter 300
dt=0.02             # default parameter 0.05

BC=0               # default parameter 0
IC=1               # initial condition
targetType=0
leadingDistance=200;

factor=1.0
speed0=factor*5.0

repstrength=factor*5.0     # default parameter 5.0
algstrength=factor*0.0     # default parameter 1.0
attstrength=factor*2.0     # default parameter 0.5
noisep=4.0;                # default parameter 0.2

attstrengthDist=0

reprange=3.0        # default parameter 1.0
algrange=5.0        # default parameter 5.0
attrange=10000.0       # default parameter 25.0


#singleLeader=True
leaderCount=1
leadershipRange=12
recruitingRange=10
recruitingAttStrength=factor*5.0
recruitingTime=dt
recruitingSpeed=1.1*speed0

leader_repstrength=repstrength
leader_algstrength=factor*4.0
leader_attstrength=2.*attstrength    

leader_reprange=reprange
leader_algrange=5.0
leader_attrange=1000.0

leader_noisep=-1

dist_dependence='zone'
int_type='matrix'
output=0.5

#dist_dependence='overlap'
#dist_dependence='zone'

# initialize system parameters
params=slc.InitParams(N=N,L=L,time=time,dt=dt,BC=BC,IC=IC,output=output,int_type=int_type,speed0=speed0,                               
                        repstrength=repstrength,reprange=reprange,
                        algstrength=algstrength,algrange=algrange,
                        attstrength=attstrength,attrange=attrange,
                        attstrengthDist=attstrengthDist,
                        noisep=noisep,
                        targetType=targetType,
                        leader_noisep=leader_noisep,
                        leaderCount=leaderCount,leadershipRange=leadershipRange,leadingDistance=leadingDistance,
                        recruitingRange=recruitingRange,recruitingTime=recruitingTime,
                        recruitingAttStrength=recruitingAttStrength,recruitingSpeed=recruitingSpeed,
                        leader_repstrength=leader_repstrength,leader_algstrength=leader_algstrength,leader_attstrength=leader_attstrength,
                        leader_reprange=leader_reprange,leader_algrange=leader_algrange,leader_attrange=leader_attrange
                        )

#########################################
agentData=slc.AgentData(params)
slc.InitAgents(agentData,params)
###########################################
#if(leaderCount>0):
#        
#        agentData.repstrength[:leaderCount]=leader_repstrength
#        agentData.algstrength[:leaderCount]=leader_algstrength
#        agentData.attstrength[:leaderCount]=leader_attstrength
#
#        agentData.reprange[:leaderCount]=leader_reprange
#        agentData.algrange[:leaderCount]=leader_algrange
#        agentData.attrange[:leaderCount]=leader_attrange
#




para1name="leadershipRange"
para1values=[0,12,18,24,24,30,36,42,48,54,60,66,72]
#para2name="noisep"
para2name="leader_algstrength"
para2values=factor*np.array([4.0,8.0,12.0])


runs=200
n_proc=38
#outpath='/mnt/DATA/leadershipModel/'
outpath='/home/prom/work/Leadership/DATA/'
outname="targetType{}_".format(targetType)+para1name+"_{}_{}".format(np.min(para1values),np.max(para1values))+"_"+para2name+"_{}_{}".format(np.min(para2values),np.max(para2values))

outparams=outpath+'para_'+outname+'.pkl'
outresult=outpath+outname+'.h5'


#####################################################################
print("N    = %d" % params['N'])
print("L    = %d" % params['L'])
print("Nl   = %d" % params['leaderCount'])
print("time = %g" % params['time'])

print("outresult={}".format(outresult))
print("outparams={}".format(outparams))

print("--------------------------------------------------------")
print("runs per para set={}".format(runs)) 
print("{} = {}".format(para1name,para1values))
print("{} = {}".format(para2name,para2values))
print("total number of runs= {}".format(len(para1values)*len(para2values)*runs))
print("--------------------------------------------------------")
input("Press Enter to continue...")
##########################################################################

outdata_list,para_list=slc.RunParallelScan(para1name,para2name,para1values,para2values,runs=runs,params=params,agentData=agentData,n_proc=n_proc)

#pkl.dump([outdata_list,para_list],open(outpath+outname,"wb"))
slc.ProcessParallelResults(para1name,para2name,para_list,outdata_list,outpath=outresult)
pkl.dump(params,open(outparams,"wb"))

