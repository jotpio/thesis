from pylab import *
import numpy as np
import sys
#sys.path.append("SozialerLeader/")
import SwarmLeadershipCouzin as slc
import pickle as pkl



#fish parameter

N=2;              # default parameter 300
L=3000                # default parameter 50
L=88
time=300.0          # default parameter 300
dt=0.05             # default parameter 0.05

BC=1               # default parameter 0, reflecting 1
IC=1               # initial condition
targetType=2
leadingDistance=2000;

factor=1.0
speed0=factor*10.0

repstrength=factor*5.0     # default parameter 5.0
algstrength=factor*0.0     # default parameter 1.0
attstrength=factor*2.0     # default parameter 0.5
noisep=5.0;                # default parameter 0.2

attstrengthDist=0

reprange=3.0        # default parameter 1.0
algrange=10.0       # default parameter 5.0
attrange=20.0       # default parameter 25.0


#singleLeader=True
leaderCount=2
leadershipRange=16
recruitingRange=8
recruitingAttStrength=factor*10.0
recruitingTime=dt
recruitingSpeed=1.0*speed0

leader_repstrength=repstrength
leader_algstrength=factor*4.0
leader_attstrength=2.*attstrength    

leader_reprange=reprange
leader_algrange=0.5
leader_attrange=1000.0

leader_noisep=noisep

leader_desiredPhi=[0.0]
#leader_desiredPhi=[0.0,None]

leadershipRangeList=[leadershipRange]
#leadershipRangeList=[leadershipRange,12]

#targetVectorList=[[2000,0]]
targetVectorList=[[80,80]]
#targetVectorList=[[2000,0],[-2000,0]]

if(leaderCount>1):
    leadershipRangeList=[leadershipRange,leadershipRange]
    #leader_desiredPhi=[0.0,np.pi]
    leader_desiredPhi=[0.0,None]
else:
    leadershipRangeList=[leadershipRange]
    leader_desiredPhi=[0.0]

dist_dependence='zone'
int_type='matrix'
output=0.5

#dist_dependence='overlap'
#dist_dependence='zone'

#if(targetType==2):
#    L=88                 # size experimental tank 
#    IC=1
#    BC=1
#    attrange=100
#    attstrength=0

# initialize system parameters
params=slc.InitParams(N=N,L=L,time=time,dt=dt,BC=BC,IC=IC,output=output,int_type=int_type,speed0=speed0,                               
                        repstrength=repstrength,reprange=reprange,
                        algstrength=algstrength,algrange=algrange,
                        attstrength=attstrength,attrange=attrange,
                        attstrengthDist=attstrengthDist,
                        noisep=noisep,
                        targetType=targetType,targetVectorList=targetVectorList,
                        leader_noisep=leader_noisep,
                        leaderCount=leaderCount,leadershipRange=leadershipRange,leadingDistance=leadingDistance,
                        recruitingRange=recruitingRange,recruitingTime=recruitingTime,
                        recruitingAttStrength=recruitingAttStrength,recruitingSpeed=recruitingSpeed,
                        leader_repstrength=leader_repstrength,leader_algstrength=leader_algstrength,leader_attstrength=leader_attstrength,
                        leader_reprange=leader_reprange,leader_algrange=leader_algrange,leader_attrange=leader_attrange,
                        leader_desiredPhi=leader_desiredPhi
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
#para1values=[0,8,10,12,14,16,18,20,22,24,24,26]
#para1values=np.arange(6.,37.,2.0)
para1values=np.arange(0.,74.0,12.0)
#para1val_addon=np.array([0,48,60,72])

random_range=True

if(leaderCount>1):
    para1name="leadershipRangeList"
    array1=para1values
    array2=np.ones(len(array1))*leadershipRange

    para1values=np.array(tuple(zip(array1,array2)))

    

#para2name="noisep"
para2name="leader_algstrength"
#para2name="recruitingAttStrength"
#para2values=factor*np.array([0.5])
para2values=factor*np.array([8.0,12.0,16.0])

runs=2
n_proc=10
#outpath='/mnt/DATA/leadershipModel/'
outpath='/home/prom/work/Leadership/DATA/'
outname="targetType{}_Nl{}_S{}_".format(targetType,leaderCount,speed0)+para1name+"_{}_{}".format(np.min(para1values),np.max(para1values))+"_"+para2name+"_{}_{}".format(np.min(para2values),np.max(para2values))

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

