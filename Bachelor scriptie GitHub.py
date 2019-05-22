from heapq import heappush, heappop
import pandas as pd  
from statistics import mean
import matplotlib.pylab as plt
import numpy as np

stack = []

ARRIVAL = 0 
DEPARTURE = 1

class Job:
    def __init__(self, i):
        self.id = i

    def __lt__(self, other):
        return self.id < other.id 
    
numberOfStations = int(input('What is the number of stations?'))

hoi = 1
#define these lists to obtain the output
StartTimes =[[] for i in range(1,numberOfStations+1)] 
DepartureTimes =[[] for i in range(1,numberOfStations+1)]
WhichServer =[[] for i in range(1,numberOfStations+1)]

class Single_server_station:
    def __init__(self, S,stationName,name):
        self.free = True
        self.queue = []
        self.service_time = S
        self.stationName = stationName 
        self.name = name #name is the name of the server in the station, e.g. 1.2

    def handle_arrival(self, time, job):
        if self.free:
            self.take_into_service(time, job)
        else:
            self.queue.append(job)

    def take_into_service(self, time, job):
        self.free=False
        dep_time = time + self.service_time
        heappush(stack, (dep_time, job, self, DEPARTURE))
        for n in range(0,numberOfStations): #to collect the output
            if str(n+1) == self.stationName:
                StartTimes[n].append(time)
                DepartureTimes[n].append(dep_time)    

    def handle_departure(self, time, job):
        self.free = True
        if self.queue:
            new_job = self.queue.pop(0)
            self.take_into_service(time, new_job)

    def check_queue(self,time):
        pass
                 
class Multiple_Station:
    def __init__(self,name):
        self.stations=[]
        self.queue = []
        self.best=""
        self.name = name
        
    def extend(self,S):
        self.stations.extend(S)
        
    def find_best_station(self): #find the station which is free and has shortest service time
        self.best = ""
        for station in self.stations:                
            if station.free == True:
                if self.best == "":
                    self.best = station
                else:
                    if station.service_time < self.best.service_time:
                        self.best = station
        return self.best
        
    def handle_arrival(self,time,job):
        self.find_best_station()
        if self.best != "":
            self.best.handle_arrival(time, job)
        else:
            self.queue.append(job)
            
    def check_queue(self,time):
        if self.queue:
            new_job = self.queue.pop(0)
            self.handle_arrival(time,new_job)
            
    def handle_departure(self, time, job):
        if self.queue:
            self.find_best_station()
            if self.best != "":
                new_job = self.queue.pop(0)
                self.best.take_into_service(time, new_job)
                
stations = []
for n in range(numberOfStations):
    numServers = int(input('How many servers has station %d? '%(n+1)))
    stationToAdd = Multiple_Station(name=str(n+1))
    for s in range(1,numServers+1):
        service_time = float(input('What is the service time of station %d server %d? '%((n+1),s)))
        stationToAdd.extend([Single_server_station(service_time,stationName=str(n+1),name='%d.%d'%(n+1,s))])
    stations.append(stationToAdd)

jobID = []
def initialization(numberArrivals):
    for i in range(1,numberArrivals+1):
        jobID.append(i)
        job = Job(i)
        heappush(stack, (0., job, stations[0], ARRIVAL))

ArrivalTimes =[[] for i in range(1,numberOfStations+1)]

RoutingMatrix = [] 

for i in range(numberOfStations):
    RoutingRow = []
    for j in range(numberOfStations):
        JobFromItoJ = float(input('What is the probability of a job to go from station %d to station %d? '%((i+1),(j+1))))
        RoutingRow.append(JobFromItoJ)
    if sum(RoutingRow)>1:
        print('ERROR, The probabilities do not add up to 1')
        break
    RoutingMatrix.append(RoutingRow)
  
def Routing(station,ProbStation):
    randomU = np.random.uniform(0,1,1)
    ReturnStation=""
    for i in range(0,numberOfStations):
        lowerbound = 0
        upperbound = 0 
        for n in range(i): 
            lowerbound = lowerbound + ProbStation[n]
        for n in range(i+1):
            upperbound = upperbound + ProbStation[n]
        if randomU[0] > lowerbound and randomU[0] <= upperbound:
            ReturnStation= stations[i]
            break
        else:
            ReturnStation= stations[-1] 
    return ReturnStation

    
def run(N=10000,numberArrivals=10):
    initialization(numberArrivals)
    iterations = 0
    
    while iterations < N:
        if stack:
            event = heappop(stack)
            time,job, station, typ = event
            if typ == ARRIVAL:
                ArrivalTimes[0].append(time)
                station.handle_arrival(time, job)
            else:
                station.handle_departure(time, job)
                for p in range(0,numberOfStations-1):
                    if station.stationName==str(p+1):
                        ArrivalTimes[p+1].append(time)
                        toStation = Routing(station,RoutingMatrix[p])
                        toStation.handle_arrival(time,job)
        for station in stations:
            station.check_queue(time)
            
        iterations +=1


def graphs(TotalNumberOfArrivals):
    global StartTimes
    StartTimes =[[] for i in range(numberOfStations)]
    global DepartureTimes
    DepartureTimes =[[] for i in range(numberOfStations)]
    global ArrivalTimes
    ArrivalTimes =[[] for i in range(numberOfStations)]
    global numberArrivals
    run(numberArrivals=TotalNumberOfArrivals)
    xAxis = [] 
    for i in range(TotalNumberOfArrivals):
        xAxis.append(i+1)
    yAxisCycleTime = DepartureTimes[-1]
    plt.figure(0)
    yAxisThroughput = [x/y for x,y in zip(xAxis,yAxisCycleTime)]
    plt.plot(xAxis,yAxisThroughput)
    plt.title('Throughput')
    plt.xlabel('Number of arrivals')
    plt.figure(1)
    plt.plot(xAxis,yAxisCycleTime)
    plt.title('Cycle time')
    plt.xlabel('Number of arrivals')
    

graphs(TotalNumberOfArrivals = 100)

#print the output table
def output_table():
    for n in range(numberOfStations):
        data = {'Job': range(1,len(StartTimes[0])+1),'ArrivalTime S%d'%(n+1): ArrivalTimes[n],'StartTime S%d'%(n+1): StartTimes[n], 'DepartureTime S%d'%(n+1): DepartureTimes[n]}
        df = pd.DataFrame(data)
        print(df)
    
output_table()
