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

# CXPB  is the probability with which two individuals
#       are crossed
#
# MUTPB is the probability for mutating an individual
CXPB, MUTPB, stock_file = sys.argv[1:3]

trends_data = np.loadtxt(stock_file,delimiter=',', skiprows=1) 

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

def main(checkpoint=None):
    pkl = "GA4_AAPLtraining2.pkl"
    n = 256
    if checkpoint:
        # A file name has been given, then load the data from the file
        with open(checkpoint, "rb") as cp_file:
            cp = pickle.load(cp_file)
        pop = cp["pop"]
        start_gen = cp["generation"]
        halloffame = cp["halloffame"]
        logbook = cp["logbook"]
        random.setstate(cp["rndstate"])
    else:
        # Start a new evolution
        pop = toolbox.population(n=n)
        start_gen = 0
        halloffame = tools.HallOfFame(maxsize=1)
        logbook = tools.Logbook()
    
    # Evaluate the entire population
    fitnesses = list(toolbox.map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    # Extracting all the fitnesses of the population
    fits = [ind.fitness.values[0] for ind in pop]
    # Variable keeping track of the number of generations
    gen = start_gen
    
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("max", np.max)
    stats.register("min", np.min)
    stats.register("std", np.std)


    best = [0, pop[0]]
    # Begin the evolution
    while gen <= 2000:
        # A new generation
        gen = gen + 1
        # Select the next generation individuals
        offspring = toolbox.select(pop, n)
        # Clone the selected individuals
        offspring = list(toolbox.map(toolbox.clone, offspring))
        
        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values
                
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        pop[:] = offspring
        
        halloffame.update(pop)
        record = stats.compile(pop)
        logbook.record(gen=gen, evals=len(invalid_ind), **record)

        
        if gen % 20 == 0:
            # Fill the dictionary using the dict(key=value[, ...]) constructor
            cp = dict(pop=pop, generation=gen, halloffame=halloffame,
                      logbook=logbook, rndstate=random.getstate())

            with open(pkl, "wb") as cp_file:
                pickle.dump(cp, cp_file)

        
        print(logbook.stream)
if __name__ == '__main__':
    main()
