#!/usr/bin/env python
import random

import numpy as np
import pandas as pd

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

from scoop import futures
import pickle

import sys

stock = "AAPL"
trends_data = np.loadtxt(f"{stock}training2.csv",delimiter=',', skiprows=1) 

def evaluation(individual):
    fitness = 0 
    for i in range(len(trends_data)-1):
        individual_arr = np.array(individual)
        trend = trends_data[i,1:].dot(individual_arr)
        if trend > 3:
            if trends_data[i+1, 0] > trends_data[i, 0]: 
                fitness +=1 
        elif trend <= 0:
            if trends_data[i+1, 0] < trends_data[i, 0]:
                fitness +=1
        else:
            if abs(trends_data[i+1, 0] == trends_data[i, 0]) < 1e-2:
                fitness +=1
    return fitness,

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
# Attribute generator 
toolbox.register("weights", random.randint, 1, 3)
# Structure initializers
toolbox.register("individual", tools.initRepeat, creator.Individual, 
    toolbox.weights, 9)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
# Evaluation function
toolbox.register("evaluate", evaluation)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutUniformInt, indpb=0.05, low=1, up=3)
toolbox.register("select", tools.selTournament, tournsize=10)

# Parallel map
toolbox.register("map", futures.map)
pkl = sys.argv[1]
n = 256
with open(pkl, "rb") as cp_file:
    cp = pickle.load(cp_file)
pop = cp["pop"]
start_gen = cp["generation"]
halloffame = cp["halloffame"]
logbook = cp["logbook"]
random.setstate(cp["rndstate"])
print(halloffame[0])
