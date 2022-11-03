import numpy as np
from math import *
#from numba import jit
#import matplotlib
#matplotlib.use('GTKAgg')
import pylab as pl
import collections 
import pandas as pd
#import pylab as pl

from sklearn.preprocessing import normalize
from functools import partial

import os
import glob
try:
    import multiprocessing as mp
    parallel=True
except:
    print("Multiprocessing module cannot be loaded!")
    parallel=False;

#from OwnFunctions import *

class AgentData(object):
    ''' A class containing all the data structures for agents ''' 
    def __init__(self,params):
        N=params['N'];
        leaderCount=params['leaderCount']
        recruitingSpeed=params['recruitingSpeed']

        # Cartesian coordinates
        self.pos=np.zeros((N,2));       # pos vectors
        self.initpos=np.zeros((N,2));   # initial position
        self.vel=np.zeros((N,2));       # velocity vectors
        self.uv =np.zeros((N,2));       # unit vector along heading
        self.up =np.zeros((N,2));       # unit vector perp to heading (angular direction)
        # Coordinates not taking boundary conditions into account 
        self.POS=np.zeros((N,2))        # auxiliary POS variable for periodic boundary to keep track of global displacement
        
        # social force variables
        self.force=np.zeros((N,2))      # 
        self.force_att=np.zeros((N,2))
        self.force_rep=np.zeros((N,2))
        self.force_alg=np.zeros((N,2))

        self.neighbors_rep=np.zeros((N,1))
        self.neighbors_alg=np.zeros((N,1))
        self.neighbors_att=np.zeros((N,1))

        # agent speeds
        self.speed=np.ones((N,1));
        # agent direction of motion (polar angle)
        self.phi=np.zeros(N);

        # social force strengths
        self.repstrength=np.ones(N);
        self.attstrength=np.ones(N);
        self.algstrength=np.ones(N);
        #social force ranges
        self.reprange=np.ones(N);
        self.attrange=np.ones(N);
        self.algrange=np.ones(N);
        #social force ranges
        self.repsteepness=np.ones(N);
        self.attsteepness=np.ones(N);
        self.algsteepness=np.ones(N);
        #individual noise strengths
        self.sigmap=np.zeros(N)

        self.centerofMassPos=np.zeros(2)
        self.centerofMassVel=np.zeros(2)

        self.targetVector    =np.nan*np.ones((N,2))
        self.currTargetVector=np.nan*np.ones((N,2))

        if(leaderCount>0):
            self.leadershipRange=np.zeros(leaderCount)
            leadershipRangeList=params['leadershipRangeList']
            if(len(leadershipRangeList)>0):
                if(len(leadershipRangeList)<leaderCount):
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print("WARNING!!! Less desiredPhi than leaders!!!!")
                self.leadershipRange[:len(leadershipRangeList)]=leadershipRangeList;
            else:
                self.leadershipRange=np.ones(leaderCount)*params['leadershipRange']

            #if(len(recruitingRangeList)>0):
            #    if(len(recruitingRangeList)<leaderCount):
            #        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            #        print("WARNING!!! RecruitingRangeList not set/to short setting all to min(recruitRange/leadershipRange)!!!!")
            #    self.recruitingRange=leadershipRangeList;
            #else:
            #    self.leadershipRange=np.ones(leaderCount)*params['leadershipRange']
            

            self.leading=np.ones(leaderCount)
            self.timer=np.zeros(leaderCount)
            self.recruitingIndex=np.zeros(leaderCount);
            self.leadingRecord=np.zeros((leaderCount,params['steps']))
            leader_desiredPhi=params['leader_desiredPhi']
            self.desiredPhi=np.zeros(leaderCount)
            if(len(leader_desiredPhi)>0):
                if(len(leader_desiredPhi)<leaderCount):
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print("WARNING!!! Less desiredPhi than leaders!!!!")
                self.desiredPhi[:len(leader_desiredPhi)]=leader_desiredPhi;


            self.leadershipWeight=np.ones(leaderCount)
            self.leadingTime=-np.ones(leaderCount)
            self.distTarget=1000*np.ones(leaderCount)
            self.recruitingSpeed=recruitingSpeed=np.ones(leaderCount)
    
    # helper methods for resetting/normalizing/updating
    def ResetForces(self):
        self.force.fill(0.0)
        self.force_att.fill(0.0)
        self.force_rep.fill(0.0)
        self.force_alg.fill(0.0)
        self.neighbors_rep.fill(0.0)
        self.neighbors_alg.fill(0.0)
        self.neighbors_att.fill(0.0)

    def NormalizeForces(self):
        self.force_att=normalize(self.force_att,axis=1,norm='l2')
        self.force_rep=normalize(self.force_rep,axis=1,norm='l2')
        self.force_alg=normalize(self.force_alg,axis=1,norm='l2')

    def UpdateDirection(self):
        self.phi=np.arctan2(self.vel[:,1],self.vel[:,0])

    def UpdateCartesian(self):
        self.uv[:,0] =np.cos(self.phi);
        self.uv[:,1] =np.sin(self.phi);
        self.up=np.copy(self.uv[:,::-1])
        self.up[:,0]*=-1
        self.vel=np.multiply(np.reshape(self.speed,(-1,1)),self.uv)

        self.centerofMassPos=np.mean(self.pos,axis=0)
        self.centerofMassVel=np.mean(self.vel,axis=0)



def InitParams(time=100,dt=0.05,output=1.0,L=50,N=10,IC=0,BC=0,
                 int_type='matrix',dist_dependence='overlap',
                 speed0=1.0,alpha=0.5,
                 wallrepdist=1,wallrepstrength=5.0,
                 attstrengthDist=0,
                 attstrength=0.2,attrange=100,attsteepness=-20,
                 repstrength=1.0,reprange=1.0,repsteepness=-20,
                 algstrength=0.5,algrange=4,algsteepness=-20,
                 blindangle=0.0*np.pi,blindanglesteepness=50,
                 kneigh=6,
                 noisep=0.01,
                 targetType=0,
                 targetVectorList=[],
                 leaderCount=1,
                 leadershipWeight=0.0,leadershipRange=100,leadershipRangeList=[],
                 recruitingRange=2.0,
                 recruitingRangeList=[],
                 recruitingTime=1.0,
                 recruitingAttStrength=5.0,
                 recruitingSpeed=-1,
                 leadingDistance=100.0,
                 leader_repstrength=0.0,
                 leader_algstrength=0.0,
                 leader_attstrength=0.0,
                 leader_reprange=0.0,
                 leader_algrange=0.0,
                 leader_attrange=0.0,
                 leader_noisep=0.1,
                 leader_desiredPhi=[]
                 ):

    
    params=collections.OrderedDict()

    ################# Base Params #########################
    params['time']=time;
    params['dt']=dt
    params['output']=output
    params['L']=L
    params['N']=N
    params['IC']=IC
    params['BC']=BC
    params['int_type']=int_type
    params['dist_dependence']=dist_dependence
    params['steps']=int(time/dt) 
    params['stepout']=int(output/dt)
    params['outsteps']=int(params['steps']/params['stepout']) 
    
    ################# Agent Params #########################
    params['alpha']=alpha
    params['speed0']=speed0
    params['wallrepdist']=wallrepdist
    params['wallrepstrength']=wallrepstrength

    params['attstrengthDist'] =attstrengthDist

    params['attstrength'] =attstrength
    params['attrange']    =attrange
    params['attsteepness']=attsteepness

    params['repstrength'] =repstrength
    params['reprange']    =reprange
    params['repsteepness']=repsteepness

    params['algstrength'] =algstrength
    params['algrange']    =algrange
    params['algsteepness']=algsteepness

    params['blindangle']=blindangle
    params['blindanglesteepness']=blindanglesteepness

    params['kneigh']=kneigh
    params['noisep']=noisep
    params['sigmap']=np.sqrt(2.0*dt*noisep);

    ######### Robofish params ##################################
    params['targetType']=targetType
    params['leaderCount']=leaderCount
    params['leadershipWeight']=leadershipWeight
    params['leadershipRangeList']=leadershipRangeList
    params['leadershipRange']=leadershipRange
    params['recruitingRangeList']=recruitingRangeList
    params['recruitingRange']=recruitingRange
    params['recruitingTime']=recruitingTime
    params['recruitingAttStrength']=recruitingAttStrength
    params['recruitingStrategy']='nearest'
    params['recruitingSpeed']=recruitingSpeed
    if(params['recruitingSpeed']<0):
        params['recruitingSpeed']=params['speed0']
    print("recruiting speed={}".format(params['recruitingSpeed']))
    params['leadingDistance']=leadingDistance

    params['targetVectorList']=targetVectorList
    params['targetVector']=targetVectorList[0]

    params['deltaDistTarget']=5;
    
    params['leader_repstrength']=leader_repstrength
    params['leader_algstrength']=leader_algstrength
    params['leader_attstrength']=leader_attstrength
    params['leader_reprange']=leader_reprange
    params['leader_algrange']=leader_algrange
    params['leader_attrange']=leader_attrange
    params['leader_desiredPhi']=leader_desiredPhi
    if(leader_noisep<0.0):
        params['leader_noisep']=noisep
    else:
        params['leader_noisep']=leader_noisep


    params['leader_sigmap']=np.sqrt(2.0*dt*params['leader_noisep']);

    return params




#def InitLeaders(params,second_leadership_range=5):
#    leaderCount=params['leaderCount']
#
#    dataLeader=collections.OrderedDict()
#    ##############################################################
#    dataLeader['leadershipWeight']=params['leadershipWeight'] # 0.0
#    dataLeader['leadershipRange']=params['leadershipRange']
#    dataLeader['recruitingRange']=params['recruitingRange']
#    dataLeader['leadershipInform']=1.0 # 1.0
#    dataLeader['recruitingStrategy']='nearest'
#    ##############################################################
#
#    ######### set leader parameters as arrays
#    dataLeader['leader_repstrength']=np.ones(leaderCount)*5.0
#    dataLeader['leader_algstrength']=np.ones(leaderCount)*0.5
#    dataLeader['leader_attstrength']=np.ones(leaderCount)*0.2    
#    dataLeader['leader_reprange']=np.ones(leaderCount)*1.0
#    dataLeader['leader_algrange']=np.ones(leaderCount)*5.0
#    dataLeader['leader_attrange']=np.ones(leaderCount)*100.0
#    dataLeader['leader_noisep']=np.ones(leaderCount)*params['leader_noisep']
#
#    dataLeader['leader_leadershipRange'] =np.ones(leaderCount)*dataLeader['leadershipRange']
#    dataLeader['leader_leadershipWeight']=np.ones(leaderCount)*dataLeader['leadershipWeight']
#    dataLeader['leader_leadershipInform']=np.ones(leaderCount)*dataLeader['leadershipInform']
#    dataLeader['leader_leadershipRange'][0]=dataLeader['leadershipRange']
#    if(leaderCount>1):
#        dataLeader['leader_leadershipRange'][1]=second_leadership_range
#
#    return dataLeader

def SetVariableAttribute(agentData,attribute_name='algstrength',meanValue=5.0,width=5.0):
    '''set given attribute to be uniformly distributed around va mean.'''
    a=getattr(agentData,attribute_name)
    a=meanValue+width*(np.random.random(len(a))-0.5)
    a=setattr(agentData,attribute_name,a)
    return

def ResetAgentData(agentData,params,dataLeader,experiment='open_leader_noinfo'):

    leaderCount=params['leaderCount']
    if(experiment=='open_leader_noinfo'):
        #### Initialize Agent Data ##############################
        agentData=AgentData(params)
        InitAgents(agentData,params)
        #########################################################
        if(params['leaderCount']>0):
            agentData.repstrength[:leaderCount]=dataLeader['leader_repstrength']
            agentData.algstrength[:leaderCount]=dataLeader['leader_algstrength']
            agentData.attstrength[:leaderCount]=dataLeader['leader_attstrength']
            agentData.sigmap[:leaderCount]=np.sqrt(2.*params['dt']*dataLeader['leader_noisep'])

            agentData.reprange[:leaderCount]=dataLeader['leader_reprange']
            agentData.algrange[:leaderCount]=dataLeader['leader_algrange']
            agentData.attrange[:leaderCount]=dataLeader['leader_attrange']
            agentData.leadershipRange=dataLeader['leader_leadershipRange']

    return

##################### BASIC RUN FUNCTION ##################################################
def SingleRunGlobal(params,agentData=None):
    ''' perform a single simulation run '''

    ### INITIALIZATION ##################################
    # initialize agents if not provided at run time 
    if(agentData==None):
        agentData=AgentData(params)
        InitAgents(agentData,params) 
    # initialize output arrays
    outdata=SaveOutData(0,agentData,None,params)

    ### PERFORM TIME INTEGRATION ######################
    for s in range(1,params.steps+1):
        # reset social forces
        agentData.ResetForces()  # call to method of the agentData class
        # calculate new social foces
        CalcInteractionGlobal(agentData,params )
        UpdateTotalSocialForce(agentData,params)
        # update direction of motion, positions/velocity vectors
        UpdateCoordinates( agentData,params)
        
        ### OUTPUT ###################
        if((s % params.stepout)==0):
            #print('t=%02f' % (para.dt*s))
            outdata=SaveOutData(s,agentData,outdata,params)

    outdata['targetVectors']=agentData.targetVector
    return outdata 

def SetTargetVectors(agentData,params):


    if(len(params['targetVectorList'])>0):
        for i in range(len(params['targetVectorList'])):
            agentData.targetVector[i]=params['targetVectorList'][i]
            agentData.currTargetVector[i]=agentData.targetVector[i]-agentData.POS[i]

    #else:
    #    if(params['targetType']==2):
    #        if(params['L']==88):
    #            params['targetVector']=np.ones(2)*75
    #        else:
    #            params['targetVector']=np.ones(2)*0.9*params['L']

    #        params['leadingDistance']=np.linalg.norm(params['targetVector'])

    #    elif(params['targetType']==1):
    #        params['targetVector']=leadingDistance*np.ones(2)/np.sqrt(2.0)
    #    elif(params['targetType']==0):
    #        params['targetVector']=leadingDistance*np.array([1,0])
    #    
    #    if(params['targetType']==0):
    #        params['deltaDistTarget']=0;
    #    else:
    #        params['deltaDistTarget']=5;
    #    

    #    params['targetVectorList']=[]
    #    for i in range(leaderCount): 
    #        params['targetVectorList'].append(params['targetVector'])
    #else:
    #    params['targetVector']=None
    #    params['leadingDistance']=None #np.linalg.norm(params['targetVector'])
    #    params['deltaDistTarget']=5;


    return

def SetInitialCoordinates(agentData,params):
    N=params['N']
    L=params['L']
        
    if(params['IC']==0):
        agentData.pos  = 10*np.ones((N,2))*np.random.random((N,2))
        agentData.phi  = np.random.uniform(-np.pi,np.pi,N)
    elif(params['IC']==1):
        #agentData.pos=0.1*L*np.ones((N,2))*np.random.random((N,2))
        agentData.pos=10*np.ones((N,2))*np.random.random((N,2))
        agentData.phi  =np.random.uniform(-0.25*np.pi,0.75*np.pi,N)
        #if(params['leaderCount']==1):
        #    if(params['targetType']==2):
        #        agentData.pos[0,:]=np.array([0.1*L,0.1*L])
        #agentData.pos[0,:]=np.array([0.1*L,0.1*L])
    elif(params['IC']==10):
        agentData.pos=0.5*L*np.ones((N,2))+2*sqrt(N)*np.random.random((N,2))
        agentData.phi  =2.*np.pi*np.random.random(N)
    elif(params['IC']==20):
        agentData.pos=0.5*L*np.ones((N,2))+2*sqrt(N)*np.random.random((N,2))
        agentData.phi  =np.zeros(N)
    elif(params['IC']==30):
        agentData.pos[:,1]=0.0
        for i in range(N):
            agentData.pos[i,0]=0.5*L-i*params['reprange']
        
        agentData.phi  =np.random.uniform(0.0,0.5*np.pi,N)
    else:
        agentData.pos=L*np.random.random((N,2))

    agentData.POS=np.copy(agentData.pos)
    
    # set polar coordinates
    agentData.speed=params['speed0']*np.ones(N)
    #update Cartesian coordinates
    agentData.UpdateCartesian()
    return

def SetInteractionParameters(agentData,params):
    N=params['N']
    agentData.repstrength=np.ones(N)*params['repstrength'];
    agentData.algstrength=np.ones(N)*params['algstrength'];
    if(params['attstrengthDist']==0):
        agentData.attstrength=np.ones(N)*params['attstrength'];
    elif(params['attstrengthDist']==1):
        agentData.attstrength*=np.random.uniform(0,params['attstrength'],N);

    agentData.reprange=np.ones(N)*params['reprange'];
    agentData.algrange=np.ones(N)*params['algrange'];
    agentData.attrange=np.ones(N)*params['attrange'];

    agentData.repsteepness=np.ones(N)*params['repsteepness'];
    agentData.algsteepness=np.ones(N)*params['algsteepness'];
    agentData.attsteepness=np.ones(N)*params['attsteepness'];

    # set leader interaction parameters
    if(params['leaderCount']>0):
        agentData.repstrength[:params['leaderCount']]=params["leader_repstrength"];
        agentData.algstrength[:params['leaderCount']]=params["leader_algstrength"];
        agentData.attstrength[:params['leaderCount']]=params["leader_attstrength"];
        agentData.sigmap[:params['leaderCount']]=np.ones(params['leaderCount'])*np.sqrt(2.*params['dt']*params["leader_noisep"]);

        agentData.reprange[:params['leaderCount']]=params["leader_reprange"];
        agentData.algrange[:params['leaderCount']]=params["leader_algrange"];
        agentData.attrange[:params['leaderCount']]=params["leader_attrange"];

        agentData.distTarget[:params['leaderCount']]=params['leadingDistance']
        agentData.recruitingSpeed[:params['leaderCount']]=params['recruitingSpeed']


    #check for random interaction range
    for i in range(params['leaderCount']):
        if(agentData.leadershipRange[i]<0):
            agentData.leadershipRange[i]=44.*np.random.random()


def InitAgents(agentData,params):

    #initialize auxiliary noise variables
    agentData.sigmap=np.ones(params['N'])*np.sqrt(2.*params['dt']*params["noisep"]);

    # set agent properties 
    SetInitialCoordinates(agentData,params)
    SetInteractionParameters(agentData,params)
    SetTargetVectors(agentData,params)

    return

def SaveOutData(s,agentData,outdata,params):
    
    if(outdata==None):
        outdata=dict()
        outdata['pos']=[]
        outdata['POS']=[]
        outdata['vel']=[]
        outdata['phi']=[]
        outdata['speed']=[]
        outdata['force']=[]
        outdata['timer_s']=[]
        outdata['t']=[]

    outdata['pos'].append(np.copy(agentData.pos))
    outdata['POS'].append(np.copy(agentData.POS))
    outdata['vel'].append(np.copy(agentData.vel))
    outdata['phi'].append(np.copy(agentData.phi))
    outdata['speed' ].append(np.copy(agentData.speed))
    outdata['force' ].append(np.copy(agentData.force))
    outdata['t'].append(s*params['dt'])

    return outdata

def CalcInteractionGlobal(agentData,params):
    ''' calculate the interaction by simple N^2 loop over all pairs'''
    for i in range(params['N']):
        for j in range(i+1,params['N']):
            CalcInteractionPair(i,j,agentData,params)
    return

def UpdateTotalSocialForce(agentData,params):

    if(params['int_type']=='voronoi'):
        NormalizeByCount(agentData)
    else:
        agentData.NormalizeForces()

    agentData.force=( agentData.repstrength*agentData.force_rep.T
                     +agentData.attstrength*agentData.force_att.T
                     +agentData.algstrength*agentData.force_alg.T).T
   
    return


def UpdateCoordinates(agentData,params):
    ''' update of coordinates for all agents ''' 
    #print(agentData.force[0,0:2])
    dphi=CalculateDirectionChange(agentData,params)
    #calculate new angle
    agentData.phi+=dphi
    # ensure angle between (0,2pi)
    agentData.phi=np.fmod(agentData.phi,2.0*np.pi)
    #  calculate speed updates
    #dspeed = CalculateSpeedChange(agentData,params)
    #agentData.speed+=dspeed

    #update Cartesian velocity vectors and positions
    agentData.UpdateCartesian()
    agentData.pos+=agentData.vel*params['dt']
    agentData.POS+=agentData.vel*params['dt']
    if(params['BC']==0):
        agentData.pos=CalcBoundaryPeriodic(agentData.pos,params['L'])
    if(params['BC']==1):
        agentData=CalcBoundaryReflecting(agentData,params)

    return 

def UpdateLeadership(distmatrix,dX,dY,agentData,params):
    
    for i in range(params['leaderCount']):
        distLeader=distmatrix[i]
        distLeader[distLeader==0]=np.inf
        minDist=np.min(distLeader)
        minIdx=np.argmin(distLeader)
        #print(i)
        #print(distLeader)
        #print("minDists={}".format(minDist))
        #print("minIdx={}".format(minIdx))
        # Calc Target Distance
        if(params['targetType']==0):
                #if(params['leaderCount']>1):
                if(type(agentData.desiredPhi[i])!=None):
                        dirSign=np.sign(np.cos(agentData.desiredPhi[i]))
                        agentData.distTarget[i]=params['leadingDistance']-dirSign*(agentData.POS[i,0]-agentData.initpos[i,0])
                #else:
                #    agentData.distTarget[i]=params['leadingDistance']-(agentData.POS[i,0]-agentData.initpos[i,0])
        else:
                if(np.isnan(agentData.targetVector[i][0])):
                    tidx=0
                else:
                    tidx=i
                agentData.currTargetVector[i]=agentData.targetVector[tidx]-agentData.POS[i]
                #print(params['targetVector'],agentData.POS[i],agentData.initpos[i],targetVector,)
                agentData.distTarget[i]=np.linalg.norm(agentData.currTargetVector[i])

        # Test for switching from leadership to recruiting
        if(agentData.leading[i]==1):
            agentData.speed[i]=params['speed0']
            agentData.force_att[i,0]=0
            agentData.force_att[i,1]=0
            
            #agentData.force_alg[i,:]=np.zeros(2)
            #alignment with x-axis (desired leading direction)
            
            if(params['targetType']==0):
                if(~np.isnan(agentData.desiredPhi[i])):
                    agentData.force_alg[i,0]=agentData.algstrength[i]*( np.cos(agentData.desiredPhi[i])-agentData.uv[i,0])
                    agentData.force_alg[i,1]=agentData.algstrength[i]*( np.sin(agentData.desiredPhi[i])-agentData.uv[i,1])
            else:
                if(~np.isnan(agentData.targetVector[i][0])):
                    targetUnitVector=agentData.currTargetVector[i]/agentData.distTarget[i]
                    agentData.force_alg[i,0]=agentData.algstrength[i]*(targetUnitVector[0]-agentData.uv[i,0])
                    agentData.force_alg[i,1]=agentData.algstrength[i]*(targetUnitVector[1]-agentData.uv[i,1])
                #else:
                #    desPhi=2*np.pi*np.random.random()
                #    targetUnitVector=np.array([np.cos(desPhi),np.sin(desPhi)])
                    

                    


            #print(agentData.force_alg)
            #agentData.force_alg[i,0]=( (1.0-agentData.leadershipWeight[i])*agentData.force_alg[i,0]
            #                         +agentData.leadershipWeight[i]*agentData.algstrength[i]*(np.cos(agentData.desiredPhi[i])-agentData.uv[i,0]) 
            #                         )
            #agentData.force_alg[i,1]=( (1.0-agentData.leadershipWeight[i])*agentData.force_alg[i,0]
            #                         +agentData.leadershipWeight[i]*agentData.algstrength[i]*(np.sin(agentData.desiredPhi[i])-agentData.uv[i,1]) 
            #                         )
            #print(agentData.force_alg[i])
            if(minDist>agentData.leadershipRange[i]):
                agentData.leading[i]=0
                agentData.timer[i]=params['recruitingTime']
                agentData.recruitingIndex[i]=minIdx
                #print("Leader={}: Switching from leadership to recruiting of individual {}".format(i,minIdx))
                agentData.attstrength[i]=params['recruitingAttStrength']
                dist=distmatrix[i,minIdx]
                #agentData.attstrength[i]=params['recruitingAttStrength']*LinearFunc(dist,36,agentData.leadershipRange[i])

        elif(agentData.leading[i]==0):
            agentData.speed[i]=params['recruitingSpeed'];
            j=int(agentData.recruitingIndex[i])
            #print("Updating recruiting force i={}".format(i))
            approachVector_X=-dX[i,j]+2.*params['reprange']*agentData.uv[j,0]
            approachVector_Y=-dY[i,j]+2.*params['reprange']*agentData.uv[j,1]

            #approachVector_X=-dX[i,j]
            #approachVector_Y=-dY[i,j]

            #agentData.force_att[i,0]=-dX[i,j]
            #agentData.force_att[i,1]=-dY[i,j]
            agentData.force_alg[i,0]=0.0
            agentData.force_alg[i,1]=0.0

            agentData.force_att[i,0]=params['leader_attstrength']*approachVector_X
            agentData.force_att[i,1]=params['leader_attstrength']*approachVector_Y

            recrRange=np.min([params['recruitingRange'],agentData.leadershipRange[i]])
            if(distLeader[int(agentData.recruitingIndex[i])]<=recrRange):
                agentData.timer[i]-=params['dt']
                #print("Leader={}: Updating recruitingTimer to: {}".format(i,agentData.timer[i]))
            if( (agentData.timer[i]<0.0) & (distLeader[int(agentData.recruitingIndex[i])]<=params['leadershipRange'])  ):
                agentData.leading[i]=1
                agentData.timer[i]=0
                agentData.attstrength[i]=0.0
                #print("Leader={}: Switching from recruiting to leadership".format(i))


        #print(agentData.leading,agentData.timer)
                
def CheckLeadingDistance(agentData,params,s): 
    for i in range(params['leaderCount']):
        if(agentData.leadingTime[i]<0.0):
            if(agentData.distTarget[i]<params['deltaDistTarget']):
                agentData.leadingTime[i]=s*params['dt']
                print('Target reached!')
                #print("params[leadingDistance]={}".format(params['leadingDistance']))
                print("i={},s={}".format(i,s)) 
                print("agentData.POS[{}]={}".format(i,agentData.POS[i]))
                print("agentData.initpos[{}]={}".format(i,agentData.initpos[i]))
                print("agentData.distTarget[{}]={}".format(i,agentData.distTarget[i]))
                print("agentData.leadingTime[{}]={}".format(i,agentData.leadingTime[i]))
                print("agentData.targetVector[{}]={}".format(i,agentData.targetVector[i]))

    return



###############################################################################################################################################
def CalculateSpeedChange(agentData,params):
    forcev=np.sum(agentData.force*agentData.uv,axis=1)
    dspeed=(params['alpha']*(params['speed0']-agentData.speed)+forcev)*params['dt']

    return dspeed


def CalculateDirectionChange(agentData,params):
    #project forces on polar angle
    forcep=np.sum(agentData.force*agentData.up,axis=1)
    #deterministic increments
    dphi  = forcep*params['dt']
    #add direction noise
    if(params['sigmap']>0.0):
        noiseP=np.random.normal(0.0,agentData.sigmap,size=params['N'])
        dphi  +=noiseP

    #account for inertia 
    dphi/=(agentData.speed+1e-10)

    return dphi

def PeriodicDist(x,y,L=10.0,dim=2):
    ''' Returns the distance vector of two position vectors x,y
        by tanking periodic boundary conditions into account.

        Input parameters: L - system size, dim - no. of dimension
    '''
    distvec=(y-x)
    distvec_periodic=np.copy(distvec)
    distvec_periodic[distvec<-0.5*L]+=L
    distvec_periodic[distvec>0.5*L]-=L

    return distvec_periodic

def SigThresh(x,x0=0.5,steepness=10):
    ''' Sigmoid function f(x)=1/2*(tanh(a*(x-x0)+1)
        
        Input parameters:
        -----------------
        x:  function argument
        x0: position of the transition point (f(x0)=1/2)
        steepness:  parameter setting the steepness of the transition.
                    (positive values: transition from 0 to 1, negative values: 
                    transition from 1 to 0)
    '''
    return 0.5*(np.tanh(steepness*(x-x0))+1)


def LinearFunc(x,xmin,xmax,ymin=0.0,ymax=1.0):
    slope=(ymax-ymin)/(xmax-xmin)
    offset=ymax-slope*xmax
    return x*slope+offset

def CalcDistVecMatrix(pos,L,BC):
    X=np.reshape(pos[:,0],(-1,1))
    Y=np.reshape(pos[:,1],(-1,1))
    dX=np.subtract(X,X.T)
    dY=np.subtract(Y,Y.T)
    if(BC==0):
        dX[dX>+0.5*L]-=L;
        dY[dY>+0.5*L]-=L;
        dX[dX<-0.5*L]+=L;
        dY[dY<-0.5*L]+=L;
    distmatrix=np.sqrt(dX**2+dY**2)
    return distmatrix,dX,dY

def CalcVelDiffVecMatrix(vel):
    VX=np.reshape(vel[:,0],(-1,1))
    VY=np.reshape(vel[:,1],(-1,1))
    dVX=np.subtract(VX,VX.T)
    dVY=np.subtract(VY,VY.T)
    return dVX,dVY

def CalcForceVecMatrix(factormatrix,distmatrix,dX,dY,normalize=True):
    if(normalize):
        with np.errstate(divide='ignore',invalid='ignore'):
            dUX=np.divide(dX,distmatrix)
            dUY=np.divide(dY,distmatrix)
        FX=np.multiply(factormatrix,dUX)
        FY=np.multiply(factormatrix,dUY)
    else:
        FX=np.multiply(factormatrix,dX)
        FY=np.multiply(factormatrix,dY)

    return FX,FY

def CalcAlgVecMatrix(factormatrix,dUX,dUY):
    FX=np.multiply(factormatrix,dUX)
    FY=np.multiply(factormatrix,dUY)
    return FX,FY

def CalcFactorMatrix(distmatrix,force_range,force_steepness):
    #factormatrix=np.int32(distmatrix<force_range)
    
    factormatrix=SigThresh(distmatrix,force_range,force_steepness)
    #factormatrix=np.multiply(force_strength,tmpmatrix)
    return factormatrix

def CalcFactorMatrixZone(distmatrix,force_range_min,force_range_max):
    factormatrix=(distmatrix>force_range_min)*(distmatrix<force_range_max)
    return np.float64(factormatrix)

def CalcDistanceVec(pos_i,pos_j,L,BC,dim=2):
    ''' Convenience function to calculate distance'''
    if(BC==0):
        distvec=PeriodicDist(pos_i,pos_j,L,dim)
    else:
        distvec=pos_j-pos_i

    return distvec

def UniqueEdgesFromTriangulation(tri):
    e1=tri.simplices[:,0:2]
    e2=tri.simplices[:,1:3]
    e3=tri.simplices[:,::2]
    edges=np.vstack((e1,e2,e3))
    edges.sort(axis=0)
    edges_c = np.ascontiguousarray(edges).view(np.dtype((np.void, edges.dtype.itemsize * edges.shape[1])))
    _, idx = np.unique(edges_c, return_index=True)
    edges_unique = edges[idx]
    return edges_unique

def CalcInteractionMatrix(agentData,params):
    distmatrix,dX,dY=CalcDistVecMatrix(agentData.pos,params['L'],params['BC'])
    dVX,dVY=CalcVelDiffVecMatrix(agentData.vel)

    if(params['dist_dependence']=='zone'):
        # Non-overlapping interaction zones - similar to Couzin model
        # repulsion
        factor_M=CalcFactorMatrixZone(distmatrix,0.0,agentData.reprange)
        FX,FY=CalcForceVecMatrix(factor_M,distmatrix,dX,dY)
        agentData.force_rep[:,0]=-np.nanmean(FX,axis=0)
        agentData.force_rep[:,1]=-np.nanmean(FY,axis=0)
        # alignment
        factor_M=CalcFactorMatrixZone(distmatrix,agentData.reprange,agentData.algrange)
        FX,FY=CalcAlgVecMatrix(factor_M,dVX,dVY)
        agentData.force_alg[:,0]=np.nanmean(FX,axis=0)
        agentData.force_alg[:,1]=np.nanmean(FY,axis=0)
        # attraction
        factor_M=CalcFactorMatrixZone(distmatrix,agentData.algrange,agentData.attrange)
        FX,FY=CalcForceVecMatrix(factor_M,distmatrix,dX,dY,normalize=False)
        agentData.force_att[:,0]=np.nanmean(FX,axis=0)
        agentData.force_att[:,1]=np.nanmean(FY,axis=0)
    else:
        # Overlapping interaction regions with 
        # strong repulsion dominating at short distances. 
        # intermediate alignment at intermediate distances
        # weak attraction at large distances
        factor_M=CalcFactorMatrix(distmatrix,agentData.reprange,agentData.repsteepness)
        FX,FY=CalcForceVecMatrix(factor_M,distmatrix,dX,dY)
        agentData.force_rep[:,0]=-np.nanmean(FX,axis=0)
        agentData.force_rep[:,1]=-np.nanmean(FY,axis=0)
        # alignment
        factor_M=CalcFactorMatrix(distmatrix,agentData.algrange,agentData.algsteepness)
        FX,FY=CalcAlgVecMatrix(factor_M,dVX,dVY)
        agentData.force_alg[:,0]=np.nanmean(FX,axis=0)
        agentData.force_alg[:,1]=np.nanmean(FY,axis=0)
        # attraction
        factor_M=CalcFactorMatrix(distmatrix,agentData.attrange,agentData.attsteepness)
        FX,FY=CalcForceVecMatrix(factor_M,distmatrix,dX,dY,normalize=False)
        agentData.force_att[:,0]=np.nanmean(FX,axis=0)
        agentData.force_att[:,1]=np.nanmean(FY,axis=0)
        #print(agentData.force_att)

    return distmatrix,dX,dY 

def CalcInteractionVoronoi(agentData,params):
    from scipy.spatial import Delaunay
    tri=Delaunay(agentData.pos)
    edges=UniqueEdgesFromTriangulation(tri)
    for e in edges:
        if(e[0]!=e[1]):
            CalcInteractionPair(e[0],e[1],agentData,params)
    return edges


def CalcSingleRepForce(i,distvec,dist,agentData):
    repfactor=SigThresh(dist,agentData.reprange[i],agentData.repsteepness[i]);
    agentData.force_rep[i]-=repfactor*distvec;
    agentData.neighbors_rep[i]+=1;
    return

def CalcSingleAlgForce(i,dvel,dist,agentData):
    algfactor=SigThresh(dist,agentData.algrange[i],agentData.algsteepness[i]);
    agentData.force_alg[i]+=algfactor*dvel;
    agentData.neighbors_alg[i]+=1;
    #agentData.force_alg[i,:]=0;
    return

def CalcSingleAttForce(i,distvec,dist,agentData):
    attfactor=SigThresh(dist,agentData.attrange[i],agentData.attsteepness[i]);
    agentData.force_att[i]+=attfactor*distvec;
    agentData.neighbors_att[i]+=1;
    return

def CalcInteractionPair(i,j,agentData,params):
    # calculate distance vector and scalar   
    distvec=CalcDistanceVec(agentData.pos[i],agentData.pos[j],params['L'],params['BC'])
    dist=0.0
    for d in range(2):
        dist+=distvec[d]**2
    dist=np.sqrt(dist);

    #### calculate repulsion ###
    if(agentData.repstrength[i]>0.0):
        CalcSingleRepForce(i,distvec,dist,agentData)
        CalcSingleRepForce(j,-distvec,dist,agentData)
    ############################    
    
    ### calculate alignment ###
    if(agentData.algstrength[i]>0.0):
        dvel=agentData.vel[j]-agentData.vel[i]
        CalcSingleAlgForce(i,+dvel,dist,agentData)
        CalcSingleAlgForce(j,-dvel,dist,agentData)
    ############################    

    ### calculate attraction ###
    if(agentData.attstrength[i]>0.0):
        CalcSingleAttForce(i,distvec,dist,agentData)
        CalcSingleAttForce(j,-distvec,dist,agentData)
    ############################    
    return

def NormalizeByCount(agentData):

    #repulsion
    idx_non_zero_count=np.nonzero(agentData.neighbors_rep)[0]
    agentData.force_rep[idx_non_zero_count]/=agentData.neighbors_rep[idx_non_zero_count]
    #alignment
    idx_non_zero_count=np.nonzero(agentData.neighbors_alg)[0]
    agentData.force_alg[idx_non_zero_count]/=agentData.neighbors_alg[idx_non_zero_count]
    #alignment
    idx_non_zero_count=np.nonzero(agentData.neighbors_att)[0]
    agentData.force_att[idx_non_zero_count]/=agentData.neighbors_att[idx_non_zero_count]

    return

def CalcBoundaryPeriodic(pos,L):

    posx=pos[:,0]
    posy=pos[:,1]

    posx[posx>L]=posx[posx>L]-L 
    posy[posy>L]=posy[posy>L]-L 
    posx[posx<0.0]=posx[posx<0.0]+L 
    posy[posy<0.0]=posy[posy<0.0]+L 

    pos[:,0]=posx
    pos[:,1]=posy

    return pos

def CalcBoundaryReflecting(agentData,params):

    L=params['L']
    posx=agentData.pos[:,0]
    posy=agentData.pos[:,1]

    velx=agentData.vel[:,0]
    vely=agentData.vel[:,1]

    ##elastic
    #velx[posx>L]*=-1.0; 
    #vely[posy>L]*=-1.0; 
    #velx[posx<0]*=-1.0; 
    #vely[posy<0]*=-1.0; 
    #inelastic
    velx[posx>L]*=0.0; 
    vely[posy>L]*=0.0; 
    velx[posx<0]*=0.0; 
    vely[posy<0]*=0.0; 


    posx[posx>L  ]= 2*L-posx[posx>L] 
    posy[posy>L  ]= 2*L-posy[posy>L] 
    posx[posx<0.0]=-posx[posx<0.0] 
    posy[posy<0.0]=-posy[posy<0.0] 


    agentData.pos[:,0]=posx
    agentData.pos[:,1]=posy
    agentData.phi = np.arctan2(vely,velx)

    agentData.vel[:,0]=params['speed0']*np.cos(agentData.phi)
    agentData.vel[:,1]=params['speed0']*np.sin(agentData.phi)

    return agentData

def CalcPolarization(phi):
    ux=np.cos(phi)
    uy=np.sin(phi)
    mean_ux=np.mean(ux)
    mean_uy=np.mean(uy)
    return np.sqrt(mean_ux**2+mean_uy**2)

def CalcLeadingPerformance(outdata,params,ignore_timepoints=0,verbose=True):

    ignore_points=int(ignore_timepoints/params['output'])
    pos=np.array(outdata['pos'][ignore_points:])
    POS=np.array(outdata['POS'][ignore_points:])
    
    ignore_points=int(ignore_timepoints/params['dt'])
    #print(ignore_points)
    leadRecord=np.array(outdata['leadingRecord'])[:,ignore_points:]
    avgdist_leader=np.nan*np.ones(params['leaderCount'])
    all_avgdeltaPos=[]
    all_avgdeltaTarget=[]
    all_avgdist=[]
    tot_avgdist=[]
    all_finaldist=[]
    tot_finaldist=[]
    all_finalx=[]
    all_finaly=[]
    
    ##########################################################################
    # calculate cohesion (avg distance to leader)
    for i in range(params['leaderCount']):
        alldistvec_alltimes=POS[:,:,:]-POS[:,i:i+1,:]
        alldist_alltimes=np.linalg.norm(alldistvec_alltimes,axis=2)
        alldist_timeavg=np.delete(np.mean(alldist_alltimes,axis=0),i)
        #dist_array_timeavg=np.delete(dist_array_timeavg,i)
        all_avgdist.append(alldist_timeavg)
        tot_avgdist.append(np.mean(alldist_timeavg))

        #print(np.shape(alldist_alltimes))
        all_finaldist.append(np.delete(alldist_alltimes[-1,:],i))
        tot_finaldist.append(np.mean(all_finaldist[-1]))
        
    outdata['all_avgdist']=all_avgdist
    outdata['tot_avgdist']=tot_avgdist
    outdata['all_finaldist']=all_finaldist
    outdata['tot_finaldist']=tot_finaldist
    
    ##########################################################################
    # calculate average leading ratio over whole time series
    leadRatio=np.sum(leadRecord,axis=1)/len(leadRecord[0])
    outdata['leadRatio']=np.array(leadRatio)

    ##########################################################################
    # calculate average displacement 
    #########################################################################
    VEL=np.gradient(POS,axis=0)/params['output']
    SPEED=np.linalg.norm(VEL,axis=2)
    all_displacement_vec=POS[-1,:,:]-POS[0,:,:]
    avg_displacement_vec=np.mean(all_displacement_vec,axis=0)
    if(params['targetType']==0):
        targetDistance=np.inf
        Vel2Target=np.inf
        #fish_displacement=np.mean(all_displacements[params['leaderCount']:],axis=0)
        #lead_displacement=all_displacements[:params['leaderCount']]

    else:
        targetVector=params['targetVectorList'][0]
        targetDistance=np.linalg.norm(targetVector)
        targetUnitVector=targetVector/targetDistance
        all_displacements=np.linalg.norm(np.multiply(all_displacement_vec,targetUnitVector),axis=1)

        finalVecToTarget=params['targetVector']-POS[-1]
        finalDistToTarget=np.linalg.norm(finalVecToTarget,axis=1)


        ############### Local displacements ################################
        targetDirection=targetVector-POS
        targetDist = np.linalg.norm(targetDirection,axis=2)
        targetDirection[:,0,:]=(targetDirection[:,0,:].T/targetDist[:,0]).T
        targetDirection[:,1,:]=(targetDirection[:,1,:].T/targetDist[:,1]).T
        dotProduct=np.multiply(VEL,targetDirection)
        Vel2Target=np.sum(dotProduct,axis=2)
    
    avg_vel2target=np.nanmean(Vel2Target,axis=0)
    avg_displacement =np.nanmean(all_displacements,axis=0)
    outdata['avg_vel2target']=avg_vel2target
    outdata['all_displacements_vec']=all_displacement_vec
    outdata['avg_displacements_vec']=avg_displacement_vec
    outdata['all_displacements']=all_displacements
    outdata['avg_displacement' ]=avg_displacement

    if(params['targetType']<2):
        outdata['finalDistToTarget']=np.nan
    else:
        outdata['finalDistToTarget']=finalDistToTarget

    targetVectorList=params['targetVectorList']
    for i in range(len(targetVectorList)):
        outdata['targetMovement{}'.format(i)]=CalcMovementSuccess(outdata['POS'],params,targetVectorList[i])

    if(verbose):
        for i in range(params['leaderCount']):
            print("-----------------------------------")
            print("Leader i={}".format(i))
            print("-----------")
            print("all_avgdist      = {}".format(outdata['all_avgdist'][i]))
            print("tot_avgdist      = {}".format(outdata['tot_avgdist'][i]) )     
            print("all_finaldist    = {}".format(outdata['all_finaldist'][i]))
            print("tot_finaldist    = {}".format(outdata['tot_finaldist'][i]) )     
            print("leadRatio        = {}".format(outdata['leadRatio'][i]))
            print("leadingTime      = {}".format(outdata['leadingTime'][0]))
            print("finalDistToTarget= {}".format(outdata['finalDistToTarget']))
            print("leadingSuccess   = {}".format(1-outdata['finalDistToTarget']/targetDistance))
            print("lead_displacement = {}".format(outdata['all_displacements'][i]))
            print("-----------------------------------")
        
            #if(params['targetType']==1):
            #    print("proj_lead_displacements = {}".format(outdata['proj_lead_displacements'][i]))
            #    print("proj_fish_displacements = {}".format(outdata['proj_fish_displacements']))
            #    print("-----------------------------------")
        if(params['targetType']):
            print("Target Unit Vector:",targetUnitVector)
            

    return #outdata


def SingleRunHelper(simdata):
    outdata=SingleRun(simdata[0],simdata[1])
    return outdata

def SingleRun(params,agentData=None):
    print("Performing a single run.")

    if(agentData==None):
        print("agentData not provided - setting to default") 
        agentData=AgentData(params)
        InitAgents(agentData,params) 

    outdata=SaveOutData(0,agentData,None,params)
    if(params['BC']==-2):
        initialPosLeader=np.copy(agentData.pos[:params['leaderCount']])
        print("initialPosLeader={}".format(initialPosLeader))


    outstep=0
    agentData.initpos=np.copy(agentData.pos)
    for s in range(1,params['steps']+1):
        agentData.ResetForces()
        
        distmatrix,dX,dY=CalcInteractionMatrix(agentData,params)

        UpdateLeadership(distmatrix,dX,dY,agentData,params)
        UpdateTotalSocialForce(agentData,params)
        #print(agentData.force[0:2])
        if(params['leaderCount']>0):
            agentData.leadingRecord[:params['leaderCount'],s-1]=agentData.leading[:params['leaderCount']]
        UpdateCoordinates(     agentData,params)
        
        if((s % params['stepout'])==0):
            #print('t=%02f' % (para.dt*s))
            outdata=SaveOutData(s,agentData,outdata,params)
            outstep+=1

        CheckLeadingDistance(agentData,params,s)
        #if(params['BC']==-2):
        if(params['BC']!=0):
            leadNo=len(params['targetVectorList'])
            if(np.all(agentData.leadingTime[:leadNo]>0.0)):
                if(np.all(agentData.leadingTime[:params['leaderCount']]>0.0)):
                    print("Distance to target {} reached by all leading agents. Stopping Simulation.".format(params['deltaDistTarget']))
                    print(agentData.leadingTime[:params['leaderCount']])
                    print("Stopping time:",s*params['dt'])
                    break;
                elif( (s*params['dt']-np.max(agentData.leadingTime[:leadNo]))>30.0):
                    print("Distance to target {} reached by all leaders + 30s extra time for naive leaders. Stopping Simulation.".format(params['deltaDistTarget']))
                    print("Stopping time:",s*params['dt'])
                    agentData.leadingTime[agentData.leadingTime<0.0]=s*params['dt']
                    print(agentData.leadingTime[:params['leaderCount']])
                    break;

    if(params['BC']!=0) :
        finalPosLeader=np.copy(agentData.pos[:params['leaderCount']])
        print("finalStep={}, finalPosLeader={}".format(s,finalPosLeader))
        #print("deltaPosLeader={}".format(deltaPosLeader))

    outdata['finalStep']=s
    outdata['finalOutStep']=outstep

    if(params['leaderCount']>0):
        outdata['leadingRecord']=agentData.leadingRecord[:,:s]
        outdata['leadingTime']=agentData.leadingTime
    print('Done!')
    return outdata 


def CreateDictEntriesForArrayData(dataDict,dataKey,dataArray):
   
    dataArray=np.array(dataArray,ndmin=1)
    #print(dataKey,dataArray)

    
    for n in range(len(dataArray)):
        #print(dataArray,n)
        key=dataKey+'{}'.format(n)
        dataDict[key]=[dataArray[n]]

    return dataDict


def CalcMovementSuccess(pos,params,targetVector):
    initTargetVec    =targetVector-pos[0]
    initTargetUnitVec=initTargetVec/np.linalg.norm(initTargetVec,axis=1)
    #print(initTargetUnitVec)
    displacementVector=pos[-1]-pos[0]
    displacementToTargetVec=np.multiply(displacementVector,initTargetUnitVec)
    #print(displacementToTargetVec)
    displacementToTarget=np.sum(np.multiply(displacementVector,initTargetUnitVec),axis=1)
    #print(displacementToTarget)
    maximalDistance=params['speed0']*params['time']
    movementSuccess=displacementToTarget/maximalDistance
    return movementSuccess
    

def ProcessParallelResults(para1name,para2name,para_list,outdata_list,outpath="./results.h5",ignore_timepoints=0):

    #columns=[para1name,para2name,"run","leadRatio","tot_avgdist","tot_finaldist","avg_displacement","tot_time","leadingTime","lead_displacement","fish_displacement"]
    #df=pd.DataFrame(columns=columns)

    df=None
    print("Starting type dataFrame=",type(df))
    for i in range(len(para_list)):
        CalcLeadingPerformance(outdata_list[i],para_list[i],ignore_timepoints=ignore_timepoints,verbose=False)
        dataLine=collections.OrderedDict()
        para1value=para_list[i][para1name]
        para2value=para_list[i][para2name]
        if(para1name=='leadershipRangeList'):
            dataKey='leadershipRange'
        else:
            dataKey=para1name
        dataLine=CreateDictEntriesForArrayData(dataLine,dataKey,para1value)
        #if(para2name=='leadershipRangeList'):
        #    dataKey='leadershipRange'
        dataLine=CreateDictEntriesForArrayData(dataLine,para2name,para2value)

        dataLine['run']=para_list[i]['run']
        dataLine=CreateDictEntriesForArrayData(dataLine,'leadRatio',  outdata_list[i]['leadRatio'])
        dataLine=CreateDictEntriesForArrayData(dataLine,'tot_avgdist',outdata_list[i]['tot_avgdist'])
        dataLine=CreateDictEntriesForArrayData(dataLine,'tot_finaldist', outdata_list[i]['tot_finaldist'])
        dataLine=CreateDictEntriesForArrayData(dataLine,'avg_displacement',outdata_list[i]['avg_displacement'])
        dataLine=CreateDictEntriesForArrayData(dataLine,'finalDistToTarget',outdata_list[i]['finalDistToTarget'])
        dataLine=CreateDictEntriesForArrayData(dataLine,'avg_vel2target',outdata_list[i]['avg_vel2target'])
        targetVectorList=para_list[i]['targetVectorList']
        for j in range(len(targetVectorList)):
            key='targetMovement{}'.format(j)
            dataLine=CreateDictEntriesForArrayData(dataLine,key,outdata_list[i][key])

        #dataLine[para2name]=para_list[i][para2name]
        #dataLine['leadRatio']    = np.mean(outdata_list[i]['leadRatio'])
        #dataLine['tot_avgdist']  = np.mean( outdata_list[i]['tot_avgdist']   )
        #dataLine['tot_finaldist']= np.mean( outdata_list[i]['tot_finaldist'] )

        #dataLine['avg_displacement']  = np.mean(outdata_list[i]['avg_displacement'])
        #dataLine['lead_displacement'] = np.mean(outdata_list[i]['lead_displacement'])
        #dataLine['fish_displacement'] = np.mean(outdata_list[i]['fish_displacement'])

        #dataLine['avg_FinalDistToTarget']=np.mean(outdata_list[i]['avg_FinalDistToTarget'])
        #dataLine['avg_FollowerFinalDistToTarget']=np.mean(outdata_list[i]['avg_FollowerFinalDistToTarget'])

        dataLine['tot_time']=[outdata_list[i]['finalStep']*para_list[i]['dt']]
        dataLine=CreateDictEntriesForArrayData(dataLine,'leadingTime',outdata_list[i]['leadingTime'])
        
        df_dataLine=pd.DataFrame.from_dict(dataLine)

        if(type(df)==type(None)):
            #print(dataLine)
            df=df_dataLine
        else:
            df=pd.concat([df,df_dataLine],ignore_index=True)

    df.to_hdf(outpath,key=para1name+"_"+para2name)

    return df



def RunParallelScan(para1name,para2name,para1values,para2values,runs=1,params=None,agentData=None,n_proc=4):

    if(params==None):
        print("No params provided!!! Initializing default params.")
        params=InitParams()
    if(agentData==None):
        print("No agentData provided set!!! Initializing default array.")
        agentData=AgentData(params)
        InitAgents(agentData,params)

    simdata_list=[]
    params_list=[]
    for p1 in para1values:
        for p2 in para2values:
            for r in range(runs):
                tmp_params=params.copy()
                tmp_params[para1name]=p1
                #print(para1name,tmp_params[para1name])
                #if( (para1name=="leadershipRangeList") & (params['attstrengthDist'])):
                #    tmp1=p1[1]+p1[1]*np.random.random()
                #    print(tmp1)
                #    tmp_params[para1name]=[p1[0],tmp1]
                #tmp_params['recruitingAttStrength']=params['recruitingAttStrength']*np.random.random()
                tmp_params[para2name]=p2
                tmp_params['run']=r
                tmp_agentData=AgentData(tmp_params)
                InitAgents(tmp_agentData,tmp_params)
                params_list.append(tmp_params)
                simdata_list.append([tmp_params,tmp_agentData])


    #outdata_list=[]
    #for simdata in simdata_list:
    #    print(simdata[0])
    #    outdata=SingleRunHelper(simdata)
    #    outdata_list.append(outdata)
    pool=mp.Pool(processes=n_proc) 
    outdata_list=pool.map(SingleRunHelper,simdata_list)

    return outdata_list,params_list
            


def SingleRunVoronoi(params,agentData=None):
    if(agentData==None):
        agentData=AgentData(params)
        InitAgents(agentData,params) 

    outdata=SaveOutData(0,agentData,None,params)

    for s in range(1,params['steps']+1):
        agentData.ResetForces()
        edges=CalcInteractionVoronoi(agentData,params)
        UpdateCoordinates(agentData,params)
        UpdateTotalSocialForce(agentData,params)
        
        if((s % params.stepout)==0):
            outdata=SaveOutData(s,agentData,outdata,params)
    #print('Done!')
    return outdata



def MakeMovie(outdata,params,parallel=parallel):
    if(parallel):

        no_of_threads=mp.cpu_count();
        print("Generating frames for movie using {} threads".format(no_of_threads))
        pool=mp.Pool(no_of_threads)
        gen_frame=partial(PlotFrame,outdata,params)
        time_array=np.arange(params['outsteps'])
        #print(time_array)
        pool.map(gen_frame,time_array)
        pool.close()
    else:
        for s in range(params['outsteps']):
            PlotFrame(outdata,params,s)

    enc_codec='mpeg4'
    moviefile='animation.mp4'
    ffmpeg_command='ffmpeg -framerate 30 -i f%04d.png -c:v '+enc_codec+' -pix_fmt yuv420p '+moviefile
    print(ffmpeg_command)
    try:
        os.system(ffmpeg_command)
    except:
        print("Encoding video failed. Is ffmpeg installed correctly?")

    return

def PlotFrame(outdata,params,s):
    
    tail_length=5
    pl.figure(figsize=(8,8))
    pl.subplot(aspect='equal')
    pl.xlim(0, params['L'])
    pl.ylim(0, params['L'])
    x=outdata['pos'][s][:,0]
    y=outdata['pos'][s][:,1]

    pl.plot(x, y, 'ro')
    if(s>tail_length):
        postail=np.array(outdata['pos'][s-tail_length:s])
        xtail=np.reshape(postail[:,:,0],(-1,1))
        ytail=np.reshape(postail[:,:,1],(-1,1))
        pl.plot(xtail, ytail, 'r.')

    pl.title('t={}'.format(params['output']*s))
    #pl.tight_layout()
    pl.savefig('f%04d.png' % s,dpi=300)
    #pl.clf()


    pl.close()

    return


def RunAnimate(params,agentData=None,doblit=False):
    if(type(agentData)==type(None)):
        agentData=AgentData(params)
        InitAgents(agentData,params)

    figsize=12
    fig=pl.figure(99,figsize=(figsize,figsize))
    ax = pl.subplot()
    ax.set_aspect('equal')
    ax.set_xlim(0, params['L'])
    ax.set_ylim(0, params['L'])
    #ax.hold(True)

    x=agentData.pos[:,0]
    y=agentData.pos[:,1]
    pl.show(False)
    pl.draw()
    points = ax.plot(x, y, 'ro')[0]
    if(params['leaderCount']>0):
        pointLeader = ax.plot(x[:params['leaderCount']], y[:params['leaderCount']], 'bo')[0]
        pointRecruiter = ax.plot(-1000*np.ones(params['leaderCount']),-1000*np.ones(params['leaderCount']), 'mo')[0]


    pointstail = ax.plot(x, y, 'r.',alpha=0.2)[0]

    if doblit:
        # cache the background
        background = fig.canvas.copy_from_bbox(ax.bbox)

    outdata=SaveOutData(0,agentData,None,params)
    #if(params.int_type=='global'):
    #    edges=[]
    #    for i in range(params.N):
    #        for j in range(i,params.N):
    #            edges.append([i,j])

    for s in range(1,params['steps']+1):
        agentData.ResetForces()
        if(params['int_type']=='global'):
            CalcInteractionGlobal(agentData,params)
        elif(params['int_type']=='matrix'):
            distmatrix,dX,dY=CalcInteractionMatrix(agentData,params)
        elif(params['int_type']=='voronoi'):
            edges=CalcInteractionVoronoi(agentData,params)
            distmatrix=None;

        UpdateLeadership(distmatrix,dX,dY,agentData,params)
        UpdateTotalSocialForce(agentData,params)
        agentData.leadingRecord[:params['leaderCount'],s-1]=agentData.leading[:params['leaderCount']]
        UpdateCoordinates( agentData,params)
        
        if((s % params['stepout'])==0):
            print('t=%02f' % (params['dt']*s))
            
            outdata=SaveOutData(s,agentData,outdata,params)
            x=agentData.pos[:,0]
            y=agentData.pos[:,1]
            if(params['output']<1.0):
                tail_length=int(3./(params['output']))
            else:
                tail_length=5
            postail=np.array(outdata['pos'][-tail_length:-1])
            xtail=np.reshape(postail[:,:,0],(-1,1))
            ytail=np.reshape(postail[:,:,1],(-1,1))

            points.set_data(x, y)
            pointstail.set_data(xtail,ytail)

            if(params['leaderCount']>0):
                xL=x[:params['leaderCount']]
                yL=y[:params['leaderCount']]
                pointLeader.set_data(xL,yL)
                xR=np.copy(xL)
                yR=np.copy(yL)
                print(agentData.leading)
                lCount=len(xR[agentData.leading==1])
                if(lCount>0):
                    xR[agentData.leading==1]=-1000*np.ones(lCount)
                    yR[agentData.leading==1]=-1000*np.ones(lCount)
                
                pointRecruiter.set_data(xR,yR)
            if(params['BC']<0):
                meanx=np.mean(x)
                meany=np.mean(y)
                ax.set_xlim(meanx-0.5*params['L'],meanx+0.5*params['L'])
                ax.set_ylim(meany-0.5*params['L'],meany+0.5*params['L'])

            if doblit:
                # restore background
                fig.canvas.restore_region(background)

                # redraw just the points
                ax.draw_artist(points)

                # fill in the axes rectangle
                fig.canvas.blit(ax.bbox)

            else:
                # redraw everything
                ax.set_title('t=%02f' % (params['dt']*s))
                fig.canvas.draw()

    #raw_input("Press Enter to continue...")
    pl.close(fig)

    return outdata,agentData 

    



