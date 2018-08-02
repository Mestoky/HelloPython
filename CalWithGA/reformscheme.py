from gaft import GAEngine
from gaft.components import BinaryIndividual
from gaft.components import Population
from gaft.operators import TournamentSelection
from gaft.operators import UniformCrossover
from gaft.operators import FlipBitMutation
from gaft.analysis.fitness_store import FitnessStore
from gaft.analysis.console_output import ConsoleOutput
from prosimu import *
import numpy as np


# Determine the reform scheme with GA
def doga(units, ploads, hload, size=50, ng=5, pc=0.8, pe=0.5, pm=0.1):
    # 计算不同典型日下，最小运行成本均值
    def calcost(indv):
        # 输入改造方案
        for chpunit, rtype in zip(chpunits, indv):
            chpunit.rtype = rtype
        meancost = 0
        # ploads为字典，key:典型日出现的概率,value:[典型日负荷曲线,风电出力极限曲线1,...,风电出力极限曲线n]
        for p in ploads.keys():
            x = ProSimu()
            x.pload = ploads[p][0]
            x.hload = hload
            wn = 0
            for wpunit in wpunits:
                wn += 1
                wpunit.maxwp = ploads[p][wn]
            x.units = units
            meancost += x.getoptvalue()*p
        return meancost

    ranges = list()
    wpunits = list()
    chpunits = list()
    for unit in units:
        if unit.ptype == 0:  # Wind Power Unit
            wpunits += [unit]
        elif unit.ptype == 2:  # CHP Unit-1
            ranges += [(0, 4)]
            chpunits += [unit]
        elif unit.ptype == 3:  # CHP Unit-2
            ranges += [(0, 3)]
            chpunits += [unit]
    template = BinaryIndividual(ranges, eps=1)
    population = Population(indv_template=template, size=size).init()
    selection = TournamentSelection()
    crossover = UniformCrossover(pc=pc, pe=pe)
    mutation = FlipBitMutation(pm=pm)
    engine = GAEngine(population=population, selection=selection, crossover=crossover, mutation=mutation,
                      analysis=[ConsoleOutput, FitnessStore])

    @engine.fitness_register
    @engine.minimize
    def fitness(indv):
        # print(type(float(calcost(indv.solution))))
        return float(calcost(indv.solution))

    engine.run(ng=ng)

    bestindv = population.best_indv(engine.fitness).solution
    for unitt, rtype in zip(chpunits, bestindv):
        unitt.rtype = rtype
    result = calcost(bestindv)
    print('Best individual:', bestindv)
    print('Optimal result:', result)

    

