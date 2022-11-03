import numpy as np

import SwarmLeadershipCouzin as slc

def init():

    #fish parameter

    N=2;              # default parameter 300
    L=1000                # default parameter 50
    L=88
    time=300.0          # default parameter 300
    dt=0.05             # default parameter 0.05



    noisep=5;         # default parameter 0.2
    BC=0; IC=0         # periodic boundary, random orientation, local random position x in [0,10], y in [0,10]
    BC=1; IC=1         # reflecting boundary, random orientation, local random position x in [0,10], y in [0,10]
    #BC=1; IC=1         # reflecting boundary, orientation biased to diagonal, local random position x in [0,10], y in [0,10]

    repstrength=5.0     # default parameter 5.0
    algstrength=0.0     # default parameter 1.0
    attstrength=2.0     # default parameter 0.5

    attstrengthDist=0   # attraction strenth distribution flag (0 - fixed/same for all, 1 - random)

    reprange=3.0        # default parameter 1.0
    algrange=10.0        # default parameter 5.0
    attrange=20.0       # default parameter 25.0

    speed0=6.0;         # speed0

    leaderCount=1       # number of leads
    ################ Set multiple leaders ##############################
    #leader_desiredPhi=[0.0,0.5*np.pi]
    #leadershipRangeList=[18,22]
    #leadershipRangeList=[10,12]

    leadershipRange=12 #-1 #12

    if(leaderCount>1):
        leadershipRangeList=[leadershipRange,50]
        leader_desiredPhi=[None,0.0]
    else:
        leadershipRangeList=[leadershipRange]
        leader_desiredPhi=[0.0]

    recruitingRange=8
    recruitingAttStrength=10
    recruitingTime=dt
    recruitingSpeed=1.0*speed0
    targetType=2  # target type: 0 - targetDist along x, 1 - diagonal, 2 - set to a certain position as in exp

    targetVectorList=[[80,80]]
    leader_repstrength=repstrength
    leader_algstrength=8.0                  #algstrength defines the alignment with the target vector (not other fish!)
    leader_attstrength=2.*attstrength 
    leader_attstrength=10.0

    leader_reprange=reprange
    leader_algrange=5.0 
    leader_attrange=100.0

    leader_noisep=5.0
    #leadingDistance=127.27
    leadingDistance=500
    int_type='matrix'
    output=0.1

    #dist_dependence='overlap'
    dist_dependence='zone'

    # initialize system parameters
    params=slc.InitParams(N=N,L=L,time=time,dt=dt,BC=BC,IC=IC,output=output,int_type=int_type,                               
                            repstrength=repstrength,reprange=reprange,leadingDistance=leadingDistance,
                            algstrength=algstrength,algrange=algrange,
                            attstrength=attstrength,attrange=attrange,speed0=speed0,
                            attstrengthDist=attstrengthDist,
                            noisep=noisep,leaderCount=leaderCount,
                            targetType=targetType,targetVectorList=targetVectorList,
                            leader_noisep=leader_noisep,leader_attstrength=leader_attstrength,leader_algstrength=leader_algstrength,leader_repstrength=leader_repstrength,
                            leader_reprange=leader_reprange,leader_algrange=leader_algrange,leader_attrange=leader_attrange,
                            leadershipRange=leadershipRange,
                            recruitingAttStrength=recruitingAttStrength,
                            recruitingRange=recruitingRange,
                            recruitingTime=recruitingTime,
                            recruitingSpeed=recruitingSpeed,
                            leader_desiredPhi=leader_desiredPhi,
                            leadershipRangeList=leadershipRangeList)

    #########################################
    agentData=slc.AgentData(params)
    slc.InitAgents(agentData,params)
    ##########################################
    if(leaderCount>0):

            agentData.repstrength[:leaderCount]=leader_repstrength
            agentData.algstrength[:leaderCount]=leader_algstrength
            agentData.attstrength[:leaderCount]=leader_attstrength

            agentData.reprange[:leaderCount]=leader_reprange
            agentData.algrange[:leaderCount]=leader_algrange
            agentData.attrange[:leaderCount]=leader_attrange
            agentData.sigmap[:leaderCount]=np.sqrt(2.*dt*params['leader_noisep'])

    print("N =",params['N'])
    print("L =",params['L'])
    print("leaderCount =",params['leaderCount'])
    print("leadRange =",params['leadershipRange'])
    print("recruitRange =",params['recruitingRange'])
    print("attstrength =",params['attstrength'])
    print("time =",params['time'])
    print("noisep =",params['noisep'])
    print("lead_noisep =",params['leader_noisep'])
    print("lead_desPhi =",params['leader_desiredPhi'])
    print("----------------------")
    #print(agentData.algstrength)
    print("agentData.sigmap     =",agentData.sigmap)
    print("agentData.desiredPhi =",agentData.desiredPhi)
    print("agentData.leadershipWeight  =",agentData.leadershipWeight)
    print("agentData.leadershipRange  =",agentData.leadershipRange)
    print("agentData.leadingTime       =",agentData.leadingTime)
    print("agentData.pos=\n",agentData.pos)
    print("agentData.initpos=\n",agentData.initpos)
    print("agentData.targetVector=\n",agentData.targetVector)

    #print(agentData.attstrength)
    
    return agentData, params
    