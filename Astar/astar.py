import numpy as np
import Queue
#import utils
from math import *
import sys, select, os

class state:
    def __init__(self,x,y,theta,phi):
        self.x = x;
        self.y = y;
        self.theta = theta;
        self.phi = phi;
    def __str__(self):
        return str(self.x) + ', '+str(self.y) + ', '+str(self.theta) + ', '+str(self.phi)

    def stateUpdate(self,v,t,L,dphi):
        # Equations of motion for the car
        newx = self.x-v*cos(self.theta+pi/2)*t
        newy = self.y-v*sin(self.theta+pi/2)*t
        newtheta = self.theta + (-v/L)*tan(self.phi)*t
        newphi = self.phi+dphi
        return state(newx,newy,newtheta,newphi)
    def getXYTheta(self):
        return tuple((self.x,self.y,self.theta))

class Astar:
    # connect8 = [(-1,0,-1),#(-1,1,-1),(-1,-1,-1),
    #             (0,-1,-1),(0,0,-1),(0,1,-1),
    #             (1,0,-1),#(1,1,-1),(1,-1,-1),
    #             (-1,-1,0),(-1,0,0),#(-1,1,-1),
    #             (0,-1,0),(0,1,0),
    #             (1,-1,0),(1,0,0),(1,1,0),
    #             (-1,0,1),#(-1,1,1),(-1,-1,1),
    #             (0,-1,1),(0,0,1),(0,1,1),
    #             (1,0,1)#,(1,1,1),(1,-1,1)]
    connect8 = [(-1,-1,-1),(-1,0,-1),(-1,1,-1),
                (0,-1,-1),(0,0,-1),(0,1,-1),
                (1,-1,-1),(1,0,-1),(1,1,-1),
                (-1,-1,0),(-1,0,0),(-1,1,-1),
                (0,-1,0),(0,1,0),
                (1,-1,0),(1,0,0),(1,1,0),
                (-1,-1,1),(-1,0,1),(-1,1,1),
                (0,-1,1),(0,0,1),(0,1,1),
                (1,-1,1),(1,0,1),(1,1,1)]
    #connect8 = [(-1,0,0),(-1,1,0),(0,1,0),(1,1,0),(1,0,0),(1,-1,0),(0,-1,0),(-1,-1,0),(0,0,1),(0,0,-1)]
    connect4 = [(-1,0,0),(0,1,0),(1,0,0),(0,-1,0),(0,0,1),(0,0,-1)]


    def h_manhattan(self,node):
        '''Returns manhattan distance from node to destination'''
        #print node
        #print self.destination

        return abs(node.x-self.destination.x) + abs(node.y-self.destination.y) + abs(node.theta -self.destination.theta)
    def h_euclidean(self,node):
        '''Returns Euclidean distance from node to destination'''
        return ((node.x-self.destination.x)**2.0 + (node.y-self.destination.y)**2.0 + ((node.theta -self.destination.theta))**2.0)**0.5

    def __init__(self,stepsize,heuristics,v, collisionCheck,maxBranch,steeringSpeed,steeringLimit,L):
        self.steeringLimit = steeringLimit

        self.maxBranch = maxBranch
        if maxBranch %2 == 0:
            self.maxBranch-=1;# Must be an odd number of branches to always contain straight line in middle
        self.stepsize = stepsize
        self.maxSteering = min(float(steeringSpeed)/stepsize,steeringLimit);
        self.steeringStep = float(self.maxSteering*2)/(self.maxBranch-1)

        self.baseSteeringSteps = np.zeros(self.maxBranch)
        for i in range(self.maxBranch):
            self.baseSteeringSteps[i]=self.steeringStep*i
        print self.baseSteeringSteps
        self.baseSteeringSteps-=self.maxSteering
        print self.baseSteeringSteps
        self.v = v #car speed
        self.steeringLimit = steeringLimit
        self.L = L

        #destination[2] = destination[2]%(2*math.pi)

        #Pointer to the function collisionCheck that will be used
        self.collisionCheck = collisionCheck
        #print self.collisionCheck

        # if connectMode == 4:
        #     self.connect = self.connect4
        # else:
        #     self.connect = self.connect8
        if heuristics == "manhattan":
            self.h = self.h_manhattan
        elif heuristics == "euclidean":
            self.h = self.h_euclidean
        # self.draw = draw

    # def neighbors(self,parent):
    #     # Define steeringLimit
    def neighbors(self,parent):
        neighbors = []
        for i in range(self.baseSteeringSteps.size):
            if abs(parent.phi + self.baseSteeringSteps[i]) < self.steeringLimit:
                neighborCandidate = parent.stateUpdate(self.v,self.stepsize,self.L,self.baseSteeringSteps[i])
                if neighborCandidate not in self.c_visited:
                    self.c_visited.append(neighborCandidate)
                    if not self.collisionCheck(neighborCandidate):
                        cost = self.v*self.stepsize
                        neighbors.append((neighborCandidate,cost))
        return neighbors


        # #print range(-self.radius,self.radius+1,1)
        #
        # for (i,j,k) in self.connect:
        #     node = (round(parent[0]+i*self.stepsize[0],ndigits=3),
        #             round(parent[1]+j*self.stepsize[1],ndigits=3),
        #             ((parent[2]+k*self.stepsize[2])%(2*math.pi))
        #             )
        #     #drawnode = (node[0],node[1],0.03)
        #     if not self.collisionCheck(node):
        #         cost = 0.0
        #         # if abs(i) + abs(j) != 1:
        #         #     diagnode1 = (parent[0] + self.stepsize[0],parent[1],parent[2],node[2])
        #         #     diagnode2 = (parent[0],parent[1]+self.stepsize[1],parent[2],node[2])
        #         #     if self.collisionCheck(diagnode1) or self.collisionCheck(diagnode2):
        #         #         if drawnode not in self.c_visited:
        #         #             #self.c_visited.append(node)
        #         #             self.draw(drawnode,np.array(((1.0,0.0,0.0))))
        #         #         continue
        #         if node not in self.c_visited:
        #             # self.draw(drawnode,np.array(((0.5,0.5,1.0))))
        #             self.c_visited.append(node)
        #         cost = ((i*self.stepsize[0])**2.0 + (j*self.stepsize[1])**2.0 + (k*self.stepsize[2])**2.0 )**0.5
        #         #print cost
        #         neighbors.append((node,cost))
        #     #else:
        #         #if node not in self.c_visited:
        #             #self.draw(drawnode,np.array(((1.0,0.0,0.0))))
        #             #self.c_visited.append(drawnode)
        # #print neighbors
        # return neighbors

    def checkClose(self,current):
        delta = 0.1;
        dx = abs(self.destination.x - current.x)
        dy = abs(self.destination.y - current.y)
        dt = abs(self.destination.theta - current.theta)
        d = sqrt(dx**2 +dy**2+ dt**2)
        if d < 2*self.v*self.stepsize:
            self.stepsize/=1.01
        else:
            self.stepsize*=1.001
        print d
        return d < delta
    def search(self,current,destination):
        self.current = current
        self.destination = destination
        self.frontier = Queue.PriorityQueue()
        #print self.current
        self.frontier.put((0,self.current))
        self.came_from = {}
        self.cost = {}
        self.came_from[self.current] = None
        self.cost[self.current]= 0
        self.f_visited = []
        self.c_visited = []
        total = 0
        while not self.frontier.empty():
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                return False
            total +=1

            #print self.frontier
            p = self.frontier.get()
            current = p[1]
            self.f_visited.append(current)
            #print p[0]
            #print current
            if self.checkClose(current):
                #Withing the acceptance limit, it's close enough to say it's the desired goal
                self.destination = current
                #print 'got it', self.getPath()
                #print total
                return self.getPath()#,self.f_visited,self.c_visited
            for nextmove,cost in self.neighbors(current):
                #print nextmove
                #print self.destination
                #print np.isclose(nextmove,self.destination)
                #print len ([i for i in np.isclose(nextmove,self.destination) if i == True])== len(current)
                #raw_input("Press enter to continue...")
                nextcost = self.cost[current] + cost
                if nextmove not in self.cost or nextcost < self.cost[nextmove]:
                    self.cost[nextmove] = nextcost
                    priority = nextcost*0.2 + 0.8*self.h(nextmove)
                    self.frontier.put((priority,nextmove))
                    self.came_from[nextmove] = current
                #raw_input("Press enter to continue...")

        #print 'ops',self.current, self.destination
        return False


    def getPath(self):
        current = self.destination
        path = []
        while current != self.current:
            # print current
            path.append(current)
            current = self.came_from[current]
        path.reverse()
        return path
