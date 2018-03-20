from gurobipy import *


def prod_simulation(plants, pload, hload, mats, pfctr):
    try:
        # Create a new model
        m = Model("prod_simulation")
        # 决策变量
        wplants = list()  # 风电场列表
        chpplants = list()  # CHP电厂列表
        wpschedules = list()  # 风电出力计划列表
        pchpschedules = list()  # CHP电厂电出力计划列表
        hchpschedules = list()  # CHP电厂热出力计划列表
        isopens = list()  # CHP电厂开机计划列表
        for plant in plants:
            if plant.ptype == 0:
                wplants.append(plant)
                wpschedules.append(list(m.addVars(list(range(len(pload))), vtype=GRB.CONTINUOUS,
                                                  name='%s wp-schedule' % plant.name).values()))
            elif plant.ptype == 1:
                chpplants.append(plant)
                pchpschedules.append(list(m.addVars(list(range(len(pload))), vtype=GRB.CONTINUOUS,
                                                    name='%s e-schedule' % plant.name).values()))
                hchpschedules.append(list(m.addVars(list(range(len(hload))), vtype=GRB.CONTINUOUS,
                                                    name='%s h-schedule' % plant.name).values()))
                isopens.append(m.addVar(vtype=GRB.BINARY, name='%s isopen' % plant.name))
        m.update()
        # 约束
        # 风电出力约束
        bigm = 10**4
        for plant, wpschedule in zip(wplants, wpschedules):
            m.addConstrs((wpschedule[i] <= plant.maxwp[i] for i in range(len(pload))),
                         name='%s wp-u-cstr' % plant.name)
            m.addConstrs((wpschedule[i] >= 0 for i in range(len(pload))),
                         name='%s wp-d-cstr' % plant.name)
        # CHP出力约束
        for plant, pchpschedule, hchpschedule, isopen in zip(chpplants, pchpschedules, hchpschedules, isopens):
            m.addConstrs((pchpschedule[i] <= isopen * bigm for i in range(len(pload))),
                         name='%s e-chp-u-cstr1' % plant.name)
            m.addConstrs((pchpschedule[i] >= 0 for i in range(len(pload))),
                         name='%s e-chp-d-cstr1' % plant.name)
            m.addConstrs((hchpschedule[i] <= isopen * bigm for i in range(len(pload))),
                         name='%s h-chp-u-cstr1' % plant.name)
            m.addConstrs((hchpschedule[i] >= 0 for i in range(len(pload))),
                         name='%s h-chp-d-cstr1' % plant.name)
            m.addConstrs((pchpschedule[i] <= plant.pbound[1] + (1-isopen) * bigm
                          for i in range(len(pload))), name='%s e-chp-u-cstr2' % plant.name)
            m.addConstrs((plant.pbound[0] - (1-isopen) * bigm <= pchpschedule[i]
                          for i in range(len(pload))), name='%s e-chp-d-cstr2' % plant.name)
            m.addConstrs((hchpschedule[i] <= plant.hbound[1] + (1-isopen) * bigm
                          for i in range(len(pload))), name='%s h-chp-u-cstr2' % plant.name)
            m.addConstrs((plant.hbound[0] - (1-isopen) * bigm <= hchpschedule[i]
                          for i in range(len(pload))), name='%s h-chp-d-cstr2' % plant.name)
        # 电热供需约束
        m.update()
        p_intime = list(zip(*(wpschedules + pchpschedules)))
        h_intime = list(zip(*hchpschedules))
        m.addConstrs((sum(p_intime[i]) == pload[i] for i in range(len(pload))), name='pload-cstr')
        m.addConstrs((sum(h_intime[i]) == hload[i] for i in range(len(hload))), name='hload-cstr')
        # 潮流约束
        m.addConstrs((quicksum(map(lambda x, y: x*y, mats[j], p_intime[i])) <= pfctr[j]
                      for j in range(len(pfctr)) for i in range(len(pload))), name='pf-u-cstr')
        m.addConstrs((quicksum(map(lambda x, y: x*y, mats[j], p_intime[i])) >= -pfctr[j]
                      for j in range(len(pfctr)) for i in range(len(pload))), name='pf-d-cstr')
        m.update()
        # Set objective
        m.setObjective(cal_cost(chpplants, pchpschedules, hchpschedules), GRB.MINIMIZE)
        m.optimize()
        for v in m.getVars():
            print(v.varName, v.x)
        print('Obj:', m.objVal)
        for c in m.getConstrs():
            print(c.ConstrName, c.Slack)
    except GurobiError:
        print('Error reported')


class Plant:
    def __init__(self, *, ptype, pbound=None, hbound=None, costfun=lambda x: 0, maxwp=None, reformtype=None, name=None):
        self.name = name
        self.ptype = ptype
        self.pbound = pbound
        self.hbound = hbound
        self.costfun = costfun
        self.maxwp = maxwp
        self.reformtype = reformtype


def cal_cost(chpplants, pchpschedules, hchpschedules):
    result = 0
    for plant, pchpschedule, hchpschedule in zip(chpplants, pchpschedules, hchpschedules):
        result = result + quicksum(map(plant.costfun, pchpschedule, hchpschedule))
    return result



