import matplotlib
matplotlib.use('TkAgg')
import SwarmLeadershipCouzin as slc
import numpy as np
import os

if __name__ == '__main__':
    N=2;              # default parameter 300
    L=200                # default parameter 50
    time=300.0          # default parameter 300
    dt=0.01             # default parameter 0.05

    noisep=4.0;         # default parameter 0.2
    BC=-1                # default parameter 0
    IC=1               # initial condition

    alpha=100.0
    speed0=5.0

    repstrength=5.0     # default parameter 5.0
    algstrength=0.0     # default parameter 1.0
    attstrength=1.0     # default parameter 0.5

    reprange=3.0        # default parameter 1.0
    algrange=5.0        # default parameter 5.0
    attrange=500.0       # default parameter 25.0

    attstrengthDist=0


    output=0.5

    int_type='matrix'
   
    #dist_dependence='overlap'
    dist_dependence='zone'

    makemovie=False

    #singleLeader=True
    leaderCount=1
    leadershipRange=24
    recruitingRange=10
    recruitingAttStrength=5.0
    recruitingTime=dt
    recruitingSpeed=1.1*speed0

    targetType=0

    leadingDistance=100

    leadershipWeight=0.0 # 0.0
    leadershipInform=1.0 # 1.0

    recruitingStrategy='nearest'

    ######### set leader parameters as arrays
    leader_noisep=0.1;

    leader_repstrength=repstrength
    leader_algstrength=4.0
    leader_attstrength=2.0*attstrength

    leader_reprange=reprange
    leader_algrange=algrange
    leader_attrange=1000

    leader_noisep=0.05

    dist_dependence='zone'
    int_type='matrix'
    
    targetType=0 # TARGET TYPE


    # initialize system parameters
    params=slc.InitParams(N=N,L=L,time=time,dt=dt,BC=BC,IC=IC,output=output,int_type=int_type,speed0=speed0,                               
                        repstrength=repstrength,reprange=reprange,
                        algstrength=algstrength,algrange=algrange,
                        attstrength=attstrength,attrange=attrange,
                        attstrengthDist=attstrengthDist,
                        noisep=noisep,
                        targetType=targetType,
                        leader_noisep=leader_noisep,
                        leaderCount=leaderCount,leadershipRange=leadershipRange,
                        recruitingRange=recruitingRange,recruitingTime=recruitingTime,
                        recruitingAttStrength=recruitingAttStrength,recruitingSpeed=recruitingSpeed,
                        leader_repstrength=leader_repstrength,leader_algstrength=leader_algstrength,leader_attstrength=leader_attstrength,
                        leader_reprange=leader_reprange,leader_algrange=leader_algrange,leader_attrange=leader_attrange
                        )

    #### Initialize Agent Data ##############################
    agentData=slc.AgentData(params)
    slc.InitAgents(agentData,params)
    #########################################################
    #if(leaderCount>0):
    #    agentData.repstrength[:leaderCount]=leader_repstrength
    #    agentData.algstrength[:leaderCount]=leader_algstrength
    #    agentData.attstrength[:leaderCount]=leader_attstrength

    #    agentData.reprange[:leaderCount]=leader_reprange
    #    agentData.algrange[:leaderCount]=leader_algrange
    #    agentData.attrange[:leaderCount]=leader_attrange
    #   
    #    agentData.leadershipRange=leader_leadershipRange

    agentData.desiredPhi[0]=0.0
    if(leaderCount>1):
        agentData.desiredPhi[1]=np.pi

    #print(agentData.desiredPhi)
    if(makemovie==False):
        outdata,agentData=slc.RunAnimate(params,agentData)
    else:
        outdata=slc.SingleRun(params,agentData)
        slc.MakeMovie(outdata,params)
        os.system('rm -r f*.png')




