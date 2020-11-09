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

from sys import argv, exit
if len(argv) < 2:
    print("ERROR: Argument 'stock' not given. Exiting...")
    exit()

pkl = argv[1]
# pkl_cp = pkl.split("/")[-1].split("_")
# stock_name = pkl_cp[0]
# CXPB = pkl_cp[1].split("CXPB")[-1]
# MUTPB = pkl_cp[2].split("MUTPB")[-1]
# n = pkl_cp[3].split("n")[-1].split('.')[0]

stock_file = argv[2]
trends_data = np.loadtxt(f"{stock_file}",delimiter=',', skiprows=1) 

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
            if abs(trends_data[i+1, 0] == trends_data[i, 0]) < 1e-5:
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
with open(pkl, "rb") as cp_file:
    cp = pickle.load(cp_file)
pop = cp["pop"]
start_gen = cp["generation"]
halloffame = cp["halloffame"]
logbook = cp["logbook"]
random.setstate(cp["rndstate"])

fitness = evaluation(halloffame[0])
print(f"Weights:{halloffame[0]} - FITNESS:{fitness}")
